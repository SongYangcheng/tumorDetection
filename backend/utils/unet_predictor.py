"""
UNet脑肿瘤分割预测器
基于ResNeXtUNet架构 - 与训练代码完全一致
"""

import os
import cv2
import torch
import numpy as np
from torch import nn
from torchvision.models import resnext50_32x4d


class ConvRelu(nn.Module):
    """卷积+ReLU模块"""
    def __init__(self, in_channels, out_channels, kernel, padding):
        super().__init__()
        self.convrelu = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel, padding=padding),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        return self.convrelu(x)


class DecoderBlock(nn.Module):
    """解码器块：上采样 + 卷积"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        
        # 1x1卷积降维
        self.conv1 = ConvRelu(in_channels, in_channels // 4, 1, 0)
        
        # 转置卷积上采样（2倍）- 与训练代码完全一致
        self.deconv = nn.ConvTranspose2d(
            in_channels // 4, 
            in_channels // 4, 
            kernel_size=4,
            stride=2, 
            padding=1, 
            output_padding=0  # 关键参数
        )
        
        # 1x1卷积
        self.conv2 = ConvRelu(in_channels // 4, out_channels, 1, 0)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.deconv(x)
        x = self.conv2(x)
        return x


class ResNeXtUNet(nn.Module):
    """基于ResNeXt50的U-Net模型 - 与训练代码完全一致"""
    
    def __init__(self, n_classes=1):
        super().__init__()
        
        # 加载ResNeXt50作为编码器
        self.base_model = resnext50_32x4d(pretrained=False)
        self.base_layers = list(self.base_model.children())
        filters = [4*64, 4*128, 4*256, 4*512]  # [256, 512, 1024, 2048]
        
        # 编码器（下采样）
        self.encoder0 = nn.Sequential(*self.base_layers[:3])
        self.encoder1 = nn.Sequential(*self.base_layers[4])
        self.encoder2 = nn.Sequential(*self.base_layers[5])
        self.encoder3 = nn.Sequential(*self.base_layers[6])
        self.encoder4 = nn.Sequential(*self.base_layers[7])

        # 解码器（上采样）
        self.decoder4 = DecoderBlock(filters[3], filters[2])
        self.decoder3 = DecoderBlock(filters[2], filters[1])
        self.decoder2 = DecoderBlock(filters[1], filters[0])
        self.decoder1 = DecoderBlock(filters[0], filters[0])

        # 最终分类头
        self.last_conv0 = ConvRelu(256, 128, 3, 1)
        self.last_conv1 = nn.Conv2d(128, n_classes, 3, padding=1)
        
    def forward(self, x):
        # 编码器路径
        x = self.encoder0(x)
        e1 = self.encoder1(x)
        e2 = self.encoder2(e1)
        e3 = self.encoder3(e2)
        e4 = self.encoder4(e3)

        # 解码器路径（带跳跃连接）
        d4 = self.decoder4(e4) + e3
        d3 = self.decoder3(d4) + e2
        d2 = self.decoder2(d3) + e1
        d1 = self.decoder1(d2)

        # 输出层
        out = self.last_conv0(d1)
        out = self.last_conv1(out)
        out = torch.sigmoid(out)  # 二分类分割
        
        return out


class UNetPredictor:
    """UNet脑肿瘤分割预测器"""
    
    def __init__(self, weight_path, device='cpu', threshold=0.3):
        """
        Args:
            weight_path: 权重文件路径
            device: 'cpu' 或 'cuda'
            threshold: 分割阈值 (0-1)，默认0.3
        """
        self.device = device
        self.threshold = threshold
        
        # 初始化模型
        print(f"加载UNet模型: {weight_path}")
        self.model = ResNeXtUNet(n_classes=1).to(device)
        
        # 加载权重 - 兼容多种保存格式（与参考代码一致）
        checkpoint = torch.load(weight_path, map_location=device, weights_only=False)
        
        if isinstance(checkpoint, dict):
            if 'state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['state_dict'])
            elif 'model' in checkpoint:
                self.model.load_state_dict(checkpoint['model'])
            else:
                # 整个checkpoint就是state_dict
                self.model.load_state_dict(checkpoint)
        else:
            self.model.load_state_dict(checkpoint)
            
        self.model.eval()
        print(f"UNet模型加载成功！设备: {device}, 阈值: {threshold}")
    
    def preprocess_image(self, image):
        """预处理图像 - 与训练代码完全一致"""
        # 转为RGB
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 调整大小到256x256（与训练一致）
        original_size = image.shape[:2]
        image_resized = cv2.resize(image, (256, 256))
        
        # 归一化 - 与训练代码完全一致（ImageNet标准化）
        image_norm = image_resized.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        image_norm = (image_norm - mean) / std
        
        # 转为tensor (CHW格式，float32类型)
        image_tensor = torch.from_numpy(image_norm).permute(2, 0, 1).unsqueeze(0).float()
        
        return image_tensor.to(self.device), original_size
    
    def predict(self, image_path):
        """
        预测单张图像 - 与训练代码完全一致
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            pred_mask: 预测掩码 (原始尺寸, uint8, 0或255)
            pred_prob: 预测概率图 (原始尺寸, float32, 0-1)
            result: 结果字典（与YOLO格式兼容）
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_size = image_rgb.shape[:2]
        
        # 预处理
        img_tensor, _ = self.preprocess_image(image)
        
        # 推理
        with torch.no_grad():
            pred_prob = self.model(img_tensor)
            pred_prob = pred_prob.cpu().numpy()[0, 0]
        
        # 二值化 - 与训练代码一致
        pred_mask = np.copy(pred_prob)
        pred_mask[pred_mask < self.threshold] = 0
        pred_mask[pred_mask >= self.threshold] = 255  # 输出255而不是1
        pred_mask = pred_mask.astype(np.uint8)
        
        # 调整回原始尺寸
        pred_mask = cv2.resize(pred_mask, (original_size[1], original_size[0]), interpolation=cv2.INTER_NEAREST)
        pred_prob = cv2.resize(pred_prob, (original_size[1], original_size[0]))
        
        # 计算指标
        tumor_pixels = np.sum(pred_mask > 0)
        total_pixels = pred_mask.shape[0] * pred_mask.shape[1]
        tumor_ratio = (tumor_pixels / total_pixels) * 100 if total_pixels > 0 else 0
        
        # 提取连通区域作为实例
        pred_mask_uint8 = (pred_mask * 255).astype(np.uint8)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(pred_mask_uint8, connectivity=8)
        
        instances = []
        instance_dicts = []  # 用于前端显示的实例信息
        confidences = []
        boxes = []
        
        for i in range(1, num_labels):  # 跳过背景(0)
            area = stats[i, cv2.CC_STAT_AREA]
            if area < 5:  # 过滤极小噪点
                continue
            
            x, y, w, h = stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_TOP], stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
            
            # 提取该实例的掩码
            instance_mask = (labels == i).astype(np.uint8)
            
            # 计算该实例的平均置信度
            instance_conf = float(np.mean(pred_prob[instance_mask > 0]))
            
            instances.append(instance_mask)
            confidences.append(instance_conf)
            boxes.append([int(x), int(y), int(x+w), int(y+h)])  # 转换为Python int
            
            # 构建前端显示用的实例信息（与YOLO格式兼容）
            instance_dicts.append({
                'id': i,
                'confidence': instance_conf,
                'area': int(area),
                'bbox': [int(x), int(y), int(x+w), int(y+h)]
            })
        
        metrics = {
            'num_instances': len(instances),
            'tumor_pixels': int(tumor_pixels),
            'total_pixels': int(total_pixels),
            'tumor_ratio': float(tumor_ratio),
            'avg_confidence': float(np.mean(confidences)) if confidences else 0.0,
            'tumor_area_ratio': float(tumor_pixels / total_pixels) if total_pixels > 0 else 0.0
        }
        
        # 构建返回结果（与YOLO格式兼容）
        result = {
            'segmentation_result': {
                'masks': instances,
                'confidences': confidences,
                'boxes': boxes
            },
            'instances': instance_dicts,  # 添加前端显示用的实例信息
            'metrics': metrics,
            'tumor_detected': bool(tumor_pixels > (total_pixels * 0.001))  # 转换为Python bool
        }
        
        return pred_mask, pred_prob, result
    
    def visualize(self, image, mask, alpha=0.5):
        """生成可视化叠加图"""
        # 确保mask是二值的
        mask_binary = (mask > 0).astype(np.uint8) * 255
        
        # 创建彩色掩码（红色）
        colored_mask = np.zeros_like(image)
        colored_mask[:, :, 2] = mask_binary  # B通道
        colored_mask[:, :, 0] = mask_binary  # R通道（混合产生紫红色）
        
        # 叠加
        overlay = cv2.addWeighted(image, 1-alpha, colored_mask, alpha, 0)
        
        # 绘制轮廓
        contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, contours, -1, (0, 255, 255), 2)  # 黄色轮廓
        
        return overlay
