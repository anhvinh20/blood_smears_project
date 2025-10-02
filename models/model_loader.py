# models/model_loader.py
import torch
import torch.nn as nn
import yaml
from ultralytics import YOLO
from torchvision import models
from config import AppConfig

class ModelsManager:
    """Quản lý việc load và sử dụng các models"""
    
    def __init__(self):
        self.detection_model = None
        self.classification_model = None
        self.model_classes = None
        self.data_info = None
        self.device = None
        
    def load_models(self):
        """Load YOLO và ConvNext_Tiny models"""
        try:
            # Cấu hình device
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"Sử dụng device: {self.device}")
            
            # Load model phát hiện (YOLO)
            self.detection_model = YOLO(AppConfig.YOLO_MODEL_PATH)
            
            # Load model phân loại (CONVNEXTTINY)
            checkpoint = torch.load(AppConfig.CONVNEXTTINY_MODEL_PATH, 
                                  map_location=self.device)
            
            # Lấy thông tin class từ checkpoint
            self.model_classes = checkpoint.get('classes', AppConfig.CONVNEXTTINY_CLASSES)
            print(f"Model classes: {self.model_classes}")
            
            # Tạo CONVNEXTTINY model
            self.classification_model = models.convnext_tiny(pretrained=False)
            num_ftrs = self.classification_model.classifier[-1].in_features
            self.classification_model.classifier[-1] = nn.Linear(num_ftrs, len(self.model_classes))

            # Load trained weights
            self.classification_model.load_state_dict(checkpoint['model_state_dict'])
            self.classification_model.to(self.device)
            self.classification_model.eval()
            
            # Load thông tin data.yaml
            with open(AppConfig.DATA_YAML_PATH, 'r', encoding='utf-8') as f:
                self.data_info = yaml.safe_load(f)
            
            print("Đã load models thành công!")
            print(f"Data.yaml classes: {self.data_info['names']}")
            return True
            
        except Exception as e:
            print(f"Lỗi khi load models: {e}")
            return False
    
    def is_loaded(self):
        """Kiểm tra xem models đã được load chưa"""
        return (self.detection_model is not None and 
                self.classification_model is not None)
    
    def get_detection_model(self):
        """Lấy model phát hiện YOLO"""
        return self.detection_model
    
    def get_classification_model(self):
        """Lấy model phân loại CONVNEXTTINY"""
        return self.classification_model
    
    def get_device(self):
        """Lấy device đang sử dụng"""
        return self.device
    
    def get_data_info(self):
        """Lấy thông tin từ data.yaml"""
        return self.data_info