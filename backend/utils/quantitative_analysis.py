import numpy as np
import cv2
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from collections import defaultdict

class TumorQuantitativeAnalyzer:
    def __init__(self):
        """
        初始化定量分析器
        """
        pass
    
    def create_quantitative_report(self, original_image, mask, segmentation_result=None):
        """
        创建定量分析报告
        :param original_image: 原始图像
        :param mask: 肿瘤分割掩码
        :param segmentation_result: 分割结果（可选）
        :return: 包含定量指标的报告
        """
        try:
            # 确保输入是numpy数组
            if isinstance(original_image, Image.Image):
                original_image = np.array(original_image)
            if isinstance(mask, Image.Image):
                mask = np.array(mask)
            
            # 确保掩码是二值化的
            mask = (mask > 0).astype(np.uint8) * 255
            
            # 计算基本指标
            basic_metrics = self._calculate_basic_metrics(original_image, mask)
            
            # 计算形态学指标
            morphological_metrics = self._calculate_morphological_metrics(mask)
            
            # 计算纹理特征
            texture_metrics = self._calculate_texture_metrics(original_image, mask)
            
            # 计算强度特征
            intensity_metrics = self._calculate_intensity_metrics(original_image, mask)
            
            # 合并所有指标
            report = {
                'basic_metrics': basic_metrics,
                'morphological_metrics': morphological_metrics,
                'texture_metrics': texture_metrics,
                'intensity_metrics': intensity_metrics,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            print(f"定量分析过程中出错: {e}")
            return {
                'error': str(e),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_basic_metrics(self, original_image, mask):
        """
        计算基本指标
        """
        # 肿瘤区域像素数
        tumor_pixels = np.sum(mask > 0)
        
        # 总像素数
        total_pixels = mask.size
        
        # 肿瘤面积占比
        area_ratio = tumor_pixels / total_pixels if total_pixels > 0 else 0
        
        # 肿瘤体积（假设每个像素代表一定的物理尺寸）
        pixel_area_mm2 = 0.1  # 假设每个像素代表0.1mm²（实际值需要根据影像参数调整）
        tumor_area_mm2 = tumor_pixels * pixel_area_mm2
        
        return {
            'tumor_pixels': int(tumor_pixels),
            'total_pixels': int(total_pixels),
            'area_ratio': float(area_ratio),
            'tumor_area_mm2': float(tumor_area_mm2),
            'tumor_volume_mm3': float(tumor_area_mm2 * 1.0)  # 假设厚度为1mm
        }
    
    def _calculate_morphological_metrics(self, mask):
        """
        计算形态学指标
        """
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return {
                'contour_count': 0,
                'largest_contour_area': 0,
                'largest_contour_perimeter': 0,
                'circularity': 0,
                'aspect_ratio': 0,
                'solidity': 0
            }
        
        # 选择最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)
        
        # 计算轮廓面积和周长
        area = cv2.contourArea(largest_contour)
        perimeter = cv2.arcLength(largest_contour, True)
        
        # 计算圆形度
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # 计算边界框
        x, y, w, h = cv2.boundingRect(largest_contour)
        aspect_ratio = float(w) / h if h > 0 else 0
        
        # 计算凸包
        hull = cv2.convexHull(largest_contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0
        
        # 计算等效直径
        equivalent_diameter = np.sqrt(4 * area / np.pi) if area > 0 else 0
        
        return {
            'contour_count': len(contours),
            'largest_contour_area': float(area),
            'largest_contour_perimeter': float(perimeter),
            'circularity': float(circularity),
            'aspect_ratio': float(aspect_ratio),
            'solidity': float(solidity),
            'equivalent_diameter': float(equivalent_diameter)
        }
    
    def _calculate_texture_metrics(self, original_image, mask):
        """
        计算纹理特征
        """
        # 确保原始图像是灰度图
        if len(original_image.shape) == 3:
            gray_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
        else:
            gray_image = original_image
        
        # 应用掩码到灰度图像
        masked_image = np.where(mask > 0, gray_image, 0)
        
        # 计算灰度共生矩阵(GLCM)特征
        glcm_features = self._calculate_glcm_features(masked_image)
        
        # 计算局部二值模式(LBP)特征
        lbp_features = self._calculate_lbp_features(masked_image)
        
        return {
            'glcm_features': glcm_features,
            'lbp_features': lbp_features
        }
    
    def _calculate_glcm_features(self, image):
        """
        计算灰度共生矩阵特征
        """
        # 这里简化实现，实际应用中可能需要更复杂的GLCM计算
        # 对于医学影像，通常需要考虑多个方向和距离
        try:
            # 计算图像的统计特征
            non_zero_pixels = image[image > 0]
            if len(non_zero_pixels) == 0:
                return {
                    'mean': 0,
                    'std': 0,
                    'energy': 0,
                    'contrast': 0,
                    'homogeneity': 0,
                    'correlation': 0
                }
            
            mean_val = float(np.mean(non_zero_pixels))
            std_val = float(np.std(non_zero_pixels))
            
            # 简化的能量和对比度计算
            energy = float(np.sum(non_zero_pixels ** 2))
            contrast = float(np.var(non_zero_pixels))
            
            # 均匀性
            hist, _ = np.histogram(non_zero_pixels, bins=256, range=(0, 256))
            hist = hist.astype(float) / np.sum(hist)  # 归一化
            homogeneity = float(np.sum(hist / (1 + np.arange(256))))
            
            return {
                'mean': mean_val,
                'std': std_val,
                'energy': energy,
                'contrast': contrast,
                'homogeneity': homogeneity,
                'correlation': 0  # 简化实现
            }
        except:
            return {
                'mean': 0,
                'std': 0,
                'energy': 0,
                'contrast': 0,
                'homogeneity': 0,
                'correlation': 0
            }
    
    def _calculate_lbp_features(self, image):
        """
        计算局部二值模式特征
        """
        try:
            # 简化的LBP特征计算
            non_zero_pixels = image[image > 0]
            if len(non_zero_pixels) == 0:
                return {'uniformity': 0, 'complexity': 0}
            
            # 计算均匀性（简化）
            unique_vals = len(np.unique(non_zero_pixels))
            total_vals = len(non_zero_pixels)
            uniformity = float(unique_vals) / total_vals if total_vals > 0 else 0
            
            return {
                'uniformity': uniformity,
                'complexity': 1 - uniformity  # 简化的复杂度
            }
        except:
            return {'uniformity': 0, 'complexity': 0}
    
    def _calculate_intensity_metrics(self, original_image, mask):
        """
        计算强度特征
        """
        # 确保原始图像是灰度图
        if len(original_image.shape) == 3:
            gray_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
        else:
            gray_image = original_image
        
        # 应用掩码获取肿瘤区域的像素值
        tumor_pixels = gray_image[mask > 0]
        
        if len(tumor_pixels) == 0:
            return {
                'mean_intensity': 0,
                'std_intensity': 0,
                'min_intensity': 0,
                'max_intensity': 0,
                'median_intensity': 0
            }
        
        return {
            'mean_intensity': float(np.mean(tumor_pixels)),
            'std_intensity': float(np.std(tumor_pixels)),
            'min_intensity': float(np.min(tumor_pixels)),
            'max_intensity': float(np.max(tumor_pixels)),
            'median_intensity': float(np.median(tumor_pixels))
        }
    
    def visualize_tumor_metrics(self, report):
        """
        可视化肿瘤指标
        """
        try:
            # 创建图表
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('Tumor Quantitative Analysis', fontsize=16)
            
            # 基本指标可视化
            basic_metrics = report.get('basic_metrics', {})
            ax1 = axes[0, 0]
            ax1.bar(['Area Ratio', 'Tumor Area (mm²)'], 
                   [basic_metrics.get('area_ratio', 0), basic_metrics.get('tumor_area_mm2', 0)])
            ax1.set_title('Basic Metrics')
            ax1.tick_params(axis='x', rotation=45)
            
            # 形态学指标可视化
            morph_metrics = report.get('morphological_metrics', {})
            ax2 = axes[0, 1]
            ax2.bar(['Circularity', 'Aspect Ratio', 'Solidity'], 
                   [morph_metrics.get('circularity', 0), 
                    morph_metrics.get('aspect_ratio', 0), 
                    morph_metrics.get('solidity', 0)])
            ax2.set_title('Morphological Metrics')
            ax2.tick_params(axis='x', rotation=45)
            
            # 强度特征可视化
            intensity_metrics = report.get('intensity_metrics', {})
            ax3 = axes[1, 0]
            intensities = [intensity_metrics.get('mean_intensity', 0), 
                          intensity_metrics.get('median_intensity', 0)]
            ax3.bar(['Mean', 'Median'], intensities)
            ax3.set_title('Intensity Metrics')
            
            # 纹理特征可视化
            texture_metrics = report.get('texture_metrics', {}).get('glcm_features', {})
            ax4 = axes[1, 1]
            texture_vals = [texture_metrics.get('homogeneity', 0), 
                           texture_metrics.get('energy', 0)]
            ax4.bar(['Homogeneity', 'Energy'], texture_vals)
            ax4.set_title('Texture Metrics')
            
            plt.tight_layout()
            
            # 将图表转换为base64字符串
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_str
            
        except Exception as e:
            print(f"可视化过程中出错: {e}")
            return ""
    
    def generate_analysis_summary(self, report):
        """
        生成分析摘要
        """
        try:
            basic_metrics = report.get('basic_metrics', {})
            morph_metrics = report.get('morphological_metrics', {})
            intensity_metrics = report.get('intensity_metrics', {})
            
            summary = {
                'tumor_size_category': self._classify_tumor_size(basic_metrics.get('tumor_area_mm2', 0)),
                'shape_characteristics': self._describe_shape_characteristics(morph_metrics),
                'intensity_characteristics': self._describe_intensity_characteristics(intensity_metrics),
                'risk_assessment': self._assess_risk_level(report)
            }
            
            return summary
        except Exception as e:
            print(f"生成摘要过程中出错: {e}")
            return {'error': str(e)}
    
    def _classify_tumor_size(self, area_mm2):
        """
        分类肿瘤大小
        """
        if area_mm2 < 10:
            return 'Small (<10mm²)'
        elif area_mm2 < 50:
            return 'Medium (10-50mm²)'
        else:
            return 'Large (>50mm²)'
    
    def _describe_shape_characteristics(self, morph_metrics):
        """
        描述形状特征
        """
        circularity = morph_metrics.get('circularity', 0)
        aspect_ratio = morph_metrics.get('aspect_ratio', 1)
        
        if circularity > 0.8:
            shape_desc = 'Regular'
        elif circularity > 0.5:
            shape_desc = 'Moderately irregular'
        else:
            shape_desc = 'Highly irregular'
        
        if aspect_ratio > 2.0 or aspect_ratio < 0.5:
            shape_desc += ', elongated'
        else:
            shape_desc += ', compact'
        
        return shape_desc
    
    def _describe_intensity_characteristics(self, intensity_metrics):
        """
        描述强度特征
        """
        mean_intensity = intensity_metrics.get('mean_intensity', 0)
        std_intensity = intensity_metrics.get('std_intensity', 0)
        
        if std_intensity > 50:
            intensity_desc = 'Highly heterogeneous'
        elif std_intensity > 20:
            intensity_desc = 'Moderately heterogeneous'
        else:
            intensity_desc = 'Homogeneous'
        
        return f"Mean: {mean_intensity:.2f}, Std: {std_intensity:.2f}, {intensity_desc}"
    
    def _assess_risk_level(self, report):
        """
        评估风险等级
        """
        basic_metrics = report.get('basic_metrics', {})
        morph_metrics = report.get('morphological_metrics', {})
        
        risk_score = 0
        
        # 基于面积的风险评分
        area_mm2 = basic_metrics.get('tumor_area_mm2', 0)
        if area_mm2 > 100:
            risk_score += 3
        elif area_mm2 > 50:
            risk_score += 2
        elif area_mm2 > 10:
            risk_score += 1
        
        # 基于形状不规则性的风险评分
        circularity = morph_metrics.get('circularity', 0)
        if circularity < 0.4:
            risk_score += 2
        elif circularity < 0.6:
            risk_score += 1
        
        # 基于不均匀性的风险评分
        solidity = morph_metrics.get('solidity', 1)
        if solidity < 0.7:
            risk_score += 1
        
        if risk_score >= 5:
            return 'High'
        elif risk_score >= 3:
            return 'Medium'
        else:
            return 'Low'
