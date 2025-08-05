# 导入所有必要的基础依赖
import streamlit as st

# Page configuration - 必须是第一个Streamlit命令
st.set_page_config(
    page_title="AI T-shirt Design Generator",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded"
)

import warnings
warnings.filterwarnings('ignore')

from PIL import Image, ImageDraw
import requests
from io import BytesIO
import base64
import numpy as np
import os
import pandas as pd
import uuid
import datetime
import json
import random
import time
import threading
import concurrent.futures
import re
import math
from collections import Counter

# Requires installation: pip install streamlit-image-coordinates
from streamlit_image_coordinates import streamlit_image_coordinates
from streamlit.components.v1 import html
from streamlit_drawable_canvas import st_canvas

# 导入OpenAI配置
from openai import OpenAI

# 导入面料纹理模块
from fabric_texture import apply_fabric_texture

# 导入SVG处理功能
from svg_utils import convert_svg_to_png

# 导入阿里云DashScope文生图API
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
try:
    from dashscope import ImageSynthesis
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    st.warning("DashScope not installed, will use OpenAI DALL-E as fallback")

# API配置信息 - 多个API密钥用于增强并发能力
API_KEYS = [
    "sk-lNVAREVHjj386FDCd9McOL7k66DZCUkTp6IbV0u9970qqdlg",
    "sk-y8x6LH0zdtyQncT0aYdUW7eJZ7v7cuKTp90L7TiK3rPu3fAg", 
    "sk-Kp59pIj8PfqzLzYaAABh2jKsQLB0cUKU3n8l7TIK3rpU61QG",
    "sk-KACPocnavR6poutXUaj7HxsqUrxvcV808S2bv0U9974Ec83g",
    "sk-YknuN0pb6fKBOP6xFOqAdeeqhoYkd1cEl9380vC5HHeC2B30"
]
BASE_URL = "https://api.deepbricks.ai/v1/"

# GPT-4o-mini API配置 - 同样使用多个密钥
GPT4O_MINI_API_KEYS = [
    "sk-lNVAREVHjj386FDCd9McOL7k66DZCUkTp6IbV0u9970qqdlg",
    "sk-y8x6LH0zdtyQncT0aYdUW7eJZ7v7cuKTp90L7TiK3rPu3fAg",
    "sk-Kp59pIj8PfqzLzYaAABh2jKsQLB0cUKU3n8l7TIK3rpU61QG", 
    "sk-KACPocnavR6poutXUaj7HxsqUrxvcV808S2bv0U9974Ec83g",
    "sk-YknuN0pb6fKBOP6xFOqAdeeqhoYkd1cEl9380vC5HHeC2B30"
]
GPT4O_MINI_BASE_URL = "https://api.deepbricks.ai/v1/"

# 阿里云DashScope API配置
DASHSCOPE_API_KEY = "sk-4f82c6e2097440f8adb2ef688c7c7551"

# API密钥轮询计数器
_api_key_counter = 0
_gpt4o_api_key_counter = 0
_api_lock = threading.Lock()

def get_next_api_key():
    """获取下一个DALL-E API密钥（轮询方式）"""
    global _api_key_counter
    with _api_lock:
        key = API_KEYS[_api_key_counter % len(API_KEYS)]
        _api_key_counter += 1
        return key

def get_next_gpt4o_api_key():
    """获取下一个GPT-4o-mini API密钥（轮询方式）"""
    global _gpt4o_api_key_counter
    with _api_lock:
        key = GPT4O_MINI_API_KEYS[_gpt4o_api_key_counter % len(GPT4O_MINI_API_KEYS)]
        _gpt4o_api_key_counter += 1
        return key

