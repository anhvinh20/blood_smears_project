# utils/file_handler.py
import os
from werkzeug.utils import secure_filename
import cv2
class FileHandler:
    """Quản lý việc upload và lưu file"""
    
    def __init__(self, config):
        self.upload_folder = config['UPLOAD_FOLDER']
        self.results_folder = config['RESULTS_FOLDER']
    
    def get_uploaded_files(self, request):
        """Lấy các file được upload từ request"""
        # Kiểm tra file ảnh (hỗ trợ cả tên 'file' và 'image')
        image_file = None
        if 'file' in request.files:
            image_file = request.files['file']
        elif 'image' in request.files:
            image_file = request.files['image']
        
        # Kiểm tra file label
        label_file = None
        if 'label' in request.files:
            label_file = request.files['label']
            if label_file.filename == '':
                label_file = None
        
        return image_file, label_file
    
    def save_files(self, image_file, label_file=None):
        """Lưu các file đã upload"""
        # Lưu file ảnh
        if not image_file or image_file.filename == '':
            raise ValueError('Không có file ảnh được chọn')
        
        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(self.upload_folder, image_filename)
        image_file.save(image_path)
        
        # Lưu file label nếu có
        label_path = None
        if label_file and label_file.filename != '':
            label_filename = secure_filename(label_file.filename)
            label_path = os.path.join(self.upload_folder, label_filename)
            label_file.save(label_path)
        
        return image_path, label_path
    
    def save_result_image(self, img, original_filename):
        """Lưu ảnh kết quả"""
        result_filename = f"result_{original_filename}"
        result_path = os.path.join(self.results_folder, result_filename)
        cv2.imwrite(result_path, img)
        return result_path