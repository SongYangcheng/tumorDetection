import numpy as np
import cv2
from PIL import Image
from scipy import ndimage
from scipy.stats import skew, kurtosis
import pywt  # 需要安装PyWavelets: pip install PyWavelets
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def extract_radiomics_features(image: np.ndarray, mask: np.ndarray) -> Dict:
    """
    提取影像组学特征
    :param image: 原始图像
    :param mask: 肿瘤分割掩码
    :return: 影像组学特征字典
    """
    try:
        # 确保输入是numpy数组
        if isinstance(image, Image.Image):
            image = np.array(image)
        if isinstance(mask, Image.Image):
            mask = np.array(mask)
        
        # 确保掩码是二值化的
        mask = (mask > 0).astype(np.uint8) * 255
        
        # 转为灰度图，确保后续处理为二维
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray_image = image
        
        # 提取肿瘤区域的像素值（一维向量）
        tumor_pixels = gray_image[mask > 0]
        tumor_pixels = np.asarray(tumor_pixels).astype(np.float32).flatten()
        
        if len(tumor_pixels) == 0:
            return {
                'first_order_features': {},
                'shape_features': {},
                'texture_features': {},
                'wavelet_features': {},
                'extraction_timestamp': datetime.utcnow().isoformat()
            }
        
        # 灰度图已在上方计算
        
        # 提取一阶统计特征
        first_order_features = extract_first_order_features(tumor_pixels)
        
        # 提取形状特征
        shape_features = extract_shape_features(mask)
        
        # 提取纹理特征
        texture_features = extract_texture_features(gray_image, mask)
        
        # 提取小波特征
        wavelet_features = extract_wavelet_features(gray_image, mask)
        
        # 组合所有特征
        radiomics_features = {
            'first_order_features': first_order_features,
            'shape_features': shape_features,
            'texture_features': texture_features,
            'wavelet_features': wavelet_features,
            'extraction_timestamp': datetime.utcnow().isoformat()
        }
        
        return radiomics_features
        
    except Exception as e:
        print(f"提取影像组学特征过程中出错: {e}")
        return {
            'error': str(e),
            'extraction_timestamp': datetime.utcnow().isoformat()
        }

def extract_first_order_features(pixels: np.ndarray) -> Dict:
    """
    提取一阶统计特征
    """
    pixels = np.asarray(pixels).astype(np.float32).flatten()
    if pixels.size == 0:
        return {}
    
    # 基本统计
    mean_val = float(np.mean(pixels))
    std_val = float(np.std(pixels))
    median_val = float(np.median(pixels))
    min_val = float(np.min(pixels))
    max_val = float(np.max(pixels))
    range_val = float(max_val - min_val)
    
    # 高阶统计
    skewness = float(skew(pixels))
    kurt = float(kurtosis(pixels))
    
    # 百分位数
    p10 = float(np.percentile(pixels, 10))
    p90 = float(np.percentile(pixels, 90))
    p25 = float(np.percentile(pixels, 25))
    p75 = float(np.percentile(pixels, 75))
    
    # 能量和熵
    # 计算直方图
    hist, _ = np.histogram(pixels, bins=256, range=(0, 256))
    hist = hist.astype(float) / np.sum(hist)  # 归一化
    hist = hist[hist > 0]  # 移除零值
    
    energy = float(np.sum(hist ** 2))
    entropy = float(-np.sum(hist * np.log2(hist + 1e-10)))  # 添加小值避免log(0)
    
    return {
        'mean': mean_val,
        'std': std_val,
        'median': median_val,
        'min': min_val,
        'max': max_val,
        'range': range_val,
        'skewness': skewness,
        'kurtosis': kurt,
        'p10': p10,
        'p90': p90,
        'p25': p25,
        'p75': p75,
        'energy': energy,
        'entropy': entropy,
        'uniformity': float(np.sum(hist ** 2))  # 也称为uniformity
    }

