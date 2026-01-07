# ===============================
# 基础依赖
# ===============================
import os
import json
import base64
import numpy as np
from datetime import datetime

import cv2
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

# ===============================
# 项目内部模块
# ===============================
from models import db
from models.medical_image import MedicalImage
from utils.segmentation import visualize_segmentation_result
from utils.quantitative_analysis import TumorQuantitativeAnalyzer
from utils.surgical_planning import generate_surgical_plan
from utils.radiomics import extract_radiomics_features

from config.paths import TMP_DIR

# ===============================
# Blueprint
# ===============================
result_display_bp = Blueprint('result_display', __name__)


# ============================================================
# 分析医学影像（主接口）
# ============================================================
@result_display_bp.route('/analyze/<int:image_id>', methods=['POST'])
@jwt_required()
def analyze_medical_image(image_id):
    try:
        # =============================
        # 1️⃣ 当前用户
        # =============================
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass

        # =============================
        # 2️⃣ 获取影像记录
        # =============================
        medical_image = MedicalImage.query.filter(
            MedicalImage.id == image_id,
            MedicalImage.uploaded_by == current_user_id
        ).first()

        if not medical_image:
            return jsonify({'error': '医学影像不存在或无权限访问'}), 404

        if not os.path.exists(medical_image.filepath):
            return jsonify({'error': '影像文件不存在'}), 404

        # =============================
        # 3️⃣ 加载影像
        # =============================
        from PIL import Image

        ext = os.path.splitext(medical_image.filepath)[1].lower()
        is_nii = medical_image.filepath.lower().endswith(('.nii', '.nii.gz'))

        try:
            if ext == '.dcm':
                import pydicom
                ds = pydicom.dcmread(medical_image.filepath)
                arr = ds.pixel_array.astype(np.float32)
                arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-6)
                arr = (arr * 255).astype(np.uint8)
                image_np = np.stack([arr] * 3, axis=-1)

            elif is_nii:
                import nibabel as nib
                img = nib.load(medical_image.filepath)
                data = img.get_fdata()
                z = data.shape[2] // 2
                slice2d = data[:, :, z]
                slice2d = (slice2d - slice2d.min()) / (slice2d.max() - slice2d.min() + 1e-6)
                arr = (slice2d * 255).astype(np.uint8)
                image_np = np.stack([arr] * 3, axis=-1)

            else:
                image_np = np.array(Image.open(medical_image.filepath).convert('RGB'))

        except Exception as e:
            current_app.logger.exception("影像加载失败")
            return jsonify({'error': f'影像加载失败: {str(e)}'}), 400

        h, w = image_np.shape[:2]

        # =============================
        # 4️⃣ 获取参数：置信度阈值和权重路径
        # =============================
        data = request.get_json(silent=True) or {}
        try:
            conf = float(data.get('conf', 0.25))
        except Exception:
            conf = 0.25
        
        weight_path = data.get('weightPath', None)
        current_app.logger.info(f"使用置信度: {conf}, 权重路径: {weight_path}")

        # =============================
        # 5️⃣ 使用 YOLO 模型进行真实分割（参考YOLO11推理脚本）
        # =============================
        try:
            from utils.segmentation import TumorSegmentation
            
            # 初始化分割器（使用指定的权重路径）
            current_app.logger.info(f"初始化YOLO分割器...")
            segmentor = TumorSegmentation(weight_path=weight_path)
            
            # 执行分割（添加imgsz参数，参考参考文件）
            current_app.logger.info(f"开始YOLO分割，置信度={conf}")
            result = segmentor.segment_and_analyze(image_np, conf=conf, imgsz=256)
            
            if not result['success']:
                current_app.logger.warning("分割未成功，使用占位符")
                pred_mask = np.zeros((h, w), dtype=np.uint8)
                has_tumor = False
                num_instances = 0
                tumor_ratio = 0.0
                avg_confidence = 0.0
                instances_info = []
            else:
                seg_result = result['segmentation_result']
                metrics = result['metrics']
                
                current_app.logger.info(f"分割成功: {metrics}")
                
                # 提取掩码和置信度
                masks = seg_result.get('masks', None)
                confidences = seg_result.get('confidences', [])
                boxes = seg_result.get('boxes', [])
                
                if masks is not None and len(masks) > 0:
                    # 合并所有掩码
                    pred_mask = np.zeros((h, w), dtype=np.uint8)
                    for mask in masks:
                        if mask.shape != (h, w):
                            mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
                        else:
                            mask_resized = mask
                        pred_mask = np.maximum(pred_mask, (mask_resized > 0.5).astype(np.uint8))
                    
                    has_tumor = True
                    num_instances = metrics.get('num_instances', len(masks))
                    tumor_ratio = metrics.get('tumor_ratio', 0.0)  # 已经是百分比
                    avg_confidence = metrics.get('avg_confidence', 0.0)
                    
                    # 构建实例详情列表（参考参考文件）
                    instances_info = []
                    for i in range(len(masks)):
                        instance = {
                            'id': i + 1,
                            'confidence': float(confidences[i]) if i < len(confidences) else 0.0,
                            'area': int(np.sum(masks[i] > 0.5))
                        }
                        if i < len(boxes):
                            instance['bbox'] = boxes[i].tolist()
                        instances_info.append(instance)
                    
                    current_app.logger.info(f"检测到 {num_instances} 个肿瘤实例，平均置信度={avg_confidence:.3f}")
                else:
                    pred_mask = np.zeros((h, w), dtype=np.uint8)
                    has_tumor = False
                    num_instances = 0
                    tumor_ratio = 0.0
                    avg_confidence = 0.0
                    instances_info = []

        except Exception as e:
            current_app.logger.exception("模型推理失败，使用占位符")
            pred_mask = np.zeros((h, w), dtype=np.uint8)
            has_tumor = False
            num_instances = 0
            tumor_ratio = 0.0
            avg_confidence = 0.0
            instances_info = []

        # =============================
        # 6️⃣ 计算风险等级和手术可达性
        # =============================
        # 风险等级判断
        # 肿瘤位置（简化）
        tumor_location = medical_image.body_part or '脑部中央区域'

        # 从 metrics 中获取更精确的值（tumor_ratio: 百分比，tumor_area_ratio: 小数）
        tumor_ratio_pct = metrics.get('tumor_ratio', 0.0) if isinstance(metrics, dict) else 0.0
        tumor_area_ratio = metrics.get('tumor_area_ratio', 0.0) if isinstance(metrics, dict) else 0.0
        tumor_pixels = metrics.get('tumor_pixels', 0) if isinstance(metrics, dict) else 0

        # 计算风险等级（基于小数形式的 tumor_area_ratio）
        risk_level = 'low'
        if has_tumor:
            if tumor_area_ratio > 0.15:  # 面积占比超过15%
                risk_level = 'high'
            elif tumor_area_ratio > 0.05:  # 面积占比5%-15%
                risk_level = 'medium'

        # 手术可达性（简化判断，基于小数形式）
        surgical_accessibility = 'moderate'
        if has_tumor:
            if tumor_area_ratio < 0.05:
                surgical_accessibility = 'easy'
            elif tumor_area_ratio > 0.15:
                surgical_accessibility = 'difficult'

        segmentation_metrics = {
            'has_tumor': has_tumor,
            'num_instances': num_instances,
            'tumor_ratio': tumor_ratio_pct,  # 百分比
            'avg_confidence': avg_confidence,
            'risk_level': risk_level,
            'surgical_accessibility': surgical_accessibility,
            'location': tumor_location,
            'tumor_count': num_instances,
            'tumor_area_ratio': tumor_area_ratio,  # 小数形式
            'total_tumor_pixels': int(tumor_pixels)
        }

        # =============================
        # 7️⃣ overlay 生成并保存
        # =============================
        overlay_data_url = None
        mask_filename = None
        overlay_filename = None
        
        try:
            # 生成叠加图
            overlay_np = visualize_segmentation_result(
                image_np, {'masks': [pred_mask]}
            )
            ok, buf = cv2.imencode('.png', overlay_np.astype(np.uint8))
            if ok:
                overlay_data_url = (
                    "data:image/png;base64," +
                    base64.b64encode(buf).decode()
                )
                
                # 保存掩码和叠加图到文件
                uploads_dir = current_app.config.get('UPLOADS_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'medical_images'))
                uploads_root = os.path.dirname(uploads_dir)
                masks_dir = os.path.join(uploads_root, 'masks')
                os.makedirs(masks_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                mask_filename = f"mask_{image_id}_{timestamp}.png"
                overlay_filename = f"overlay_{image_id}_{timestamp}.png"
                
                mask_path = os.path.join(masks_dir, mask_filename)
                overlay_path = os.path.join(masks_dir, overlay_filename)
                
                # 保存掩码图（黑白）
                cv2.imwrite(mask_path, pred_mask * 255)
                # 保存叠加图（彩色）
                cv2.imwrite(overlay_path, overlay_np.astype(np.uint8))
                
                current_app.logger.info(f"已保存分割结果: {mask_path}, {overlay_path}")
        except Exception as e:
            current_app.logger.exception(f"overlay 生成或保存失败: {e}")

        # =============================
        # 8️⃣ 定量分析 / 影像组学 / 手术规划
        # =============================
        analyzer = TumorQuantitativeAnalyzer()
        mask_255 = pred_mask * 255

        quantitative_report = analyzer.create_quantitative_report(
            image_np, mask_255, {'masks': [pred_mask]}
        )

        radiomics_features = extract_radiomics_features(image_np, mask_255)

        surgical_plan = generate_surgical_plan(
            quantitative_report,
            {
                'age': medical_image.age or 50,
                'tumor_type': 'unknown',
                'tumor_location': medical_image.body_part or 'brain'
            },
            mask_255
        )

        # =============================
        # 9️⃣ 返回前端（包含完整的肿瘤检测数据）
        # =============================
        response = {
            'image_info': medical_image.to_dict(),
            'segmentation_result': {
                'success': has_tumor,
                'overlay': overlay_data_url,
                # ⭐ 重要：添加所有肿瘤详细信息，供前端WorkbenchView显示
                'has_tumor': has_tumor,
                'num_instances': num_instances,
                'tumor_ratio': tumor_ratio_pct,  # 使用正确的百分比变量
                'avg_confidence': avg_confidence,
                'risk_level': risk_level,
                'surgical_accessibility': surgical_accessibility,
                'location': tumor_location,
                'instances': instances_info  # ⭐ 添加每个实例的详细信息
            },
            'quantitative_analysis': quantitative_report,
            'radiomics_features': radiomics_features,
            'surgical_plan': surgical_plan,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }

        # =============================
        # 🔟 数据库存储（完整YOLO检测结果）
        # =============================
        # 保存YOLO检测结果到数据库
        medical_image.yolo_has_tumor = has_tumor
        medical_image.yolo_num_instances = num_instances
        medical_image.yolo_avg_confidence = avg_confidence
        medical_image.yolo_tumor_ratio = tumor_ratio_pct  # 百分比
        medical_image.yolo_tumor_pixels = int(tumor_pixels)
        medical_image.yolo_total_pixels = h * w
        
        # 保存实例级别详细信息
        if instances_info:
            medical_image.yolo_instances = json.dumps(instances_info, ensure_ascii=False)
        
        # 保存风险评估结果
        medical_image.yolo_risk_level = risk_level
        medical_image.yolo_surgical_accessibility = surgical_accessibility
        medical_image.yolo_location_description = tumor_location
        
        # 保存掩码和叠加图路径
        if mask_filename and overlay_filename:
            medical_image.yolo_mask_path = f'/uploads/masks/{mask_filename}'
            medical_image.yolo_mask_overlay_path = f'/uploads/masks/{overlay_filename}'
            current_app.logger.info(f"已设置掩码路径: {medical_image.yolo_mask_overlay_path}")
        
        # 计算肿瘤中心点和边界框（如果有检测结果）
        if has_tumor and len(boxes) > 0:
            # 使用第一个检测框的坐标
            medical_image.yolo_tumor_bbox_x1 = float(boxes[0][0])
            medical_image.yolo_tumor_bbox_y1 = float(boxes[0][1])
            medical_image.yolo_tumor_bbox_x2 = float(boxes[0][2])
            medical_image.yolo_tumor_bbox_y2 = float(boxes[0][3])
            
            # 计算中心点
            medical_image.yolo_tumor_centroid_x = (boxes[0][0] + boxes[0][2]) / 2
            medical_image.yolo_tumor_centroid_y = (boxes[0][1] + boxes[0][3]) / 2
        
        # 保存旧的detection_result字段（向后兼容）
        db_result = {
            'segmentation': {
                'tumor_detected': has_tumor,
                'metrics': segmentation_metrics,
                'instances': instances_info
            },
            'quantitative_analysis': quantitative_report,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        medical_image.tumor_detected = has_tumor
        medical_image.detection_result = json.dumps(db_result, ensure_ascii=False)
        medical_image.status = 'completed'
        
        try:
            db.session.commit()
            current_app.logger.info(f"成功保存检测结果到数据库，影像ID: {image_id}")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"保存检测结果失败: {e}")

        return jsonify(response), 200

    except Exception as e:
        current_app.logger.exception("分析医学影像失败")
        return jsonify({'error': f'分析失败: {str(e)}'}), 500
