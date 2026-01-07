"""
3D重建和术前规划路由
"""

import os
import json
import cv2
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
import numpy as np

from models.medical_image import MedicalImage, db
from utils.mesh_reconstruction import (
    reconstruct_3d_from_slices,
    reconstruct_3d_from_nii,
    export_to_stl,
    mesh_to_json
)


reconstruction_bp = Blueprint('reconstruction', __name__, url_prefix='/api/reconstruction')


@reconstruction_bp.route('/upload-nii', methods=['POST'])
@jwt_required()
def upload_nii_for_reconstruction():
    """
    直接上传NII文件进行3D重建（不依赖其他模块）
    
    POST /api/reconstruction/upload-nii
    Form-data:
        file: NII文件 (.nii 或 .nii.gz)
        spacing: 可选，体素间距 JSON字符串 [1.0, 1.0, 1.0]
        use_unet: 可选，是否使用UNet分割 (true/false)
    
    Returns:
        {
            "success": true,
            "image_id": 123,
            "model_data": {...},
            "analysis": {...}
        }
    """
    try:
        current_user_id = get_jwt_identity()
        current_app.logger.info(f"收到NII上传请求，用户ID: {current_user_id}")
        
        if 'file' not in request.files:
            current_app.logger.error("请求中没有file字段")
            return jsonify({'error': '未上传文件', 'detail': 'Form-data中缺少file字段'}), 400
        
        file = request.files['file']
        current_app.logger.info(f"接收到文件: {file.filename}")
        
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 验证文件类型
        allowed_extensions = {'.nii', '.nii.gz', '.gz'}
        file_ext = ''.join([ext for ext in ['.nii.gz', '.nii', '.gz'] if file.filename.endswith(ext)])
        if not file_ext:
            return jsonify({
                'error': '仅支持.nii或.nii.gz文件',
                'detail': f'收到文件类型: {file.filename}'
            }), 400
        
        # 保存文件到独立的NII目录
        filename = secure_filename(file.filename)
        # 获取backend根目录
        backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # NII文件存储在backend/uploads/nii_files，与PNG/JPG分开
        upload_dir = os.path.join(backend_root, 'uploads', 'nii_files')
        os.makedirs(upload_dir, exist_ok=True)
        
        current_app.logger.info(f"NII上传目录: {upload_dir}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_filename = f"{timestamp}_{filename}"
        nii_path = os.path.join(upload_dir, saved_filename)
        file.save(nii_path)
        
        current_app.logger.info(f"NII文件已保存: {nii_path}")
        
        # 解析参数
        spacing = json.loads(request.form.get('spacing', '[1.0, 1.0, 1.0]'))
        use_unet = request.form.get('use_unet', 'false').lower() == 'true'
        
        # 加载NII文件并重建
        try:
            import nibabel as nib
            nii = nib.load(nii_path)
            volume = nii.get_fdata()
            H, W, D = volume.shape
            
            current_app.logger.info(f"NII文件维度: {H}x{W}x{D}")
            
            # 如果使用UNet进行分割
            if use_unet:
                # 尝试加载UNet模型
                try:
                    from utils.predictor import BrainTumorPredictor
                    
                    # 灵活查找权重文件 - 支持多种路径结构
                    backend_dir = os.path.dirname(os.path.abspath(__file__))
                    backend_root = os.path.dirname(backend_dir)
                    
                    possible_paths = [
                        # 1. backend/weights/ (用户指定的位置)
                        os.path.join(backend_root, 'weights', 'ResNeXt50_best.pt'),
                        os.path.join('backend', 'weights', 'ResNeXt50_best.pt'),
                        # 2. backend/ai/brain_tumor/weights/ (参考代码位置)
                        os.path.join(backend_root, 'ai', 'brain_tumor', 'weights', 'ResNeXt50_best.pt'),
                        # 3. 相对路径
                        'weights/ResNeXt50_best.pt',
                        'ResNeXt50_best.pt',
                        # 4. 绝对路径（如果用户提供）
                        r'E:\python_demo\tumorDetection\tumorDetection\backend\weights\ResNeXt50_best.pt'
                    ]
                    
                    model_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            model_path = os.path.abspath(path)
                            break
                    
                    if not model_path:
                        return jsonify({
                            'error': 'UNet模型文件不存在',
                            'hint': f'请将ResNeXt50_best.pt放置到: backend/weights/ 目录下',
                            'searched_paths': possible_paths[:3]  # 只显示主要路径
                        }), 400
                    
                    current_app.logger.info(f"找到UNet模型: {model_path}")
                    
                    # 检查是否有GPU
                    import torch
                    device = 'cuda' if torch.cuda.is_available() else 'cpu'
                    current_app.logger.info(f"使用设备: {device}")
                    
                    predictor = BrainTumorPredictor(model_path, device=device, threshold=0.1)
                    
                    current_app.logger.info("开始UNet逐切片预测（包含脑部轮廓提取）...")
                    reconstruction_data = reconstruct_3d_from_nii(
                        nii_path, predictor, spacing=tuple(spacing), include_brain_outline=True
                    )
                    
                    if reconstruction_data is None:
                        return jsonify({
                            'error': '3D重建失败',
                            'hint': 'UNet预测未检测到肿瘤区域，请检查NII文件内容'
                        }), 400
                    
                except ImportError as e:
                    current_app.logger.error(f"UNet模块导入失败: {e}")
                    return jsonify({
                        'error': 'UNet模型加载失败',
                        'detail': str(e),
                        'hint': '请检查ai/brain_tumor/inference/predictor.py是否存在'
                    }), 500
                except Exception as e:
                    current_app.logger.error(f"UNet预测失败: {e}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({
                        'error': 'UNet预测过程出错',
                        'detail': str(e)
                    }), 500
            else:
                # 假设NII文件已经是分割好的掩码（直接二值化）
                current_app.logger.info("使用直接二值化方法处理NII文件")
                
                # 导入mesh_reconstruction模块
                from utils.mesh_reconstruction import extract_brain_outline
                
                masks = []
                for i in range(D):
                    slice_img = volume[:, :, i]
                    
                    # 归一化到0-255
                    if slice_img.max() > slice_img.min():
                        slice_normalized = cv2.normalize(
                            slice_img, None, 0, 255, cv2.NORM_MINMAX
                        ).astype(np.uint8)
                    else:
                        # 全零切片
                        slice_normalized = np.zeros_like(slice_img, dtype=np.uint8)
                    
                    # 二值化（阈值127）
                    _, binary_mask = cv2.threshold(
                        slice_normalized, 127, 255, cv2.THRESH_BINARY
                    )
                    masks.append(binary_mask)
                
                current_app.logger.info(f"已处理{D}个切片，开始3D重建...")
                
                # 3D重建
                vertices, faces, normals, tumor_volume = reconstruct_3d_from_slices(
                    masks, spacing=tuple(spacing), smooth=True
                )
                
                if vertices is None or len(vertices) == 0:
                    current_app.logger.warning("Marching cubes未生成有效网格")
                    
                    # 诊断信息
                    non_zero_slices = sum(1 for m in masks if np.any(m > 0))
                    total_voxels = sum(np.sum(m > 0) for m in masks)
                    
                    return jsonify({
                        'error': '3D重建失败',
                        'hint': 'NII文件可能不包含有效的肿瘤区域，或需要启用use_unet=true进行分割',
                        'diagnostics': {
                            'total_slices': D,
                            'non_zero_slices': non_zero_slices,
                            'total_voxels': int(total_voxels),
                            'volume_shape': [H, W, D],
                            'volume_min': float(np.min(volume)),
                            'volume_max': float(np.max(volume))
                        }
                    }), 400
                
                current_app.logger.info(f"3D重建成功: 顶点={len(vertices)}, 面={len(faces)}, 体积={tumor_volume:.2f}mm³")
                
                reconstruction_data = {
                    'vertices': vertices.tolist(),
                    'faces': faces.tolist(),
                    'normals': normals.tolist(),
                    'volume': float(tumor_volume),
                    'dimensions': {'height': H, 'width': W, 'depth': D},
                    'voxel_count': int(np.sum(np.stack(masks, axis=2) > 127)),
                    'spacing': spacing
                }
                
                # 也为直接二值化分支添加脑部轮廓
                try:
                    current_app.logger.info("尝试提取脑部轮廓（直接二值化模式）...")
                    brain_data = extract_brain_outline(volume, tuple(spacing))
                    if brain_data:
                        reconstruction_data['brain_outline'] = brain_data
                        current_app.logger.info(f"[成功] 脑部轮廓添加成功: 顶点{len(brain_data['vertices'])}, 面{len(brain_data['faces'])}")
                    else:
                        current_app.logger.warning("[警告] 脑部轮廓提取返回None")
                except Exception as brain_err:
                    current_app.logger.error(f"脑部轮廓提取失败: {brain_err}")
            
            # 保存到数据库（使用专用标记，与普通医学影像区分）
            medical_image = MedicalImage(
                filename=filename,
                original_filename=file.filename,
                filepath=nii_path,  # 使用filepath而不是file_url
                uploaded_by=current_user_id,
                last_model_used='nii_reconstruction'  # 专用标记，用于过滤
            )
            db.session.add(medical_image)
            db.session.commit()
            
            # 计算分析数据
            volume_cm3 = reconstruction_data['volume'] / 1000
            surface_area = estimate_surface_area(reconstruction_data['faces'], reconstruction_data['vertices'])
            vertices_array = np.array(reconstruction_data['vertices'])
            centroid = vertices_array.mean(axis=0)
            
            bbox_min = vertices_array.min(axis=0)
            bbox_max = vertices_array.max(axis=0)
            
            # 计算不规则度和紧凑度
            bbox_volume = np.prod(bbox_max - bbox_min)
            compactness = reconstruction_data['volume'] / bbox_volume if bbox_volume > 0 else 0
            
            # 风险评分
            risk_score = calculate_risk_score(
                volume_cm3,
                compactness,
                centroid
            )
            
            analysis_data = {
                'volume': reconstruction_data['volume'],
                'volume_cm3': volume_cm3,
                'surface_area': surface_area,
                'centroid': centroid.tolist(),
                'bounding_box': {
                    'min': bbox_min.tolist(),
                    'max': bbox_max.tolist()
                },
                'compactness': float(compactness),
                'risk_score': float(risk_score),
                'voxel_count': reconstruction_data['voxel_count']
            }
            
            # 验证返回数据
            has_brain_outline = 'brain_outline' in reconstruction_data
            current_app.logger.info(f"返回数据包含脑部轮廓: {has_brain_outline}")
            if has_brain_outline:
                current_app.logger.info(f"  脑部轮廓顶点数: {len(reconstruction_data['brain_outline']['vertices'])}")
                current_app.logger.info(f"  脑部轮廓面数: {len(reconstruction_data['brain_outline']['faces'])}")
            
            return jsonify({
                'success': True,
                'image_id': medical_image.id,
                'model_data': reconstruction_data,
                'analysis': analysis_data,
                'message': '3D重建成功'
            }), 200
            
        except Exception as e:
            current_app.logger.exception("NII文件处理失败")
            import traceback
            error_detail = traceback.format_exc()
            current_app.logger.error(f"完整错误堆栈:\n{error_detail}")
            
            # 清理已上传的文件
            if 'nii_path' in locals() and os.path.exists(nii_path):
                try:
                    os.remove(nii_path)
                except:
                    pass
            
            return jsonify({
                'error': f'NII处理失败: {str(e)}',
                'type': type(e).__name__,
                'detail': error_detail if current_app.debug else str(e)
            }), 500
            
    except Exception as e:
        current_app.logger.exception("upload_nii_for_reconstruction外层异常")
        import traceback
        return jsonify({
            'error': f'请求处理失败: {str(e)}',
            'type': type(e).__name__,
            'detail': traceback.format_exc() if current_app.debug else str(e)
        }), 500
            
    except Exception as e:
        current_app.logger.exception("NII上传失败")
        return jsonify({
            'error': f'上传失败: {str(e)}',
            'detail': str(e),
            'type': type(e).__name__
        }), 500


