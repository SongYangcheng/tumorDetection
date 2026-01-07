"""
模型对比API路由
支持YOLO和UNet模型的切换和对比
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.medical_image import MedicalImage
from utils.model_manager import ModelManager
import os
import json
from datetime import datetime

model_comparison_bp = Blueprint('model_comparison', __name__)


@model_comparison_bp.route('/predict/<int:image_id>', methods=['POST'])
@jwt_required()
def predict_with_model(image_id):
    """
    使用指定模型进行预测
    
    POST /api/model/predict/<image_id>
    Body: {
        "model_type": "yolo" | "unet",
        "weight_path": "weights/Yolov11_best.pt",
        "conf_threshold": 0.25
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        model_type = data.get('model_type', 'yolo')
        weight_path = data.get('weight_path', '')
        conf_threshold = data.get('conf_threshold', 0.25)
        
        # 获取医学影像
        medical_image = MedicalImage.query.filter_by(
            id=image_id,
            uploaded_by=int(current_user_id)
        ).first()
        
        if not medical_image:
            return jsonify({'error': '影像不存在或无权限访问'}), 404
        
        if not os.path.exists(medical_image.filepath):
            return jsonify({'error': '影像文件不存在'}), 404
        
        # 初始化模型管理器
        backend_root = os.path.dirname(os.path.dirname(__file__))
        manager = ModelManager(backend_root)
        
        # 解析权重路径
        if weight_path:
            full_weight_path = os.path.join(backend_root, weight_path)
            if not os.path.exists(full_weight_path):
                return jsonify({'error': f'权重文件不存在: {weight_path}'}), 404
        else:
            # 使用默认权重
            if model_type == 'yolo':
                full_weight_path = os.path.join(backend_root, 'weights', 'Yolov11_best.pt')
            else:
                full_weight_path = os.path.join(backend_root, 'weights', 'ResNeXt50_best.pt')
        
        # 加载模型
        device = 'cuda' if current_app.config.get('USE_GPU', False) else 'cpu'
        model, detected_type = manager.load_model(
            full_weight_path,
            model_type=model_type,
            conf_threshold=conf_threshold,
            device=device
        )
        
        # 预测
        result = manager.predict(model, detected_type, medical_image.filepath)
        
        # 保存预测结果和可视化
        uploads_root = os.path.dirname(current_app.config.get('UPLOADS_DIR', ''))
        masks_dir = os.path.join(uploads_root, 'masks')
        os.makedirs(masks_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 生成可视化图像
        import cv2
        import numpy as np
        
        image = cv2.imread(medical_image.filepath)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        masks = result['segmentation_result']['masks']
        combined_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        if masks:
            for mask in masks:
                if mask.shape != image.shape[:2]:
                    mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
                combined_mask = np.maximum(combined_mask, (mask > 0.5).astype(np.uint8) * 255)
            
            # 生成叠加图
            colored_mask = np.zeros_like(image_rgb)
            if detected_type == 'yolo':
                colored_mask[:, :, 0] = combined_mask  # 红色
            else:
                colored_mask[:, :, 2] = combined_mask  # 蓝色
            
            overlay = cv2.addWeighted(image_rgb, 0.7, colored_mask, 0.3, 0)
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay, contours, -1, (255, 255, 0), 2)
        else:
            # 即使没有检测到肿瘤，也生成原图overlay
            overlay = image_rgb.copy()
            # 添加"未检测到肿瘤"文字提示
            cv2.putText(overlay, 'No tumor detected', (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 100, 100), 2)
        
        # 保存overlay
        overlay_filename = f'{detected_type}_overlay_{image_id}_{timestamp}.png'
        overlay_path = os.path.join(masks_dir, overlay_filename)
        cv2.imwrite(overlay_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        overlay_url = f'/uploads/masks/{overlay_filename}'
        
        # 保存结果到数据库
        from models.medical_image import db
        
        if detected_type == 'yolo':
            # 保存YOLO结果
            medical_image.yolo_has_tumor = result['tumor_detected']
            medical_image.yolo_num_instances = result['metrics']['num_instances']
            medical_image.yolo_tumor_ratio = result['metrics']['tumor_ratio']
            medical_image.yolo_avg_confidence = result['metrics']['avg_confidence']
            medical_image.yolo_tumor_pixels = result['metrics']['tumor_pixels']
            medical_image.yolo_total_pixels = result['metrics']['total_pixels']
            medical_image.yolo_mask_overlay_path = overlay_url
            
            # 构建完整的实例信息并序列化为JSON
            if result['segmentation_result']['confidences']:
                import json
                yolo_instances = [
                    {
                        'id': i + 1,
                        'confidence': float(conf),
                        'area': int(np.sum(mask > 0)) if i < len(result['segmentation_result']['masks']) else 0,
                        'bbox': result['segmentation_result']['boxes'][i] if i < len(result['segmentation_result']['boxes']) else None
                    }
                    for i, (conf, mask) in enumerate(zip(
                        result['segmentation_result']['confidences'],
                        result['segmentation_result']['masks']
                    ))
                ]
                medical_image.yolo_instances = json.dumps(yolo_instances)
            
            # 计算位置信息（如果有检测到肿瘤）
            if result['tumor_detected'] and result['segmentation_result']['boxes']:
                boxes = result['segmentation_result']['boxes']
                # 使用第一个（最大）实例的边界框
                bbox = boxes[0]
                medical_image.yolo_tumor_bbox_x1 = float(bbox[0])
                medical_image.yolo_tumor_bbox_y1 = float(bbox[1])
                medical_image.yolo_tumor_bbox_x2 = float(bbox[2])
                medical_image.yolo_tumor_bbox_y2 = float(bbox[3])
                
                # 计算中心点
                centroid_x = (bbox[0] + bbox[2]) / 2
                centroid_y = (bbox[1] + bbox[3]) / 2
                medical_image.yolo_tumor_centroid_x = float(centroid_x)
                medical_image.yolo_tumor_centroid_y = float(centroid_y)
                
                # 计算风险等级
                from routes.yolo_detection import calculate_risk_level, calculate_surgical_accessibility, generate_location_description
                medical_image.yolo_risk_level = calculate_risk_level(
                    result['metrics']['tumor_ratio'], 
                    result['metrics']['num_instances']
                )
                
                # 计算手术可达性（使用已读取的image变量）
                img_height, img_width = image.shape[:2]
                medical_image.yolo_surgical_accessibility = calculate_surgical_accessibility(
                    centroid_x, centroid_y, img_width, img_height
                )
                
                # 生成位置描述
                medical_image.yolo_location_description = generate_location_description(
                    bbox, img_width, img_height
                )
            
            # 保存模型版本
            medical_image.yolo_model_version = 'YOLO11'
        else:
            # 保存UNet结果到新字段
            medical_image.unet_has_tumor = result['tumor_detected']
            medical_image.unet_num_instances = result['metrics']['num_instances']
            medical_image.unet_tumor_ratio = result['metrics']['tumor_ratio']
            medical_image.unet_avg_confidence = result['metrics']['avg_confidence']
            medical_image.unet_tumor_pixels = result['metrics']['tumor_pixels']
            medical_image.unet_total_pixels = result['metrics']['total_pixels']
            medical_image.unet_mask_overlay_path = overlay_url
            
            # 序列化instances为JSON
            if 'instances' in result and result['instances']:
                import json
                medical_image.unet_instances = json.dumps(result['instances'])
            
            # 计算位置信息（如果有检测到肿瘤）
            if result['tumor_detected'] and result['segmentation_result']['boxes']:
                boxes = result['segmentation_result']['boxes']
                # 使用第一个（最大）实例的边界框
                bbox = boxes[0]
                medical_image.unet_tumor_bbox_x1 = float(bbox[0])
                medical_image.unet_tumor_bbox_y1 = float(bbox[1])
                medical_image.unet_tumor_bbox_x2 = float(bbox[2])
                medical_image.unet_tumor_bbox_y2 = float(bbox[3])
                
                # 计算中心点
                centroid_x = (bbox[0] + bbox[2]) / 2
                centroid_y = (bbox[1] + bbox[3]) / 2
                medical_image.unet_tumor_centroid_x = float(centroid_x)
                medical_image.unet_tumor_centroid_y = float(centroid_y)
                
                # 计算风险等级
                from routes.yolo_detection import calculate_risk_level, calculate_surgical_accessibility, generate_location_description
                medical_image.unet_risk_level = calculate_risk_level(
                    result['metrics']['tumor_ratio'], 
                    result['metrics']['num_instances']
                )
                
                # 计算手术可达性（使用已读取的image变量）
                img_height, img_width = image.shape[:2]
                medical_image.unet_surgical_accessibility = calculate_surgical_accessibility(
                    centroid_x, centroid_y, img_width, img_height
                )
                
                # 生成位置描述
                medical_image.unet_location_description = generate_location_description(
                    bbox, img_width, img_height
                )
            
            # 保存模型版本
            medical_image.unet_model_version = 'UNet (ResNeXt50)'
            
        # 记录最后使用的模型
        medical_image.last_model_used = detected_type
        
        try:
            db.session.commit()
            current_app.logger.info(f"{detected_type.upper()}预测结果已保存到数据库")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"保存结果到数据库失败: {e}")
        
        # 返回结果
        return jsonify({
            'success': True,
            'model_type': detected_type,
            'data': {
                **result['metrics'],
                'tumor_detected': result['tumor_detected'],
                'overlay_url': overlay_url,
                'num_instances': result['metrics']['num_instances'],
                'instances': [
                    {
                        'instance_id': i+1,
                        'confidence': float(conf),
                        'bbox': box
                    }
                    for i, (conf, box) in enumerate(zip(
                        result['segmentation_result']['confidences'],
                        result['segmentation_result']['boxes']
                    ))
                ]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.exception("模型预测失败")
        return jsonify({'error': f'预测失败: {str(e)}'}), 500


@model_comparison_bp.route('/compare/<int:image_id>', methods=['POST'])
@jwt_required()
def compare_models(image_id):
    """
    对比YOLO和UNet两个模型的预测结果
    
    POST /api/model/compare/<image_id>
    Body: {
        "yolo_weight": "weights/Yolov11_best.pt",
        "unet_weight": "weights/ResNeXt50_best.pt",
        "conf_threshold": 0.25
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        yolo_weight = data.get('yolo_weight', 'weights/Yolov11_best.pt')
        unet_weight = data.get('unet_weight', 'weights/ResNeXt50_best.pt')
        conf_threshold = data.get('conf_threshold', 0.25)
        
        # 获取医学影像
        medical_image = MedicalImage.query.filter_by(
            id=image_id,
            uploaded_by=int(current_user_id)
        ).first()
        
        if not medical_image:
            return jsonify({'error': '影像不存在或无权限访问'}), 404
        
        if not os.path.exists(medical_image.filepath):
            return jsonify({'error': '影像文件不存在'}), 404
        
        # 初始化模型管理器
        backend_root = os.path.dirname(os.path.dirname(__file__))
        manager = ModelManager(backend_root)
        
        # 加载YOLO模型
        yolo_path = os.path.join(backend_root, yolo_weight)
        if not os.path.exists(yolo_path):
            return jsonify({'error': f'YOLO权重文件不存在: {yolo_weight}'}), 404
        
        device = 'cuda' if current_app.config.get('USE_GPU', False) else 'cpu'
        yolo_model, _ = manager.load_model(yolo_path, model_type='yolo', conf_threshold=conf_threshold, device=device)
        
        # 加载UNet模型
        unet_path = os.path.join(backend_root, unet_weight)
        if not os.path.exists(unet_path):
            return jsonify({'error': f'UNet权重文件不存在: {unet_weight}'}), 404
        
        unet_model, _ = manager.load_model(unet_path, model_type='unet', conf_threshold=conf_threshold, device=device)
        
        # 对比预测
        uploads_root = os.path.dirname(current_app.config.get('UPLOADS_DIR', ''))
        comparison_dir = os.path.join(uploads_root, 'comparisons')
        
        comparison_result = manager.compare_models(
            yolo_model,
            unet_model,
            medical_image.filepath,
            comparison_dir
        )
        
        # 转换路径为URL
        comparison_url = f"/uploads/comparisons/{os.path.basename(comparison_result['comparison_path'])}"
        yolo_url = f"/uploads/comparisons/{os.path.basename(comparison_result['yolo_path'])}"
        unet_url = f"/uploads/comparisons/{os.path.basename(comparison_result['unet_path'])}"
        
        return jsonify({
            'success': True,
            'data': {
                'comparison_url': comparison_url,
                'yolo_overlay_url': yolo_url,
                'unet_overlay_url': unet_url,
                'yolo_metrics': comparison_result['yolo_metrics'],
                'unet_metrics': comparison_result['unet_metrics'],
                'metrics_diff': comparison_result['metrics_comparison']
            }
        }), 200
        
    except Exception as e:
        current_app.logger.exception("模型对比失败")
        return jsonify({'error': f'对比失败: {str(e)}'}), 500


@model_comparison_bp.route('/list-weights', methods=['GET'])
@jwt_required()
def list_weights():
    """
    列出可用的模型权重文件
    
    GET /api/model/list-weights
    """
    try:
        backend_root = os.path.dirname(os.path.dirname(__file__))
        weights_dir = os.path.join(backend_root, 'weights')
        
        if not os.path.exists(weights_dir):
            return jsonify({'yolo_weights': [], 'unet_weights': []}), 200
        
        yolo_weights = []
        unet_weights = []
        
        for filename in os.listdir(weights_dir):
            if filename.endswith('.pt'):
                filepath = os.path.join(weights_dir, filename)
                file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                
                weight_info = {
                    'name': filename,
                    'path': f'weights/{filename}',
                    'size_mb': round(file_size, 2)
                }
                
                if 'yolo' in filename.lower():
                    yolo_weights.append(weight_info)
                elif 'resnext' in filename.lower() or 'unet' in filename.lower():
                    unet_weights.append(weight_info)
        
        return jsonify({
            'yolo_weights': yolo_weights,
            'unet_weights': unet_weights
        }), 200
        
    except Exception as e:
        current_app.logger.exception("列出权重文件失败")
        return jsonify({'error': f'列出失败: {str(e)}'}), 500
