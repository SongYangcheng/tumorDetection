"""Flask 应用入口（应用工厂 + 配置集中管理）"""

from __future__ import annotations

import base64
import os
import threading
import time
import uuid
from io import BytesIO
from typing import Any, Dict

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from PIL import Image
from ultralytics import YOLO

from middleware import require_auth
from models import db
from routes.auth import auth_bp
from routes.medical_images import medical_images_bp
from routes.result_display import result_display_bp
from routes.user_management import user_management_bp
from routes.extra_endpoints import extra_bp
from routes.yolo_detection import yolo_detection_bp
from routes.video_detection import video_detection_bp
from routes.model_comparison import model_comparison_bp
from routes.reconstruction import reconstruction_bp
from utils.image_processing import postprocess_results, preprocess_image

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

try:
    import dotenv

    dotenv.load_dotenv()
except Exception:
    pass


# 构建数据库URL的函数
def _get_database_uri() -> str:
    """从环境变量构建数据库URL"""
    # 首先尝试使用完整的 DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # 如果 DATABASE_URL 包含变量占位符，展开它们
        if "${" in database_url:
            db_user = os.getenv("DB_USER", "root")
            db_password = os.getenv("DB_PASSWORD", "")
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "3306")
            db_name = os.getenv("DB_NAME", "jieke")
            database_url = database_url.replace("${DB_USER}", db_user)
            database_url = database_url.replace("${DB_PASSWORD}", db_password)
            database_url = database_url.replace("${DB_HOST}", db_host)
            database_url = database_url.replace("${DB_PORT}", db_port)
            database_url = database_url.replace("${DB_NAME}", db_name)
        return database_url
    
    # 从单个环境变量组装 MySQL URL
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "AAAaaa211")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "jieke")
    
    # 必须使用 MySQL（删除了 SQLite 默认选项）
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


# -----------------------------
# 应用工厂
# -----------------------------
def create_app(config_overrides: Dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)

    # backend目录路径
    backend_root = os.path.dirname(os.path.abspath(__file__))
    # 医学影像上传目录：backend/uploads/medical_images
    default_uploads = os.path.join(backend_root, "uploads", "medical_images")
    # 默认使用训练好的YOLOv11分割模型
    default_model_path = os.path.join(backend_root, "weights", "Yolov11_best.pt")

    app.config.from_mapping(
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "change-me"),
        JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")),
        SQLALCHEMY_DATABASE_URI=_get_database_uri(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOADS_DIR=os.getenv("UPLOADS_DIR", default_uploads),
        MODEL_PATH=os.getenv("MODEL_PATH", default_model_path),
        SAMPLE_IMAGE=os.getenv(
            "SAMPLE_IMAGE",
            os.path.join(os.path.dirname(backend_root), "tumorDetection", "images", "TCGA_HT_A61A_20000127_45.tif"),
        ),
        AUTO_LOAD_MODEL=os.getenv("AUTO_LOAD_MODEL", "true").lower() == "true",
    )

    if config_overrides:
        app.config.update(config_overrides)

    os.makedirs(app.config["UPLOADS_DIR"], exist_ok=True)

    CORS(app)
    JWTManager(app)
    db.init_app(app)

    register_blueprints(app)
    register_core_routes(app)

    if app.config.get("AUTO_LOAD_MODEL", True):
        load_model(app)

    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(medical_images_bp, url_prefix="/api/medical")
    app.register_blueprint(result_display_bp, url_prefix="/api/results")
    app.register_blueprint(user_management_bp, url_prefix="/api/admin")
    app.register_blueprint(extra_bp, url_prefix="/api")
    app.register_blueprint(video_detection_bp, url_prefix="/api/video")
    app.register_blueprint(yolo_detection_bp, url_prefix="/api/yolo")
    app.register_blueprint(model_comparison_bp, url_prefix="/api/model")
    app.register_blueprint(reconstruction_bp)


def resolve_weight_path(app: Flask, weight_path: str | None) -> str:
    project_root = os.path.dirname(os.path.dirname(__file__))
    # 优先查找 backend/weights 目录
    default_weight = os.path.join(project_root, "backend", "weights", "Yolov11_best.pt")
    if weight_path:
        if os.path.isabs(weight_path) and os.path.exists(weight_path):
            return weight_path
        # 查找 backend/weights 目录
        candidate = os.path.join(project_root, "backend", "weights", os.path.basename(weight_path))
        if os.path.exists(candidate):
            return candidate
    if os.path.exists(default_weight):
        return default_weight
    backend_default = app.config.get("MODEL_PATH")
    return backend_default if backend_default and os.path.exists(backend_default) else "yolov8n.pt"


def load_model(app: Flask) -> None:
    model_path = resolve_weight_path(app, app.config.get("MODEL_PATH"))
    try:
        app.logger.info(f"Loading YOLO model from {model_path}")
        app.extensions["yolo_model"] = YOLO(model_path)
    except Exception:
        app.logger.warning("Fallback to ultralytics default segmentation model")
        # 使用分割模型而非检测模型
        app.extensions["yolo_model"] = YOLO("yolov8n-seg.pt")


def get_model(app: Flask):
    return app.extensions.get("yolo_model")


