#!/usr/bin/env python3
"""
Railway部署检查脚本
验证Railway部署所需的所有配置
"""

import os
import sys

def check_railway_config():
    """检查Railway配置"""
    print("🔍 检查Railway配置...")
    
    # 检查必要文件
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
    
    # 检查Procfile内容
    try:
        with open('Procfile', 'r') as f:
            content = f.read().strip()
            if content == 'web: python run.py':
                print("✅ Procfile配置正确")
            else:
                print(f"❌ Procfile配置错误: {content}")
                return False
    except Exception as e:
        print(f"❌ 读取Procfile失败: {e}")
        return False
    
    # 检查railway.json
    try:
        with open('railway.json', 'r') as f:
            content = f.read()
            if '"builder": "NIXPACKS"' in content:
                print("✅ railway.json配置正确")
            else:
                print("❌ railway.json配置错误")
                return False
    except Exception as e:
        print(f"❌ 读取railway.json失败: {e}")
        return False
    
    return True

def check_dependencies():
    """检查依赖配置"""
    print("\n🔍 检查依赖配置...")
    
    try:
        with open('requirements_railway.txt', 'r') as f:
            content = f.read()
            required_deps = ['streamlit', 'openai', 'requests', 'Pillow', 'dashscope']
            
            missing_deps = []
            for dep in required_deps:
                if dep not in content:
                    missing_deps.append(dep)
            
            if missing_deps:
                print(f"❌ 缺失依赖: {missing_deps}")
                return False
            else:
                print("✅ 所有必要依赖都已包含")
                return True
    except Exception as e:
        print(f"❌ 读取requirements_railway.txt失败: {e}")
        return False

def check_run_script():
    """检查启动脚本"""
    print("\n🔍 检查启动脚本...")
    
    try:
        with open('run.py', 'r') as f:
            content = f.read()
            
            # 检查关键配置
            checks = [
                ('PORT环境变量', 'os.environ.get(\'PORT\''),
                ('0.0.0.0地址', '0.0.0.0'),
                ('streamlit run', 'streamlit', 'run', 'app_railway.py'),
                ('headless模式', 'headless=true')
            ]
            
            for check_name, *keywords in checks:
                if all(keyword in content for keyword in keywords):
                    print(f"✅ {check_name}正确")
                else:
                    print(f"❌ {check_name}错误")
                    print(f"   缺少关键词: {[k for k in keywords if k not in content]}")
                    return False
            
            return True
    except Exception as e:
        print(f"❌ 读取run.py失败: {e}")
        return False

def check_api_config():
    """检查API配置"""
    print("\n🔍 检查API配置...")
    
    try:
        with open('design_functions.py', 'r') as f:
            content = f.read()
            
            # 检查API密钥配置
            if 'DASHSCOPE_API_KEY' in content and 'sk-4f82c6e2097440f8adb2ef688c7c7551' in content:
                print("✅ DashScope API密钥配置正确")
            else:
                print("❌ DashScope API密钥配置错误")
                return False
            
            # 检查OpenAI API配置
            if 'API_KEYS' in content and 'BASE_URL' in content:
                print("✅ OpenAI API配置正确")
            else:
                print("❌ OpenAI API配置错误")
                return False
            
            return True
    except Exception as e:
        print(f"❌ 读取design_functions.py失败: {e}")
        return False

def main():
    """主检查函数"""
    print("🚀 Railway部署配置检查")
    print("=" * 50)
    
    checks = [
        ("Railway配置", check_railway_config),
        ("依赖配置", check_dependencies),
        ("启动脚本", check_run_script),
        ("API配置", check_api_config),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n🔍 检查: {check_name}")
        try:
            if check_func():
                passed += 1
                print(f"✅ {check_name} 通过")
            else:
                print(f"❌ {check_name} 失败")
        except Exception as e:
            print(f"❌ {check_name} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 检查结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有检查通过！可以部署到Railway")
        print("\n📋 Railway部署步骤:")
        print("1. 将代码推送到GitHub")
        print("2. 在Railway.app创建新项目")
        print("3. 连接GitHub仓库")
        print("4. 配置环境变量:")
        print("   - PORT (Railway自动设置)")
        print("   - 其他API密钥 (可选)")
        print("5. 等待部署完成")
        return 0
    else:
        print("⚠️  部分检查失败，请修复上述问题后再部署")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 