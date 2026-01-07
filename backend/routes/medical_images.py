from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.user import User
from models.medical_image import MedicalImage, Dataset, dataset_images
from utils.image_processing import preprocess_image
from werkzeug.utils import secure_filename
from PIL import Image
import os
import json
from datetime import datetime
from typing import List

medical_images_bp = Blueprint('medical_images', __name__)

# 上传目录 - 使用应用配置中的路径
def get_upload_folder():
    """获取上传文件夹路径（从Flask应用配置）"""
    from flask import current_app
    # 优先使用配置中的UPLOADS_DIR
    uploads_dir = current_app.config.get('UPLOADS_DIR')
    if uploads_dir:
        return uploads_dir
    # 默认路径：backend/uploads/medical_images
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(backend_root, 'uploads', 'medical_images')

@medical_images_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_medical_image():
    """上传医学影像"""
    try:
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': '用户不存在'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 获取其他表单数据
        patient_id = request.form.get('patient_id', '')
        patient_name = request.form.get('patient_name', '')
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '')
        scan_date_str = request.form.get('scan_date', '')
        modality = request.form.get('modality', 'MRI')
        body_part = request.form.get('body_part', 'Brain')
        diagnosis = request.form.get('diagnosis', '')
        
        # 解析扫描日期
        scan_date = None
        if scan_date_str:
            try:
                scan_date = datetime.strptime(scan_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '无效的扫描日期格式，应为YYYY-MM-DD'}), 400
        
        # 安全处理文件名
        filename = secure_filename(file.filename)
        
        allowed_extensions = {'png', 'jpg', 'jpeg', 'tiff', 'tif', 'dcm', 'nii', 'nii.gz'}
        lower_name = filename.lower()
        ext_valid = False
        if '.' in lower_name:
            simple_ext = lower_name.rsplit('.', 1)[1]
            if simple_ext in allowed_extensions:
                ext_valid = True
        if lower_name.endswith('.nii') or lower_name.endswith('.nii.gz'):
            ext_valid = True
        if not ext_valid:
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 生成唯一文件名
        import uuid
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_folder = get_upload_folder()
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, unique_filename)
        
        file.save(filepath)
        
        # 获取文件大小
        file_size = os.path.getsize(filepath)
        
        # 创建医学影像记录
        medical_image = MedicalImage(
            filename=filename,
            original_filename=file.filename,
            filepath=filepath,
            file_size=file_size,
            mime_type=file.content_type,
            patient_id=patient_id,
            patient_name=patient_name,
            age=age,
            gender=gender,
            scan_date=scan_date,
            modality=modality,
            body_part=body_part,
            diagnosis=diagnosis,
            uploaded_by=current_user_id
        )
        
        # 生成预览PNG
        preview_path = None
        try:
            from PIL import Image
            import numpy as np
            ext = os.path.splitext(filepath)[1].lower()
            if lower_name.endswith('.nii') or lower_name.endswith('.nii.gz'):
                try:
                    import nibabel as nib
                    img = nib.load(filepath)
                    data = img.get_fdata()
                    if data.ndim == 3:
                        z = data.shape[2] // 2
                        slice2d = data[:, :, z]
                    elif data.ndim == 4:
                        z = data.shape[2] // 2
                        slice2d = data[:, :, z, 0]
                    else:
                        slice2d = np.squeeze(data)
                    slice2d = slice2d.astype(np.float32)
                    mn, mx = float(slice2d.min()), float(slice2d.max())
                    norm = (slice2d - mn) / (mx - mn + 1e-6)
                    arr = (norm * 255.0).clip(0, 255).astype(np.uint8)
                    img_pil = Image.fromarray(arr)
                    preview_filename = f"{os.path.splitext(unique_filename)[0]}_preview.png"
                    preview_path = os.path.join(upload_folder, preview_filename)
                    img_pil.save(preview_path)
                except Exception:
                    preview_path = None
            elif ext == '.dcm':
                try:
                    import pydicom
                    ds = pydicom.dcmread(filepath)
                    arr = ds.pixel_array
                    arr = arr.astype(np.float32)
                    mn, mx = float(arr.min()), float(arr.max())
                    norm = (arr - mn) / (mx - mn + 1e-6)
                    arr = (norm * 255.0).clip(0, 255).astype(np.uint8)
                    if arr.ndim == 2:
                        img_pil = Image.fromarray(arr)
                    else:
                        img_pil = Image.fromarray(arr)
                    preview_filename = f"{os.path.splitext(unique_filename)[0]}_preview.png"
                    preview_path = os.path.join(upload_folder, preview_filename)
                    img_pil.save(preview_path)
                except Exception:
                    preview_path = None
            else:
                try:
                    img_pil = Image.open(filepath)
                    preview_filename = f"{os.path.splitext(unique_filename)[0]}_preview.png"
                    preview_path = os.path.join(upload_folder, preview_filename)
                    img_pil.save(preview_path)
                except Exception:
                    preview_path = None
        except Exception:
            preview_path = None

        # 添加到数据库
        db.session.add(medical_image)
        db.session.commit()
        
        current_app.logger.info(f"医学影像上传成功: ID={medical_image.id}, 文件={medical_image.filename}")
        
        return jsonify({
            'message': '医学影像上传成功',
            'image_id': medical_image.id,
            'filename': medical_image.filename,
            'image': medical_image.to_dict()  # 返回完整信息用于调试
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_detail = traceback.format_exc()
        current_app.logger.error(f"上传医学影像失败: {str(e)}\n{error_detail}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@medical_images_bp.route('/list', methods=['GET'])
@jwt_required()
def list_medical_images():
    """列出医学影像"""
    try:
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        per_page = min(per_page, 100)  # 限制最大每页数量
        
        # 过滤参数
        patient_id = request.args.get('patient_id')
        modality = request.args.get('modality')
        body_part = request.args.get('body_part')
        is_annotated = request.args.get('is_annotated', type=bool)
        is_validated = request.args.get('is_validated', type=bool)
        tumor_detected = request.args.get('tumor_detected')
        
        # 构建查询 - 排除NII文件（用于3D规划的文件）
        # 注意：必须使用 or_ 和 is_not 来正确处理 NULL 值
        from sqlalchemy import or_
        query = MedicalImage.query.filter(
            MedicalImage.uploaded_by == current_user_id,
            or_(
                MedicalImage.last_model_used.is_(None),  # 包含NULL值
                MedicalImage.last_model_used != 'nii_reconstruction'  # 排除NII重建文件
            )
        )
        
        current_app.logger.info(f"查询医学影像列表: 用户ID={current_user_id}, page={page}, per_page={per_page}")
        
        if patient_id:
            query = query.filter(MedicalImage.patient_id == patient_id)
        if modality:
            query = query.filter(MedicalImage.modality == modality)
        if body_part:
            query = query.filter(MedicalImage.body_part == body_part)
        if is_annotated is not None:
            query = query.filter(MedicalImage.is_annotated == is_annotated)
        if is_validated is not None:
            query = query.filter(MedicalImage.is_validated == is_validated)
        if tumor_detected is not None:
            query = query.filter(MedicalImage.tumor_detected == (tumor_detected.lower() == 'true'))
        
        # 执行查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        images = pagination.items
        
        current_app.logger.info(f"查询结果: 找到{len(images)}条记录, 总数{pagination.total}")
        
        # 调试：输出前几条记录的关键信息
        if len(images) > 0:
            for img in images[:3]:  # 只输出前3条
                current_app.logger.info(f"  - ID={img.id}, 文件={img.filename}, uploaded_by={img.uploaded_by}, last_model_used={img.last_model_used}")
        else:
            # 如果没有结果，检查是否有该用户的所有记录
            total_user_images = MedicalImage.query.filter(
                MedicalImage.uploaded_by == current_user_id
            ).count()
            current_app.logger.warning(f"[警告] 查询结果为空！该用户总共有 {total_user_images} 条记录")
            
            # 检查最近的记录
            recent = MedicalImage.query.filter(
                MedicalImage.uploaded_by == current_user_id
            ).order_by(MedicalImage.id.desc()).first()
            if recent:
                current_app.logger.info(f"  最近一条记录: ID={recent.id}, last_model_used={recent.last_model_used}")
        
        return jsonify({
            'images': [img.to_dict() for img in images],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"列出医学影像失败: {str(e)}")
        return jsonify({'error': '获取影像列表失败'}), 500

@medical_images_bp.route('/<int:image_id>', methods=['GET'])
@jwt_required()
def get_medical_image(image_id):
    """获取特定医学影像信息"""
    try:
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass
        
        medical_image = MedicalImage.query.filter(
            MedicalImage.id == image_id,
            MedicalImage.uploaded_by == current_user_id
        ).first()
        
        if not medical_image:
            return jsonify({'error': '医学影像不存在或无权限访问'}), 404
        
        return jsonify(medical_image.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"获取医学影像失败: {str(e)}")
        return jsonify({'error': '获取影像信息失败'}), 500

@medical_images_bp.route('/<int:image_id>', methods=['PUT'])
@jwt_required()
def update_medical_image(image_id):
    """更新医学影像信息"""
    try:
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except Exception:
            pass
        
        medical_image = MedicalImage.query.filter(
            MedicalImage.id == image_id,
            MedicalImage.uploaded_by == current_user_id
        ).first()
        
        if not medical_image:
            return jsonify({'error': '医学影像不存在或无权限访问'}), 404
        
        # 获取更新数据
        data = request.get_json()
        
        # 更新允许的字段
        if 'patient_name' in data:
            medical_image.patient_name = data['patient_name']
        if 'age' in data:
            medical_image.age = data['age']
        if 'gender' in data:
            medical_image.gender = data['gender']
        if 'scan_date' in data:
            if data['scan_date']:
                medical_image.scan_date = datetime.strptime(data['scan_date'], '%Y-%m-%d').date()
            else:
                medical_image.scan_date = None
        if 'modality' in data:
            medical_image.modality = data['modality']
        if 'body_part' in data:
            medical_image.body_part = data['body_part']
        if 'diagnosis' in data:
            medical_image.diagnosis = data['diagnosis']
        if 'annotation_data' in data:
            medical_image.annotation_data = json.dumps(data['annotation_data'])
            medical_image.is_annotated = True
        if 'is_validated' in data:
            medical_image.is_validated = data['is_validated']
        if 'tumor_detected' in data:
            medical_image.tumor_detected = data['tumor_detected']
        if 'detection_result' in data:
            medical_image.detection_result = json.dumps(data['detection_result'])
        
        # 更新时间
        medical_image.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': '医学影像信息更新成功',
            'image': medical_image.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"更新医学影像失败: {str(e)}")
        return jsonify({'error': '更新影像信息失败'}), 500

@medical_images_bp.route('/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_medical_image(image_id):
    """删除医学影像"""
    try:
        current_user_id = get_jwt_identity()
        
        medical_image = MedicalImage.query.filter(
            MedicalImage.id == image_id,
            MedicalImage.uploaded_by == current_user_id
        ).first()
        
        if not medical_image:
            return jsonify({'error': '医学影像不存在或无权限访问'}), 404
        
        # 删除文件（原图、预览、分割掩码）
        medical_image.delete_file()
        base = os.path.splitext(medical_image.filepath)[0]
        preview_path = f"{base}_preview.png"
        if os.path.exists(preview_path):
            os.remove(preview_path)
        
        # 从数据库删除记录
        db.session.delete(medical_image)
        db.session.commit()
        
        return jsonify({'message': '医学影像删除成功'}), 200
        
    except Exception as e:
        current_app.logger.error(f"删除医学影像失败: {str(e)}")
        return jsonify({'error': '删除影像失败'}), 500


@medical_images_bp.route('/delete-batch', methods=['POST'])
@jwt_required()
def delete_medical_images_batch():
    """批量删除医学影像（限定当前用户）"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        ids: List[int] = data.get('ids') or []
        if not isinstance(ids, list) or not ids:
            return jsonify({'error': '缺少待删除ID列表'}), 400

        # 拉取记录并校验归属
        images = MedicalImage.query.filter(
            MedicalImage.uploaded_by == current_user_id,
            MedicalImage.id.in_(ids)
        ).all()

        if not images:
            return jsonify({'error': '未找到可删除的影像'}), 404

        deleted_ids = []
        for img in images:
            img.delete_file()
            base = os.path.splitext(img.filepath)[0]
            preview_path = f"{base}_preview.png"
            if os.path.exists(preview_path):
                os.remove(preview_path)
            deleted_ids.append(img.id)
            db.session.delete(img)

        db.session.commit()

        return jsonify({'message': '批量删除成功', 'deleted_ids': deleted_ids}), 200

    except Exception as e:
        current_app.logger.error(f"批量删除医学影像失败: {str(e)}")
        return jsonify({'error': '批量删除失败'}), 500
