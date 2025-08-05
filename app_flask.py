#!/usr/bin/env python3
"""
AI T-shirt Design Generator - Flask版本
脱离Streamlit的完整Web应用
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
import os
import uuid
import datetime
import json
import random
import time
import threading
import concurrent.futures
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import requests
import numpy as np

# 导入现有的功能模块（去除Streamlit依赖）
from design_functions_flask import *
from fabric_texture import apply_fabric_texture
from svg_utils import convert_svg_to_png

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
CORS(app)

# 全局配置
UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

# 生成随机数量的设计（1-10个）
def get_random_design_count():
    """随机生成1-10个设计数量"""
    return random.randint(1, 10)

@app.route('/')
def index():
    """主页"""
    # 初始化会话变量
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['start_time'] = datetime.datetime.now().isoformat()
        session['design_count'] = get_random_design_count()
        
        # 根据随机生成的设计数量设置推荐级别
        if session['design_count'] <= 2:
            session['recommendation_level'] = "low"
        elif session['design_count'] <= 5:
            session['recommendation_level'] = "medium"
        else:  # 6-10个设计
            session['recommendation_level'] = "high"
    
    return render_template('index.html', 
                         design_count=session.get('design_count', 5),
                         recommendation_level=session.get('recommendation_level', 'medium'))

@app.route('/api/generate_designs', methods=['POST'])
def generate_designs():
    """生成T恤设计API"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', '').strip()
        
        if not keywords:
            return jsonify({'error': '请输入至少一个关键词'}), 400
        
        # 获取设计数量
        design_count = session.get('design_count', 5)
        
        # 记录开始时间
        start_time = time.time()
        
        # 收集生成的设计
        designs = []
        
        # 生成单个设计的安全函数
        def generate_single_safely(design_index):
            try:
                return generate_complete_design_flask(keywords, design_index)
            except Exception as e:
                return None, {"error": f"Failed to generate design: {str(e)}"}
        
        # 对于单个设计，直接生成
        if design_count == 1:
            design, info = generate_single_safely(0)
            if design:
                # 保存设计图像
                design_filename = f"design_{session['user_id']}_{int(time.time())}_0.png"
                design_path = os.path.join(GENERATED_FOLDER, design_filename)
                design.save(design_path)
                designs.append({
                    'index': 0,
                    'filename': design_filename,
                    'info': info
                })
        else:
            # 为多个设计使用并行处理
            with concurrent.futures.ThreadPoolExecutor(max_workers=design_count) as executor:
                # 提交所有任务
                future_to_id = {executor.submit(generate_single_safely, i): i for i in range(design_count)}
                
                # 收集结果
                for future in concurrent.futures.as_completed(future_to_id):
                    design_id = future_to_id[future]
                    try:
                        design, info = future.result()
                        if design:
                            # 保存设计图像
                            design_filename = f"design_{session['user_id']}_{int(time.time())}_{design_id}.png"
                            design_path = os.path.join(GENERATED_FOLDER, design_filename)
                            design.save(design_path)
                            designs.append({
                                'index': design_id,
                                'filename': design_filename,
                                'info': info
                            })
                    except Exception as e:
                        print(f"Design {design_id} generation failed: {str(e)}")
        
        # 按照ID排序设计
        designs.sort(key=lambda x: x['index'])
        
        # 记录结束时间
        end_time = time.time()
        generation_time = end_time - start_time
        
        # 存储到会话
        session['generated_designs'] = designs
        session['user_prompt'] = keywords
        
        return jsonify({
            'success': True,
            'designs': designs,
            'generation_time': generation_time,
            'design_count': len(designs)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_design_image/<filename>')
def get_design_image(filename):
    """获取生成的设计图像"""
    try:
        file_path = os.path.join(GENERATED_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/png')
        else:
            return "File not found", 404
    except Exception as e:
        return str(e), 500

@app.route('/api/get_base_tshirt')
def get_base_tshirt():
    """获取基础T恤图像"""
    try:
        # 尝试多个可能的路径
        possible_paths = [
            "white_shirt.png",
            "./white_shirt.png",
            "../white_shirt.png",
            "images/white_shirt.png",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return send_file(path, mimetype='image/png')
        
        return "Base T-shirt image not found", 404
    except Exception as e:
        return str(e), 500

@app.route('/api/session_info')
def session_info():
    """获取会话信息"""
    return jsonify({
        'user_id': session.get('user_id'),
        'design_count': session.get('design_count'),
        'recommendation_level': session.get('recommendation_level'),
        'generated_designs_count': len(session.get('generated_designs', []))
    })

@app.route('/test')
def test_page():
    """测试页面"""
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return render_template('test.html', python_version=python_version)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 启动Flask AI T恤设计生成器...")
    print(f"📡 端口: {port}")
    print(f"🌐 地址: 0.0.0.0")
    print(f"🐛 调试模式: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)