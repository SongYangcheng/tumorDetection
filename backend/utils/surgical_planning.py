import numpy as np
import cv2
from PIL import Image
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class SurgicalPlanning:
    def __init__(self):
        """
        初始化手术规划工具
        """
        pass

def generate_surgical_plan(quantitative_report: Dict, patient_data: Dict, mask: np.ndarray) -> Dict:
    """
    生成手术计划
    :param quantitative_report: 定量分析报告
    :param patient_data: 患者数据
    :param mask: 肿瘤分割掩码
    :return: 手术计划
    """
    try:
        # 解析报告数据
        basic_metrics = quantitative_report.get('basic_metrics', {})
        morph_metrics = quantitative_report.get('morphological_metrics', {})
        intensity_metrics = quantitative_report.get('intensity_metrics', {})
        
        # 获取患者信息
        age = patient_data.get('age', 50)
        tumor_type = patient_data.get('tumor_type', 'unknown')
        tumor_location = patient_data.get('tumor_location', 'brain')
        
        # 计算手术难度指标
        surgical_difficulty = calculate_surgical_difficulty(
            basic_metrics, morph_metrics, patient_data
        )
        
        # 生成手术路径建议
        surgical_approach = generate_surgical_approach(
            basic_metrics, morph_metrics, tumor_location
        )
        
        # 评估手术风险
        risk_assessment = assess_surgical_risks(
            basic_metrics, morph_metrics, patient_data
        )
        
        # 生成手术计划
        surgical_plan = {
            'patient_info': {
                'age': age,
                'tumor_type': tumor_type,
                'tumor_location': tumor_location
            },
            'tumor_characteristics': {
                'size_category': classify_tumor_size(basic_metrics.get('tumor_area_mm2', 0)),
                'shape_irregularity': classify_shape_irregularity(morph_metrics),
                'intensity_heterogeneity': classify_intensity_heterogeneity(intensity_metrics)
            },
            'surgical_difficulty': surgical_difficulty,
            'surgical_approach': surgical_approach,
            'risk_assessment': risk_assessment,
            'recommended_procedures': generate_procedure_recommendations(
                basic_metrics, morph_metrics, patient_data
            ),
            'preoperative_considerations': generate_preoperative_considerations(
                basic_metrics, morph_metrics, patient_data
            ),
            'intraoperative_guidance': generate_intraoperative_guidance(
                basic_metrics, morph_metrics, mask
            ),
            'postoperative_monitoring': generate_postoperative_monitoring(
                basic_metrics, morph_metrics
            ),
            'planning_timestamp': datetime.utcnow().isoformat()
        }
        
        return surgical_plan
        
    except Exception as e:
        print(f"生成手术计划过程中出错: {e}")
        return {
            'error': str(e),
            'planning_timestamp': datetime.utcnow().isoformat()
        }

def calculate_surgical_difficulty(basic_metrics: Dict, morph_metrics: Dict, patient_data: Dict) -> Dict:
    """
    计算手术难度
    """
    # 基于肿瘤大小的难度评分
    size_score = 0
    area_mm2 = basic_metrics.get('tumor_area_mm2', 0)
    if area_mm2 > 100:
        size_score = 3  # 高难度
    elif area_mm2 > 50:
        size_score = 2  # 中等难度
    elif area_mm2 > 10:
        size_score = 1  # 低难度
    else:
        size_score = 0  # 极低难度
    
    # 基于形状不规则性的难度评分
    shape_score = 0
    circularity = morph_metrics.get('circularity', 1)
    if circularity < 0.4:
        shape_score = 3
    elif circularity < 0.6:
        shape_score = 2
    elif circularity < 0.8:
        shape_score = 1
    
    # 基于患者年龄的难度评分
    age_score = 0
    age = patient_data.get('age', 50)
    if age > 70:
        age_score = 2
    elif age > 60:
        age_score = 1
    
    # 计算总难度评分
    total_score = size_score + shape_score + age_score
    difficulty_level = 'Low' if total_score <= 2 else 'Moderate' if total_score <= 4 else 'High'
    
    return {
        'total_score': total_score,
        'difficulty_level': difficulty_level,
        'size_score': size_score,
        'shape_score': shape_score,
        'age_score': age_score
    }

