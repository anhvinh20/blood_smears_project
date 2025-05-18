# utils/analysis.py
import cv2
import numpy as np
from config import AppConfig
from utils.ground_truth import GroundTruthProcessor

class Analyzer:
    """Phân tích ảnh và tính toán kết quả"""
    
    def __init__(self, models_manager, image_processor):
        self.models_manager = models_manager
        self.image_processor = image_processor
        self.gt_processor = GroundTruthProcessor()
    
    def analyze_two_stages(self, image_path, label_path=None):
        """Phân tích 2 giai đoạn với hoặc không có ground truth"""
        # Đọc ảnh
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Không thể đọc ảnh từ {image_path}")
        
        img_height, img_width = img.shape[:2]
        
        # Lấy thông tin cần thiết
        data_info = self.models_manager.get_data_info()
        data_classes = data_info['names']
        detection_model = self.models_manager.get_detection_model()
        classification_model = self.models_manager.get_classification_model()
        device = self.models_manager.get_device()
        
        # GIAI ĐOẠN 1: Phát hiện và phân loại sơ bộ Healthy/Unhealthy
        stage1_results = self._stage1_detection(img, detection_model)
        
        # GIAI ĐOẠN 2: Phân loại chi tiết các tế bào Unhealthy
        stage2_results = self._stage2_classification(
            img, stage1_results, classification_model, device, data_classes
        )
        
        # Xử lý ground truth nếu có
        gt_results = None
        comparison_results = None
        
        if label_path:
            gt_results = self._process_ground_truth(
                label_path, img_width, img_height, data_classes
            )
            
            comparison_results = self._compare_with_ground_truth(
                stage2_results, gt_results, img, data_info
            )
        
        # Chuẩn bị response
        response = self._prepare_response(
            stage1_results, stage2_results, gt_results, comparison_results, img
        )
        
        return response
    
    def _stage1_detection(self, img, detection_model):
        """Giai đoạn 1: Phát hiện Healthy và Unhealthy"""
        results = detection_model(img, conf=0.25)
        
        boxes = []
        stage1_classes = []  # 0: Healthy, 1: Unhealthy
        yolo_classes = []
        
        for box in results[0].boxes:
            box_xyxy = box.xyxy[0].cpu().numpy().astype(int).tolist()
            yolo_cls = int(box.cls[0].cpu().numpy())
            
            boxes.append(box_xyxy)
            yolo_classes.append(yolo_cls)
            
            # YOLO model: 0=Healthy, 1=Unhealthy
            stage1_classes.append(yolo_cls)
        
        # Đếm số lượng
        num_healthy = stage1_classes.count(0)
        num_unhealthy = stage1_classes.count(1)
        
        # Vẽ kết quả giai đoạn 1
        stage1_img = self.image_processor.draw_stage1_results(
            img, boxes, stage1_classes, num_healthy, num_unhealthy
        )
        
        return {
            'boxes': boxes,
            'stage1_classes': stage1_classes,
            'yolo_classes': yolo_classes,
            'num_healthy': num_healthy,
            'num_unhealthy': num_unhealthy,
            'image': stage1_img
        }
    
    def _stage2_classification(self, img, stage1_results, classification_model, 
                              device, data_classes):
        """Giai đoạn 2: Phân loại chi tiết"""
        boxes = stage1_results['boxes']
        stage1_classes = stage1_results['stage1_classes']
        
        cell_counts = {}
        pred_classes = []
        
        for box, stage1_cls in zip(boxes, stage1_classes):
            if stage1_cls == 0:  # Healthy
                class_name = "Healthy"
                pred_classes.append(4)  # Map to index 4
                cell_counts[class_name] = cell_counts.get(class_name, 0) + 1
            else:  # Unhealthy - cần phân loại chi tiết
                # Crop và phân loại
                x1, y1, x2, y2 = box
                crop = img[y1:y2, x1:x2]
                
                if crop.size == 0:
                    continue
                
                # Phân loại bằng EfficientNet
                pred_idx = self.image_processor.classify_cell(
                    crop, classification_model, device
                )
                
                # Map từ EfficientNet prediction sang data.yaml class
                if pred_idx in AppConfig.EFFICIENTNET_TO_YAML:
                    yaml_idx = AppConfig.EFFICIENTNET_TO_YAML[pred_idx]
                    class_name = data_classes[yaml_idx]
                    pred_classes.append(yaml_idx)
                else:
                    # Fallback
                    class_name = data_classes.get(stage1_cls, f"Class-{stage1_cls}")
                    pred_classes.append(stage1_cls)
                
                cell_counts[class_name] = cell_counts.get(class_name, 0) + 1
        
        # Vẽ kết quả giai đoạn 2
        stage2_img = self.image_processor.draw_detection_results(
            img, boxes, pred_classes, data_classes, AppConfig.CELL_COLORS
        )
        
        return {
            'boxes': boxes,
            'classes': pred_classes,
            'cell_counts': cell_counts,
            'total_cells': sum(cell_counts.values()),
            'image': stage2_img
        }
    
    def _process_ground_truth(self, label_path, img_width, img_height, data_classes):
        """Xử lý ground truth"""
        gt_boxes, gt_classes = self.gt_processor.parse_yolo_label(
            label_path, img_width, img_height
        )
        
        # Đếm các class trong GT
        gt_counts = {}
        for cls in gt_classes:
            class_name = data_classes[cls] if cls < len(data_classes) else f"Class-{cls}"
            gt_counts[class_name] = gt_counts.get(class_name, 0) + 1
        
        return {
            'boxes': gt_boxes,
            'classes': gt_classes,
            'counts': gt_counts,
            'total': len(gt_boxes)
        }
    
    def _compare_with_ground_truth(self, stage2_results, gt_results, img, data_info):
        """So sánh với ground truth"""
        comparison = self.gt_processor.compare_with_ground_truth(
            stage2_results['boxes'], stage2_results['classes'],
            gt_results['boxes'], gt_results['classes']
        )
        
        # Tạo ảnh FP/FN
        fp_img, fn_img, fp_count, fn_count = self.image_processor.create_fp_fn_images(
            img, 
            stage2_results['boxes'], stage2_results['classes'],
            gt_results['boxes'], gt_results['classes'],
            comparison, data_info
        )
        
        return {
            'metrics': comparison,
            'fp_image': fp_img,
            'fn_image': fn_img,
            'fp_count': fp_count,
            'fn_count': fn_count
        }
    
    def _prepare_response(self, stage1_results, stage2_results, 
                         gt_results=None, comparison_results=None, original_img=None):
        """Chuẩn bị response cho client"""
        response = {
            'success': True,
            # Giai đoạn 1
            'stage1': {
                'num_healthy': stage1_results['num_healthy'],
                'num_unhealthy': stage1_results['num_unhealthy'],
                'total': stage1_results['num_healthy'] + stage1_results['num_unhealthy'],
                'image': self.image_processor.image_to_base64(stage1_results['image'])
            },
            # Giai đoạn 2
            'stage2': {
                'cell_counts': stage2_results['cell_counts'],
                'total_cells': stage2_results['total_cells'],
                'image': self.image_processor.image_to_base64(stage2_results['image'])
            }
        }
        
        # Thêm ground truth nếu có
        if gt_results:
            # Vẽ GT image
            gt_img = self.image_processor.draw_detection_results(
                original_img, gt_results['boxes'], gt_results['classes'],
                self.models_manager.get_data_info()['names'],
                AppConfig.CELL_COLORS
            )
            
            response['ground_truth'] = {
                'counts': gt_results['counts'],
                'total': gt_results['total'],
                'image': self.image_processor.image_to_base64(gt_img)
            }
            
            # Thêm comparison nếu có
            if comparison_results:
                response['comparison'] = comparison_results['metrics']
                response['fp_image'] = self.image_processor.image_to_base64(
                    comparison_results['fp_image']
                )
                response['fn_image'] = self.image_processor.image_to_base64(
                    comparison_results['fn_image']
                )
                response['fp_count'] = comparison_results['fp_count']
                response['fn_count'] = comparison_results['fn_count']
                
                # Chuẩn bị chart data
                all_classes = set(list(stage2_results['cell_counts'].keys()) + 
                                list(gt_results['counts'].keys()))
                chart_data = {
                    'labels': sorted(list(all_classes)),
                    'detection': [],
                    'groundTruth': []
                }
                
                for label in chart_data['labels']:
                    chart_data['detection'].append(
                        stage2_results['cell_counts'].get(label, 0)
                    )
                    chart_data['groundTruth'].append(
                        gt_results['counts'].get(label, 0)
                    )
                
                response['chart_data'] = chart_data
        
        return response