def extract_shape_features(mask: np.ndarray) -> Dict:
    """
    提取形状特征
    """
    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) == 0:
        return {}
    
    # 选择最大的轮廓
    largest_contour = max(contours, key=cv2.contourArea)
    
    # 基本形状指标
    area = cv2.contourArea(largest_contour)
    perimeter = cv2.arcLength(largest_contour, True)
    
    # 计算各种形状特征
    if area > 0:
        # 圆形度
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # 球形度
        sphericity = np.sqrt(4 * np.pi * area) / perimeter if perimeter > 0 else 0
        
        # 紧凑度
        compactness = area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # 扁平度
        x, y, w, h = cv2.boundingRect(largest_contour)
        aspect_ratio = float(w) / h if h > 0 else 0
    else:
        circularity = 0
        sphericity = 0
        compactness = 0
        aspect_ratio = 0
    
    # 凸性
    hull = cv2.convexHull(largest_contour)
    hull_area = cv2.contourArea(hull)
    solidity = float(area) / hull_area if hull_area > 0 else 0
    
    # 延伸度
    rect = cv2.minAreaRect(largest_contour)
    width, height = rect[1]
    if width > height:
        width, height = height, width
    elongation = float(height / width) if width > 0 else 0
    
    # 计算边界框
    x, y, w, h = cv2.boundingRect(largest_contour)
    bbox_area = w * h
    
    # 计算边界框比例
    bbox_ratio = float(area) / bbox_area if bbox_area > 0 else 0
    
    return {
        'area': float(area),
        'perimeter': float(perimeter),
        'circularity': float(circularity),
        'sphericity': float(sphericity),
        'compactness': float(compactness),
        'aspect_ratio': float(aspect_ratio),
        'solidity': float(solidity),
        'elongation': float(elongation),
        'bbox_area': float(bbox_area),
        'bbox_ratio': float(bbox_ratio)
    }

def extract_texture_features(image: np.ndarray, mask: np.ndarray) -> Dict:
    """
    提取纹理特征
    """
    # 应用掩码到图像
    masked_image = np.where(mask > 0, image, 0)
    
    # 计算灰度共生矩阵(GLCM)特征
    glcm_features = calculate_glcm_features(masked_image)
    
    # 计算灰度游程矩阵(GRLM)特征
    grlm_features = calculate_grlm_features(masked_image)
    
    # 计算邻域灰度差分矩阵(NGTDM)特征
    ngtdm_features = calculate_ngtdm_features(masked_image)
    
    return {
        'glcm_features': glcm_features,
        'grlm_features': grlm_features,
        'ngtdm_features': ngtdm_features
    }

def calculate_glcm_features(image: np.ndarray, distances: List[int] = [1], angles: List[float] = [0, 45, 90, 135]) -> Dict:
    """
    计算灰度共生矩阵特征
    """
    # 简化实现，实际应用中可能需要更复杂的GLCM计算
    try:
        # 获取非零像素
        non_zero_pixels = image[image > 0]
        non_zero_pixels = np.asarray(non_zero_pixels).astype(np.float32).flatten()
        if non_zero_pixels.size == 0:
            return {
                'contrast': 0,
                'correlation': 0,
                'energy': 0,
                'homogeneity': 0
            }
        
        # 计算简化版本的GLCM特征
        # 创建简化GLCM矩阵（使用直方图近似）
        hist, _ = np.histogram(non_zero_pixels, bins=16, range=(0, 256))
        hist = hist.astype(float) / np.sum(hist)  # 归一化
        
        # 计算能量（Energy）
        energy = float(np.sum(hist ** 2))
        
        # 计算同质性（Homogeneity）
        homogeneity = float(np.sum(hist / (1 + np.arange(len(hist)))))
        
        # 计算对比度（Contrast）- 简化版本
        contrast = float(np.var(non_zero_pixels))
        
        # 计算相关性（Correlation）- 简化版本
        mean_val = float(np.mean(non_zero_pixels))
        std_val = float(np.std(non_zero_pixels))
        correlation = float(1) if std_val == 0 else float(np.mean((non_zero_pixels - mean_val) ** 2) / std_val)
        
        return {
            'contrast': contrast,
            'correlation': correlation,
            'energy': energy,
            'homogeneity': homogeneity
        }
    except Exception as e:
        print(f"计算GLCM特征时出错: {e}")
        return {
            'contrast': 0,
            'correlation': 0,
            'energy': 0,
            'homogeneity': 0
        }

