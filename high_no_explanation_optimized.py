import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
from openai import OpenAI
import re
import math
from fabric_texture import apply_fabric_texture
import json
import concurrent.futures
import time
import threading
from http import HTTPStatus
import random
from collections import Counter
import platform

# 尝试导入可选依赖
try:
    from dashscope import ImageSynthesis
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    st.warning("DashScope not installed, will use fallback methods")

# API配置信息 - 使用环境变量或默认值
API_KEYS = [
    os.getenv("OPENAI_API_KEY_1", "sk-lNVAREVHjj386FDCd9McOL7k66DZCUkTp6IbV0u9970qqdlg"),
    os.getenv("OPENAI_API_KEY_2", "sk-y8x6LH0zdtyQncT0aYdUW7eJZ7v7cuKTp90L7TiK3rPu3fAg"),
    os.getenv("OPENAI_API_KEY_3", "sk-Kp59pIj8PfqzLzYaAABh2jKsQLB0cUKU3n8l7TIK3rpU61QG"),
    os.getenv("OPENAI_API_KEY_4", "sk-KACPocnavR6poutXUaj7HxsqUrxvcV808S2bv0U9974Ec83g"),
    os.getenv("OPENAI_API_KEY_5", "sk-YknuN0pb6fKBOP6xFOqAdeeqhoYkd1cEl9380vC5HHeC2B30")
]
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepbricks.ai/v1/")

# DashScope API配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-4f82c6e2097440f8adb2ef688c7c7551")

# API密钥轮询计数器
_api_key_counter = 0
_api_lock = threading.Lock()

def get_next_api_key():
    """获取下一个API密钥（轮询方式）"""
    global _api_key_counter
    with _api_lock:
        key = API_KEYS[_api_key_counter % len(API_KEYS)]
        _api_key_counter += 1
        return key

def create_simple_geometric_logo(design_prompt, size=(200, 200)):
    """创建简单的几何图形logo作为备选方案"""
    try:
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        shapes = ['heart', 'diamond', 'hexagon']
        colors = ['#000000', '#FFFFFF', '#FF0000', '#0000FF', '#00AA00']
        
        # 使用设计提示词的hash来确定形状和颜色
        import hashlib
        hash_obj = hashlib.md5(design_prompt.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        shape = shapes[hash_int % len(shapes)]
        color = colors[hash_int % len(colors)]
        
        center_x, center_y = size[0] // 2, size[1] // 2
        radius = min(size) // 4
        
        outline_color = '#FFFFFF' if color == '#000000' else '#000000'
        
        if shape == 'heart':
            heart_points = []
            for t in range(0, 360, 10):
                rad = math.radians(t)
                x = radius * (16 * math.sin(rad)**3) / 16
                y = -radius * (13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad)) / 16
                heart_points.append((center_x + x, center_y + y))
            if len(heart_points) > 2:
                draw.polygon(heart_points, fill=color, outline=outline_color, width=3)
        elif shape == 'diamond':
            points = [
                (center_x, center_y - radius),
                (center_x + radius, center_y),
                (center_x, center_y + radius),
                (center_x - radius, center_y)
            ]
            draw.polygon(points, fill=color, outline=outline_color, width=3)
        elif shape == 'hexagon':
            hex_points = []
            for i in range(6):
                angle = math.pi * i / 3
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                hex_points.append((x, y))
            draw.polygon(hex_points, fill=color, outline=outline_color, width=3)
        
        return img
        
    except Exception as e:
        print(f"生成几何图形logo失败: {e}")
        return None

