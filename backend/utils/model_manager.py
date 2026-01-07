"""
模型管理器 - 统一YOLO和UNet模型接口
"""

import os
import cv2
import numpy as np
from datetime import datetime


class ModelManager:
    """模型管理器 - 支持YOLO和UNet切换"""
    
    SUPPORTED_MODELS = {
        'yolo': ['Yolov11_best.pt', 'yolov8n.pt', 'yolov11n-seg.pt'],
        'unet': ['ResNeXt50_best.pt', 'ResNeXt50_last.pt']
    }
    
    def __init__(self, backend_root):
        self.backend_root = backend_root
        self.weights_dir = os.path.join(backend_root, 'weights')
        self.yolo_model = None
        self.unet_model = None
    
    def detect_model_type(self, weight_path):
        """自动检测模型类型"""
        weight_name = os.path.basename(weight_path).lower()
        
        # 根据文件名判断
        if 'yolo' in weight_name:
            return 'yolo'
        elif 'resnext' in weight_name or 'unet' in weight_name:
            return 'unet'
        
        # 根据文件扩展名和内容判断
        if weight_name.endswith('.pt'):
            try:
                import torch
                checkpoint = torch.load(weight_path, map_location='cpu', weights_only=False)
                
                # 检查state_dict的键
                if isinstance(checkpoint, dict):
                    keys = checkpoint.get('state_dict', checkpoint).keys()
                    key_str = ' '.join(str(k) for k in list(keys)[:10])
                    
                    if 'encoder' in key_str or 'decoder' in key_str or 'base_model' in key_str:
                        return 'unet'
                    elif 'model' in key_str or 'detect' in key_str:
                        return 'yolo'
            except Exception as e:
                print(f"检测模型类型失败: {e}")
        
        # 默认返回YOLO
        return 'yolo'
    
    def load_model(self, weight_path, model_type=None, conf_threshold=0.25, device='cpu'):
        """
        加载模型
        
        Args:
            weight_path: 权重文件路径
            model_type: 'yolo' 或 'unet'，如果为None则自动检测
            conf_threshold: 置信度阈值
            device: 'cpu' 或 'cuda'
        
        Returns:
            model: 加载的模型实例
            model_type: 实际的模型类型
        """
        # 自动检测模型类型
        if model_type is None:
            model_type = self.detect_model_type(weight_path)
        
        print(f"加载{model_type.upper()}模型: {weight_path}")
        
        if model_type == 'yolo':
            from ultralytics import YOLO
            model = YOLO(weight_path)
            model.conf = conf_threshold
            return model, 'yolo'
        
        elif model_type == 'unet':
            from utils.unet_predictor import UNetPredictor
            # UNet使用参考代码的默认阈值0.3，或用户指定的阈值
            model = UNetPredictor(weight_path, device=device, threshold=conf_threshold)
            return model, 'unet'
        
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
    
    def predict(self, model, model_type, image_path, **kwargs):
        """
        统一的预测接口
        
        Args:
            model: 模型实例
            model_type: 'yolo' 或 'unet'
            image_path: 图像路径
            **kwargs: 额外参数
        
        Returns:
            result: 统一格式的预测结果
        """
        if model_type == 'yolo':
            return self._predict_yolo(model, image_path, **kwargs)
        elif model_type == 'unet':
            return self._predict_unet(model, image_path, **kwargs)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
    
    def _predict_yolo(self, model, image_path, imgsz=256):
        """YOLO模型预测"""
        results = model(image_path, imgsz=imgsz, verbose=False)
        result = results[0]
        
        if result.masks is None or len(result.masks) == 0:
            # 未检测到肿瘤
            image = cv2.imread(image_path)
            h, w = image.shape[:2]
            
            return {
                'segmentation_result': {
                    'masks': [],
                    'confidences': [],
                    'boxes': []
                },
                'metrics': {
                    'num_instances': 0,
                    'tumor_pixels': 0,
                    'total_pixels': h * w,
                    'tumor_ratio': 0.0,
                    'avg_confidence': 0.0,
                    'tumor_area_ratio': 0.0
                },
                'tumor_detected': False
            }
        
        # 提取YOLO结果
        masks_tensor = result.masks.data
        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        
        # 转换masks为numpy
        masks = []
        for mask_tensor in masks_tensor:
            mask_np = mask_tensor.cpu().numpy()
            # 调整到原始图像尺寸
            image = cv2.imread(image_path)
            h, w = image.shape[:2]
            mask_resized = cv2.resize(mask_np, (w, h), interpolation=cv2.INTER_NEAREST)
            masks.append(mask_resized)
        
        # 计算指标
        combined_mask = np.zeros((h, w), dtype=np.uint8)
        for mask in masks:
            combined_mask = np.maximum(combined_mask, (mask > 0.5).astype(np.uint8))
        
        tumor_pixels = np.sum(combined_mask > 0)
        total_pixels = h * w
        tumor_ratio = (tumor_pixels / total_pixels) * 100
        
        return {
            'segmentation_result': {
                'masks': masks,
                'confidences': confidences.tolist(),
                'boxes': boxes.tolist()
            },
            'metrics': {
                'num_instances': len(masks),
                'tumor_pixels': int(tumor_pixels),
                'total_pixels': int(total_pixels),
                'tumor_ratio': float(tumor_ratio),
                'avg_confidence': float(np.mean(confidences)),
                'tumor_area_ratio': float(tumor_pixels / total_pixels)
            },
            'tumor_detected': True
        }
    
    def _predict_unet(self, model, image_path):
        """UNet模型预测"""
        pred_mask, pred_prob, result = model.predict(image_path)
        return result
    
    def compare_models(self, yolo_model, unet_model, image_path, output_dir):
        """
        对比两个模型的预测结果
        
        Args:
            yolo_model: YOLO模型实例
            unet_model: UNet模型实例
            image_path: 图像路径
            output_dir: 输出目录
        
        Returns:
            comparison: 对比结果字典
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 读取原始图像
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]
        
        # YOLO预测
        yolo_result = self._predict_yolo(yolo_model, image_path)
        yolo_masks = yolo_result['segmentation_result']['masks']
        yolo_metrics = yolo_result['metrics']
        
        # UNet预测
        unet_pred_mask, unet_pred_prob, unet_result = unet_model.predict(image_path)
        unet_metrics = unet_result['metrics']
        
        # 生成可视化
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # YOLO可视化
        yolo_overlay = image_rgb.copy()
        if yolo_masks:
            combined_yolo = np.zeros((h, w), dtype=np.uint8)
            for mask in yolo_masks:
                if mask.shape != (h, w):
                    mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
                combined_yolo = np.maximum(combined_yolo, (mask > 0.5).astype(np.uint8) * 255)
            
            colored_mask = np.zeros_like(yolo_overlay)
            colored_mask[:, :, 0] = combined_yolo  # 红色
            yolo_overlay = cv2.addWeighted(yolo_overlay, 0.7, colored_mask, 0.3, 0)
            
            contours, _ = cv2.findContours(combined_yolo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(yolo_overlay, contours, -1, (255, 255, 0), 2)
        
        # UNet可视化
        unet_overlay = unet_model.visualize(image_rgb, unet_pred_mask, alpha=0.3)
        
        # 保存对比图
        comparison_image = np.hstack([
            image_rgb,
            yolo_overlay,
            unet_overlay
        ])
        
        # 添加标题
        comparison_with_title = np.zeros((comparison_image.shape[0] + 60, comparison_image.shape[1], 3), dtype=np.uint8)
        comparison_with_title[60:, :] = comparison_image
        comparison_with_title[:60, :] = 255
        
        # 添加文字
        cv2.putText(comparison_with_title, 'Original', (w//2-50, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(comparison_with_title, f'YOLO ({yolo_metrics["num_instances"]} inst)', 
                    (w + w//2-80, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(comparison_with_title, f'UNet ({unet_metrics["num_instances"]} inst)', 
                    (2*w + w//2-80, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        
        comparison_path = os.path.join(output_dir, f'comparison_{timestamp}.png')
        cv2.imwrite(comparison_path, cv2.cvtColor(comparison_with_title, cv2.COLOR_RGB2BGR))
        
        # 保存单独的结果
        yolo_path = os.path.join(output_dir, f'yolo_{timestamp}.png')
        unet_path = os.path.join(output_dir, f'unet_{timestamp}.png')
        cv2.imwrite(yolo_path, cv2.cvtColor(yolo_overlay, cv2.COLOR_RGB2BGR))
        cv2.imwrite(unet_path, cv2.cvtColor(unet_overlay, cv2.COLOR_RGB2BGR))
        
        return {
            'comparison_path': comparison_path,
            'yolo_path': yolo_path,
            'unet_path': unet_path,
            'yolo_metrics': yolo_metrics,
            'unet_metrics': unet_metrics,
            'metrics_comparison': {
                'tumor_ratio_diff': abs(yolo_metrics['tumor_ratio'] - unet_metrics['tumor_ratio']),
                'confidence_diff': abs(yolo_metrics['avg_confidence'] - unet_metrics['avg_confidence']),
                'instances_diff': abs(yolo_metrics['num_instances'] - unet_metrics['num_instances'])
            }
        }
