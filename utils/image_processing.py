# utils/image_processing.py
import cv2
import torch
import numpy as np
import base64
from PIL import Image
import torchvision.transforms as transforms
from io import BytesIO

class ImageProcessor:
    """Xử lý ảnh và tiền xử lý cho models"""
    
    @staticmethod
    def preprocess_image(img, size=224):
        """Tiền xử lý ảnh cho model phân loại"""
        transform = transforms.Compose([
            transforms.Resize((size, size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        return transform(img)
    
    @staticmethod
    def classify_cell(crop_img, model, device):
        """Phân loại tế bào từ ảnh đã crop"""
        if isinstance(crop_img, np.ndarray):
            crop_img = Image.fromarray(cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB))
        
        input_tensor = ImageProcessor.preprocess_image(crop_img).unsqueeze(0).to(device)
        with torch.no_grad():
            output = model(input_tensor)
        return torch.argmax(output).item()
    
    @staticmethod
    def image_to_base64(img):
        """Chuyển đổi ảnh thành base64 string"""
        _, buffer = cv2.imencode('.jpg', img)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
    
    @staticmethod
    def draw_detection_results(img, boxes, classes, class_names, colors):
        """Vẽ kết quả phát hiện lên ảnh"""
        result_img = img.copy()
        
        for box, cls in zip(boxes, classes):
            class_name = class_names[cls] if cls < len(class_names) else f"Class-{cls}"
            color = colors.get(class_name, (200, 200, 200))
            
            # Vẽ bounding box
            cv2.rectangle(result_img, (box[0], box[1]), (box[2], box[3]), color, 2)
            
            # Vẽ nhãn
            cv2.putText(result_img, class_name, (box[0], box[1]-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return result_img
    
    @staticmethod
    def draw_stage1_results(img, boxes, stage1_classes, num_healthy, num_unhealthy):
        """Vẽ kết quả giai đoạn 1 (Healthy/Unhealthy)"""
        result_img = img.copy()
        
        colors = {
            'Healthy': (0, 255, 0),    # Green
            'Unhealthy': (255, 0, 0)   # Red
        }
        
        for box, cls in zip(boxes, stage1_classes):
            class_name = 'Healthy' if cls == 0 else 'Unhealthy'
            color = colors[class_name]
            
            # Vẽ bounding box
            cv2.rectangle(result_img, (box[0], box[1]), (box[2], box[3]), color, 2)
            
            # Vẽ nhãn
            cv2.putText(result_img, class_name, (box[0], box[1]-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Thêm thống kê lên ảnh
        stats_text = f"Healthy: {num_healthy} | Unhealthy: {num_unhealthy}"
        cv2.putText(result_img, stats_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(result_img, stats_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
        
        return result_img
    
    @staticmethod
    def create_fp_fn_images(img, pred_boxes, pred_classes, gt_boxes, gt_classes, 
                           comparison_result, data_info):
        """Tạo ảnh hiển thị False Positives và False Negatives"""
        from config import AppConfig
        
        fp_img = img.copy()
        fn_img = img.copy()
        
        colors = AppConfig.CELL_COLORS
        data_classes = data_info['names']
        fp_count = 0
        fn_count = 0
        
        # Tìm false positives (predictions không match)
        for i, (box, cls) in enumerate(zip(pred_boxes, pred_classes)):
            if i not in comparison_result['matched_pred']:
                class_name = data_classes[cls] if cls < len(data_classes) else f"Class-{cls}"
                color = colors.get(class_name, (200, 200, 200))
                cv2.rectangle(fp_img, (box[0], box[1]), (box[2], box[3]), color, 3)
                cv2.putText(fp_img, f"FP: {class_name}", (box[0], box[1]-5), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                fp_count += 1
        
        # Tìm false negatives (ground truth không match)
        for i, (box, cls) in enumerate(zip(gt_boxes, gt_classes)):
            if i not in comparison_result['matched_gt']:
                class_name = data_classes[cls] if cls < len(data_classes) else f"Class-{cls}"
                color = colors.get(class_name, (200, 200, 200))
                cv2.rectangle(fn_img, (box[0], box[1]), (box[2], box[3]), color, 3)
                cv2.putText(fn_img, f"FN: {class_name}", (box[0], box[1]-5), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                fn_count += 1
        
        return fp_img, fn_img, fp_count, fn_count