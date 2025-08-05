#!/bin/bash

# 安装系统依赖
apt-get update
apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:/app"

# 确保目录存在
mkdir -p /app

echo "Setup completed successfully!" 