"""
YOLO11脑肿瘤检测路由
集成YOLO11模型进行脑肿瘤检测和分割，保存结果到数据库
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from functools import wraps
import os
import json
import traceback
from datetime import datetime
import cv2
import numpy as np

from models import db, MedicalImage, User

try:
    from backend.utils.predictor import YOLO11TumorPredictor
except ImportError:
    try:
        from backend.utils.predictor import YOLO11TumorPredictor
    except ImportError:
        # 如果自定义predictor不可用，使用基础的YOLO模型
        from ultralytics import YOLO
        YOLO11TumorPredictor = None

yolo_detection_bp = Blueprint('yolo_detection', __name__, url_prefix='/api/yolo')


def get_yolo_predictor():
    """获取或初始化YOLO11预测器（单例模式）"""
    if not hasattr(current_app, '_yolo_predictor'):
        model_path = current_app.config.get('MODEL_PATH', 'backend/yolov8n.pt')
        try:
            # 尝试使用自定义的YOLO11脑肿瘤模型
            if YOLO11TumorPredictor:
                custom_model = current_app.config.get('YOLO11_TUMOR_MODEL', None)
                if custom_model and os.path.exists(custom_model):
                    model_path = custom_model
                
                current_app._yolo_predictor = YOLO11TumorPredictor(
                    weight_path=model_path,
                    conf_threshold=current_app.config.get('YOLO_CONF_THRESHOLD', 0.25),
                    iou_threshold=current_app.config.get('YOLO_IOU_THRESHOLD', 0.7)
                )
            else:
                # 使用基础YOLO模型
                current_app._yolo_predictor = YOLO(model_path)
        except Exception as e:
            current_app.logger.error(f"YOLO模型加载失败: {e}")
            current_app._yolo_predictor = None
    
    return current_app._yolo_predictor


def calculate_risk_level(tumor_ratio, num_instances):
    """根据肿瘤面积比和实例数计算风险等级"""
    if not tumor_ratio:
        return 'low'
    
    if tumor_ratio > 50 or num_instances > 3:
        return 'high'
    elif tumor_ratio > 20 or num_instances > 1:
        return 'medium'
    else:
        return 'low'


def calculate_surgical_accessibility(centroid_x, centroid_y, img_width, img_height):
    """
    根据肿瘤位置计算手术可达性
    中央区域难以接近，外围区域易接近
    """
    if centroid_x is None or centroid_y is None or img_width is None or img_height is None:
        return 'moderate'
    
    # 计算到中心的相对距离
    center_x, center_y = img_width / 2, img_height / 2
    distance_to_center = np.sqrt(
        ((centroid_x - center_x) / (img_width / 2)) ** 2 +
        ((centroid_y - center_y) / (img_height / 2)) ** 2
    )
    
    # 距离中心越近，可达性越差
    if distance_to_center < 0.3:
        return 'difficult'
    elif distance_to_center < 0.6:
        return 'moderate'
    else:
        return 'easy'


def generate_location_description(bbox, img_width, img_height):
    """
    根据边界框位置生成位置描述
    """
    if bbox is None:
        return "位置未知"
    
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    
    # 确定左右位置
    if center_x < img_width / 3:
        horizontal = "左侧"
    elif center_x > 2 * img_width / 3:
        horizontal = "右侧"
    else:
        horizontal = "中央"
    
    # 确定上下位置
    if center_y < img_height / 3:
        vertical = "上部"
    elif center_y > 2 * img_height / 3:
        vertical = "下部"
    else:
        vertical = "中部"
    
    return f"{horizontal}{vertical}脑组织"


@yolo_detection_bp.route('/detect/<int:image_id>', methods=['POST'])
@jwt_required()
def detect_tumor(image_id):
    """
    对指定的医学影像进行YOLO11肿瘤检测
    
    Returns:
        {
            "success": bool,
            "message": str,
            "data": {
                "image_id": int,
                "has_tumor": bool,
                "num_instances": int,
                "tumor_ratio": float,
                "avg_confidence": float,
                "risk_level": str,
                "surgical_accessibility": str,
                "segmentation_mask_url": str,
                "instances": [...]
            }
        }
    """
    try:
        # 查询医学影像
        medical_image = MedicalImage.query.get(image_id)
        if not medical_image:
            return jsonify({'success': False, 'message': '医学影像不存在'}), 404
        
        # 检查文件是否存在
        if not os.path.exists(medical_image.filepath):
            return jsonify({'success': False, 'message': '文件不存在'}), 400
        
        # 获取预测器
        predictor = get_yolo_predictor()
        if not predictor:
            return jsonify({'success': False, 'message': 'YOLO模型未初始化'}), 500
        
        # 获取图像尺寸
        img = cv2.imread(medical_image.filepath)
        if img is None:
            return jsonify({'success': False, 'message': '无法读取图像'}), 400
        
        img_height, img_width = img.shape[:2]
        
        # 执行检测
        import time
        start_time = time.time()
        analysis = predictor.analyze_prediction(medical_image.filepath, imgsz=256)
        inference_time = time.time() - start_time
        
        # 生成分割掩码
        combined_mask, num_instances = predictor.get_combined_mask(medical_image.filepath, imgsz=256)
        
        # 保存掩码
        uploads_dir = current_app.config.get('UPLOADS_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'medical_images'))
        # 获取uploads根目录（去掉medical_images）
        uploads_root = os.path.dirname(uploads_dir)
        masks_dir = os.path.join(uploads_root, 'masks')
        os.makedirs(masks_dir, exist_ok=True)
        
        mask_filename = f"mask_{image_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        mask_path = os.path.join(masks_dir, mask_filename)
        cv2.imwrite(mask_path, combined_mask)
        
        # 生成掩码叠加图
        overlay_img = img.copy()
        overlay_img[combined_mask > 0] = [0, 255, 0]  # 绿色叠加
        overlay_filename = f"overlay_{image_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        overlay_path = os.path.join(masks_dir, overlay_filename)
        cv2.imwrite(overlay_path, overlay_img)
        
        # 获取详细预测结果（包括置信度和边界框）
        results, masks, boxes, confidences = predictor.predict(
            medical_image.filepath, imgsz=256
        )
        
        # 计算肿瘤中心和边界框
        centroid_x = None
        centroid_y = None
        bbox_x1 = None
        bbox_y1 = None
        bbox_x2 = None
        bbox_y2 = None
        
        if len(boxes) > 0:
            # 合并所有边界框
            all_x1 = [int(b[0]) for b in boxes]
            all_y1 = [int(b[1]) for b in boxes]
            all_x2 = [int(b[2]) for b in boxes]
            all_y2 = [int(b[3]) for b in boxes]
            
            bbox_x1 = min(all_x1)
            bbox_y1 = min(all_y1)
            bbox_x2 = max(all_x2)
            bbox_y2 = max(all_y2)
            
            centroid_x = (bbox_x1 + bbox_x2) / 2
            centroid_y = (bbox_y1 + bbox_y2) / 2
        
        # 计算术前规划相关信息
        risk_level = calculate_risk_level(
            analysis['tumor_ratio'], 
            analysis['num_instances']
        )
        
        surgical_accessibility = calculate_surgical_accessibility(
            centroid_x, centroid_y, img_width, img_height
        )
        
        location_description = generate_location_description(
            (bbox_x1, bbox_y1, bbox_x2, bbox_y2) if bbox_x1 else None,
            img_width, img_height
        )
        
        # 生成诊断报告
        diagnostic_report = {
            'detection_time': datetime.now().isoformat(),
            'has_tumor': analysis['has_tumor'],
            'num_instances': analysis['num_instances'],
            'tumor_ratio': round(analysis['tumor_ratio'], 2),
            'avg_confidence': round(analysis['avg_confidence'], 4),
            'risk_level': risk_level,
            'surgical_accessibility': surgical_accessibility,
            'location': location_description,
            'recommendation': '建议进一步的临床评估' if analysis['has_tumor'] else '未检测到肿瘤'
        }
        
        # 准备实例信息
        instances_data = []
        for i, (conf, box) in enumerate(zip(confidences, boxes)):
            x1, y1, x2, y2 = box.astype(int).tolist()
            instances_data.append({
                'instance_id': i + 1,
                'confidence': round(float(conf), 4),
                'bbox': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
                'area': (x2 - x1) * (y2 - y1)
            })
        
        # 更新医学影像记录
        medical_image.yolo_has_tumor = analysis['has_tumor']
        medical_image.yolo_num_instances = analysis['num_instances']
        medical_image.yolo_avg_confidence = round(analysis['avg_confidence'], 4)
        medical_image.yolo_tumor_ratio = round(analysis['tumor_ratio'], 2)
        medical_image.yolo_tumor_pixels = analysis['tumor_pixels']
        medical_image.yolo_total_pixels = analysis['total_pixels']
        medical_image.yolo_mask_path = f'/uploads/masks/{mask_filename}'
        medical_image.yolo_mask_overlay_path = f'/uploads/masks/{overlay_filename}'
        medical_image.yolo_tumor_centroid_x = centroid_x
        medical_image.yolo_tumor_centroid_y = centroid_y
        medical_image.yolo_tumor_bbox_x1 = bbox_x1
        medical_image.yolo_tumor_bbox_y1 = bbox_y1
        medical_image.yolo_tumor_bbox_x2 = bbox_x2
        medical_image.yolo_tumor_bbox_y2 = bbox_y2
        medical_image.yolo_risk_level = risk_level
        medical_image.yolo_surgical_accessibility = surgical_accessibility
        medical_image.yolo_location_description = location_description
        medical_image.yolo_instances = json.dumps(instances_data, ensure_ascii=False)
        medical_image.yolo_segmentation_quality = 0.85  # 可根据实际情况调整
        medical_image.yolo_model_version = '11n'
        medical_image.yolo_inference_time = round(inference_time, 3)
        medical_image.yolo_diagnostic_report = json.dumps(diagnostic_report, ensure_ascii=False)
        medical_image.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '检测完成',
            'data': {
                'image_id': image_id,
                'has_tumor': analysis['has_tumor'],
                'num_instances': analysis['num_instances'],
                'tumor_ratio': round(analysis['tumor_ratio'], 2),
                'avg_confidence': round(analysis['avg_confidence'], 4),
                'risk_level': risk_level,
                'surgical_accessibility': surgical_accessibility,
                'location': location_description,
                'segmentation_mask_url': f'/uploads/masks/{mask_filename}',
                'overlay_url': f'/uploads/masks/{overlay_filename}',
                'inference_time': round(inference_time, 3),
                'instances': instances_data,
                'diagnostic_report': diagnostic_report
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"YOLO检测出错: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'检测失败: {str(e)}'
        }), 500


@yolo_detection_bp.route('/results/<int:image_id>', methods=['GET'])
@jwt_required()
def get_detection_results(image_id):
    """
    获取医学影像的YOLO11检测结果
    """
    try:
        medical_image = MedicalImage.query.get(image_id)
        if not medical_image:
            return jsonify({'success': False, 'message': '医学影像不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'image_id': image_id,
                'has_tumor': medical_image.yolo_has_tumor,
                'num_instances': medical_image.yolo_num_instances,
                'avg_confidence': medical_image.yolo_avg_confidence,
                'tumor_ratio': medical_image.yolo_tumor_ratio,
                'tumor_pixels': medical_image.yolo_tumor_pixels,
                'total_pixels': medical_image.yolo_total_pixels,
                'risk_level': medical_image.yolo_risk_level,
                'surgical_accessibility': medical_image.yolo_surgical_accessibility,
                'location': medical_image.yolo_location_description,
                'centroid': {
                    'x': medical_image.yolo_tumor_centroid_x,
                    'y': medical_image.yolo_tumor_centroid_y
                },
                'bbox': {
                    'x1': medical_image.yolo_tumor_bbox_x1,
                    'y1': medical_image.yolo_tumor_bbox_y1,
                    'x2': medical_image.yolo_tumor_bbox_x2,
                    'y2': medical_image.yolo_tumor_bbox_y2
                },
                'mask_url': medical_image.yolo_mask_path,
                'overlay_url': medical_image.yolo_mask_overlay_path,
                'instances': json.loads(medical_image.yolo_instances) if medical_image.yolo_instances else [],
                'segmentation_quality': medical_image.yolo_segmentation_quality,
                'model_version': medical_image.yolo_model_version,
                'inference_time': medical_image.yolo_inference_time,
                'diagnostic_report': json.loads(medical_image.yolo_diagnostic_report) if medical_image.yolo_diagnostic_report else None,
                'detection_time': medical_image.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取检测结果出错: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }), 500


@yolo_detection_bp.route('/batch-detect', methods=['POST'])
@jwt_required()
def batch_detect():
    """
    批量检测多个医学影像
    
    Request:
        {
            "image_ids": [1, 2, 3, ...]
        }
    """
    try:
        data = request.get_json()
        image_ids = data.get('image_ids', [])
        
        if not image_ids:
            return jsonify({'success': False, 'message': '未提供图像ID'}), 400
        
        results = []
        for image_id in image_ids:
            medical_image = MedicalImage.query.get(image_id)
            if not medical_image or not os.path.exists(medical_image.filepath):
                continue
            
            try:
                predictor = get_yolo_predictor()
                if not predictor:
                    continue
                
                analysis = predictor.analyze_prediction(medical_image.filepath)
                results.append({
                    'image_id': image_id,
                    'filename': medical_image.original_filename,
                    'has_tumor': analysis['has_tumor'],
                    'num_instances': analysis['num_instances'],
                    'tumor_ratio': round(analysis['tumor_ratio'], 2),
                    'avg_confidence': round(analysis['avg_confidence'], 4)
                })
            except Exception as e:
                current_app.logger.error(f"批量检测 {image_id} 失败: {e}")
                continue
        
        return jsonify({
            'success': True,
            'message': f'完成 {len(results)} 个检测',
            'data': results
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"批量检测出错: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'批量检测失败: {str(e)}'
        }), 500
