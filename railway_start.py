#!/usr/bin/env python3
"""
Railway直接启动脚本 - 备选方案
"""

import os
import streamlit.web.cli as stcli
import sys

def main():
    """直接启动Streamlit应用"""
    # 获取端口
    port = int(os.environ.get('PORT', 8000))
    
    # 设置命令行参数
    sys.argv = [
        "streamlit",
        "run",
        "app_railway.py",
        f"--server.port={port}",
        "--server.address=::",  # 使用IPv6
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--server.fileWatcherType=none"
    ]
    
    print(f"🚀 启动AI T恤设计生成器...")
    print(f"📡 端口: {port}")
    print(f"🌐 地址: :: (IPv6)")
    
    # 直接调用Streamlit
    stcli.main()

if __name__ == "__main__":
    main()