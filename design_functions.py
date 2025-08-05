import streamlit as st
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

def create_simple_geometric_logo(design_prompt, size=(200, 200)):
    """
    创建一个简单的几何图形logo作为备选方案
    创建具有清晰轮廓和透明背景的图案
    """
    try:
        # 创建一个透明背景的图像
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 根据设计提示词选择不同的几何图形和颜色
        shapes = ['heart', 'diamond', 'hexagon']  # 改为更具识别度的形状
        # 使用对比度高的颜色，确保在各种背景下都清晰可见
        colors = ['#000000', '#FFFFFF', '#FF0000', '#0000FF', '#00AA00']  # 高对比度颜色
        
        # 使用设计提示词的hash来确定形状和颜色（保持一致性）
        hash_obj = hashlib.md5(design_prompt.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        shape = shapes[hash_int % len(shapes)]
        color = colors[hash_int % len(colors)]
        
        # 计算图形位置和大小
        center_x, center_y = size[0] // 2, size[1] // 2
        radius = min(size) // 4  # 稍微小一点
        
        # 使用对比色的轮廓
        outline_color = '#FFFFFF' if color == '#000000' else '#000000'
        
        if shape == 'heart':
            # 绘制心形图案
            heart_points = []
            for t in range(0, 360, 10):  # 每10度一个点
                rad = math.radians(t)
                # 心形参数方程
                x = radius * (16 * math.sin(rad)**3) / 16
                y = -radius * (13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad)) / 16
                heart_points.append((center_x + x, center_y + y))
            if len(heart_points) > 2:
                draw.polygon(heart_points, fill=color, outline=outline_color, width=3)
        elif shape == 'diamond':
            # 绘制菱形
            points = [
                (center_x, center_y - radius),          # 上
                (center_x + radius, center_y),          # 右
                (center_x, center_y + radius),          # 下
                (center_x - radius, center_y)           # 左
            ]
            draw.polygon(points, fill=color, outline=outline_color, width=3)
        elif shape == 'hexagon':
            # 绘制六边形
            hex_points = []
            for i in range(6):
                angle = math.pi * i / 3  # 每60度一个点
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                hex_points.append((x, y))
            draw.polygon(hex_points, fill=color, outline=outline_color, width=3)
        
        print(f"生成了几何图形logo: {shape}, 颜色: {color}")
        return img
        
    except Exception as e:
        print(f"生成几何图形logo失败: {e}")
        return None

