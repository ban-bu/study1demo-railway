# 🚀 Flask版本部署指南

## 📋 概述

这是AI T恤设计生成器的Flask版本，完全脱离了Streamlit，使用标准Web技术栈：

- **后端**: Flask + Gunicorn
- **前端**: HTML5 + Bootstrap + jQuery
- **AI功能**: OpenAI DALL-E + 阿里云DashScope
- **部署**: Railway平台

## 🎯 优势

相比Streamlit版本，Flask版本具有以下优势：

✅ **无502错误** - 标准HTTP服务器，稳定可靠  
✅ **更好性能** - Gunicorn多进程处理  
✅ **响应式设计** - 支持移动设备  
✅ **自定义UI** - 完全控制用户界面  
✅ **标准部署** - 兼容所有云平台  

## 📁 文件结构

```
Flask版本文件:
├── app_flask.py                 # Flask主应用
├── design_functions_flask.py    # 设计功能模块(无Streamlit依赖)
├── requirements_flask.txt       # Flask依赖包
├── Procfile.flask              # Flask部署配置
├── templates/                   # HTML模板
│   ├── base.html               # 基础模板
│   ├── index.html              # 主页
│   ├── test.html               # 测试页
│   ├── 404.html                # 404错误页
│   └── 500.html                # 500错误页
├── static/                     # 静态文件目录
│   ├── css/                    # CSS文件
│   ├── js/                     # JavaScript文件
│   └── images/                 # 图片文件
├── uploads/                    # 用户上传目录
└── generated/                  # 生成设计目录
```

## 🚀 Railway部署步骤

### 1. 准备部署文件

确保以下文件在您的仓库中：

```bash
# 核心应用文件
app_flask.py
design_functions_flask.py
fabric_texture.py
svg_utils.py
white_shirt.png

# Flask专用配置
requirements_flask.txt
Procfile.flask
templates/
static/

# 可选保留
FLASK_DEPLOYMENT_GUIDE.md
```

### 2. 更新部署配置

**方法1: 替换现有Procfile**
```bash
# 备份原Procfile
mv Procfile Procfile.streamlit.backup

# 使用Flask Procfile
mv Procfile.flask Procfile

# 使用Flask requirements
mv requirements.txt requirements_streamlit.backup
mv requirements_flask.txt requirements.txt
```

**方法2: 修改Railway配置**

在Railway项目设置中：
- **Root Directory**: 保持默认
- **Build Command**: `pip install -r requirements_flask.txt`
- **Start Command**: `gunicorn app_flask:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120`

### 3. 部署到Railway

```bash
# 提交更改
git add .
git commit -m "转换为Flask应用 - 脱离Streamlit"
git push origin main
```

Railway将自动检测更改并重新部署。

### 4. 验证部署

部署完成后，访问您的Railway URL：

- **主页**: `https://your-app.up.railway.app/`
- **测试页**: `https://your-app.up.railway.app/test`
- **API测试**: `https://your-app.up.railway.app/api/session_info`

## 🔧 本地开发

### 1. 安装依赖

```bash
pip install -r requirements_flask.txt
```

### 2. 设置环境变量

```bash
export FLASK_DEBUG=True
export SECRET_KEY=your-secret-key-here
```

### 3. 运行应用

```bash
# 开发模式
python app_flask.py

# 生产模式
gunicorn app_flask:app --bind 0.0.0.0:5000 --workers 4
```

访问 http://localhost:5000

## 🎨 功能特性

### 核心功能

- ✅ **AI设计生成** - 支持1-10个随机设计
- ✅ **关键词输入** - 智能解析用户需求
- ✅ **实时进度** - Ajax异步生成
- ✅ **设计预览** - 响应式图片展示
- ✅ **会话管理** - 保持用户状态

### UI特性

- 🎨 **Bootstrap 5** - 现代响应式界面
- 📱 **移动优化** - 完美支持手机访问
- 🎭 **动画效果** - 流畅的交互体验
- 🌈 **主题色彩** - 品牌一致性设计

### API接口

- `GET /` - 主页
- `POST /api/generate_designs` - 生成设计
- `GET /api/get_design_image/<filename>` - 获取设计图片
- `GET /api/get_base_tshirt` - 获取基础T恤图片
- `GET /api/session_info` - 获取会话信息

## 🔍 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r requirements_flask.txt --no-cache-dir
   ```

2. **端口绑定错误**
   - 确保使用 `0.0.0.0:$PORT`
   - Railway自动设置PORT环境变量

3. **静态文件404**
   - 检查static目录结构
   - 确保文件路径正确

4. **模板错误**
   - 检查templates目录
   - 验证Jinja2语法

### 日志调试

```bash
# 查看Railway日志
railway logs

# 本地调试
export FLASK_DEBUG=True
python app_flask.py
```

## 📊 性能优化

### 生产配置

```bash
# Gunicorn优化配置
gunicorn app_flask:app \
  --bind 0.0.0.0:$PORT \
  --workers 4 \
  --worker-class gthread \
  --threads 2 \
  --timeout 120 \
  --keep-alive 2 \
  --max-requests 1000 \
  --max-requests-jitter 50
```

### 缓存设置

```python
# 在app_flask.py中添加
from flask import send_from_directory
import os

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename, 
                             cache_timeout=3600)  # 1小时缓存
```

## 🎉 完成！

Flask版本成功部署后，您将获得：

- 🚀 **稳定的Web应用** - 无Streamlit相关问题
- 📱 **现代化界面** - 响应式设计
- ⚡ **高性能** - Gunicorn多进程
- 🔧 **易于维护** - 标准Flask架构

享受您的全新AI T恤设计生成器！