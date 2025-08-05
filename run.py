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
    port = int(os.environ.get('PORT', '8000'))
    
    print(f"🚀 启动AI T恤设计生成器...")
    print(f"📡 端口: {port}")
    print(f"🌐 地址: 0.0.0.0")
    print(f"🏁 Python版本: {sys.version}")
    print(f"📦 Streamlit: {os.popen('streamlit --version').read().strip()}")
    
    # 启动Streamlit应用
    try:
        # 确保使用正确的IPv6绑定
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app_railway.py',
            f'--server.port={port}',
            '--server.address=::',  # 使用IPv6绑定
            '--server.headless=true',
            '--browser.gatherUsageStats=false',
            '--server.enableCORS=false',
            '--server.enableXsrfProtection=false',
            '--server.allowRunOnSave=false',
            '--server.runOnSave=false',
            '--server.fileWatcherType=none'  # 禁用文件监视器
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 应用已停止")
        sys.exit(0)

if __name__ == "__main__":
    main() 