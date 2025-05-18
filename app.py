# app.py

from flask import Flask
from config import AppConfig
from models.model_loader import ModelsManager
from utils.image_processing import ImageProcessor
from utils.analysis import Analyzer
from utils.file_handler import FileHandler
from routes.views import index, about, detail_results
from routes.api import init_routes

# Khởi tạo Flask app
app = Flask(__name__)
app.config.from_object(AppConfig)

# Khởi tạo các manager
models_manager = ModelsManager()
image_processor = ImageProcessor()
analyzer = Analyzer(models_manager, image_processor)
file_handler = FileHandler(app.config)

# Load models khi khởi động
models_loaded = models_manager.load_models()

# Đăng ký các route view
app.route('/')(index)
app.route('/about')(about)
app.route('/detail-results')(detail_results)

# Khởi tạo các route API
init_routes(app, file_handler, analyzer)

if __name__ == '__main__':
    if models_loaded:
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Không thể load models. Vui lòng kiểm tra lại file model.")