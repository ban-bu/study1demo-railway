#!/usr/bin/env python3
"""
应用功能测试脚本
测试AI T恤设计生成器的核心功能
"""

import requests
import time
import json
from PIL import Image
import os

def test_app_availability():
    """测试应用是否可访问"""
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            print("✅ 应用可访问")
            return True
        else:
            print(f"❌ 应用响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法访问应用: {e}")
        return False

def test_api_connectivity():
    """测试API连接性"""
    from design_functions import get_ai_design_suggestions
    
    try:
        # 测试AI设计建议功能
        suggestions = get_ai_design_suggestions("casual t-shirt")
        
        if suggestions and "error" not in suggestions:
            print("✅ AI设计建议API正常")
            print(f"   颜色: {suggestions.get('color', {}).get('name', 'N/A')}")
            print(f"   面料: {suggestions.get('fabric', 'N/A')}")
            return True
        else:
            print(f"❌ AI设计建议API异常: {suggestions}")
            return False
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        return False

def test_image_processing():
    """测试图像处理功能"""
    try:
        from design_functions import create_simple_geometric_logo, make_background_transparent
        
        # 测试几何logo生成
        logo = create_simple_geometric_logo("test design")
        if logo:
            print("✅ 几何logo生成正常")
        else:
            print("❌ 几何logo生成失败")
            return False
        
        # 测试背景透明化
        test_image = Image.new('RGBA', (100, 100), (255, 255, 255, 255))
        transparent_image = make_background_transparent(test_image)
        if transparent_image:
            print("✅ 背景透明化功能正常")
        else:
            print("❌ 背景透明化功能失败")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 图像处理测试失败: {e}")
        return False

def test_design_generation():
    """测试设计生成功能"""
    try:
        from design_functions import generate_complete_design
        
        # 测试单个设计生成
        design, info = generate_complete_design("test design")
        
        if design and info and "error" not in info:
            print("✅ 设计生成功能正常")
            print(f"   设计信息: {info.get('color', {}).get('name', 'N/A')} {info.get('fabric', 'N/A')}")
            return True
        else:
            print(f"❌ 设计生成失败: {info}")
            return False
    except Exception as e:
        print(f"❌ 设计生成测试失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    required_files = [
        'app_railway.py',
        'design_functions.py',
        'fabric_texture.py',
        'svg_utils.py',
        'requirements_railway.txt',
        'Procfile',
        'railway.json',
        'run.py',
        'white_shirt.png'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺失文件: {missing_files}")
        return False
    else:
        print("✅ 所有必要文件都存在")
        return True

def main():
    """主测试函数"""
    print("🧪 AI T恤设计生成器功能测试")
    print("=" * 50)
    
    tests = [
        ("文件结构检查", test_file_structure),
        ("应用可访问性", test_app_availability),
        ("图像处理功能", test_image_processing),
        ("API连接性", test_api_connectivity),
        ("设计生成功能", test_design_generation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用功能正常")
        print("\n🌐 应用访问地址: http://localhost:8501")
        print("📝 使用说明:")
        print("   1. 在浏览器中打开 http://localhost:8501")
        print("   2. 输入设计关键词（如：casual, sport, vintage等）")
        print("   3. 点击'🎲 Randomize & Generate Designs'按钮")
        print("   4. 等待AI生成1-10个随机设计")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 