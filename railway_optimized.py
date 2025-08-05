#!/usr/bin/env python3
"""
Railway优化启动脚本
专门针对Railway环境的502错误修复
"""

import os
import sys
import time
import socket
import subprocess

def check_port_binding(port):
    """检查端口是否可以绑定"""
    try:
        # 测试IPv4
        sock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock4.bind(('0.0.0.0', port))
        sock4.close()
        print(f"✅ IPv4端口 {port} 可用")
        
        # 测试IPv6
        sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock6.bind(('::', port))
        sock6.close()
        print(f"✅ IPv6端口 {port} 可用")
        return True
    except Exception as e:
        print(f"❌ 端口绑定检查失败: {e}")
        return False

def main():
    """Railway优化启动函数"""
    # 获取Railway环境变量
    port = int(os.environ.get('PORT', '8000'))
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')
    
    print(f"🚀 Railway优化启动...")
    print(f"📡 端口: {port}")
    print(f"🌐 Railway环境: {railway_env}")
    print(f"🐍 Python: {sys.version}")
    
    # 检查端口
    if not check_port_binding(port):
        print("⚠️ 端口检查失败，但继续尝试启动...")
    
    # 设置环境变量
    env = os.environ.copy()
    env.update({
        'STREAMLIT_SERVER_HEADLESS': 'true',
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
        'STREAMLIT_SERVER_ENABLE_CORS': 'false',
        'STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION': 'false',
        'STREAMLIT_SERVER_FILE_WATCHER_TYPE': 'none'
    })
    
    # 启动命令 - 使用IPv6绑定
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'app_railway.py',
        f'--server.port={port}',
        '--server.address=::',  # IPv6绑定对Railway更好
        '--server.headless=true',
        '--browser.gatherUsageStats=false',
        '--server.enableCORS=false',
        '--server.enableXsrfProtection=false',
        '--server.fileWatcherType=none',
        '--server.allowRunOnSave=false',
        '--server.runOnSave=false'
    ]
    
    print(f"📦 启动命令: {' '.join(cmd)}")
    
    # 启动应用
    try:
        print("🎬 启动Streamlit应用...")
        process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, universal_newlines=True)
        
        # 实时输出日志
        for line in iter(process.stdout.readline, ''):
            print(line.rstrip())
            
        process.wait()
        
        if process.returncode != 0:
            print(f"❌ 应用退出，返回码: {process.returncode}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("🛑 应用被手动停止")
        if 'process' in locals():
            process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()