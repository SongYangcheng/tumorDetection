"""
视频检测路由
支持视频上传检测和实时流检测
"""

from flask import Blueprint, request, jsonify, current_app, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.user import User
from models.medical_image import MedicalImage
from utils.video_processing import VideoProcessor, analyze_video_summary
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import cv2
import numpy as np

video_detection_bp = Blueprint('video_detection', __name__)

# 视频上传目录 - 使用应用配置中的路径
def get_video_upload_folder():
    """获取视频上传文件夹路径（从Flask应用配置）"""
    from flask import current_app
    uploads_dir = current_app.config.get('UPLOADS_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'medical_images'))
    # 获取uploads根目录（去掉medical_images）
    uploads_root = os.path.dirname(uploads_dir)
    video_folder = os.path.join(uploads_root, 'videos')
    os.makedirs(video_folder, exist_ok=True)
    return video_folder

# 全局视频处理器
video_processor = None

def get_video_processor():
    """获取或初始化视频处理器"""
    global video_processor
    if video_processor is None:
        model_path = current_app.config.get('MODEL_PATH', 'backend/yolov8n.pt')
        video_processor = VideoProcessor(model_path)
    return video_processor


@video_detection_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_video():
    """
    上传视频进行检测
    
    POST /api/video/upload
    Form-data:
        - file: 视频文件
        - patient_id: 患者ID
        - patient_name: 患者姓名
        - conf_threshold: 置信度阈值（可选，默认0.25）
        - frame_interval: 帧间隔（可选，默认30）
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id))
        
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 验证视频格式
        allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if ext not in allowed_extensions:
            return jsonify({'error': '不支持的视频格式，仅支持: mp4, avi, mov, mkv, flv, wmv'}), 400
        
        # 获取参数
        patient_id = request.form.get('patient_id', '')
        patient_name = request.form.get('patient_name', '')
        conf_threshold = float(request.form.get('conf_threshold', 0.25))
        frame_interval = int(request.form.get('frame_interval', 30))
        
        # 保存视频
        import uuid
        unique_filename = f"{uuid.uuid4()}_{filename}"
        video_folder = get_video_upload_folder()
        video_path = os.path.join(video_folder, unique_filename)
        file.save(video_path)
        
        # 获取视频信息
        processor = get_video_processor()
        video_info = processor.get_video_info(video_path)
        
        # 提取关键帧并检测
        frame_results = []
        for frame_num, frame in processor.extract_frames(
            video_path, 
            frame_interval=frame_interval,
            max_frames=100
        ):
            detection = processor.detect_frame(frame, conf_threshold)
            frame_results.append({
                'frame': frame_num,
                **detection
            })
        
        # 生成摘要
        summary = analyze_video_summary(frame_results)
        
        # 创建医学影像记录
        medical_image = MedicalImage(
            filename=filename,
            original_filename=file.filename,
            filepath=video_path,
            file_size=os.path.getsize(video_path),
            mime_type=file.content_type,
            patient_id=patient_id,
            patient_name=patient_name,
            modality='Video',
            body_part='Brain',
            scan_date=datetime.utcnow().date(),
            status='completed',
            tumor_detected=summary['frames_with_tumor'] > 0,
            confidence_score=summary['avg_confidence'],
            detection_result=json.dumps({
                'video_info': video_info,
                'summary': summary,
                'frame_results': frame_results[:10]  # 只保存前10帧详情
            }),
            uploaded_by=current_user_id
        )
        
        db.session.add(medical_image)
        db.session.commit()
        
        return jsonify({
            'message': '视频上传并分析成功',
            'image_id': medical_image.id,
            'video_info': video_info,
            'summary': summary,
            'sample_frames': frame_results[:5]  # 返回前5帧结果
        }), 201
    
    except Exception as e:
        db.session.rollback()
        import traceback
        error_detail = traceback.format_exc()
        current_app.logger.error(f"视频上传失败: {str(e)}\n{error_detail}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@video_detection_bp.route('/stream/detect', methods=['POST'])
@jwt_required()
def detect_stream_frame():
    """
    实时流帧检测
    
    POST /api/video/stream/detect
    JSON Body:
        - frame: base64编码的图像帧
        - conf_threshold: 置信度阈值（可选）
    """
    try:
        data = request.get_json()
        
        if 'frame' not in data:
            return jsonify({'error': '缺少帧数据'}), 400
        
        frame_base64 = data['frame']
        conf_threshold = data.get('conf_threshold', 0.25)
        
        # 解码帧
        processor = get_video_processor()
        frame = processor.base64_to_frame(frame_base64)
        
        # 检测
        detection = processor.detect_frame(frame, conf_threshold)
        
        # 在帧上绘制检测框
        if detection['has_tumor']:
            for box, conf in zip(detection['boxes'], detection['confidences']):
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f'{conf:.2f}', (x1, y1-10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # 转换回base64
        annotated_frame = processor.frame_to_base64(frame)
        
        return jsonify({
            'detection': detection,
            'annotated_frame': annotated_frame
        }), 200
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        current_app.logger.error(f"实时检测失败: {str(e)}\n{error_detail}")
        return jsonify({'error': f'检测失败: {str(e)}'}), 500


@video_detection_bp.route('/stream/info', methods=['GET'])
@jwt_required()
def get_stream_info():
    """
    获取流检测配置信息
    
    GET /api/video/stream/info
    """
    try:
        processor = get_video_processor()
        
        return jsonify({
            'model_loaded': processor.model is not None,
            'supported_formats': ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'],
            'default_conf_threshold': 0.25,
            'max_frame_size': '1920x1080'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@video_detection_bp.route('/process/<int:video_id>', methods=['POST'])
@jwt_required()
def process_uploaded_video(video_id):
    """
    处理已上传的视频，生成带检测框的视频
    
    POST /api/video/process/<video_id>
    JSON Body:
        - conf_threshold: 置信度阈值（可选）
        - frame_interval: 帧间隔（可选）
    """
    try:
        current_user_id = get_jwt_identity()
        
        medical_image = MedicalImage.query.filter_by(
            id=video_id,
            uploaded_by=int(current_user_id)
        ).first()
        
        if not medical_image:
            return jsonify({'error': '视频不存在'}), 404
        
        if not os.path.exists(medical_image.filepath):
            return jsonify({'error': '视频文件不存在'}), 404
        
        data = request.get_json() or {}
        conf_threshold = data.get('conf_threshold', 0.25)
        frame_interval = data.get('frame_interval', 1)
        
        # 生成输出路径
        output_filename = f"processed_{os.path.basename(medical_image.filepath)}"
        video_folder = get_video_upload_folder()
        output_path = os.path.join(video_folder, output_filename)
        
        # 处理视频
        processor = get_video_processor()
        results = processor.process_video(
            medical_image.filepath,
            output_path,
            conf_threshold,
            frame_interval
        )
        
        # 生成摘要
        summary = analyze_video_summary(results)
        
        # 更新数据库记录
        medical_image.detection_result = json.dumps({
            'summary': summary,
            'processed_video_path': output_path,
            'conf_threshold': conf_threshold
        })
        medical_image.tumor_detected = summary['frames_with_tumor'] > 0
        medical_image.confidence_score = summary['avg_confidence']
        medical_image.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'message': '视频处理完成',
            'summary': summary,
            'processed_video_url': f'/uploads/videos/{output_filename}'
        }), 200
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        current_app.logger.error(f"视频处理失败: {str(e)}\n{error_detail}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500
