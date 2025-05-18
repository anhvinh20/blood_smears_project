# routes/views.py

from flask import render_template

def index():
    """Trang chủ"""
    return render_template('index.html')

def about():
    """Trang giới thiệu"""
    return render_template('about.html')

def detail_results():
    """Trang chi tiết kết quả"""
    return render_template('detail_results.html')