def calculate_grlm_features(image: np.ndarray) -> Dict:
    """
    计算灰度游程矩阵特征
    """
    try:
        # 简化实现
        # 获取非零像素
        non_zero_pixels = image[image > 0]
        non_zero_pixels = np.asarray(non_zero_pixels).astype(np.float32).flatten()
        if non_zero_pixels.size == 0:
            return {
                'short_run_emphasis': 0,
                'long_run_emphasis': 0,
                'gray_level_nonuniformity': 0,
                'run_length_nonuniformity': 0
            }
        
        # 计算简化版本的GRLM特征
        # 将图像量化到较少的灰度级以简化计算
        qmin = float(np.min(non_zero_pixels))
        qmax = float(np.max(non_zero_pixels))
        denom = (qmax - qmin) + 1e-10
        quantized = np.floor((non_zero_pixels - qmin) / denom * 15).astype(int)
        
        # 计算游程长度特征
        unique_vals, counts = np.unique(quantized, return_counts=True)
        
        if len(counts) == 0:
            return {
                'short_run_emphasis': 0,
                'long_run_emphasis': 0,
                'gray_level_nonuniformity': 0,
                'run_length_nonuniformity': 0
            }
        
        # 简化的游程特征
        total_runs = np.sum(counts)
        if total_runs == 0:
            total_runs = 1
        
        short_run_emphasis = float(np.sum(counts * (1 / (np.arange(len(counts)) + 1)**2))) / total_runs
        long_run_emphasis = float(np.sum(counts * (np.arange(len(counts)) + 1)**2)) / total_runs
        
        return {
            'short_run_emphasis': short_run_emphasis,
            'long_run_emphasis': long_run_emphasis,
            'gray_level_nonuniformity': float(np.sum(counts**2)) / total_runs,
            'run_length_nonuniformity': 0  # 简化
        }
    except Exception as e:
        print(f"计算GRLM特征时出错: {e}")
        return {
            'short_run_emphasis': 0,
            'long_run_emphasis': 0,
            'gray_level_nonuniformity': 0,
            'run_length_nonuniformity': 0
        }

def calculate_ngtdm_features(image: np.ndarray) -> Dict:
    """
    计算邻域灰度差分矩阵特征
    """
    try:
        # 简化实现
        non_zero_pixels = image[image > 0]
        non_zero_pixels = np.asarray(non_zero_pixels).astype(np.float32).flatten()
        if non_zero_pixels.size == 0:
            return {
                'coarseness': 0,
                'contrast': 0,
                'busyness': 0,
                'complexity': 0,
                'strength': 0
            }
        
        # 计算简化版本的NGTDM特征
        # 使用局部邻域差异来计算
        coarseness = float(np.mean(np.abs(np.diff(non_zero_pixels))))
        contrast = float(np.std(non_zero_pixels))
        
        return {
            'coarseness': coarseness,
            'contrast': contrast,
            'busyness': 0,  # 简化
            'complexity': 0,  # 简化
            'strength': 0  # 简化
        }
    except Exception as e:
        print(f"计算NGTDM特征时出错: {e}")
        return {
            'coarseness': 0,
            'contrast': 0,
            'busyness': 0,
            'complexity': 0,
            'strength': 0
        }

def extract_wavelet_features(image: np.ndarray, mask: np.ndarray) -> Dict:
    """
    提取小波特征
    """
    try:
        # 应用掩码到图像
        masked_image = np.where(mask > 0, image, 0).astype(np.float32)
        
        # 执行小波变换
        coeffs = pywt.dwt2(masked_image, 'db4')
        cA, (cH, cV, cD) = coeffs  # 近似、水平、垂直、对角线系数
        
        # 计算各频带的能量
        energy_a = float(np.sum(cA ** 2))
        energy_h = float(np.sum(cH ** 2))
        energy_v = float(np.sum(cV ** 2))
        energy_d = float(np.sum(cD ** 2))
        
        # 计算各频带的标准差
        std_a = float(np.std(cA))
        std_h = float(np.std(cH))
        std_v = float(np.std(cV))
        std_d = float(np.std(cD))
        
        # 计算频带能量比例
        total_energy = energy_a + energy_h + energy_v + energy_d
        if total_energy == 0:
            total_energy = 1
        
        ratio_a = energy_a / total_energy
        ratio_h = energy_h / total_energy
        ratio_v = energy_v / total_energy
        ratio_d = energy_d / total_energy
        
        return {
            'wavelet_coefficients': {
                'approximation_energy': energy_a,
                'horizontal_energy': energy_h,
                'vertical_energy': energy_v,
                'diagonal_energy': energy_d,
                'approximation_std': std_a,
                'horizontal_std': std_h,
                'vertical_std': std_v,
                'diagonal_std': std_d,
                'approximation_ratio': ratio_a,
                'horizontal_ratio': ratio_h,
                'vertical_ratio': ratio_v,
                'diagonal_ratio': ratio_d
            }
        }
    except Exception as e:
        print(f"提取小波特征时出错: {e}")
        return {
            'error': str(e),
            'wavelet_coefficients': {
                'approximation_energy': 0,
                'horizontal_energy': 0,
                'vertical_energy': 0,
                'diagonal_energy': 0,
                'approximation_std': 0,
                'horizontal_std': 0,
                'vertical_std': 0,
                'diagonal_std': 0,
                'approximation_ratio': 0,
                'horizontal_ratio': 0,
                'vertical_ratio': 0,
                'diagonal_ratio': 0
            }
        }

