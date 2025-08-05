#!/usr/bin/env python3
"""
AI T-shirt Design Generator - Railway Deployment
简化启动脚本
"""

import os
import sys
import subprocess

def main():
    """主启动函数"""
    # 设置环境变量
    os.environ.setdefault('STREAMLIT_SERVER_PORT', '8000')
    os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
    
    # 启动Streamlit应用
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app_railway.py',
            '--server.port=8000',
            '--server.address=0.0.0.0',
            '--server.headless=true',
            '--browser.gatherUsageStats=false'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("应用已停止")
        sys.exit(0)

if __name__ == "__main__":
    main() 