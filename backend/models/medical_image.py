from . import db  # 从同级目录的__init__.py导入db
from datetime import datetime
import os
try:
    from sqlalchemy.dialects.mysql import LONGTEXT as MYSQL_LONGTEXT
except Exception:
    MYSQL_LONGTEXT = None

class MedicalImage(db.Model):
    __tablename__ = 'medical_images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    mime_type = db.Column(db.String(100))  # MIME类型
    patient_id = db.Column(db.String(100))  # 患者ID
    scan_date = db.Column(db.Date)
    modality = db.Column(db.String(50))  # 影像模态 (CT, MRI等)
    body_part = db.Column(db.String(100))  # 检查部位
    institution = db.Column(db.String(255))
    patient_name = db.Column(db.String(255))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    diagnosis = db.Column(db.Text)
    status = db.Column(db.String(50), default='new')  # 状态: new, processing, completed
    
    # 检测结果字段
    detection_results = db.Column(db.Text)
    # Use db.Text with a MySQL LONGTEXT variant when available to avoid
    # SQLite compilation errors (SQLite doesn't know LONGTEXT)
    detection_result = db.Column(db.Text().with_variant(MYSQL_LONGTEXT, 'mysql') if MYSQL_LONGTEXT else db.Text)
    tumor_detected = db.Column(db.Boolean, default=False)
    confidence_score = db.Column(db.Float)
    segmentation_mask_path = db.Column(db.String(500))
    annotation_data = db.Column(db.Text)
    is_annotated = db.Column(db.Boolean, default=False)
    is_validated = db.Column(db.Boolean, default=False)
    
    # 定量分析结果
    tumor_volume = db.Column(db.Float)  # 肿瘤体积 (mm³)
    tumor_area = db.Column(db.Float)  # 肿瘤面积 (mm²)
    max_diameter = db.Column(db.Float)  # 最大直径 (mm)
    
    # 影像组学特征
    radiomics_features = db.Column(db.Text)  # 影像组学特征JSON字符串
    
    # 手术规划
    surgical_plan = db.Column(db.Text)  # 手术规划JSON字符串
    
    # ========== YOLO11脑肿瘤检测结果字段 ==========
    # 基础检测信息
    yolo_has_tumor = db.Column(db.Boolean, default=False)  # 是否检测到肿瘤
    yolo_num_instances = db.Column(db.Integer, default=0)  # 检测到的肿瘤实例数
    yolo_avg_confidence = db.Column(db.Float)  # 平均置信度 (0-1)
    yolo_tumor_ratio = db.Column(db.Float)  # 肿瘤占脑区面积比例 (%)
    yolo_tumor_pixels = db.Column(db.Integer)  # 肿瘤像素数
    yolo_total_pixels = db.Column(db.Integer)  # 总像素数
    
    # 实例级别信息 (JSON格式，存储每个检测实例的详细信息)
    yolo_instances = db.Column(db.Text().with_variant(MYSQL_LONGTEXT, 'mysql') if MYSQL_LONGTEXT else db.Text)
    
    # 分割掩码相关
    yolo_mask_path = db.Column(db.String(500))  # 分割掩码路径
    yolo_mask_overlay_path = db.Column(db.String(500))  # 掩码叠加图路径
    
    # 肿瘤位置和几何特征
    yolo_tumor_centroid_x = db.Column(db.Float)  # 肿瘤中心X坐标
    yolo_tumor_centroid_y = db.Column(db.Float)  # 肿瘤中心Y坐标
    yolo_tumor_bbox_x1 = db.Column(db.Float)  # 外接矩形左上角X
    yolo_tumor_bbox_y1 = db.Column(db.Float)  # 外接矩形左上角Y
    yolo_tumor_bbox_x2 = db.Column(db.Float)  # 外接矩形右下角X
    yolo_tumor_bbox_y2 = db.Column(db.Float)  # 外接矩形右下角Y
    
    # 术前规划相关字段
    yolo_risk_level = db.Column(db.String(50))  # 风险等级: 'low', 'medium', 'high'
    yolo_surgical_accessibility = db.Column(db.String(50))  # 手术可达性: 'easy', 'moderate', 'difficult'
    yolo_location_description = db.Column(db.Text)  # 肿瘤位置描述
    yolo_proximity_to_vessels = db.Column(db.Float)  # 与血管的最小距离 (mm)
    yolo_proximity_to_eloquent_area = db.Column(db.Float)  # 与言语功能区的距离 (mm)
    
    # 检测质量评估
    yolo_segmentation_quality = db.Column(db.Float)  # 分割质量评分 (0-1)
    yolo_model_version = db.Column(db.String(50))  # 使用的YOLO模型版本
    yolo_inference_time = db.Column(db.Float)  # 推理耗时 (秒)
    
    # 诊断建议
    yolo_diagnostic_report = db.Column(db.Text)  # 诊断报告 (JSON)
    
    # ========== UNet脑肿瘤检测结果字段 ==========
    # 基础检测信息
    unet_has_tumor = db.Column(db.Boolean, default=False)  # 是否检测到肿瘤
    unet_num_instances = db.Column(db.Integer, default=0)  # 检测到的肿瘤实例数
    unet_avg_confidence = db.Column(db.Float)  # 平均置信度 (0-1)
    unet_tumor_ratio = db.Column(db.Float)  # 肿瘤占脑区面积比例 (%)
    unet_tumor_pixels = db.Column(db.Integer)  # 肿瘤像素数
    unet_total_pixels = db.Column(db.Integer)  # 总像素数
    
    # 实例级别信息
    unet_instances = db.Column(db.Text)
    
    # 分割掩码相关
    unet_mask_path = db.Column(db.String(500))  # 分割掩码路径
    unet_mask_overlay_path = db.Column(db.String(500))  # 掩码叠加图路径
    
    # 肿瘤位置信息
    unet_tumor_centroid_x = db.Column(db.Float)  # 肿瘤中心X坐标
    unet_tumor_centroid_y = db.Column(db.Float)  # 肿瘤中心Y坐标
    unet_tumor_bbox_x1 = db.Column(db.Float)  # 外接矩形左上角X
    unet_tumor_bbox_y1 = db.Column(db.Float)  # 外接矩形左上角Y
    unet_tumor_bbox_x2 = db.Column(db.Float)  # 外接矩形右下角X
    unet_tumor_bbox_y2 = db.Column(db.Float)  # 外接矩形右下角Y
    
    # 临床评估
    unet_risk_level = db.Column(db.String(50))  # 风险等级: 'low', 'medium', 'high'
    unet_surgical_accessibility = db.Column(db.String(50))  # 手术可达性: 'easy', 'moderate', 'difficult'
    unet_location_description = db.Column(db.Text)  # 肿瘤位置描述
    
    # 检测质量评估
    unet_model_version = db.Column(db.String(50))  # 使用的UNet模型版本
    
    # 记录最后使用的模型
    last_model_used = db.Column(db.String(20))  # 'yolo' 或 'unet'
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 上传用户
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('medical_images', lazy=True))
    
    def to_dict(self):
        """将医学影像对象转换为字典"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'filepath': self.filepath,
            'file_url': self.file_url,
            'preview_url': self.preview_url,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'patient_id': self.patient_id,
            'scan_date': self.scan_date.isoformat() if self.scan_date else None,
            'modality': self.modality,
            'body_part': self.body_part,
            'institution': self.institution,
            'patient_name': self.patient_name,
            'age': self.age,
            'gender': self.gender,
            'diagnosis': self.diagnosis,
            'status': self.status or 'new',
            'detection_results': self.detection_results,
            'detection_result': self.detection_result,
            'tumor_detected': self.tumor_detected,
            'confidence_score': self.confidence_score,
            'segmentation_mask_path': self.segmentation_mask_path,
            'annotation_data': self.annotation_data,
            'is_annotated': self.is_annotated,
            'is_validated': self.is_validated,
            'tumor_volume': self.tumor_volume,
            'tumor_area': self.tumor_area,
            'max_diameter': self.max_diameter,
            'radiomics_features': self.radiomics_features,
            'surgical_plan': self.surgical_plan,
            # YOLO11检测结果
            'yolo_has_tumor': self.yolo_has_tumor,
            'yolo_num_instances': self.yolo_num_instances,
            'yolo_avg_confidence': self.yolo_avg_confidence,
            'yolo_tumor_ratio': self.yolo_tumor_ratio,
            'yolo_tumor_pixels': self.yolo_tumor_pixels,
            'yolo_total_pixels': self.yolo_total_pixels,
            'yolo_instances': self.yolo_instances,
            'yolo_mask_path': self.yolo_mask_path,
            'yolo_mask_overlay_path': self.yolo_mask_overlay_path,
            'yolo_tumor_centroid_x': self.yolo_tumor_centroid_x,
            'yolo_tumor_centroid_y': self.yolo_tumor_centroid_y,
            'yolo_tumor_bbox_x1': self.yolo_tumor_bbox_x1,
            'yolo_tumor_bbox_y1': self.yolo_tumor_bbox_y1,
            'yolo_tumor_bbox_x2': self.yolo_tumor_bbox_x2,
            'yolo_tumor_bbox_y2': self.yolo_tumor_bbox_y2,
            'yolo_risk_level': self.yolo_risk_level,
            'yolo_surgical_accessibility': self.yolo_surgical_accessibility,
            'yolo_location_description': self.yolo_location_description,
            'yolo_proximity_to_vessels': self.yolo_proximity_to_vessels,
            'yolo_proximity_to_eloquent_area': self.yolo_proximity_to_eloquent_area,
            'yolo_segmentation_quality': self.yolo_segmentation_quality,
            'yolo_model_version': self.yolo_model_version,
            'yolo_inference_time': self.yolo_inference_time,
            'yolo_diagnostic_report': self.yolo_diagnostic_report,
            # UNet检测结果
            'unet_has_tumor': self.unet_has_tumor,
            'unet_num_instances': self.unet_num_instances,
            'unet_avg_confidence': self.unet_avg_confidence,
            'unet_tumor_ratio': self.unet_tumor_ratio,
            'unet_tumor_pixels': self.unet_tumor_pixels,
            'unet_total_pixels': self.unet_total_pixels,
            'unet_instances': self.unet_instances,
            'unet_mask_path': self.unet_mask_path,
            'unet_mask_overlay_path': self.unet_mask_overlay_path,
            'unet_tumor_centroid_x': self.unet_tumor_centroid_x,
            'unet_tumor_centroid_y': self.unet_tumor_centroid_y,
            'unet_tumor_bbox_x1': self.unet_tumor_bbox_x1,
            'unet_tumor_bbox_y1': self.unet_tumor_bbox_y1,
            'unet_tumor_bbox_x2': self.unet_tumor_bbox_x2,
            'unet_tumor_bbox_y2': self.unet_tumor_bbox_y2,
            'unet_risk_level': self.unet_risk_level,
            'unet_surgical_accessibility': self.unet_surgical_accessibility,
            'unet_location_description': self.unet_location_description,
            'unet_model_version': self.unet_model_version,
            # 模型选择
            'last_model_used': self.last_model_used,
            'uploaded_at': self.uploaded_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'uploaded_by': self.uploaded_by
        }
    
    @property
    def file_url(self):
        """获取文件访问URL"""
        from flask import current_app
        import os
        if os.path.exists(self.filepath):
            return f'/uploads/medical_images/{os.path.basename(self.filepath)}'
        return None
    
    @property
    def preview_url(self):
        from flask import current_app
        import os
        base = os.path.splitext(os.path.basename(self.filepath))[0]
        preview_filename = f'{base}_preview.png'
        preview_path = os.path.join(os.path.dirname(self.filepath), preview_filename)
        if os.path.exists(preview_path):
            return f'/uploads/medical_images/{preview_filename}'
        return None
    
    def delete_file(self):
        """删除物理文件"""
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        if self.segmentation_mask_path and os.path.exists(self.segmentation_mask_path):
            os.remove(self.segmentation_mask_path)

# 中间表 - 数据集与医学影像的多对多关系
dataset_images = db.Table('dataset_images',
    db.Column('dataset_id', db.Integer, db.ForeignKey('datasets.id'), primary_key=True),
    db.Column('medical_image_id', db.Integer, db.ForeignKey('medical_images.id'), primary_key=True)
)

class Dataset(db.Model):
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 关系
    creator = db.relationship('User', backref=db.backref('datasets', lazy=True))
    medical_images = db.relationship('MedicalImage', secondary=dataset_images, lazy='subquery',
                                     backref=db.backref('datasets', lazy=True))
    
    def to_dict(self):
        """将数据集对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'image_count': len(self.medical_images)
        }