def calculate_high_order_features(image: np.ndarray, mask: np.ndarray) -> Dict:
    """
    计算高阶特征
    """
    try:
        # 应用掩码到图像
        masked_image = np.where(mask > 0, image, 0)
        
        # 计算局部二值模式（LBP）特征
        lbp_features = calculate_lbp_features(masked_image)
        
        # 计算局部图像特征（Local Image Features）
        lif_features = calculate_local_image_features(masked_image)
        
        return {
            'lbp_features': lbp_features,
            'local_image_features': lif_features
        }
    except Exception as e:
        print(f"计算高阶特征时出错: {e}")
        return {
            'lbp_features': {},
            'local_image_features': {}
        }

def calculate_lbp_features(image: np.ndarray, radius: int = 3, n_points: int = 24) -> Dict:
    """
    计算局部二值模式特征
    """
    try:
        # 简化LBP实现
        height, width = image.shape
        lbp_image = np.zeros_like(image, dtype=np.uint8)
        
        # 使用简化的LBP算法
        for i in range(1, height-1):
            for j in range(1, width-1):
                center = image[i, j]
                code = 0
                power = 1
                
                # 检查3x3邻域
                for ni in [-1, -1, -1, 0, 1, 1, 1, 0]:
                    for nj in [-1, 0, 1, 1, 1, 0, -1, -1]:
                        neighbor = image[i+ni, j+nj]
                        if neighbor >= center:
                            code += power
                        power *= 2
                
                lbp_image[i, j] = code % 256
        
        # 计算LBP直方图
        hist, _ = np.histogram(lbp_image, bins=256, range=(0, 256))
        
        # 计算LBP特征
        uniform_patterns = count_uniform_patterns(lbp_image)
        uniform_ratio = uniform_patterns / (height * width) if height * width > 0 else 0
        
        return {
            'uniform_patterns': int(uniform_patterns),
            'uniformity_ratio': float(uniform_ratio),
            'histogram_entropy': float(-np.sum((hist[hist > 0] / np.sum(hist)) * 
                                            np.log2(hist[hist > 0] / np.sum(hist) + 1e-10)))
        }
    except Exception as e:
        print(f"计算LBP特征时出错: {e}")
        return {
            'uniform_patterns': 0,
            'uniformity_ratio': 0,
            'histogram_entropy': 0
        }

def count_uniform_patterns(lbp_image: np.ndarray) -> int:
    """
    计算LBP中的均匀模式数量
    """
    count = 0
    height, width = lbp_image.shape
    
    for i in range(height):
        for j in range(width):
            # 检查是否为均匀模式（最多两个0-1或1-0转换）
            binary_str = format(lbp_image[i, j], '08b')
            transitions = 0
            for k in range(len(binary_str)):
                if binary_str[k] != binary_str[(k + 1) % len(binary_str)]:
                    transitions += 1
            
            if transitions <= 2:
                count += 1
    
    return count

def calculate_local_image_features(image: np.ndarray) -> Dict:
    """
    计算局部图像特征
    """
    try:
        # 计算局部统计特征
        # 使用滑动窗口计算局部均值和标准差
        window_size = 5
        height, width = image.shape
        
        local_means = []
        local_stds = []
        
        for i in range(window_size//2, height - window_size//2):
            for j in range(window_size//2, width - window_size//2):
                patch = image[i - window_size//2:i + window_size//2 + 1,
                             j - window_size//2:j + window_size//2 + 1]
                
                local_means.append(np.mean(patch))
                local_stds.append(np.std(patch))
        
        return {
            'local_mean_mean': float(np.mean(local_means)) if local_means else 0,
            'local_mean_std': float(np.std(local_means)) if local_means else 0,
            'local_std_mean': float(np.mean(local_stds)) if local_stds else 0,
            'local_std_std': float(np.std(local_stds)) if local_stds else 0
        }
    except Exception as e:
        print(f"计算局部图像特征时出错: {e}")
        return {
            'local_mean_mean': 0,
            'local_mean_std': 0,
            'local_std_mean': 0,
            'local_std_std': 0
        }

def normalize_features(features: Dict) -> Dict:
    """
    标准化特征值
    """
    normalized_features = {}
    
    for category, feats in features.items():
        if isinstance(feats, dict):
            normalized_features[category] = {}
            for key, value in feats.items():
                if isinstance(value, (int, float)):
                    # 这里可以实现具体的标准化逻辑
                    # 为了简化，我们只复制值
                    normalized_features[category][key] = value
                else:
                    normalized_features[category][key] = value
        else:
            normalized_features[category] = feats
    
    return normalized_features
