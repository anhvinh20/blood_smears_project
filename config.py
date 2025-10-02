# config.py
import os

class AppConfig:
    """Cấu hình cho ứng dụng Flask"""
    
    # Thư mục upload và results
    UPLOAD_FOLDER = 'uploads'
    RESULTS_FOLDER = 'results'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # Đường dẫn models
    YOLO_MODEL_PATH = 'models_data/yolov11_best_final.pt'
    CONVNEXTTINY_MODEL_PATH = 'models_data/convnext_tiny_6class.pt'
    DATA_YAML_PATH = 'models_data/data.yaml'
    
    # Các class cho phân loại
    CONVNEXTTINY_CLASSES = ['Diff', 'G', 'Others', 'S', 'TA', 'TJ']
    
    # Mapping giữa CONVNEXTTINY và data.yaml
    CONVNEXTTINY_TO_YAML = {
        0: 6,  # Diff -> data.yaml index 6
        1: 3,  # G -> data.yaml index 3
        2: 5,  # Others -> data.yaml index 5
        3: 2,  # S -> data.yaml index 2
        4: 1,  # TA -> data.yaml index 1
        5: 0   # TJ -> data.yaml index 0
    }
    
    # Màu sắc cho từng loại tế bào
    CELL_COLORS = {
        'TJ': (128, 0, 128),      # Purple
        'TA': (255, 0, 255),      # Magenta
        'S': (0, 255, 255),       # Yellow
        'G': (0, 0, 255),         # Red
        'Healthy': (0, 255, 0),   # Green
        'Others': (255, 255, 0),  # Cyan
        'Diff': (255, 0, 0)       # Blue
    }
    
    @staticmethod
    def init_folders():
        """Tạo các thư mục cần thiết"""
        folders = [
            AppConfig.UPLOAD_FOLDER,
            AppConfig.RESULTS_FOLDER,
            'static/css',
            'templates'
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)

# Khởi tạo thư mục khi import
AppConfig.init_folders()