# Custom CSS styles
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .design-area {
        border: 2px dashed #f63366;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 20px;
    }
    .highlight-text {
        color: #f63366;
        font-weight: bold;
    }
    .purchase-intent {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .rating-container {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
    }
    .welcome-card {
        background-color: #f8f9fa;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    .group-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        border: 1px solid #e0e0e0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .group-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .design-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 10px;
        margin: 20px 0;
    }
    .design-item {
        border: 2px solid transparent;
        border-radius: 5px;
        transition: border-color 0.2s;
        cursor: pointer;
    }
    .design-item.selected {
        border-color: #f63366;
    }
    .movable-box {
        cursor: move;
    }
</style>
""", unsafe_allow_html=True)

# 生成随机数量的设计（1-10个）
def get_random_design_count():
    """随机生成1-10个设计数量"""
    return random.randint(1, 10)

# 每次会话开始时生成随机设计数量
if 'design_count' not in st.session_state:
    st.session_state.design_count = get_random_design_count()

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.datetime.now()
if 'base_image' not in st.session_state:
    st.session_state.base_image = None
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'current_box_position' not in st.session_state:
    st.session_state.current_box_position = None
if 'generated_design' not in st.session_state:
    st.session_state.generated_design = None
if 'final_design' not in st.session_state:
    st.session_state.final_design = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'selected_preset' not in st.session_state:
    st.session_state.selected_preset = None
if 'preset_design' not in st.session_state:
    st.session_state.preset_design = None
if 'drawn_design' not in st.session_state:
    st.session_state.drawn_design = None
if 'preset_position' not in st.session_state:
    st.session_state.preset_position = (0, 0)  # 默认居中，表示相对红框左上角的偏移
if 'preset_scale' not in st.session_state:
    st.session_state.preset_scale = 40  # 默认为40%
if 'design_mode' not in st.session_state:
    st.session_state.design_mode = "preset"  # 默认使用预设设计模式
if 'fabric_type' not in st.session_state:
    st.session_state.fabric_type = None  # 初始状态下没有特定面料类型
if 'apply_texture' not in st.session_state:
    st.session_state.apply_texture = False  # 初始状态下不应用纹理

# 导入所有功能函数
from design_functions import *

def main():
    st.title("👕 AI T-shirt Design Generator")
    st.markdown("### Generate Random T-shirt Designs")
    
    # 显示实验组信息
    st.info("AI will generate random T-shirt design options for you")
    
    # 初始化会话状态变量
    if 'user_prompt' not in st.session_state:
        st.session_state.user_prompt = ""
    if 'final_design' not in st.session_state:
        st.session_state.final_design = None
    if 'design_info' not in st.session_state:
        st.session_state.design_info = None
    if 'is_generating' not in st.session_state:
        st.session_state.is_generating = False
    if 'should_generate' not in st.session_state:
        st.session_state.should_generate = False
    if 'recommendation_level' not in st.session_state:
        # 根据随机生成的设计数量设置推荐级别
        if st.session_state.design_count <= 2:
            st.session_state.recommendation_level = "low"
        elif st.session_state.design_count <= 5:
            st.session_state.recommendation_level = "medium"
        else:  # 6-10个设计
            st.session_state.recommendation_level = "high"
    if 'generated_designs' not in st.session_state:
        st.session_state.generated_designs = []
    if 'selected_design_index' not in st.session_state:
        st.session_state.selected_design_index = 0
    if 'original_tshirt' not in st.session_state:
        # 加载原始白色T恤图像
        try:
            original_image_path = "white_shirt.png"
            possible_paths = [
                "white_shirt.png",
                "./white_shirt.png",
                "../white_shirt.png",
                "images/white_shirt.png",
            ]
            
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    original_image_path = path
                    found = True
                    break
            
            if found:
                st.session_state.original_tshirt = Image.open(original_image_path).convert("RGBA")
            else:
                st.error("Could not find base T-shirt image")
                st.session_state.original_tshirt = None
        except Exception as e:
            st.error(f"Error loading T-shirt image: {str(e)}")
            st.session_state.original_tshirt = None
    
    # 创建两列布局
    design_col, input_col = st.columns([3, 2])
    
    with design_col:
        # 创建占位区域用于T恤设计展示
        design_area = st.empty()
        
        # 在设计区域显示当前状态的T恤设计
        if st.session_state.final_design is not None:
            with design_area.container():
                st.markdown("### Your Custom T-shirt Design")
                st.image(st.session_state.final_design, use_container_width=True)
        elif len(st.session_state.generated_designs) > 0:
            with design_area.container():
                st.markdown("### Generated Design Options")
                
                # 创建多列来显示设计
                design_count = len(st.session_state.generated_designs)
                
                # 每行最多显示3个设计
                max_cols_per_row = 3
                
                # 始终创建固定数量的列以保持图标大小一致
                rows_needed = (design_count + max_cols_per_row - 1) // max_cols_per_row  # 向上取整
                
                for row in range(rows_needed):
                    # 计算当前行的设计索引范围
                    start_idx = row * max_cols_per_row
                    end_idx = min(start_idx + max_cols_per_row, design_count)
                    
                    # 始终创建3列以保持大小一致
                    row_cols = st.columns(max_cols_per_row)
                    
                    # 显示当前行的设计
                    for col_idx in range(max_cols_per_row):
                        design_idx = start_idx + col_idx
                        with row_cols[col_idx]:
                            if design_idx < design_count:
                                # 有设计要显示
                                design, _ = st.session_state.generated_designs[design_idx]
                                st.markdown(f"<p style='text-align:center;'>Design {design_idx+1}</p>", unsafe_allow_html=True)
                                st.image(design, use_container_width=True)
                            else:
                                # 空列，保持布局一致
                                st.empty()
        else:
            # 显示原始空白T恤
            with design_area.container():
                st.markdown("### T-shirt Design Preview")
                if st.session_state.original_tshirt is not None:
                    st.image(st.session_state.original_tshirt, use_container_width=True)
                else:
                    st.info("Could not load original T-shirt image, please refresh the page")
    
    with input_col:
        # 设计提示词和推荐级别选择区
        st.markdown("### Design Options")
        
        # 提示词输入区
        st.markdown("#### Describe your desired T-shirt design:")
        
        # 添加简短说明
        st.markdown("""
        <div style="margin-bottom: 15px; padding: 10px; background-color: #f0f2f6; border-radius: 5px;">
        <p style="margin: 0; font-size: 14px;">Enter keywords to describe your ideal T-shirt design. 
        Our AI will combine these features to create unique designs for you.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 初始化关键词状态
        if 'keywords' not in st.session_state:
            st.session_state.keywords = ""
        
        # 关键词输入框
        keywords = st.text_input("Enter keywords for your design", value=st.session_state.keywords, 
                              placeholder="please only input one word", key="input_keywords")
        
        # 随机生成设计按钮（集成了生成功能）
        generate_button = st.button("🎲 Randomize & Generate Designs", key="randomize_and_generate", use_container_width=True)
        
        # 创建进度和消息区域在输入框下方
        progress_area = st.empty()
        message_area = st.empty()
        
        # 随机生成设计按钮事件处理
        if generate_button:
            # 首先随机化设计数量
            st.session_state.design_count = get_random_design_count()
            
            # 保存用户输入的关键词
            st.session_state.keywords = keywords
            
            # 检查是否输入了关键词
            if not keywords:
                st.error("Please enter at least one keyword")
            else:
                # 直接使用用户输入的关键词作为提示词
                user_prompt = keywords
                
                # 保存用户输入
                st.session_state.user_prompt = user_prompt
                
                # 使用新随机生成的设计数量
                design_count = st.session_state.design_count
                
                # 清空之前的设计
                st.session_state.final_design = None
                st.session_state.generated_designs = []
                
                try:
                    # 显示生成进度
                    with design_area.container():
                        st.markdown("### Generating T-shirt Designs")
                        if st.session_state.original_tshirt is not None:
                            st.image(st.session_state.original_tshirt, use_container_width=True)
                    
                    # 创建进度条和状态消息在输入框下方
                    progress_bar = progress_area.progress(0)
                    message_area.info(f"AI is generating {design_count} unique designs for you. This may take about a minute. Please do not refresh the page or close the browser. Thank you for your patience! ♪(･ω･)ﾉ")
                    # 记录开始时间
                    start_time = time.time()
                    
                    # 收集生成的设计
                    designs = []
                    
                    # 生成单个设计的安全函数
                    def generate_single_safely(design_index):
                        try:
                            return generate_complete_design(user_prompt, design_index)
                        except Exception as e:
                            message_area.error(f"Error generating design: {str(e)}")
                            return None, {"error": f"Failed to generate design: {str(e)}"}
                    
                    # 对于单个设计，直接生成
                    if design_count == 1:
                        design, info = generate_single_safely(0)
                        if design:
                            designs.append((design, info))
                        progress_bar.progress(100)
                        message_area.success("Design generation complete!")
                    else:
                        # 为多个设计使用并行处理
                        completed_count = 0
                        
                        # 进度更新函数
                        def update_progress():
                            nonlocal completed_count
                            completed_count += 1
                            progress = int(100 * completed_count / design_count)
                            progress_bar.progress(progress)
                            message_area.info(f"Generated {completed_count}/{design_count} designs...")
                        
                        # 使用线程池并行生成多个设计
                        with concurrent.futures.ThreadPoolExecutor(max_workers=design_count) as executor:
                            # 提交所有任务
                            future_to_id = {executor.submit(generate_single_safely, i): i for i in range(design_count)}
                            
                            # 收集结果
                            for future in concurrent.futures.as_completed(future_to_id):
                                design_id = future_to_id[future]
                                try:
                                    design, info = future.result()
                                    if design:
                                        designs.append((design, info))
                                except Exception as e:
                                    message_area.error(f"Design {design_id} generation failed: {str(e)}")
                                
                                # 更新进度
                                update_progress()
                        
                        # 按照ID排序设计
                        designs.sort(key=lambda x: x[1].get("design_index", 0) if x[1] and "design_index" in x[1] else 0)
                    
                    # 记录结束时间
                    end_time = time.time()
                    generation_time = end_time - start_time
                    
                    # 存储生成的设计
                    if designs:
                        st.session_state.generated_designs = designs
                        st.session_state.selected_design_index = 0
                        message_area.success(f"Generated {len(designs)} designs in {generation_time:.1f} seconds!")
                    else:
                        message_area.error("Could not generate any designs. Please try again.")
                    
                    # 重新渲染设计区域以显示新生成的设计
                    st.rerun()
                except Exception as e:
                    import traceback
                    message_area.error(f"An error occurred: {str(e)}")
                    st.error(traceback.format_exc())

# Run application
if __name__ == "__main__":
    main() 