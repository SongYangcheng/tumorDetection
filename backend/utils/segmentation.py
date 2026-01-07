import numpy as np
import cv2
from PIL import Image
import torch
from ultralytics import YOLO
import os
from datetime import datetime

class TumorSegmentation:
    def __init__(self, weight_path: str | None = None):
        """
        初始化肿瘤分割器
        Args:
            weight_path: 权重文件路径（可以是相对路径如 'weights/Yolov11_best.pt' 或绝对路径）
        """
        # 尝试加载预训练模型
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            
            if weight_path:
                # 如果提供了权重路径，尝试多种方式解析
                resolved_path = None
                
                # 1. 尝试作为绝对路径
                if os.path.exists(weight_path):
                    resolved_path = weight_path
                # 2. 尝试相对于 backend 目录
                elif os.path.exists(os.path.join(project_root, 'backend', weight_path)):
                    resolved_path = os.path.join(project_root, 'backend', weight_path)
                # 3. 尝试相对于项目根目录
                elif os.path.exists(os.path.join(project_root, weight_path)):
                    resolved_path = os.path.join(project_root, weight_path)
                
                if resolved_path:
                    try:
                        print(f"加载权重文件: {resolved_path}")
                        self.model = YOLO(resolved_path)
                        # 验证是否为分割模型
                        if self.model.task != 'segment':
                            print(f"警告: {resolved_path} 不是分割模型（任务类型: {self.model.task}）")
                            print("尝试加载默认分割模型...")
                            self.model = YOLO('yolov8n-seg.pt')
                        else:
                            print(f"成功加载分割模型: {resolved_path}")
                    except Exception as e:
                        print(f"加载权重失败: {e}")
                        print("使用默认分割模型...")
                        try:
                            self.model = YOLO('yolov8n-seg.pt')
                        except Exception:
                            self.model = None
                else:
                    print(f"找不到权重文件: {weight_path}")
                    print("使用默认Yolov11_best.pt...")
                    # 回退到默认权重
                    weight_path = None
            
            if not weight_path:
                # 优先从 backend/weights 中加载 Yolov11_best.pt
                yolo11_path = os.path.join(project_root, 'backend', 'weights', 'Yolov11_best.pt')
                if os.path.exists(yolo11_path):
                    try:
                        print(f"加载默认权重: {yolo11_path}")
                        self.model = YOLO(yolo11_path)
                        print(f"成功加载默认分割模型")
                    except Exception as e:
                        print(f"加载默认权重失败: {e}")
                        try:
                            self.model = YOLO('yolov8n-seg.pt')
                        except Exception:
                            self.model = None
                else:
                    # 找不到Yolov11_best.pt，尝试utils本地模型文件
                    model_path = os.path.join(os.path.dirname(__file__), 'models', 'tumor_segmentation.pt')
                    if os.path.exists(model_path):
                        try:
                            self.model = YOLO(model_path)
                        except Exception:
                            try:
                                self.model = YOLO('yolov8n-seg.pt')
                            except Exception:
                                self.model = None
                    else:
                        # 再次尝试后端目录下的示例模型
                        backend_default = os.path.join(project_root, 'backend', 'yolov8n.pt')
                        if os.path.exists(backend_default):
                            try:
                                self.model = YOLO(backend_default)
                            except Exception:
                                try:
                                    self.model = YOLO('yolov8n-seg.pt')
                                except Exception:
                                    self.model = None
                        else:
                            # 使用Ultralytics提供的默认预训练分割模型
                            try:
                                self.model = YOLO('yolov8n-seg.pt')
                            except Exception:
                                print("无法加载任何YOLO分割模型，将使用传统分割算法")
                                self.model = None
        except Exception as e:
            print(f"模型加载失败，使用基础分割算法: {e}")
            self.model = None
    
    def segment_and_analyze(self, image, conf: float = 0.25, imgsz: int = 256):
        """
        执行肿瘤分割和分析（参考YOLO11TumorPredictor实现）
        
        Args:
            image: 输入图像 (numpy array or PIL Image)
            conf: 置信度阈值 (0-1)
            imgsz: 推理时的图像尺寸
            
        Returns:
            分割结果字典，包含success, segmentation_result, metrics
        """
        try:
            # 确保输入是numpy数组
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            # 如果图像有3个维度但只有1个通道，扩展到3个通道
            if len(image.shape) == 3 and image.shape[2] == 1:
                image = np.repeat(image, 3, axis=2)
            elif len(image.shape) == 2:
                image = np.stack([image] * 3, axis=-1)
            
            # 确保图像是RGB格式
            if len(image.shape) == 3 and image.shape[2] == 4:  # RGBA
                image = image[:, :, :3]
            
            h, w = image.shape[:2]
            
            # 如果有模型，使用模型进行预测
            if self.model is not None:
                print(f"YOLO推理: imgsz={imgsz}, conf={conf}")
                
                # ⭐ 参考 YOLO11TumorPredictor.predict() 的实现
                results = self.model.predict(
                    source=image,
                    imgsz=imgsz,
                    conf=conf,
                    iou=0.7,  # NMS的IoU阈值
                    save=False,
                    verbose=False
                )
                
                result = results[0]
                
                # 提取结果（参考参考文件的实现）
                masks = []
                boxes = []
                confidences = []
                
                if result.masks is not None:
                    # 获取分割掩码 - 关键：直接从result.masks.data获取
                    masks_data = result.masks.data.cpu().numpy()
                    print(f"检测到 {len(masks_data)} 个肿瘤实例")
                    
                    # 获取检测框和置信度
                    boxes_data = result.boxes.xyxy.cpu().numpy()
                    conf_data = result.boxes.conf.cpu().numpy()
                    
                    for i in range(len(masks_data)):
                        masks.append(masks_data[i])
                        boxes.append(boxes_data[i])
                        confidences.append(float(conf_data[i]))
                        print(f"   实例 {i+1}: 置信度={conf_data[i]:.3f}")
                else:
                    print(f"未检测到肿瘤")
                
                # 构建分割结果
                segmentation_result = {
                    'masks': masks if len(masks) > 0 else None,
                    'boxes': boxes if len(boxes) > 0 else [],
                    'confidences': confidences if len(confidences) > 0 else [],
                    'original_image_shape': (h, w, 3)
                }
                
                # 计算详细指标（参考 analyze_prediction 的实现）
                metrics = self._calculate_metrics(image, segmentation_result, confidences)
                
            else:
                print(f"YOLO模型未加载，使用基础分割算法")
                # 使用基础分割算法（如果模型不可用）
                segmentation_result, metrics = self._basic_segmentation(image)
            
            return {
                'success': True,
                'segmentation_result': segmentation_result,
                'metrics': metrics
            }
            
        except Exception as e:
            print(f"分割过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'segmentation_result': None,
                'metrics': {},
                'error': str(e)
            }
    
    def _basic_segmentation(self, image):
        """
        基础分割算法（当模型不可用时使用）
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # 应用阈值分割
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学操作去噪
        kernel = np.ones((3,3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 过滤小轮廓（可能是噪声）
        min_area = 100
        filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area]
        
        # 创建掩码
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, filtered_contours, -1, 255, -1)
        
        # 计算指标
        tumor_count = len(filtered_contours)
        total_pixels = np.sum(mask > 0)
        tumor_area_ratio = total_pixels / (gray.shape[0] * gray.shape[1])
        
        segmentation_result = {
            'masks': np.array([mask]) if len(filtered_contours) > 0 else None,
            'boxes': [],
            'confidences': [],
            'original_image_shape': image.shape
        }
        
        metrics = {
            'tumor_count': tumor_count,
            'tumor_area_ratio': float(tumor_area_ratio),
            'total_tumor_pixels': int(total_pixels)
        }
        
        return segmentation_result, metrics
    
    def _calculate_metrics(self, original_image, segmentation_result, confidences=None):
        """
        计算分割结果的指标（参考 YOLO11TumorPredictor.analyze_prediction）
        
        Args:
            original_image: 原始图像
            segmentation_result: 分割结果
            confidences: 置信度列表
            
        Returns:
            metrics字典，包含tumor_count, tumor_ratio, avg_confidence等
        """
        masks = segmentation_result.get('masks')
        
        if masks is None or len(masks) == 0:
            return {
                'tumor_count': 0,
                'num_instances': 0,
                'tumor_ratio': 0.0,
                'total_tumor_pixels': 0,
                'avg_confidence': 0.0,
                'confidences': []
            }
        
        h, w = original_image.shape[:2]
        total_pixels = h * w
        
        # 计算肿瘤像素总数（合并所有掩码）
        combined_mask = np.zeros((h, w), dtype=np.uint8)
        
        for mask in masks:
            if isinstance(mask, torch.Tensor):
                mask = mask.cpu().numpy()
            
            # 调整掩码尺寸到原图大小
            if mask.shape != (h, w):
                mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
            else:
                mask_resized = mask
            
            # 二值化并合并
            mask_binary = (mask_resized > 0.5).astype(np.uint8)
            combined_mask = np.maximum(combined_mask, mask_binary)
        
        tumor_pixels = np.sum(combined_mask > 0)
        tumor_ratio = (tumor_pixels / total_pixels * 100) if total_pixels > 0 else 0.0
        
        # 计算平均置信度
        if confidences and len(confidences) > 0:
            avg_confidence = float(np.mean(confidences))
        else:
            avg_confidence = 0.0
        
        metrics = {
            'tumor_count': len(masks),
            'num_instances': len(masks),
            'tumor_ratio': float(tumor_ratio),  # 百分比形式
            'tumor_pixels': int(tumor_pixels),
            'total_pixels': int(total_pixels),
            'total_tumor_pixels': int(tumor_pixels),
            'tumor_area_ratio': float(tumor_pixels / total_pixels) if total_pixels > 0 else 0.0,  # 小数形式
            'avg_confidence': avg_confidence,
            'confidences': confidences if confidences else []
        }
        
        print(f"分割指标: {metrics['num_instances']}个实例, 占比={metrics['tumor_ratio']:.2f}%, 置信度={avg_confidence:.3f}")
        
        return metrics

def visualize_segmentation_result(original_image, segmentation_result):
    """
    可视化分割结果（参考 YOLO11TumorPredictor.predict_with_visualization）
    
    Args:
        original_image: 原始图像 (H, W, 3) numpy array
        segmentation_result: 包含masks, boxes, confidences的字典
        
    Returns:
        overlay: 叠加了分割结果的图像
    """
    # 确保是numpy数组且是RGB格式
    if isinstance(original_image, Image.Image):
        overlay = np.array(original_image)
    else:
        overlay = original_image.copy()
    
    if overlay.dtype != np.uint8:
        overlay = (overlay * 255).astype(np.uint8) if overlay.max() <= 1.0 else overlay.astype(np.uint8)
    
    h, w = overlay.shape[:2]
    
    masks = segmentation_result.get('masks')
    boxes = segmentation_result.get('boxes') or []
    confidences = segmentation_result.get('confidences') or []
    
    # 如果没有掩码，直接返回原图
    if masks is None or len(masks) == 0:
        return overlay
    
    print(f"可视化 {len(masks)} 个分割掩码...")
    
    # 绘制每个检测到的肿瘤（参考参考文件的实现）
    for i, mask in enumerate(masks):
        if isinstance(mask, torch.Tensor):
            mask = mask.cpu().numpy()
        
        # 调整掩码尺寸到原图大小
        if mask.shape != (h, w):
            mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
        else:
            mask_resized = mask
        
        # 二值化掩码 (阈值0.5)
        mask_binary = (mask_resized > 0.5).astype(np.uint8)
        
        # 提取轮廓
        contours, _ = cv2.findContours(
            mask_binary, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # 绘制轮廓（红色，参考文件用红色表示预测）
        cv2.drawContours(overlay, contours, -1, (255, 0, 0), 2)
        
        # 创建半透明的彩色掩码叠加
        color_mask = np.zeros((h, w, 3), dtype=np.uint8)
        color_mask[mask_binary > 0] = [255, 0, 0]  # 红色
        overlay = cv2.addWeighted(overlay, 1.0, color_mask, 0.3, 0)
        
        # 显示置信度（如果有检测框）
        if i < len(boxes) and i < len(confidences):
            x1, y1, x2, y2 = boxes[i].astype(int)
            conf = confidences[i]
            label = f"{conf:.2f}"
            cv2.putText(overlay, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    return overlay
