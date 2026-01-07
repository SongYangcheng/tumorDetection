from PIL import Image
import numpy as np

def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    预处理图像用于YOLO模型
    """
    # 调整大小到640x640（YOLO标准输入）
    image = image.resize((640, 640))
    # 确保为RGB三通道
    if image.mode != 'RGB':
        image = image.convert('RGB')
    # 转换为numpy数组
    img_array = np.array(image)
    return img_array

def postprocess_results(results):
    """
    后处理检测结果
    """
    processed = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            processed.append({
                'class': result.names[int(box.cls[0])],
                'confidence': float(box.conf[0]),
                'bbox': box.xyxy[0].tolist()
            })
    return processed