def make_background_transparent(image, threshold=100):
    """
    将图像的白色/浅色背景转换为透明背景
    
    Args:
        image: PIL图像对象，RGBA模式
        threshold: 背景色识别阈值，数值越大识别的背景范围越大
    
    Returns:
        处理后的PIL图像对象，透明背景
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # 获取图像数据
    data = image.getdata()
    new_data = []
    
    # 分析边缘像素来确定背景色（更可靠的方法）
    width, height = image.size
    edge_pixels = []
    
    # 采样边缘像素
    for x in range(width):
        edge_pixels.append(image.getpixel((x, 0)))         # 上边
        edge_pixels.append(image.getpixel((x, height-1)))  # 下边
    for y in range(height):
        edge_pixels.append(image.getpixel((0, y)))         # 左边
        edge_pixels.append(image.getpixel((width-1, y)))   # 右边
    
    # 找出最常见的边缘颜色作为背景色
    color_counts = Counter()
    for pixel in edge_pixels:
        if len(pixel) >= 3:
            # 将相似的颜色归为一组（容差为20）
            rounded_color = (pixel[0]//20*20, pixel[1]//20*20, pixel[2]//20*20)
            color_counts[rounded_color] += 1
    
    if color_counts:
        bg_color = color_counts.most_common(1)[0][0]
        bg_r, bg_g, bg_b = bg_color
    else:
        # 备选方案：使用四个角的平均色
        corner_pixels = [
            image.getpixel((0, 0)),           # 左上角
            image.getpixel((width-1, 0)),     # 右上角
            image.getpixel((0, height-1)),    # 左下角
            image.getpixel((width-1, height-1)) # 右下角
        ]
        bg_r = sum(p[0] for p in corner_pixels) // 4
        bg_g = sum(p[1] for p in corner_pixels) // 4
        bg_b = sum(p[2] for p in corner_pixels) // 4
    
    print(f"检测到的背景颜色: RGB({bg_r}, {bg_g}, {bg_b})")
    
    # 遍历所有像素
    transparent_count = 0
    for item in data:
        r, g, b, a = item
        
        # 计算当前像素与背景色的差异
        diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
        
        # 另外检查是否是浅色（可能是背景）
        brightness = (r + g + b) / 3
        is_very_light = brightness > 220  # 很亮的像素
        is_light = brightness > 180  # 亮的像素
        
        # 检查是否接近灰白色
        gray_similarity = abs(r - g) + abs(g - b) + abs(r - b)
        is_grayish = gray_similarity < 30  # 颜色差异小说明是灰色系
        
        # 更精确的透明化条件
        should_transparent = False
        
        # 主要判断：与检测到的背景色的相似度
        if diff < threshold:
            should_transparent = True
        # 次要判断：非常亮的像素且是灰白色系
        elif brightness > 230 and is_grayish:
            should_transparent = True
        # 最严格判断：几乎是纯白色的像素
        elif brightness > 245 and r > 240 and g > 240 and b > 240:
            should_transparent = True
        
        if should_transparent:
            # 设置为完全透明
            new_data.append((r, g, b, 0))
            transparent_count += 1
        else:
            # 保持原像素，确保不透明
            new_data.append((r, g, b, 255))
    
    print(f"透明化了 {transparent_count} 个像素，占总像素的 {transparent_count/(image.size[0]*image.size[1])*100:.1f}%")
    
    # 创建新图像
    transparent_image = Image.new('RGBA', image.size)
    transparent_image.putdata(new_data)
    
    return transparent_image

def get_ai_design_suggestions(user_preferences=None):
    """Get design suggestions from GPT-4o-mini with more personalized features"""
    client = OpenAI(api_key=get_next_gpt4o_api_key(), base_url=GPT4O_MINI_BASE_URL)
    
    # Default prompt if no user preferences provided
    if not user_preferences:
        user_preferences = "casual fashion t-shirt design"
    
    # Construct the prompt
    prompt = f"""
    As a design consultant, please provide personalized design suggestions for a "{user_preferences}" style.
    
    Please provide the following design suggestions in JSON format:

    1. Color: Select the most suitable color for this style (provide name and hex code)
    2. Fabric: Select the most suitable fabric type (Cotton, Polyester, Cotton-Polyester Blend, Jersey, Linen, or Bamboo)
    3. Text: A suitable phrase or slogan that matches the style (keep it concise and impactful)
    4. Logo: A brief description of a logo element that would complement the design

    Return your response as a valid JSON object with the following structure:
    {{
        "color": {{
            "name": "Color name",
            "hex": "#XXXXXX"
        }},
        "fabric": "Fabric type",
        "text": "Suggested text or slogan",
        "logo": "Logo/graphic description"
    }}
    """
    
    try:
        # 调用GPT-4o-mini
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional design consultant. Provide design suggestions in JSON format exactly as requested."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回建议内容
        if response.choices and len(response.choices) > 0:
            suggestion_text = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                # 查找JSON格式的内容
                json_match = re.search(r'```json\s*(.*?)\s*```', suggestion_text, re.DOTALL)
                if json_match:
                    suggestion_json = json.loads(json_match.group(1))
                else:
                    # 尝试直接解析整个内容
                    suggestion_json = json.loads(suggestion_text)
                
                return suggestion_json
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                return {"error": f"Failed to parse design suggestions: {str(e)}"}
        else:
            return {"error": "Failed to get AI design suggestions. Please try again later."}
    except Exception as e:
        return {"error": f"Error getting AI design suggestions: {str(e)}"}

def generate_vector_image(prompt, background_color=None):
    """Generate a vector-style logo with transparent background using DashScope as primary service"""
    
    # 构建矢量图logo专用的提示词
    vector_style_prompt = f"""创建一个矢量风格的logo设计: {prompt}
    要求:
    1. 简洁的矢量图风格，线条清晰
    2. 必须是透明背景，不能有任何白色或彩色背景
    3. 专业的logo设计，适合印刷到T恤上
    4. 高对比度，颜色鲜明
    5. 几何形状简洁，不要过于复杂
    6. 不要包含文字或字母
    7. 不要显示T恤或服装模型
    8. 纯粹的图形标志设计
    9. 矢量插画风格，扁平化设计
    10. 重要：背景必须完全透明，不能有任何颜色填充
    11. 请生成PNG格式的透明背景图标
    12. 图标应该是独立的，没有任何背景元素"""
    
    # 主要方案: 使用DashScope API
    if DASHSCOPE_AVAILABLE:
        try:
            print(f'----使用DashScope生成矢量logo，提示词: {vector_style_prompt}----')
            
            # 方法1: 尝试使用DashScope SDK
            try:
                rsp = ImageSynthesis.call(
                    api_key=DASHSCOPE_API_KEY,
                    model="wanx2.0-t2i-turbo",
                    prompt=vector_style_prompt,
                    n=1,
                    size='1024*1024'
                )
                print('DashScope SDK响应: %s' % rsp)
                
                if rsp.status_code == HTTPStatus.OK:
                    # 下载生成的图像
                    for result in rsp.output.results:
                        image_resp = requests.get(result.url, timeout=30)
                        if image_resp.status_code == 200:
                            # 加载图像并转换为RGBA模式
                            img = Image.open(BytesIO(image_resp.content)).convert("RGBA")
                            print(f"DashScope SDK生成的logo尺寸: {img.size}")
                            
                            # 后处理：将白色背景转换为透明
                            img_processed = make_background_transparent(img, threshold=120)
                            print(f"背景透明化处理完成")
                            return img_processed
                        else:
                            print(f"DashScope SDK图像下载失败, 状态码: {image_resp.status_code}")
                else:
                    print('DashScope SDK调用失败, status_code: %s, code: %s, message: %s' %
                          (rsp.status_code, rsp.code, rsp.message))
                    
            except Exception as e:
                print(f"DashScope SDK调用失败: {e}")
            
            # 方法2: 使用requests直接调用DashScope API（备选方案）
            try:
                print(f'----尝试使用requests直接调用DashScope API----')
                
                # 设置更长的超时时间和重试机制
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                headers = {
                    'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': 'wanx2.0-t2i-turbo',
                    'input': {
                        'prompt': vector_style_prompt
                    },
                    'parameters': {
                        'size': '1024*1024',
                        'n': 1
                    }
                }
                
                # 使用更长的超时时间，禁用SSL验证
                response = requests.post(
                    'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis',
                    headers=headers,
                    json=data,
                    timeout=60,
                    verify=False  # 禁用SSL验证以解决连接问题
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'output' in result and 'results' in result['output']:
                        image_url = result['output']['results'][0]['url']
                        print(f"DashScope API生成成功，下载图像: {image_url}")
                        
                        # 下载图像
                        image_resp = requests.get(image_url, timeout=30)
                        if image_resp.status_code == 200:
                            img = Image.open(BytesIO(image_resp.content)).convert("RGBA")
                            print(f"DashScope API生成的logo尺寸: {img.size}")
                            
                            # 后处理：将白色背景转换为透明
                            img_processed = make_background_transparent(img, threshold=120)
                            print(f"背景透明化处理完成")
                            return img_processed
                        else:
                            print(f"DashScope API图像下载失败, 状态码: {image_resp.status_code}")
                    else:
                        print(f"DashScope API返回异常: {result}")
                else:
                    print(f'DashScope API调用失败, status_code: {response.status_code}, response: {response.text}')
                    
            except Exception as e:
                print(f"DashScope API调用错误: {e}")
                
        except Exception as e:
            print(f"DashScope所有方法都失败: {e}")
    
    # 备选方案: 使用OpenAI DALL-E
    try:
        print(f'----DashScope失败，尝试使用OpenAI DALL-E生成矢量logo----')
        client = OpenAI(api_key=get_next_api_key(), base_url=BASE_URL)
        
        dall_e_prompt = f"""Create a professional vector logo design: {prompt}
        Requirements: 
        1. Simple professional design
        2. IMPORTANT: Transparent background (PNG format)
        3. Clear and distinct graphic with high contrast
        4. Vector-style illustration suitable for T-shirt printing
        5. Must not include any text, numbers or color name, only logo graphic
        6. IMPORTANT: Do NOT include any mockups or product previews
        7. IMPORTANT: Create ONLY the logo graphic itself
        8. NO META REFERENCES - do not show the logo applied to anything
        9. Design should be a standalone graphic symbol/icon only
        10. CRITICAL: Clean vector art style with crisp lines and solid colors"""
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=dall_e_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        if response.data and len(response.data) > 0:
            image_url = response.data[0].url
            print(f"OpenAI DALL-E生成成功，下载图像: {image_url}")
            
            # 下载图像
            image_resp = requests.get(image_url, timeout=30)
            if image_resp.status_code == 200:
                # 加载图像并转换为RGBA模式
                img = Image.open(BytesIO(image_resp.content)).convert("RGBA")
                print(f"OpenAI DALL-E生成的logo尺寸: {img.size}")
                
                # 后处理：将白色背景转换为透明
                img_processed = make_background_transparent(img, threshold=120)
                print(f"背景透明化处理完成")
                return img_processed
            else:
                print(f"OpenAI DALL-E图像下载失败, 状态码: {image_resp.status_code}")
        else:
            print("OpenAI DALL-E生成失败，没有返回图像")
            
    except Exception as e:
        print(f"OpenAI DALL-E调用错误: {e}")
    
    # 如果所有AI服务都失败，返回None让调用方处理备选方案
    print("所有AI图像生成服务都失败，将使用程序生成的几何图形")
    return None

def change_shirt_color(image, color_hex, apply_texture=False, fabric_type=None):
    """Change T-shirt color with optional fabric texture"""
    # 转换十六进制颜色为RGB
    color_rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # 创建副本避免修改原图
    colored_image = image.copy().convert("RGBA")
    
    # 获取图像数据
    data = colored_image.getdata()
    
    # 创建新数据
    new_data = []
    # 白色阈值 - 调整这个值可以控制哪些像素被视为白色/浅色并被改变
    threshold = 200
    
    for item in data:
        # 判断是否是白色/浅色区域 (RGB值都很高)
        if item[0] > threshold and item[1] > threshold and item[2] > threshold and item[3] > 0:
            # 保持原透明度，改变颜色
            new_color = (color_rgb[0], color_rgb[1], color_rgb[2], item[3])
            new_data.append(new_color)
        else:
            # 保持其他颜色不变
            new_data.append(item)
    
    # 更新图像数据
    colored_image.putdata(new_data)
    
    # 如果需要应用纹理
    if apply_texture and fabric_type:
        return apply_fabric_texture(colored_image, fabric_type)
    
    return colored_image

def apply_text_to_shirt(image, text, color_hex="#FFFFFF", font_size=80):
    """Apply text to T-shirt image"""
    if not text:
        return image
    
    # 创建副本避免修改原图
    result_image = image.copy().convert("RGBA")
    img_width, img_height = result_image.size
    
    # 创建透明的文本图层
    text_layer = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    
    # 尝试加载字体
    from PIL import ImageFont
    import platform
    
    font = None
    try:
        system = platform.system()
        
        # 根据不同系统尝试不同的字体路径
        if system == 'Windows':
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/ARIAL.TTF",
                "C:/Windows/Fonts/calibri.ttf",
            ]
        elif system == 'Darwin':  # macOS
            font_paths = [
                "/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]
        else:  # Linux或其他
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            ]
        
        # 尝试加载每个字体
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
    except Exception as e:
        print(f"Error loading font: {e}")
    
    # 如果加载失败，使用默认字体
    if font is None:
        try:
            font = ImageFont.load_default()
        except:
            print("Could not load default font")
            return result_image
    
    # 将十六进制颜色转换为RGB
    color_rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    text_color = color_rgb + (255,)  # 添加不透明度
    
    # 计算文本位置 (居中)
    text_bbox = text_draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (img_width - text_width) // 2
    text_y = (img_height // 3) - (text_height // 2)  # 放在T恤上部位置
    
    # 绘制文本
    text_draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    # 组合图像
    result_image = Image.alpha_composite(result_image, text_layer)
    
    return result_image

def apply_logo_to_shirt(shirt_image, logo_image, position="center", size_percent=60, background_color=None):
    """Apply logo to T-shirt image with better blending to reduce shadows"""
    if logo_image is None:
        return shirt_image
    
    # 创建副本避免修改原图
    result_image = shirt_image.copy().convert("RGBA")
    img_width, img_height = result_image.size
    
    # 定义T恤前胸区域
    chest_width = int(img_width * 0.95)
    chest_height = int(img_height * 0.6)
    chest_left = (img_width - chest_width) // 2
    chest_top = int(img_height * 0.2)
    
    # 提取logo前景
    logo_with_bg = logo_image.copy().convert("RGBA")
    
    # 调整Logo大小
    logo_size_factor = size_percent / 100
    logo_width = int(chest_width * logo_size_factor * 0.5)  # 稍微小一点
    logo_height = int(logo_width * logo_with_bg.height / logo_with_bg.width)
    logo_resized = logo_with_bg.resize((logo_width, logo_height), Image.LANCZOS)
    
    # 根据位置确定坐标
    position = position.lower() if isinstance(position, str) else "center"
    
    if position == "top-center":
        logo_x, logo_y = chest_left + (chest_width - logo_width) // 2, chest_top + 10
    elif position == "center":
        logo_x, logo_y = chest_left + (chest_width - logo_width) // 2, chest_top + (chest_height - logo_height) // 2 + 30  # 略微偏下
    else:  # 默认中间
        logo_x, logo_y = chest_left + (chest_width - logo_width) // 2, chest_top + (chest_height - logo_height) // 2 + 30
    
    # 对于透明背景的logo，直接使用alpha通道作为蒙版
    if logo_resized.mode == 'RGBA':
        # 使用alpha通道作为蒙版
        logo_mask = logo_resized.split()[-1]  # 获取alpha通道
        print(f"使用RGBA模式logo的alpha通道作为蒙版")
    else:
        # 如果不是RGBA模式，创建传统的基于颜色差异的蒙版
        logo_mask = Image.new("L", logo_resized.size, 0)  # 创建一个黑色蒙版（透明）
        
        # 如果提供了背景颜色，使用它来判断什么是背景
        if background_color:
            bg_color_rgb = tuple(int(background_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        else:
            # 默认假设白色是背景
            bg_color_rgb = (255, 255, 255)
        
        # 遍历像素，创建蒙版
        for y in range(logo_resized.height):
            for x in range(logo_resized.width):
                pixel = logo_resized.getpixel((x, y))
                if len(pixel) >= 3:  # 至少有RGB值
                    # 计算与背景颜色的差异
                    r_diff = abs(pixel[0] - bg_color_rgb[0])
                    g_diff = abs(pixel[1] - bg_color_rgb[1])
                    b_diff = abs(pixel[2] - bg_color_rgb[2])
                    diff = r_diff + g_diff + b_diff
                    
                    # 如果差异大于阈值，则认为是前景
                    if diff > 60:  # 可以调整阈值
                        # 根据差异程度设置不同的透明度
                        transparency = min(255, diff)
                        logo_mask.putpixel((x, y), transparency)
    
    # 对于透明背景的logo，使用PIL的alpha合成功能
    if logo_resized.mode == 'RGBA':
        # 检查logo是否真的有透明像素
        has_transparency = False
        fully_transparent_pixels = 0
        total_pixels = logo_resized.width * logo_resized.height
        
        for pixel in logo_resized.getdata():
            if len(pixel) == 4:
                if pixel[3] < 255:  # 有alpha通道且不完全不透明
                    has_transparency = True
                if pixel[3] == 0:  # 完全透明
                    fully_transparent_pixels += 1
        
        transparency_ratio = fully_transparent_pixels / total_pixels
        print(f"Logo模式: {logo_resized.mode}, 有透明像素: {has_transparency}, 透明度比例: {transparency_ratio:.2f}")
        
        if has_transparency and transparency_ratio > 0.05:  # 降低透明度要求到5%
            # 直接使用PIL的alpha合成，这样处理透明背景更准确
            print(f"将透明背景logo应用到T恤位置: ({logo_x}, {logo_y})")
            result_image.paste(logo_resized, (logo_x, logo_y), logo_resized)
        else:
            # 如果没有足够的透明像素，先处理背景透明化
            print("Logo透明度不足，进行背景透明化处理")
            transparent_logo = make_background_transparent(logo_resized, threshold=60)  # 降低阈值，更宽松
            result_image.paste(transparent_logo, (logo_x, logo_y), transparent_logo)
    else:
        # 对于非透明背景的logo，使用传统的像素级混合方法
        shirt_region = result_image.crop((logo_x, logo_y, logo_x + logo_width, logo_y + logo_height))
        
        # 合成logo和T恤区域，使用蒙版确保只有logo的非背景部分被使用
        for y in range(logo_height):
            for x in range(logo_width):
                mask_value = logo_mask.getpixel((x, y))
                if mask_value > 20:  # 有一定的不透明度
                    # 获取logo像素
                    logo_pixel = logo_resized.getpixel((x, y))
                    # 获取T恤对应位置的像素
                    shirt_pixel = shirt_region.getpixel((x, y))
                    
                    # 根据透明度混合像素
                    alpha = mask_value / 255.0
                    blended_pixel = (
                        int(logo_pixel[0] * alpha + shirt_pixel[0] * (1 - alpha)),
                        int(logo_pixel[1] * alpha + shirt_pixel[1] * (1 - alpha)),
                        int(logo_pixel[2] * alpha + shirt_pixel[2] * (1 - alpha)),
                        255  # 完全不透明
                    )
                    
                    # 更新T恤区域的像素
                    shirt_region.putpixel((x, y), blended_pixel)
        
        # 将修改后的区域粘贴回T恤
        result_image.paste(shirt_region, (logo_x, logo_y))
    
    return result_image

def apply_geometric_logo_to_shirt(shirt_image, logo_image, position="center", size_percent=60):
    """专门用于应用程序生成的几何图形logo到T恤"""
    if logo_image is None:
        return shirt_image
    
    # 创建副本避免修改原图
    result_image = shirt_image.copy().convert("RGBA")
    img_width, img_height = result_image.size
    
    # 定义T恤前胸区域
    chest_width = int(img_width * 0.95)
    chest_height = int(img_height * 0.6)
    chest_left = (img_width - chest_width) // 2
    chest_top = int(img_height * 0.2)
    
    # 确保logo是RGBA模式
    logo_rgba = logo_image.convert("RGBA")
    
    # 调整Logo大小（几何图形相对小一些）
    logo_size_factor = size_percent / 100
    logo_width = int(chest_width * logo_size_factor * 0.4)  # 几何图形稍小
    logo_height = int(logo_width * logo_rgba.height / logo_rgba.width)
    logo_resized = logo_rgba.resize((logo_width, logo_height), Image.LANCZOS)
    
    # 计算位置
    position = position.lower() if isinstance(position, str) else "center"
    
    if position == "top-center":
        logo_x = chest_left + (chest_width - logo_width) // 2
        logo_y = chest_top + 20
    elif position == "center":
        logo_x = chest_left + (chest_width - logo_width) // 2
        logo_y = chest_top + (chest_height - logo_height) // 2 + 20
    else:  # 默认中间
        logo_x = chest_left + (chest_width - logo_width) // 2
        logo_y = chest_top + (chest_height - logo_height) // 2 + 20
    
    print(f"应用几何图形logo到位置: ({logo_x}, {logo_y}), 大小: {logo_width}x{logo_height}")
    
    # 直接使用PIL的alpha合成功能
    # 几何图形logo有正确的透明背景，直接合成即可
    result_image.paste(logo_resized, (logo_x, logo_y), logo_resized)
    
    return result_image

def generate_complete_design(design_prompt, variation_id=None):
    """Generate complete T-shirt design based on prompt"""
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
        
        # 1. 应用颜色和纹理
        colored_shirt = change_shirt_color(
            original_image,
            color_hex,
            apply_texture=True,
            fabric_type=fabric_type
        )
        
        # 2. 生成Logo - 确保每个设计都有logo
        logo_description = design_suggestions.get("logo", "")
        
        # 如果AI没有提供logo描述，使用用户输入的关键词作为备选
        if not logo_description:
            logo_description = f"simple minimalist design inspired by {design_prompt}"
        
        # 修改Logo提示词，生成透明背景的矢量图logo
        logo_prompt = f"""Create a professional vector logo design: {logo_description}. 
        Requirements: 
        1. Simple professional design
        2. IMPORTANT: Transparent background (PNG format)
        3. Clear and distinct graphic with high contrast
        4. Vector-style illustration suitable for T-shirt printing
        5. Must not include any text, numbers or color name, only logo graphic
        6. IMPORTANT: Do NOT include any mockups or product previews
        7. IMPORTANT: Create ONLY the logo graphic itself
        8. NO META REFERENCES - do not show the logo applied to anything
        9. Design should be a standalone graphic symbol/icon only
        10. CRITICAL: Clean vector art style with crisp lines and solid colors"""
        
        # 生成透明背景的矢量logo
        logo_image = generate_vector_image(logo_prompt)
        logo_type = "ai"  # 标记logo类型
        
        # 如果logo生成失败，多次重试AI生成
        if logo_image is None:
            print("第一次logo生成失败，尝试简化的logo...")
            simple_logo_prompt = f"""Create a simple logo design: {design_prompt.split()[0] if design_prompt.split() else 'design'}.
            Requirements:
            1. Very simple and minimal design
            2. IMPORTANT: Transparent background (PNG format)
            3. Clean vector style graphic
            4. No text or letters, only graphic symbol
            5. High contrast colors"""
            
            logo_image = generate_vector_image(simple_logo_prompt)
            
            # 如果简化版也失败，再尝试基础几何描述
            if logo_image is None:
                print("简化logo生成失败，尝试基础几何图形描述...")
                fallback_logo_prompt = f"""Create a simple geometric icon: basic shape design.
                Requirements:
                1. Very simple geometric shape (star, heart, or diamond)
                2. IMPORTANT: Transparent background (PNG format)
                3. Solid color design with clear outline
                4. Minimalist style suitable for T-shirt printing
                5. No text or letters, only geometric graphic"""
                
                logo_image = generate_vector_image(fallback_logo_prompt)
                
                # 最后备选：程序生成的几何图形
                if logo_image is None:
                    print("所有AI生成都失败，使用程序生成的几何图形...")
                    logo_image = create_simple_geometric_logo(design_prompt)
                    logo_type = "geometric"  # 标记为几何图形
        
        # 最终设计 - 确保每个设计都有logo
        final_design = colored_shirt
        
        # 应用Logo - 根据logo类型使用不同的策略
        if logo_image:
            if logo_type == "geometric":
                # 对于程序生成的几何图形，直接应用
                print("应用程序生成的几何图形logo")
                final_design = apply_geometric_logo_to_shirt(colored_shirt, logo_image, "center", 60)
            else:
                # 对于AI生成的logo，使用标准方法
                print("应用AI生成的logo")
                final_design = apply_logo_to_shirt(colored_shirt, logo_image, "center", 60)
        else:
            # 如果所有logo生成都失败，添加简单的文本作为最后备选
            try:
                # 使用用户输入的第一个关键词作为文本
                keywords = design_prompt.split()
                if keywords:
                    fallback_text = keywords[0][:8]  # 限制长度避免太长
                else:
                    fallback_text = "DESIGN"
                
                # 根据T恤颜色选择合适的文本颜色
                # 如果T恤是深色，使用白色文字；如果是浅色，使用深色文字
                shirt_brightness = sum(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) / 3
                text_color = "#FFFFFF" if shirt_brightness < 128 else "#000000"
                
                final_design = apply_text_to_shirt(colored_shirt, fallback_text.upper(), 
                                                 color_hex=text_color, font_size=50)
                print(f"应用了文本logo: '{fallback_text.upper()}', 颜色: {text_color}")
            except Exception as e:
                print(f"文本logo应用失败: {e}")
                # 如果连文本都添加失败，至少返回有颜色的T恤
                final_design = colored_shirt
        
        return final_design, {
            "color": {"hex": color_hex, "name": color_name},
            "fabric": fabric_type,
            "logo": logo_description,
            "design_index": 0 if variation_id is None else variation_id  # 使用design_index替代variation_id
        }
    
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        return None, {"error": f"Error generating design: {str(e)}\n{traceback_str}"}

def generate_single_design(design_prompt, design_index):
    try:
        # 为每个设计添加轻微的提示词变化，确保设计多样性
        design_variations = [
            "",  # 原始提示词
            "modern and minimalist",
            "colorful and vibrant",
            "vintage and retro",
            "elegant and simple"
        ]
        
        # 选择合适的变化描述词
        variation_desc = ""
        if design_index < len(design_variations):
            variation_desc = design_variations[design_index]
        
        # 创建变化的提示词
        if variation_desc:
            # 将变化描述词添加到原始提示词
            varied_prompt = f"{design_prompt}, {variation_desc}"
        else:
            varied_prompt = design_prompt
        
        # 完整的独立流程 - 每个设计独立获取AI建议、生成图片，确保颜色一致性
        # 使用独立提示词生成完全不同的设计
        design, info = generate_complete_design(varied_prompt)
        
        # 添加设计索引到信息中以便排序
        if info and isinstance(info, dict):
            info["design_index"] = design_index
        
        return design, info
    except Exception as e:
        print(f"Error generating design {design_index}: {e}")
        return None, {"error": f"Failed to generate design {design_index}"}

def generate_multiple_designs(design_prompt, count=1):
    """Generate multiple T-shirt designs in parallel - independent designs rather than variations"""
    if count <= 1:
        # 如果只需要一个设计，直接生成不需要并行
        base_design, base_info = generate_complete_design(design_prompt)
        if base_design:
            return [(base_design, base_info)]
        else:
            return []
    
    designs = []
    
    # 创建线程池
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(count, 5)) as executor:
        # 提交所有任务
        future_to_id = {executor.submit(generate_single_design, design_prompt, i): i for i in range(count)}
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_id):
            design_id = future_to_id[future]
            try:
                design, info = future.result()
                if design:
                    designs.append((design, info))
            except Exception as e:
                print(f"Design {design_id} generated an exception: {e}")
    
    # 按照设计索引排序
    designs.sort(key=lambda x: x[1].get("design_index", 0) if x[1] and "design_index" in x[1] else 0)
    
    return designs 