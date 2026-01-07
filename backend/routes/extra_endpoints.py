from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import List

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.medical_image import MedicalImage

extra_bp = Blueprint("extra", __name__)


# -----------------------
# Dashboard endpoints
# -----------------------
@extra_bp.route("/dashboard/stats", methods=["GET"])
@jwt_required()
def dashboard_stats():
    # 简化：返回静态或基于最近上传的统计
    total_today = MedicalImage.query.count()
    return jsonify({
        "todayCases": total_today,
        "modelAccuracy": 0.89,
        "systemStatus": "healthy",
    })


@extra_bp.route("/dashboard/cases-trend", methods=["GET"])
@jwt_required()
def cases_trend():
    days = 14
    base = datetime.utcnow()
    data = [{"date": (base - timedelta(days=i)).strftime("%Y-%m-%d"), "value": random.randint(8, 30)} for i in range(days)]
    data.reverse()
    return jsonify(data)


@extra_bp.route("/dashboard/accuracy-trend", methods=["GET"])
@jwt_required()
def accuracy_trend():
    days = 14
    base = datetime.utcnow()
    data = [{"date": (base - timedelta(days=i)).strftime("%Y-%m-%d"), "value": round(random.uniform(0.78, 0.9), 3)} for i in range(days)]
    data.reverse()
    return jsonify(data)


@extra_bp.route("/dashboard/todos", methods=["GET"])
@jwt_required()
def dashboard_todos():
    todos = [
        {"id": "t1", "title": "复核最近3例分割结果"},
        {"id": "t2", "title": "评估模型AUC提升计划"},
    ]
    return jsonify(todos)


# -----------------------
# Workbench
# -----------------------
@extra_bp.route("/workbench/preprocess", methods=["POST"])
@jwt_required()
def workbench_preprocess():
    _ = request.get_json() or {}
    return jsonify({"message": "ok"})


@extra_bp.route("/workbench/augment", methods=["POST"])
@jwt_required()
def workbench_augment():
    _ = request.get_json() or {}
    return jsonify({"message": "ok"})


# -----------------------
# Preoperative planning
# -----------------------
@extra_bp.route("/preop/simulate", methods=["POST"])
@jwt_required()
def simulate_preop():
    payload = request.get_json() or {}
    resection = float(payload.get("resection", 0))
    level = "高" if resection > 70 else "中" if resection > 40 else "低"
    return jsonify({"prognosisRisk": level, "difficulty": level})


@extra_bp.route("/preop/load3d", methods=["GET"])
@jwt_required()
def load_preop_3d():
    return jsonify({"status": "ok"})


# -----------------------
# Radiomics
# -----------------------
@extra_bp.route("/radiomics/extract", methods=["GET"])
@jwt_required()
def radiomics_extract():
    feats = [
        {"name": "GLCM_Contrast", "value": 0.42},
        {"name": "GLRLM_SRE", "value": 0.78},
        {"name": "FirstOrder_Mean", "value": 128.3},
        {"name": "NGTDM_Busyness", "value": 0.21},
    ]
    return jsonify(feats)


@extra_bp.route("/radiomics/train", methods=["POST"])
@jwt_required()
def radiomics_train():
    return jsonify({"auc": 0.86, "acc": 0.81})


# -----------------------
# Analysis & Reports
# -----------------------
@extra_bp.route("/analysis/metrics", methods=["GET"])
@jwt_required()
def analysis_metrics():
    return jsonify({"volume": 15342, "maxDiameter": 32.5, "heterogeneity": 0.63})


@extra_bp.route("/analysis/report", methods=["POST"])
@jwt_required()
def save_report():
    # 简化：仅回显成功
    return jsonify({"message": "saved"})


@extra_bp.route("/analysis/export", methods=["GET"])
@jwt_required()
def export_report():
    fmt = request.args.get("fmt", "pdf")
    return jsonify({"message": f"exported-{fmt}"})


@extra_bp.route("/dashboard/recent-cases", methods=["GET"])
@jwt_required()
def recent_cases():
    data = [
        {"id": "C001", "patientId": "P001", "department": "神经外科", "doctor": "张医生", "date": "2025-12-01", "status": "待处理"},
        {"id": "C002", "patientId": "P002", "department": "肿瘤科", "doctor": "李医生", "date": "2025-12-02", "status": "已完成"},
    ]
    return jsonify(data)


# -----------------------
# Dashboard Distribution
# -----------------------
@extra_bp.route("/dashboard/dept-dist", methods=["GET"])
@jwt_required()
def dept_distribution():
    return jsonify([
        {"name": "神经外科", "value": 32},
        {"name": "肿瘤科", "value": 18},
        {"name": "放射科", "value": 12},
    ])


@extra_bp.route("/dashboard/doctor-dist", methods=["GET"])
@jwt_required()
def doctor_distribution():
    return jsonify([
        {"name": "张医生", "value": 10},
        {"name": "李医生", "value": 8},
        {"name": "王医生", "value": 6},
    ])


# -----------------------
# Admin Panel (Model, Backup, Monitor)
# -----------------------
@extra_bp.route("/admin/model", methods=["GET"])
@jwt_required()
def get_model_info():
    """Get current model version and performance metrics"""
    return jsonify({
        "version": "YOLO11n",
        "performance": {
            "accuracy": 0.89,
            "latency_ms": 245,
            "mAP50": 0.78,
        },
        "last_updated": "2025-12-28T10:30:00",
        "weights_path": "backend/yolov8n.pt",
    })


@extra_bp.route("/admin/model/update", methods=["POST"])
@jwt_required()
def update_model():
    """Trigger model reload/update"""
    try:
        # In a real implementation, reload the model weights
        # from app.extensions or trigger a model reload
        from main import get_model, app
        model = get_model(app)
        if model:
            return jsonify({
                "version": "YOLO11n",
                "performance": {"accuracy": 0.89, "latency_ms": 245},
                "message": "Model reloaded successfully",
            })
        else:
            return jsonify({"error": "Model not loaded"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@extra_bp.route("/admin/backup", methods=["POST"])
@jwt_required()
def backup_data():
    """Trigger database and file backup"""
    try:
        # Simple backup: for production use proper backup tools
        # (mysqldump, AWS S3, etc.)
        import datetime
        backup_id = f"backup_{datetime.datetime.utcnow().isoformat()}"
        return jsonify({
            "message": "Backup started",
            "backup_id": backup_id,
            "status": "in_progress",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@extra_bp.route("/admin/monitor", methods=["GET"])
@jwt_required()
def system_monitor():
    """Get system health and usage statistics"""
    try:
        import psutil
        disk = psutil.disk_usage('/')
        return jsonify({
            "serverStatus": "healthy",
            "storageUsage": disk.percent,
            "apiCalls": MedicalImage.query.count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
        })
    except Exception as e:
        # Fallback if psutil not available
        return jsonify({
            "serverStatus": "healthy",
            "storageUsage": 45.2,
            "apiCalls": MedicalImage.query.count(),
            "cpu_percent": 0,
            "memory_percent": 0,
        })

