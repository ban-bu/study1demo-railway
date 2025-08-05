#!/usr/bin/env python3
"""
AI T-shirt Design Generator - Railway Deployment
Railway优化启动脚本
"""

import os
import sys
import subprocess

def main():
    """主启动函数"""
    # 获取Railway环境变量
    port = os.environ.get('PORT', '8000')
    
    # 设置Streamlit环境变量
    os.environ.setdefault('STREAMLIT_SERVER_PORT', port)
    os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
    os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
    os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')
    
    print(f"🚀 启动AI T恤设计生成器...")
    print(f"📡 端口: {port}")
    print(f"🌐 地址: 0.0.0.0")
    
    # 启动Streamlit应用
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app_railway.py',
            f'--server.port={port}',
            '--server.address=0.0.0.0',
            '--server.headless=true',
            '--browser.gatherUsageStats=false',
            '--server.enableCORS=false',
            '--server.enableXsrfProtection=false'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 应用已停止")
        sys.exit(0)

if __name__ == "__main__":
    main() 