def generate_surgical_approach(basic_metrics: Dict, morph_metrics: Dict, tumor_location: str) -> Dict:
    """
    生成手术路径建议
    """
    approach_recommendations = []
    
    # 根据肿瘤大小建议手术方式
    area_mm2 = basic_metrics.get('tumor_area_mm2', 0)
    if area_mm2 < 10:
        approach_recommendations.append("Minimally invasive approach recommended")
    elif area_mm2 < 50:
        approach_recommendations.append("Standard open surgery or endoscopic approach")
    else:
        approach_recommendations.append("Extensive open surgery required")
    
    # 根据形状不规则性建议
    circularity = morph_metrics.get('circularity', 1)
    if circularity < 0.5:
        approach_recommendations.append("Consider margin expansion due to irregular shape")
    
    # 根据位置建议
    if tumor_location.lower() in ['brain', 'head']:
        approach_recommendations.extend([
            "Neuronavigation system recommended",
            "Intraoperative MRI consideration",
            "Awake craniotomy if eloquent area involved"
        ])
    elif tumor_location.lower() in ['liver', 'abdomen']:
        approach_recommendations.extend([
            "Laparoscopic approach consideration",
            "Pringle maneuver preparation",
            "Hepatic inflow control planning"
        ])
    elif tumor_location.lower() in ['lung', 'thorax']:
        approach_recommendations.extend([
            "Video-assisted thoracoscopic surgery (VATS) consideration",
            "One-lung ventilation preparation",
            "Bronchial blocker positioning"
        ])
    
    return {
        'recommendations': approach_recommendations,
        'primary_approach': approach_recommendations[0] if approach_recommendations else "Standard approach",
        'alternative_approaches': approach_recommendations[1:] if len(approach_recommendations) > 1 else []
    }

def assess_surgical_risks(basic_metrics: Dict, morph_metrics: Dict, patient_data: Dict) -> Dict:
    """
    评估手术风险
    """
    risks = {
        'major_complications': [],
        'minor_complications': [],
        'risk_level': 'Low'
    }
    
    area_mm2 = basic_metrics.get('tumor_area_mm2', 0)
    circularity = morph_metrics.get('circularity', 1)
    age = patient_data.get('age', 50)
    
    # 评估主要并发症风险
    if area_mm2 > 50:
        risks['major_complications'].append('Bleeding risk - large tumor volume')
    if circularity < 0.5:
        risks['major_complications'].append('Incomplete resection risk - irregular shape')
    if age > 70:
        risks['major_complications'].append('Cardiopulmonary complications - advanced age')
    
    # 评估次要并发症风险
    if area_mm2 > 20:
        risks['minor_complications'].append('Wound healing issues - moderate size')
    if age > 65:
        risks['minor_complications'].append('Prolonged recovery - age factor')
    
    # 确定风险等级
    total_risks = len(risks['major_complications']) + len(risks['minor_complications'])
    if total_risks >= 3:
        risks['risk_level'] = 'High'
    elif total_risks >= 1:
        risks['risk_level'] = 'Moderate'
    else:
        risks['risk_level'] = 'Low'
    
    return risks

def generate_procedure_recommendations(basic_metrics: Dict, morph_metrics: Dict, patient_data: Dict) -> List[str]:
    """
    生成手术程序推荐
    """
    recommendations = []
    
    area_mm2 = basic_metrics.get('tumor_area_mm2', 0)
    circularity = morph_metrics.get('circularity', 1)
    age = patient_data.get('age', 50)
    
    # 基于大小的推荐
    if area_mm2 > 50:
        recommendations.extend([
            "Extensive resection with adequate margins",
            "Consider staged resection if multiple lesions",
            "Prepare for blood transfusion",
            "Intraoperative frozen section analysis"
        ])
    elif area_mm2 > 10:
        recommendations.extend([
            "Standard resection with 1-2cm margins",
            "Intraoperative ultrasound for margin assessment",
            "Consider sentinel lymph node biopsy if applicable"
        ])
    else:
        recommendations.extend([
            "Local excision with minimal margins",
            "Simple enucleation if feasible",
            "Minimally invasive technique preference"
        ])
    
    # 基于形状的推荐
    if circularity < 0.5:
        recommendations.append("Extended margins due to irregular shape")
        recommendations.append("Consider adjuvant therapy planning")
    
    # 基于年龄的推荐
    if age > 70:
        recommendations.extend([
            "Minimize anesthesia time",
            "Early mobilization protocol",
            "Enhanced recovery pathway"
        ])
    
    return recommendations

def generate_preoperative_considerations(basic_metrics: Dict, morph_metrics: Dict, patient_data: Dict) -> List[str]:
    """
    生成术前考虑事项
    """
    considerations = []
    
    area_mm2 = basic_metrics.get('tumor_area_mm2', 0)
    age = patient_data.get('age', 50)
    tumor_location = patient_data.get('tumor_location', 'unknown')
    
    # 基于大小的考虑
    if area_mm2 > 50:
        considerations.extend([
            "Blood product availability check",
            "Anesthesia consultation for lengthy procedure",
            "ICU bed reservation",
            "Multidisciplinary team discussion"
        ])
    
    # 基于年龄的考虑
    if age > 70:
        considerations.extend([
            "Cardiopulmonary evaluation",
            "Anesthesia risk stratification",
            "Postoperative care planning",
            "Nutritional assessment"
        ])
    
    # 基于位置的考虑
    if tumor_location.lower() in ['brain', 'head']:
        considerations.extend([
            "Neurological baseline assessment",
            "Corticosteroid preparation",
            "Anticonvulsant prophylaxis planning"
        ])
    elif tumor_location.lower() in ['liver', 'abdomen']:
        considerations.extend([
            "Liver function tests",
            "Coagulation profile",
            "Bowel preparation if needed"
        ])
    
    return considerations

