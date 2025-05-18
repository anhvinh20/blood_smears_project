# utils/ground_truth.py
import os

class GroundTruthProcessor:
    """Xử lý ground truth labels và so sánh kết quả"""
    
    @staticmethod
    def parse_yolo_label(label_path, img_width, img_height):
        """Parse file label định dạng YOLO"""
        boxes = []
        classes = []
        
        if not os.path.exists(label_path):
            return boxes, classes
        
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5:
                class_id = int(parts[0])
                x_center = float(parts[1]) * img_width
                y_center = float(parts[2]) * img_height
                width = float(parts[3]) * img_width
                height = float(parts[4]) * img_height
                
                x1 = int(x_center - width/2)
                y1 = int(y_center - height/2)
                x2 = int(x_center + width/2)
                y2 = int(y_center + height/2)
                
                boxes.append([x1, y1, x2, y2])
                classes.append(class_id)
        
        return boxes, classes
    
    @staticmethod
    def calculate_iou(box1, box2):
        """Tính Intersection over Union giữa hai boxes"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union = area1 + area2 - intersection
        
        if union == 0:
            return 0
        
        return intersection / union
    
    @staticmethod
    def compare_with_ground_truth(pred_boxes, pred_classes, gt_boxes, gt_classes, 
                                 iou_threshold=0.5):
        """So sánh predictions với ground truth"""
        tp = 0  # True positives
        fp = 0  # False positives
        fn = 0  # False negatives
        
        matched_gt = []
        matched_pred = []
        class_comparison = []
        
        # Kiểm tra từng prediction
        for i, (pred_box, pred_class) in enumerate(zip(pred_boxes, pred_classes)):
            matched = False
            for j, (gt_box, gt_class) in enumerate(zip(gt_boxes, gt_classes)):
                if j in matched_gt:
                    continue
                    
                iou = GroundTruthProcessor.calculate_iou(pred_box, gt_box)
                if iou >= iou_threshold:
                    matched = True
                    matched_gt.append(j)
                    matched_pred.append(i)
                    
                    if pred_class == gt_class:
                        tp += 1
                        class_comparison.append({
                            'pred': pred_class, 
                            'gt': gt_class, 
                            'correct': True, 
                            'pred_idx': i, 
                            'gt_idx': j
                        })
                    else:
                        fp += 1
                        class_comparison.append({
                            'pred': pred_class, 
                            'gt': gt_class, 
                            'correct': False, 
                            'pred_idx': i, 
                            'gt_idx': j
                        })
                    break
            
            if not matched:
                fp += 1
                class_comparison.append({
                    'pred': pred_class, 
                    'gt': None, 
                    'correct': False, 
                    'pred_idx': i, 
                    'gt_idx': None
                })
        
        # Kiểm tra các ground truth box bị miss
        fn = len(gt_boxes) - len(matched_gt)
        
        # Tính các metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'class_comparison': class_comparison,
            'matched_pred': matched_pred,
            'matched_gt': matched_gt
        }