@reconstruction_bp.route('/generate/<int:image_id>', methods=['POST'])
@jwt_required()
def generate_3d_model(image_id):
    """
    为指定医学影像生成3D模型
    
    POST /api/reconstruction/generate/<image_id>
    Body: {
        "model_type": "yolo" or "unet",
        "spacing": [1.0, 1.0, 1.0],  // 可选，体素间距
        "export_stl": false  // 可选，是否导出STL
    }
    
    Returns:
        {
            "success": true,
            "model_data": {
                "vertices": [[x,y,z], ...],
                "faces": [[i,j,k], ...],
                "normals": [[nx,ny,nz], ...],
                "volume": 1234.56,  // 立方毫米
                "voxel_count": 5678,
                "dimensions": {"height": 256, "width": 256, "depth": 155}
            },
            "stl_url": "/uploads/3d_models/tumor_21.stl"  // 如果export_stl=true
        }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # 获取医学影像
        medical_image = MedicalImage.query.filter_by(
            id=image_id,
            uploaded_by=current_user_id
        ).first()
        
        if not medical_image:
            return jsonify({'error': '医学影像不存在'}), 404
        
        # 获取参数
        model_type = data.get('model_type', 'unet')
        spacing = data.get('spacing', [1.0, 1.0, 1.0])
        export_stl_flag = data.get('export_stl', False)
        
        # 检查是否有分割结果
        if model_type == 'yolo':
            mask_path = medical_image.yolo_mask_path
        else:
            mask_path = medical_image.unet_mask_path
        
        if not mask_path or not os.path.exists(mask_path):
            return jsonify({'error': f'未找到{model_type.upper()}分割结果，请先运行分割'}), 400
        
        current_app.logger.info(f"开始为影像 {image_id} 生成3D模型 (模型: {model_type})")
        
        # TODO: 实现从2D masks重建3D的逻辑
        # 这里需要根据实际情况调整，因为当前只保存了overlay图像
        # 可能需要保存完整的mask序列或使用NII文件
        
        # 临时返回示例数据
        model_data = {
            'vertices': [],
            'faces': [],
            'normals': [],
            'volume': 0,
            'voxel_count': 0,
            'dimensions': {'height': 256, 'width': 256, 'depth': 1}
        }
        
        response = {
            'success': True,
            'model_data': model_data,
            'message': '3D重建功能开发中，当前返回示例数据'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.exception("3D模型生成失败")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


@reconstruction_bp.route('/tumor-analysis/<int:image_id>', methods=['GET'])
@jwt_required()
def analyze_tumor_3d(image_id):
    """
    获取肿瘤的3D分析数据
    
    GET /api/reconstruction/tumor-analysis/<image_id>
    
    Returns:
        {
            "volume": 1234.56,  // 立方毫米
            "surface_area": 789.01,  // 平方毫米
            "centroid": [x, y, z],
            "bounding_box": {
                "min": [x, y, z],
                "max": [x, y, z]
            },
            "irregularity": 0.75,  // 不规则度 (0-1)
            "compactness": 0.68,  // 紧凑度
            "risk_score": 7.5  // 风险评分 (0-10)
        }
    """
    try:
        current_user_id = get_jwt_identity()
        
        medical_image = MedicalImage.query.filter_by(
            id=image_id,
            uploaded_by=current_user_id
        ).first()
        
        if not medical_image:
            return jsonify({'error': '医学影像不存在'}), 404
        
        # 基于已有的2D数据估算3D参数
        model_used = medical_image.last_model_used or 'yolo'
        
        if model_used == 'yolo':
            tumor_pixels = medical_image.yolo_tumor_pixels or 0
            total_pixels = medical_image.yolo_total_pixels or 1
            bbox_x1 = medical_image.yolo_tumor_bbox_x1
            bbox_y1 = medical_image.yolo_tumor_bbox_y1
            bbox_x2 = medical_image.yolo_tumor_bbox_x2
            bbox_y2 = medical_image.yolo_tumor_bbox_y2
            centroid_x = medical_image.yolo_tumor_centroid_x
            centroid_y = medical_image.yolo_tumor_centroid_y
        else:
            tumor_pixels = medical_image.unet_tumor_pixels or 0
            total_pixels = medical_image.unet_total_pixels or 1
            bbox_x1 = medical_image.unet_tumor_bbox_x1
            bbox_y1 = medical_image.unet_tumor_bbox_y1
            bbox_x2 = medical_image.unet_tumor_bbox_x2
            bbox_y2 = medical_image.unet_tumor_bbox_y2
            centroid_x = medical_image.unet_tumor_centroid_x
            centroid_y = medical_image.unet_tumor_centroid_y
        
        # 估算3D体积（假设切片厚度1mm，像素间距1mm）
        pixel_spacing = 1.0  # mm
        slice_thickness = 1.0  # mm
        estimated_volume = tumor_pixels * pixel_spacing * pixel_spacing * slice_thickness
        
        # 估算表面积（简化计算）
        if bbox_x1 and bbox_x2:
            width = abs(bbox_x2 - bbox_x1)
            height = abs(bbox_y2 - bbox_y1)
            estimated_surface_area = 2 * (width * height + width * slice_thickness + height * slice_thickness)
        else:
            estimated_surface_area = 0
        
        # 计算紧凑度（球形度）
        if estimated_volume > 0 and estimated_surface_area > 0:
            # 理想球体的表面积 = 4πr², 体积 = 4/3πr³
            ideal_radius = (3 * estimated_volume / (4 * np.pi)) ** (1/3)
            ideal_surface = 4 * np.pi * ideal_radius ** 2
            compactness = min(ideal_surface / estimated_surface_area, 1.0)
        else:
            compactness = 0
        
        # 不规则度（1 - 紧凑度）
        irregularity = 1.0 - compactness
        
        # 风险评分（基于体积和不规则度）
        volume_score = min(estimated_volume / 1000, 5.0)  # 0-5分
        shape_score = irregularity * 5.0  # 0-5分
        risk_score = volume_score + shape_score
        
        analysis_data = {
            'volume': float(estimated_volume),
            'surface_area': float(estimated_surface_area),
            'centroid': [
                float(centroid_x) if centroid_x else 0,
                float(centroid_y) if centroid_y else 0,
                0  # Z坐标暂时设为0
            ],
            'bounding_box': {
                'min': [
                    float(bbox_x1) if bbox_x1 else 0,
                    float(bbox_y1) if bbox_y1 else 0,
                    0
                ],
                'max': [
                    float(bbox_x2) if bbox_x2 else 0,
                    float(bbox_y2) if bbox_y2 else 0,
                    0
                ]
            },
            'irregularity': float(irregularity),
            'compactness': float(compactness),
            'risk_score': float(risk_score),
            'pixel_count': int(tumor_pixels),
            'tumor_ratio': float((tumor_pixels / total_pixels) * 100) if total_pixels > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis_data
        }), 200
        
    except Exception as e:
        current_app.logger.exception("肿瘤3D分析失败")
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@reconstruction_bp.route('/surgical-path/<int:image_id>', methods=['POST'])
@jwt_required()
def plan_surgical_path(image_id):
    """
    规划手术路径
    
    POST /api/reconstruction/surgical-path/<image_id>
    Body: {
        "entry_point": [x, y, z],
        "target_point": [x, y, z],
        "avoid_regions": [[x,y,z], ...]  // 需要避开的重要区域
    }
    
    Returns:
        {
            "path": [[x,y,z], ...],  // 路径点序列
            "length": 45.6,  // 路径长度(mm)
            "safety_score": 8.5,  // 安全评分(0-10)
            "warnings": ["路径接近血管", ...]
        }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        medical_image = MedicalImage.query.filter_by(
            id=image_id,
            uploaded_by=current_user_id
        ).first()
        
        if not medical_image:
            return jsonify({'error': '医学影像不存在'}), 404
        
        entry_point = data.get('entry_point', [0, 0, 0])
        target_point = data.get('target_point', [0, 0, 0])
        
        # 简单的直线路径（实际应该使用路径规划算法）
        path = [entry_point, target_point]
        
        # 计算路径长度
        length = np.linalg.norm(
            np.array(target_point) - np.array(entry_point)
        )
        
        # 安全评分（临时简化）
        safety_score = 7.5
        
        warnings = []
        if length > 100:
            warnings.append("路径较长，建议选择更近的入口点")
        
        return jsonify({
            'success': True,
            'path': path,
            'length': float(length),
            'safety_score': float(safety_score),
            'warnings': warnings
        }), 200
        
    except Exception as e:
        current_app.logger.exception("手术路径规划失败")
        return jsonify({'error': f'规划失败: {str(e)}'}), 500