def generate_intraoperative_guidance(basic_metrics: Dict, morph_metrics: Dict, mask: np.ndarray) -> Dict:
    """
    生成术中指导
    """
    # 分析掩码以获取边界信息
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boundary_info = {}
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        
        # 获取边界框
        x, y, w, h = cv2.boundingRect(largest_contour)
        boundary_info = {
            'center_x': int(x + w / 2),
            'center_y': int(y + h / 2),
            'width': int(w),
            'height': int(h),
            'area': int(cv2.contourArea(largest_contour))
        }
    
    guidance = {
        'tumor_boundary_mapping': boundary_info,
        'resection_margin_guidance': calculate_resection_margin(morph_metrics),
        'critical_structure_avoidance': identify_critical_structures(mask),
        'monitoring_recommendations': [
            "Continuous monitoring of vital signs",
            "Neurological monitoring if brain tumor",
            "Hemostasis verification"
        ]
    }
    
    return guidance

def calculate_resection_margin(morph_metrics: Dict) -> Dict:
    """
    计算切除边缘
    """
    circularity = morph_metrics.get('circularity', 1)
    
    if circularity < 0.5:
        # 不规则形状需要更大边缘
        margin = 2.0  # cm
        recommendation = "Extended margins recommended due to irregular shape"
    elif circularity < 0.7:
        margin = 1.5  # cm
        recommendation = "Standard extended margins"
    else:
        margin = 1.0  # cm
        recommendation = "Standard margins appropriate"
    
    return {
        'recommended_margin_cm': margin,
        'rationale': recommendation
    }

def identify_critical_structures(mask: np.ndarray) -> List[Dict]:
    """
    识别关键结构（简化版本）
    """
    # 这里是简化的实现，实际应用中可能需要更复杂的解剖结构识别
    return [
        {
            'structure_name': 'Major blood vessel',
            'distance_mm': 5.0,
            'risk_level': 'Moderate',
            'avoidance_strategy': 'Careful dissection with vessel loops'
        },
        {
            'structure_name': 'Nerve bundle',
            'distance_mm': 8.0,
            'risk_level': 'High',
            'avoidance_strategy': 'Nerve monitoring and preservation'
        }
    ]

def generate_postoperative_monitoring(basic_metrics: Dict, morph_metrics: Dict) -> Dict:
    """
    生成术后监测计划
    """
    area_mm2 = basic_metrics.get('tumor_area_mm2', 0)
    circularity = morph_metrics.get('circularity', 1)
    
    monitoring_plan = {
        'immediate_postoperative': [],
        'early_recovery': [],
        'follow_up_schedule': []
    }
    
    # 立即术后监测
    if area_mm2 > 50:
        monitoring_plan['immediate_postoperative'].extend([
            "ICU monitoring for 24-48 hours",
            "Hourly neurological checks if brain tumor",
            "Bleeding and infection monitoring"
        ])
    else:
        monitoring_plan['immediate_postoperative'].extend([
            "Regular ward monitoring",
            "Pain management protocol",
            "Early mobilization"
        ])
    
    # 早期康复监测
    if circularity < 0.5:
        monitoring_plan['early_recovery'].append("Enhanced surveillance for recurrence")
    
    # 随访计划
    monitoring_plan['follow_up_schedule'].extend([
        {"timeframe": "1 week", "tests": ["Wound check", "Basic labs"]},
        {"timeframe": "1 month", "tests": ["Imaging", "Tumor markers if applicable"]},
        {"timeframe": "3 months", "tests": ["Comprehensive imaging", "Oncology consultation"]}
    ])
    
    return monitoring_plan

def classify_tumor_size(area_mm2: float) -> str:
    """
    分类肿瘤大小
    """
    if area_mm2 < 10:
        return 'Small'
    elif area_mm2 < 50:
        return 'Medium'
    else:
        return 'Large'

def classify_shape_irregularity(morph_metrics: Dict) -> str:
    """
    分类形状不规则性
    """
    circularity = morph_metrics.get('circularity', 1)
    
    if circularity > 0.8:
        return 'Regular'
    elif circularity > 0.6:
        return 'Moderately irregular'
    else:
        return 'Highly irregular'

def classify_intensity_heterogeneity(intensity_metrics: Dict) -> str:
    """
    分类强度异质性
    """
    std_intensity = intensity_metrics.get('std_intensity', 0)
    
    if std_intensity > 50:
        return 'Highly heterogeneous'
    elif std_intensity > 20:
        return 'Moderately heterogeneous'
    else:
        return 'Homogeneous'