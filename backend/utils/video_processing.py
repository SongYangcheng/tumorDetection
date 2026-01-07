"""
视频处理工具模块
支持视频上传、帧提取、实时流检测
"""

import cv2
import numpy as np
import os
from typing import Generator, Tuple, List, Optional
import base64
from PIL import Image
import io


class VideoProcessor:
    """视频处理类"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化视频处理器
        
        Args:
            model_path: YOLO模型路径（可选）
        """
        self.model = None
        if model_path and os.path.exists(model_path):
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_path)
                print(f"[成功] YOLO模型加载成功: {model_path}")
            except Exception as e:
                print(f"YOLO模型加载失败: {e}")
    
    def extract_frames(self, video_path: str, frame_interval: int = 30, 
                      max_frames: int = 100) -> Generator[Tuple[int, np.ndarray], None, None]:
        """
        从视频中提取关键帧
        
        Args:
            video_path: 视频文件路径
            frame_interval: 帧间隔（每隔多少帧提取一帧）
            max_frames: 最大提取帧数
            
        Yields:
            (frame_number, frame_image): 帧编号和图像数据
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        frame_count = 0
        extracted_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # 按间隔提取帧
                if frame_count % frame_interval == 0:
                    yield (frame_count, frame)
                    extracted_count += 1
                    
                    if extracted_count >= max_frames:
                        break
                
                frame_count += 1
        
        finally:
            cap.release()
    
    def get_video_info(self, video_path: str) -> dict:
        """
        获取视频信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        info = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return info
    
    def detect_frame(self, frame: np.ndarray, conf_threshold: float = 0.25) -> dict:
        """
        对单帧进行检测
        
        Args:
            frame: 图像帧
            conf_threshold: 置信度阈值
            
        Returns:
            检测结果字典
        """
        if self.model is None:
            return {
                'has_tumor': False,
                'num_instances': 0,
                'confidences': [],
                'boxes': []
            }
        
        try:
            results = self.model.predict(
                source=frame,
                conf=conf_threshold,
                verbose=False
            )
            
            result = results[0]
            
            # 提取检测结果
            boxes = []
            confidences = []
            
            if result.boxes is not None:
                boxes_data = result.boxes.xyxy.cpu().numpy()
                conf_data = result.boxes.conf.cpu().numpy()
                
                for i in range(len(boxes_data)):
                    boxes.append(boxes_data[i].tolist())
                    confidences.append(float(conf_data[i]))
            
            return {
                'has_tumor': len(boxes) > 0,
                'num_instances': len(boxes),
                'confidences': confidences,
                'boxes': boxes,
                'avg_confidence': float(np.mean(confidences)) if confidences else 0.0
            }
        
        except Exception as e:
            print(f"检测失败: {e}")
            return {
                'has_tumor': False,
                'num_instances': 0,
                'confidences': [],
                'boxes': []
            }
    
    def process_video(self, video_path: str, output_path: str, 
                     conf_threshold: float = 0.25, 
                     frame_interval: int = 1) -> List[dict]:
        """
        处理视频并生成检测结果视频
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            conf_threshold: 置信度阈值
            frame_interval: 处理间隔（1=每帧都处理）
            
        Returns:
            每帧的检测结果列表
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        # 获取视频属性
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        results_list = []
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # 按间隔处理
                if frame_count % frame_interval == 0:
                    detection_result = self.detect_frame(frame, conf_threshold)
                    results_list.append({
                        'frame': frame_count,
                        **detection_result
                    })
                    
                    # 在帧上绘制检测框
                    if detection_result['has_tumor']:
                        for box, conf in zip(detection_result['boxes'], 
                                           detection_result['confidences']):
                            x1, y1, x2, y2 = map(int, box)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            cv2.putText(frame, f'{conf:.2f}', (x1, y1-10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                out.write(frame)
                frame_count += 1
        
        finally:
            cap.release()
            out.release()
        
        return results_list
    
    def frame_to_base64(self, frame: np.ndarray) -> str:
        """
        将帧转换为base64字符串
        
        Args:
            frame: 图像帧
            
        Returns:
            base64编码的字符串
        """
        # 转换为RGB
        if len(frame.shape) == 3:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            frame_rgb = frame
        
        # 转换为PIL Image
        pil_img = Image.fromarray(frame_rgb)
        
        # 转换为base64
        buffered = io.BytesIO()
        pil_img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_str}"
    
    def base64_to_frame(self, base64_str: str) -> np.ndarray:
        """
        将base64字符串转换为帧
        
        Args:
            base64_str: base64编码的字符串
            
        Returns:
            图像帧
        """
        # 移除data URL前缀
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        # 解码
        img_data = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_data))
        
        # 转换为numpy数组
        frame = np.array(img)
        
        # 转换为BGR（OpenCV格式）
        if len(frame.shape) == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        return frame


def analyze_video_summary(results_list: List[dict]) -> dict:
    """
    分析视频检测结果摘要
    
    Args:
        results_list: 帧检测结果列表
        
    Returns:
        摘要统计信息
    """
    total_frames = len(results_list)
    tumor_frames = sum(1 for r in results_list if r['has_tumor'])
    
    all_confidences = []
    for r in results_list:
        all_confidences.extend(r['confidences'])
    
    return {
        'total_frames_analyzed': total_frames,
        'frames_with_tumor': tumor_frames,
        'tumor_detection_rate': tumor_frames / total_frames if total_frames > 0 else 0,
        'avg_confidence': float(np.mean(all_confidences)) if all_confidences else 0.0,
        'max_confidence': float(np.max(all_confidences)) if all_confidences else 0.0,
        'total_detections': len(all_confidences)
    }