def make_background_transparent(image, threshold=100):
    """将图像的白色/浅色背景转换为透明背景"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    data = image.getdata()
    new_data = []
    
    width, height = image.size
    edge_pixels = []
    
    # 采样边缘像素
    for x in range(width):
        edge_pixels.append(image.getpixel((x, 0)))
        edge_pixels.append(image.getpixel((x, height-1)))
    for y in range(height):
        edge_pixels.append(image.getpixel((0, y)))
        edge_pixels.append(image.getpixel((width-1, y)))
    
    # 找出最常见的边缘颜色作为背景色
    color_counts = Counter()
    for pixel in edge_pixels:
        if len(pixel) >= 3:
            rounded_color = (pixel[0]//20*20, pixel[1]//20*20, pixel[2]//20*20)
            color_counts[rounded_color] += 1
    
    if color_counts:
        bg_color = color_counts.most_common(1)[0][0]
        bg_r, bg_g, bg_b = bg_color
    else:
        corner_pixels = [
            image.getpixel((0, 0)),
            image.getpixel((width-1, 0)),
            image.getpixel((0, height-1)),
            image.getpixel((width-1, height-1))
        ]
        bg_r = sum(p[0] for p in corner_pixels) // 4
        bg_g = sum(p[1] for p in corner_pixels) // 4
        bg_b = sum(p[2] for p in corner_pixels) // 4
    
    # 遍历所有像素
    for item in data:
        r, g, b, a = item
        
        diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
        brightness = (r + g + b) / 3
        gray_similarity = abs(r - g) + abs(g - b) + abs(r - b)
        is_grayish = gray_similarity < 30
        
        should_transparent = False
        
        if diff < threshold:
            should_transparent = True
        elif brightness > 230 and is_grayish:
            should_transparent = True
        elif brightness > 245 and r > 240 and g > 240 and b > 240:
            should_transparent = True
        
        if should_transparent:
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, 255))
    
    transparent_image = Image.new('RGBA', image.size)
    transparent_image.putdata(new_data)
    
    return transparent_image

def get_random_design_count():
    """随机生成1-10个设计数量"""
    return random.randint(1, 10)

# 每次会话开始时生成随机设计数量
if 'design_count' not in st.session_state:
    st.session_state.design_count = get_random_design_count()

def get_ai_design_suggestions(user_preferences=None):
    """从GPT-4o-mini获取设计建议"""
    client = OpenAI(api_key=get_next_api_key(), base_url=BASE_URL)
    
    if not user_preferences:
        user_preferences = "casual fashion t-shirt design"
    
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
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional design consultant. Provide design suggestions in JSON format exactly as requested."},
                {"role": "user", "content": prompt}
            ]
        )
        
        if response.choices and len(response.choices) > 0:
            suggestion_text = response.choices[0].message.content
            
            try:
                json_match = re.search(r'```json\s*(.*?)\s*```', suggestion_text, re.DOTALL)
                if json_match:
                    suggestion_json = json.loads(json_match.group(1))
                else:
                    suggestion_json = json.loads(suggestion_text)
                
                return suggestion_json
            except Exception as e:
                return {"error": f"Failed to parse design suggestions: {str(e)}"}
        else:
            return {"error": "Failed to get AI design suggestions. Please try again later."}
    except Exception as e:
        return {"error": f"Error getting AI design suggestions: {str(e)}"}

def generate_vector_image(prompt, background_color=None):
    """使用DashScope API生成矢量风格logo"""
    
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
    10. 重要：背景必须完全透明，不能有任何颜色填充"""
    
    if DASHSCOPE_AVAILABLE:
        try:
            rsp = ImageSynthesis.call(
                api_key=DASHSCOPE_API_KEY,
                model="wanx2.0-t2i-turbo",
                prompt=vector_style_prompt,
                n=1,
                size='1024*1024'
            )
            
            if rsp.status_code == HTTPStatus.OK:
                for result in rsp.output.results:
                    image_resp = requests.get(result.url)
                    if image_resp.status_code == 200:
                        img = Image.open(BytesIO(image_resp.content)).convert("RGBA")
                        img_processed = make_background_transparent(img, threshold=120)
                        return img_processed
                    else:
                        st.error(f"下载图像失败, 状态码: {image_resp.status_code}")
            else:
                st.error(f"DashScope API调用失败: {rsp.message}")
                
        except Exception as e:
            st.error(f"DashScope API调用错误: {e}")
    
    return None

def change_shirt_color(image, color_hex, apply_texture=False, fabric_type=None):
    """改变T恤颜色并可选应用面料纹理"""
    color_rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    colored_image = image.copy().convert("RGBA")
    data = colored_image.getdata()
    
    new_data = []
    threshold = 200
    
    for item in data:
        if item[0] > threshold and item[1] > threshold and item[2] > threshold and item[3] > 0:
            new_color = (color_rgb[0], color_rgb[1], color_rgb[2], item[3])
            new_data.append(new_color)
        else:
            new_data.append(item)
    
    colored_image.putdata(new_data)
    
    if apply_texture and fabric_type:
        return apply_fabric_texture(colored_image, fabric_type)
    
    return colored_image

