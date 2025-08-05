"""
设计功能模块 - Flask版本 (无Streamlit依赖)
包含所有T恤设计生成功能
"""

from PIL import Image, ImageDraw
import requests
from io import BytesIO
import os
import random
import time
import threading
import concurrent.futures
import re
import math
import json
import hashlib
from collections import Counter
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
    print("DashScope not installed, will use OpenAI DALL-E as fallback")

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

def get_ai_design_suggestions(user_prompt, max_retries=3):
    """Get AI design suggestions using GPT-4o-mini"""
    for attempt in range(max_retries):
        try:
            api_key = get_next_gpt4o_api_key()
            client = OpenAI(api_key=api_key, base_url=GPT4O_MINI_BASE_URL)
            
            system_prompt = """You are an expert T-shirt designer. Based on the user's prompt, provide design suggestions in JSON format with the following structure:

{
    "design_prompt": "A detailed, creative description for generating the T-shirt design",
    "color": {
        "name": "Color name",
        "hex": "#HEXCODE"
    },
    "fabric": "Cotton/Polyester/Blend",
    "placement": "center/left/right",
    "size": "small/medium/large",
    "style": "modern/vintage/minimalist/artistic"
}

Make sure the design_prompt is creative and detailed for best AI image generation results."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a T-shirt design for: {user_prompt}"}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            # 解析JSON响应
            try:
                suggestions = json.loads(response.choices[0].message.content)
                return suggestions
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试提取JSON部分
                content = response.choices[0].message.content
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group())
                    return suggestions
                else:
                    return {"error": "Failed to parse AI response"}
                    
        except Exception as e:
            print(f"GPT-4o-mini API attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                return {"error": f"Failed to get AI suggestions: {str(e)}"}
            time.sleep(1)
    
    return {"error": "Failed to get AI suggestions after all retries"}

def generate_design_image(prompt, variation_id=None, max_retries=3):
    """Generate design image using AI"""
    # 添加变体ID到提示词以确保不同的结果
    if variation_id is not None:
        enhanced_prompt = f"{prompt}, variation {variation_id}, unique design"
    else:
        enhanced_prompt = prompt
    
    # 首先尝试阿里云DashScope
    if DASHSCOPE_AVAILABLE:
        for attempt in range(max_retries):
            try:
                print(f"尝试使用阿里云DashScope生成图像 (attempt {attempt + 1})")
                
                # 设置API密钥
                os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY
                
                rsp = ImageSynthesis.call(
                    model=ImageSynthesis.Models.wanx_v1,
                    prompt=enhanced_prompt,
                    n=1,
                    size='1024*1024'
                )
                
                if rsp.status_code == HTTPStatus.OK:
                    # 获取图像URL
                    image_url = rsp.output.results[0].url
                    
                    # 下载图像
                    response = requests.get(image_url, timeout=30)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        print(f"✅ 阿里云DashScope图像生成成功")
                        return image
                    else:
                        print(f"❌ 下载阿里云图像失败: {response.status_code}")
                else:
                    print(f"❌ 阿里云DashScope调用失败: {rsp.message}")
                    
            except Exception as e:
                print(f"阿里云DashScope尝试 {attempt + 1} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
    
    # 如果阿里云失败，回退到OpenAI DALL-E
    print("回退到OpenAI DALL-E")
    for attempt in range(max_retries):
        try:
            api_key = get_next_api_key()
            client = OpenAI(api_key=api_key, base_url=BASE_URL)
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # 下载图像
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code == 200:
                image = Image.open(BytesIO(img_response.content))
                print(f"✅ OpenAI DALL-E图像生成成功")
                return image
            else:
                print(f"❌ 下载OpenAI图像失败: {img_response.status_code}")
                
        except Exception as e:
            print(f"OpenAI DALL-E尝试 {attempt + 1} 失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    print("❌ 所有图像生成方法都失败了")
    return None

def apply_logo_to_tshirt(base_image, logo_image, placement="center", size="medium"):
    """Apply logo to T-shirt at specified position and size"""
    if base_image is None or logo_image is None:
        return base_image
    
    result_image = base_image.copy()
    
    # 定义T恤胸部区域 (根据你的T恤图像调整这些数值)
    chest_left = 380    # 胸部区域左边界
    chest_right = 620   # 胸部区域右边界  
    chest_top = 320     # 胸部区域上边界
    chest_bottom = 560  # 胸部区域下边界
    
    chest_width = chest_right - chest_left
    chest_height = chest_bottom - chest_top
    
    # 根据size参数确定logo大小
    size_multipliers = {
        "small": 0.3,
        "medium": 0.5,
        "large": 0.7
    }
    
    size_multiplier = size_multipliers.get(size, 0.5)
    max_logo_width = int(chest_width * size_multiplier)
    max_logo_height = int(chest_height * size_multiplier)
    
    # 保持logo的宽高比
    logo_width, logo_height = logo_image.size
    aspect_ratio = logo_width / logo_height
    
    if logo_width > logo_height:
        # 横向logo
        new_logo_width = min(max_logo_width, logo_width)
        new_logo_height = int(new_logo_width / aspect_ratio)
        if new_logo_height > max_logo_height:
            new_logo_height = max_logo_height
            new_logo_width = int(new_logo_height * aspect_ratio)
    else:
        # 纵向logo
        new_logo_height = min(max_logo_height, logo_height)
        new_logo_width = int(new_logo_height * aspect_ratio)
        if new_logo_width > max_logo_width:
            new_logo_width = max_logo_width
            new_logo_height = int(new_logo_width / aspect_ratio)
    
    # 调整logo大小
    logo_resized = logo_image.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)
    
    # 根据placement参数确定logo位置
    if placement == "center":
        logo_x = chest_left + (chest_width - new_logo_width) // 2
        logo_y = chest_top + (chest_height - new_logo_height) // 2
    elif placement == "left":
        logo_x = chest_left + 20
        logo_y = chest_top + (chest_height - new_logo_height) // 2
    elif placement == "right":
        logo_x = chest_right - new_logo_width - 20
        logo_y = chest_top + (chest_height - new_logo_height) // 2
    else:
        # 默认居中
        logo_x = chest_left + (chest_width - new_logo_width) // 2
        logo_y = chest_top + (chest_height - new_logo_height) // 2 + 20
    
    print(f"应用logo到位置: ({logo_x}, {logo_y}), 大小: {new_logo_width}x{new_logo_height}")
    
    # 直接使用PIL的alpha合成功能
    result_image.paste(logo_resized, (logo_x, logo_y), logo_resized)
    
    return result_image

def generate_complete_design_flask(design_prompt, variation_id=None):
    """Generate complete T-shirt design based on prompt - Flask version"""
    if not design_prompt:
        return None, {"error": "Please enter a design prompt"}
    
    # 获取AI设计建议
    design_suggestions = get_ai_design_suggestions(design_prompt)
    
    if "error" in design_suggestions:
        return None, design_suggestions
    
    # 加载原始T恤图像
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
        
        if not found:
            return None, {"error": "Could not find base T-shirt image"}
        
        # 加载原始白色T恤图像
        original_image = Image.open(original_image_path).convert("RGBA")
    except Exception as e:
        return None, {"error": f"Error loading T-shirt image: {str(e)}"}
    
    try:
        # 使用AI建议的颜色和面料
        color_hex = design_suggestions.get("color", {}).get("hex", "#FFFFFF")
        color_name = design_suggestions.get("color", {}).get("name", "Custom Color")
        fabric_type = design_suggestions.get("fabric", "Cotton")
        
        # 应用颜色变化到T恤
        colored_tshirt = apply_color_to_tshirt(original_image, color_hex)
        
        # 应用面料纹理
        textured_tshirt = apply_fabric_texture(colored_tshirt, fabric_type)
        
        # 生成设计图像
        design_prompt_for_ai = design_suggestions.get("design_prompt", design_prompt)
        logo_image = generate_design_image(design_prompt_for_ai, variation_id)
        
        if logo_image is None:
            return None, {"error": "Failed to generate design image"}
        
        # 应用设计到T恤上
        placement = design_suggestions.get("placement", "center")
        size = design_suggestions.get("size", "medium")
        final_design = apply_logo_to_tshirt(textured_tshirt, logo_image, placement, size)
        
        # 返回设计信息
        design_info = {
            "design_index": variation_id if variation_id is not None else 0,
            "prompt": design_prompt,
            "ai_suggestions": design_suggestions,
            "color": color_name,
            "fabric": fabric_type,
            "placement": placement,
            "size": size
        }
        
        return final_design, design_info
        
    except Exception as e:
        return None, {"error": f"Error generating design: {str(e)}"}

def apply_color_to_tshirt(tshirt_image, color_hex):
    """Apply color to T-shirt while preserving shadows and highlights"""
    if not color_hex or color_hex == "#FFFFFF":
        return tshirt_image
    
    try:
        # 转换hex颜色到RGB
        color_hex = color_hex.lstrip('#')
        target_color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        
        # 创建一个副本进行处理
        result = tshirt_image.copy()
        pixels = result.load()
        
        width, height = result.size
        
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                
                # 只处理非透明像素
                if a > 0:
                    # 计算像素的亮度
                    brightness = (r + g + b) / 3.0 / 255.0
                    
                    # 如果是接近白色的像素（T恤主体），应用颜色
                    if brightness > 0.7:  # 白色区域
                        # 根据亮度调整目标颜色
                        new_r = int(target_color[0] * brightness)
                        new_g = int(target_color[1] * brightness)
                        new_b = int(target_color[2] * brightness)
                        
                        pixels[x, y] = (new_r, new_g, new_b, a)
        
        return result
        
    except Exception as e:
        print(f"Error applying color: {e}")
        return tshirt_image