def estimate_surface_area(faces, vertices):
    """
    估算表面积
    """
    vertices_array = np.array(vertices)
    faces_array = np.array(faces)
    
    total_area = 0
    for face in faces_array:
        v0, v1, v2 = vertices_array[face]
        # 三角形面积
        area = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0))
        total_area += area
    
    return total_area


def calculate_risk_score(volume_cm3, compactness, centroid):
    """
    计算风险评分 (0-10)
    """
    risk = 0
    
    # 基于体积
    if volume_cm3 > 5.0:
        risk += 4
    elif volume_cm3 > 2.0:
        risk += 2
    else:
        risk += 1
    
    # 基于形状不规则度
    if compactness < 0.5:
        risk += 3
    elif compactness < 0.7:
        risk += 2
    else:
        risk += 1
    
    # 基于位置（假设中心区域更危险）
    distance_from_center = np.linalg.norm(centroid - np.array([128, 128, 128]))
    if distance_from_center < 50:
        risk += 3
    elif distance_from_center < 100:
        risk += 2
    else:
        risk += 1
    
    return min(risk, 10)


@reconstruction_bp.route('/nii-files', methods=['GET'])
@jwt_required()
def list_nii_files():
    """
    获取用户上传的NII文件列表（仅用于术前规划）
    
    GET /api/reconstruction/nii-files
    
    Returns:
        {
            "files": [
                {
                    "id": 123,
                    "filename": "brain_scan_001.nii.gz",
                    "original_filename": "brain_scan_001.nii.gz",
                    "uploaded_at": "2026-01-06T10:30:00"
                }
            ],
            "total": 10
        }
    """
    try:
        current_user_id = get_jwt_identity()
        
        # 查询NII重建文件
        nii_files = MedicalImage.query.filter(
            MedicalImage.uploaded_by == current_user_id,
            MedicalImage.last_model_used == 'nii_reconstruction'
        ).order_by(MedicalImage.uploaded_at.desc()).all()
        
        # 只返回文件名和基本信息
        files_list = []
        for img in nii_files:
            files_list.append({
                'id': img.id,
                'filename': img.filename,
                'original_filename': img.original_filename,
                'uploaded_at': img.uploaded_at.isoformat() if img.uploaded_at else None
            })
        
        return jsonify({
            'success': True,
            'files': files_list,
            'total': len(files_list)
        })
    
    except Exception as e:
        current_app.logger.error(f"获取NII文件列表失败: {e}")
        return jsonify({'error': str(e)}), 500