# -----------------------------
# 核心路由注册
# -----------------------------
def register_core_routes(app: Flask) -> None:
    seg_jobs: Dict[str, Dict[str, Any]] = {}

    # 统一的uploads静态文件服务
    @app.route("/uploads/<path:subpath>/<path:filename>")
    def serve_uploads(subpath: str, filename: str):
        """提供uploads目录下所有子目录的文件访问"""
        uploads_root = os.path.dirname(app.config["UPLOADS_DIR"])  # 获取uploads根目录
        target_dir = os.path.join(uploads_root, subpath)
        return send_from_directory(target_dir, filename)
    
    # 兼容旧路径（医学影像）
    @app.route("/uploads/medical_images/<path:filename>")
    def serve_medical_upload(filename: str):
        return send_from_directory(app.config["UPLOADS_DIR"], filename)
    
    # 新增：comparisons目录支持
    @app.route("/uploads/comparisons/<path:filename>")
    def serve_comparisons(filename: str):
        uploads_root = os.path.dirname(app.config["UPLOADS_DIR"])
        comparisons_dir = os.path.join(uploads_root, 'comparisons')
        return send_from_directory(comparisons_dir, filename)

    @app.route("/")
    def home():
        return jsonify(
            {
                "message": "欢迎使用肿瘤检测API",
                "version": "1.0",
                "endpoints": {
                    "health": "/health",
                    "auth": "/api/auth/*",
                    "medical_images": "/api/medical/*",
                    "results": "/api/results/*",
                    "users": "/api/admin/*",
                },
            }
        )

    @app.route("/favicon.ico")
    def favicon():
        return "", 204

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy", "model_loaded": get_model(app) is not None})

    def run_segmentation_job(job_id: str, cfg: dict):
        try:
            seg_jobs[job_id] = {"progress": 1, "status": "running"}
            weight_path = resolve_weight_path(app, cfg.get("weightPath"))
            conf = float(cfg.get("conf", 0.25))
            try:
                yolo = YOLO(weight_path)
            except Exception:
                fallback = app.config.get("MODEL_PATH")
                yolo = YOLO(fallback if fallback and os.path.exists(fallback) else "yolov8n.pt")

            sample_image = app.config.get("SAMPLE_IMAGE")
            for p in [10, 25, 40, 60, 80]:
                seg_jobs[job_id]["progress"] = p
                time.sleep(0.5)
            if sample_image and os.path.exists(sample_image):
                img = Image.open(sample_image)
                _ = yolo(img)
            seg_jobs[job_id]["progress"] = 100
            seg_jobs[job_id]["status"] = "done"
        except Exception as exc:
            seg_jobs[job_id] = {"progress": 0, "status": "error", "error": str(exc)}

    @app.route("/segmentation/start", methods=["POST"])
    def segmentation_start():
        try:
            cfg = request.get_json() or {}
            job_id = uuid.uuid4().hex
            t = threading.Thread(target=run_segmentation_job, args=(job_id, cfg), daemon=True)
            t.start()
            return jsonify({"id": job_id})
        except Exception as exc:
            return jsonify({"error": f"启动失败: {str(exc)}"}), 500

    @app.route("/segmentation/<job_id>/progress", methods=["GET"])
    def segmentation_progress(job_id: str):
        info = seg_jobs.get(job_id)
        if not info:
            return jsonify({"progress": 0, "status": "unknown"}), 404
        return jsonify(
            {
                "progress": info.get("progress", 0),
                "status": info.get("status", "running"),
                "error": info.get("error"),
            }
        )

    @app.route("/upload", methods=["POST"])
    @require_auth
    def upload_image(current_user):
        if "file" not in request.files:
            return jsonify({"error": "没有文件"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "文件名为空"}), 400

        try:
            allowed_extensions = {"png", "jpg", "jpeg", "tif", "tiff", "dcm"}
            if "." not in file.filename or file.filename.rsplit(".", 1)[1].lower() not in allowed_extensions:
                return jsonify({"error": "不支持的文件类型"}), 400

            image = Image.open(file.stream)
            processed_image = preprocess_image(image)

            model = get_model(app)
            if model is None:
                return jsonify({"error": "模型未加载"}), 500

            results = model(processed_image)
            processed_results = postprocess_results(results)
            return jsonify({"message": "检测完成", "results": processed_results})
        except Exception as exc:
            return jsonify({"error": f"处理图像时出错: {str(exc)}"}), 500

    @app.route("/detect", methods=["POST"])
    @require_auth
    def detect_tumor(current_user):
        try:
            data = request.get_json()
            if not data or "image" not in data:
                return jsonify({"error": "缺少图像数据"}), 400

            image_data = data["image"]
            if image_data.startswith("data:image"):
                image_data = image_data.split(",", 1)[1]

            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            processed_image = preprocess_image(image)

            model = get_model(app)
            if model is None:
                return jsonify({"error": "模型未加载"}), 500

            results = model(processed_image)
            processed_results = postprocess_results(results)
            return jsonify({"message": "检测完成", "results": processed_results})
        except Exception as exc:
            return jsonify({"error": f"检测时出错: {str(exc)}"}), 500


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=8000, use_reloader=False)
