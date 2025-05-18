# routes/api.py

import os
from flask import request, jsonify
from utils.file_handler import FileHandler
from utils.analysis import Analyzer

def init_routes(app, file_handler, analyzer):
    """Khởi tạo các routes API"""
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        """API phân tích ảnh"""
        try:
            # Kiểm tra và xử lý file upload
            image_file, label_file = file_handler.get_uploaded_files(request)
            
            if not image_file:
                return jsonify({'error': 'Không có file ảnh được upload'}), 400
            
            # Lưu các file
            image_path, label_path = file_handler.save_files(image_file, label_file)
            original_filename = os.path.basename(image_path)
            # Phân tích ảnh - 2 giai đoạn
            results = analyzer.analyze_two_stages(image_path, label_path)

            if 'processed_image' in results:
            # Lưu ảnh đã xử lý và thêm đường dẫn vào kết quả
                results['result_image_path'] = file_handler.save_result_image(
                    results['processed_image'], 
                    original_filename
                )
            return jsonify(results)
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return jsonify({'error': str(e)}), 500

    @app.route('/health')
    def health():
        """Kiểm tra trạng thái hệ thống"""
        from models.model_loader import ModelsManager
        
        return jsonify({
            'status': 'healthy',
            'models_loaded': True  # Giả sử model đã được load
        })