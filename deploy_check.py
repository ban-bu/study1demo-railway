#!/usr/bin/env python3
"""
部署检查脚本
验证Railway部署所需的所有文件是否存在
"""

import os
import sys

def check_files():
    """检查必要文件是否存在"""
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
    
    print("🔍 检查部署文件...")
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 缺失")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 发现 {len(missing_files)} 个缺失文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("\n✅ 所有必要文件都存在")
        return True

def check_dependencies():
    """检查依赖文件内容"""
    print("\n🔍 检查依赖文件...")
    
    # 检查requirements文件
    if os.path.exists('requirements_railway.txt'):
        with open('requirements_railway.txt', 'r') as f:
            content = f.read()
            if 'streamlit' in content and 'openai' in content:
                print("✅ requirements_railway.txt 包含必要依赖")
            else:
                print("❌ requirements_railway.txt 缺少必要依赖")
                return False
    else:
        print("❌ requirements_railway.txt 不存在")
        return False
    
    # 检查Procfile
    if os.path.exists('Procfile'):
        with open('Procfile', 'r') as f:
            content = f.read()
            if 'python run.py' in content:
                print("✅ Procfile 配置正确")
            else:
                print("❌ Procfile 配置不正确")
                return False
    else:
        print("❌ Procfile 不存在")
        return False
    
    return True

def main():
    """主检查函数"""
    print("🚀 Railway部署检查工具")
    print("=" * 50)
    
    # 检查文件存在性
    files_ok = check_files()
    
    # 检查依赖配置
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 50)
    
    if files_ok and deps_ok:
        print("🎉 所有检查通过！可以部署到Railway")
        print("\n📋 部署步骤:")
        print("1. 将代码推送到GitHub")
        print("2. 在Railway.app创建新项目")
        print("3. 连接GitHub仓库")
        print("4. 配置环境变量")
        print("5. 等待部署完成")
        return 0
    else:
        print("❌ 检查失败，请修复上述问题后再部署")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 