"""
脑肿瘤MRI分割 - 推理模块
使用训练好的ResNeXtUNet权重进行预测
"""

import os
import cv2
import torch
import numpy as np
from torch import nn
from torchvision.models import resnext50_32x4d


# =====================================================
# 1. 模型定义（必须与训练时完全一致）
# =====================================================

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
        
        # 转置卷积上采样（2倍）
        self.deconv = nn.ConvTranspose2d(
            in_channels // 4, 
            in_channels // 4, 
            kernel_size=4,
            stride=2, 
            padding=1, 
            output_padding=0
        )
        
        # 1x1卷积
        self.conv2 = ConvRelu(in_channels // 4, out_channels, 1, 0)
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.deconv(x)
        x = self.conv2(x)
        return x


class ResNeXtUNet(nn.Module):
    """基于ResNeXt50的U-Net模型"""
    
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


# =====================================================
# 2. 推理类
# =====================================================

class BrainTumorPredictor:
    """脑肿瘤分割预测器"""
    
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
        print(f"正在加载模型...")
        self.model = ResNeXtUNet(n_classes=1).to(device)
        
        # 加载权重
        print(f"正在加载权重文件: {weight_path}")
        checkpoint = torch.load(weight_path, map_location=device)
        
        # 调试：检查checkpoint内容
        if isinstance(checkpoint, dict):
            print(f"Checkpoint keys: {checkpoint.keys()}")
            if 'state_dict' in checkpoint:
                print(f"使用 state_dict 加载权重")
                state_dict = checkpoint['state_dict']
            else:
                print(f"直接使用 checkpoint 作为 state_dict")
                state_dict = checkpoint
        else:
            print(f"Checkpoint 是模型参数字典")
            state_dict = checkpoint
        
        # 加载权重并检查
        try:
            self.model.load_state_dict(state_dict)
            print(f"[成功] 权重加载成功")
        except Exception as e:
            print(f"[错误] 权重加载失败: {e}")
            print(f"尝试严格匹配=False")
            self.model.load_state_dict(state_dict, strict=False)
            
        self.model.eval()
        print(f"模型加载成功 设备: {device}, 阈值: {threshold}")
        
        # 预处理参数
        self.resize_size = 256
        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])
    
    def predict(self, image_path):
        """
        预测单张图像
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            pred_mask: 预测掩码 (256x256, numpy array)
            pred_prob: 预测概率图 (256x256, numpy array)
        """
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_size = image.shape[:2]
        
        # 预处理
        img = cv2.resize(image, (self.resize_size, self.resize_size))
        img = img.astype(np.float32) / 255.0
        img = (img - self.mean) / self.std
        img_tensor = torch.from_numpy(img).float().permute(2, 0, 1).unsqueeze(0).to(self.device)
        
        # 推理
        with torch.no_grad():
            pred_prob = self.model(img_tensor)
            pred_prob = pred_prob.cpu().numpy()[0, 0]
        
        # 二值化
        pred_mask = np.copy(pred_prob)
        pred_mask[pred_mask < self.threshold] = 0
        pred_mask[pred_mask >= self.threshold] = 255
        pred_mask = pred_mask.astype(np.uint8)
        
        # 调整回原始尺寸
        pred_mask = cv2.resize(pred_mask, (original_size[1], original_size[0]))
        pred_prob = cv2.resize(pred_prob, (original_size[1], original_size[0]))
        
        return pred_mask, pred_prob

    def predict_array(self, image_array):
        """
        接受 numpy 数组输入的快速预测，用于内存态切片
        
        Args:
            image_array: numpy数组图像
            
        Returns:
            pred_mask: 预测掩码
            pred_prob: 预测概率图
        """
        if image_array is None:
            raise ValueError("image_array 不能为空")

        img = image_array

        # 将浮点/其他类型归一化到0-255并转为uint8
        if img.dtype != np.uint8:
            v_min, v_max = float(np.min(img)), float(np.max(img))
            img = ((img - v_min) / (v_max - v_min + 1e-8) * 255.0).astype(np.uint8)

        # 转换为RGB
        if len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1):
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            img = img.astype(np.uint8)

        original_size = img.shape[:2]

        # 预处理
        img_resized = cv2.resize(img, (self.resize_size, self.resize_size))
        img_resized = img_resized.astype(np.float32) / 255.0
        img_resized = (img_resized - self.mean) / self.std
        img_tensor = torch.from_numpy(img_resized).float().permute(2, 0, 1).unsqueeze(0).to(self.device)

        # 推理
        with torch.no_grad():
            pred_prob = self.model(img_tensor)
            
            # 调试：检查模型输出
            print(f"  模型输出shape: {pred_prob.shape}, min={pred_prob.min():.4f}, max={pred_prob.max():.4f}, mean={pred_prob.mean():.4f}")
            
            pred_prob = pred_prob.cpu().numpy()[0, 0]
            
        print(f"  预测概率图: min={pred_prob.min():.4f}, max={pred_prob.max():.4f}, >0.1的像素数={np.sum(pred_prob > 0.1)}")

        # 二值化
        pred_mask = np.copy(pred_prob)
        pred_mask[pred_mask < self.threshold] = 0
        pred_mask[pred_mask >= self.threshold] = 255
        pred_mask = pred_mask.astype(np.uint8)

        # 调整回原始尺寸
        pred_mask = cv2.resize(pred_mask, (original_size[1], original_size[0]))
        pred_prob = cv2.resize(pred_prob, (original_size[1], original_size[0]))

        return pred_mask, pred_prob