def apply_text_to_shirt(image, text, color_hex="#FFFFFF", font_size=80):
    """在T恤上应用文本"""
    if not text:
        return image
    
    result_image = image.copy().convert("RGBA")
    img_width, img_height = result_image.size
    
    text_layer = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    
    font = None
    try:
        system = platform.system()
        
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
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
    except Exception as e:
        print(f"Error loading font: {e}")
    
    if font is None:
        try:
            font = ImageFont.load_default()
        except:
            return result_image
    
    color_rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    text_color = color_rgb + (255,)
    
    text_bbox = text_draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (img_width - text_width) // 2
    text_y = (img_height // 3) - (text_height // 2)
    
    text_draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    result_image = Image.alpha_composite(result_image, text_layer)
    
    return result_image

def apply_logo_to_shirt(shirt_image, logo_image, position="center", size_percent=60, background_color=None):
    """将logo应用到T恤图像"""
    if logo_image is None:
        return shirt_image
    
    result_image = shirt_image.copy().convert("RGBA")
    img_width, img_height = result_image.size
    
    chest_width = int(img_width * 0.95)
    chest_height = int(img_height * 0.6)
    chest_left = (img_width - chest_width) // 2
    chest_top = int(img_height * 0.2)
    
    logo_with_bg = logo_image.copy().convert("RGBA")
    
    logo_size_factor = size_percent / 100
    logo_width = int(chest_width * logo_size_factor * 0.5)
    logo_height = int(logo_width * logo_with_bg.height / logo_with_bg.width)
    logo_resized = logo_with_bg.resize((logo_width, logo_height), Image.LANCZOS)
    
    position = position.lower() if isinstance(position, str) else "center"
    
    if position == "top-center":
        logo_x, logo_y = chest_left + (chest_width - logo_width) // 2, chest_top + 10
    elif position == "center":
        logo_x, logo_y = chest_left + (chest_width - logo_width) // 2, chest_top + (chest_height - logo_height) // 2 + 30
    else:
        logo_x, logo_y = chest_left + (chest_width - logo_width) // 2, chest_top + (chest_height - logo_height) // 2 + 30
    
    if logo_resized.mode == 'RGBA':
        has_transparency = False
        fully_transparent_pixels = 0
        total_pixels = logo_resized.width * logo_resized.height
        
        for pixel in logo_resized.getdata():
            if len(pixel) == 4:
                if pixel[3] < 255:
                    has_transparency = True
                if pixel[3] == 0:
                    fully_transparent_pixels += 1
        
        transparency_ratio = fully_transparent_pixels / total_pixels
        
        if has_transparency and transparency_ratio > 0.05:
            result_image.paste(logo_resized, (logo_x, logo_y), logo_resized)
        else:
            transparent_logo = make_background_transparent(logo_resized, threshold=60)
            result_image.paste(transparent_logo, (logo_x, logo_y), transparent_logo)
    
    return result_image

def generate_complete_design(design_prompt, variation_id=None):
    """基于提示词生成完整的T恤设计"""
    if not design_prompt:
        return None, {"error": "Please enter a design prompt"}
    
    design_suggestions = get_ai_design_suggestions(design_prompt)
    
    if "error" in design_suggestions:
        return None, design_suggestions
    
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
        
        original_image = Image.open(original_image_path).convert("RGBA")
    except Exception as e:
        return None, {"error": f"Error loading T-shirt image: {str(e)}"}
    
    try:
        color_hex = design_suggestions.get("color", {}).get("hex", "#FFFFFF")
        color_name = design_suggestions.get("color", {}).get("name", "Custom Color")
        fabric_type = design_suggestions.get("fabric", "Cotton")
        
        # 应用颜色和纹理
        colored_shirt = change_shirt_color(
            original_image,
            color_hex,
            apply_texture=True,
            fabric_type=fabric_type
        )
        
        # 生成Logo
        logo_description = design_suggestions.get("logo", "")
        
        if not logo_description:
            logo_description = f"simple minimalist design inspired by {design_prompt}"
        
        logo_prompt = f"""Create a professional vector logo design: {logo_description}. 
        Requirements: 
        1. Simple professional design
        2. IMPORTANT: Transparent background (PNG format)
        3. Clear and distinct graphic with high contrast
        4. Vector-style illustration suitable for T-shirt printing
        5. Must not include any text, numbers or color name, only logo graphic"""
        
        logo_image = generate_vector_image(logo_prompt)
        logo_type = "ai"
        
        # 如果logo生成失败，尝试备选方案
        if logo_image is None:
            simple_logo_prompt = f"""Create a simple logo design: {design_prompt.split()[0] if design_prompt.split() else 'design'}.
            Requirements:
            1. Very simple and minimal design
            2. IMPORTANT: Transparent background (PNG format)
            3. Clean vector style graphic
            4. No text or letters, only graphic symbol"""
            
            logo_image = generate_vector_image(simple_logo_prompt)
            
            if logo_image is None:
                logo_image = create_simple_geometric_logo(design_prompt)
                logo_type = "geometric"
        
        final_design = colored_shirt
        
        # 应用Logo
        if logo_image:
            final_design = apply_logo_to_shirt(colored_shirt, logo_image, "center", 60)
        else:
            # 如果所有logo生成都失败，添加文本作为备选
            try:
                keywords = design_prompt.split()
                if keywords:
                    fallback_text = keywords[0][:8]
                else:
                    fallback_text = "DESIGN"
                
                shirt_brightness = sum(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) / 3
                text_color = "#FFFFFF" if shirt_brightness < 128 else "#000000"
                
                final_design = apply_text_to_shirt(colored_shirt, fallback_text.upper(), 
                                                 color_hex=text_color, font_size=50)
            except Exception as e:
                final_design = colored_shirt
        
        return final_design, {
            "color": {"hex": color_hex, "name": color_name},
            "fabric": fabric_type,
            "logo": logo_description,
            "design_index": 0 if variation_id is None else variation_id
        }
    
    except Exception as e:
        return None, {"error": f"Error generating design: {str(e)}"}

def generate_single_design(design_index, design_prompt):
    """生成单个设计"""
    try:
        design_variations = [
            "",
            "modern and minimalist",
            "colorful and vibrant",
            "vintage and retro",
            "elegant and simple"
        ]
        
        variation_desc = ""
        if design_index < len(design_variations):
            variation_desc = design_variations[design_index]
        
        if variation_desc:
            varied_prompt = f"{design_prompt}, {variation_desc}"
        else:
            varied_prompt = design_prompt
        
        design, info = generate_complete_design(varied_prompt)
        
        if info and isinstance(info, dict):
            info["design_index"] = design_index
        
        return design, info
    except Exception as e:
        return None, {"error": f"Failed to generate design {design_index}"}

def show_high_recommendation_without_explanation():
    """显示高推荐级别界面（无解释）"""
    if 'design_count' not in st.session_state:
        st.session_state.design_count = get_random_design_count()
    
    st.title("👕 AI Recommendation Experiment Platform")
    st.markdown("### Study1-Let AI Design Your T-shirt")
    
    st.info("You are currently in Study1, and AI will generate T-shirt design options for you")
    
    # 初始化会话状态变量
    if 'user_prompt' not in st.session_state:
        st.session_state.user_prompt = ""
    if 'final_design' not in st.session_state:
        st.session_state.final_design = None
    if 'design_info' not in st.session_state:
        st.session_state.design_info = None
    if 'generated_designs' not in st.session_state:
        st.session_state.generated_designs = []
    if 'selected_design_index' not in st.session_state:
        st.session_state.selected_design_index = 0
    if 'original_tshirt' not in st.session_state:
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
        design_area = st.empty()
        
        if st.session_state.final_design is not None:
            with design_area.container():
                st.markdown("### Your Custom T-shirt Design")
                st.image(st.session_state.final_design, use_container_width=True)
        elif len(st.session_state.generated_designs) > 0:
            with design_area.container():
                st.markdown("### Generated Design Options")
                
                design_count = len(st.session_state.generated_designs)
                max_cols_per_row = 3
                rows_needed = (design_count + max_cols_per_row - 1) // max_cols_per_row
                
                for row in range(rows_needed):
                    start_idx = row * max_cols_per_row
                    end_idx = min(start_idx + max_cols_per_row, design_count)
                    
                    row_cols = st.columns(max_cols_per_row)
                    
                    for col_idx in range(max_cols_per_row):
                        design_idx = start_idx + col_idx
                        with row_cols[col_idx]:
                            if design_idx < design_count:
                                design, _ = st.session_state.generated_designs[design_idx]
                                st.markdown(f"<p style='text-align:center;'>Design {design_idx+1}</p>", unsafe_allow_html=True)
                                st.image(design, use_container_width=True)
                            else:
                                st.empty()
        else:
            with design_area.container():
                st.markdown("### T-shirt Design Preview")
                if st.session_state.original_tshirt is not None:
                    st.image(st.session_state.original_tshirt, use_container_width=True)
                else:
                    st.info("Could not load original T-shirt image, please refresh the page")
    
    with input_col:
        st.markdown("### Design Options")
        
        st.markdown("#### Describe your desired T-shirt design:")
        
        st.markdown("""
        <div style="margin-bottom: 15px; padding: 10px; background-color: #f0f2f6; border-radius: 5px;">
        <p style="margin: 0; font-size: 14px;">Enter keywords to describe your ideal T-shirt design. 
        Our AI will combine these features to create unique designs for you.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'keywords' not in st.session_state:
            st.session_state.keywords = ""
        
        keywords = st.text_input("Enter keywords for your design", value=st.session_state.keywords, 
                              placeholder="please only input one word", key="input_keywords")
        
        generate_button = st.button("🎲 Randomize & Generate Designs", key="randomize_and_generate", use_container_width=True)
        
        progress_area = st.empty()
        message_area = st.empty()
        
        if generate_button:
            st.session_state.design_count = get_random_design_count()
            st.session_state.keywords = keywords
            
            if not keywords:
                st.error("Please enter at least one keyword")
            else:
                user_prompt = keywords
                st.session_state.user_prompt = user_prompt
                
                design_count = st.session_state.design_count
                
                st.session_state.final_design = None
                st.session_state.generated_designs = []
                
                try:
                    with design_area.container():
                        st.markdown("### Generating T-shirt Designs")
                        if st.session_state.original_tshirt is not None:
                            st.image(st.session_state.original_tshirt, use_container_width=True)
                    
                    progress_bar = progress_area.progress(0)
                    message_area.info(f"AI is generating {design_count} unique designs for you. This may take about a minute. Please do not refresh the page or close the browser. Thank you for your patience! ♪(･ω･)ﾉ")
                    
                    start_time = time.time()
                    designs = []
                    
                    if design_count == 1:
                        design, info = generate_complete_design(user_prompt, 0)
                        if design:
                            designs.append((design, info))
                        progress_bar.progress(100)
                        message_area.success("Design generation complete!")
                    else:
                        completed_count = 0
                        
                        def update_progress():
                            nonlocal completed_count
                            completed_count += 1
                            progress = int(100 * completed_count / design_count)
                            progress_bar.progress(progress)
                            message_area.info(f"Generated {completed_count}/{design_count} designs...")
                        
                        with concurrent.futures.ThreadPoolExecutor(max_workers=design_count) as executor:
                            future_to_id = {executor.submit(generate_single_design, i, user_prompt): i for i in range(design_count)}
                            
                            for future in concurrent.futures.as_completed(future_to_id):
                                design_id = future_to_id[future]
                                try:
                                    design, info = future.result()
                                    if design:
                                        designs.append((design, info))
                                except Exception as e:
                                    message_area.error(f"Design {design_id} generation failed: {str(e)}")
                                
                                update_progress()
                        
                        designs.sort(key=lambda x: x[1].get("design_index", 0) if x[1] and "design_index" in x[1] else 0)
                    
                    end_time = time.time()
                    generation_time = end_time - start_time
                    
                    if designs:
                        st.session_state.generated_designs = designs
                        st.session_state.selected_design_index = 0
                        message_area.success(f"Generated {len(designs)} designs in {generation_time:.1f} seconds!")
                    else:
                        message_area.error("Could not generate any designs. Please try again.")
                    
                    st.rerun()
                except Exception as e:
                    message_area.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    show_high_recommendation_without_explanation()