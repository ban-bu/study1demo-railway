# 🚀 AI T-shirt Design Generator - Railway部署指南

## 📋 项目概述

这是一个基于Streamlit的AI T恤设计生成器，具有以下功能：

- 🎲 **随机设计生成**: 每次生成1-10个随机T恤设计
- 🎨 **AI驱动设计**: 使用GPT-4o-mini提供设计建议
- 👕 **面料纹理**: 支持多种面料类型的纹理应用
- 🖼️ **透明Logo**: 生成透明背景的矢量logo
- 📱 **响应式界面**: 适配各种设备屏幕

## 🛠️ 技术栈

- **前端**: Streamlit 1.43.2
- **AI服务**: OpenAI GPT-4o-mini, DashScope
- **图像处理**: Pillow, OpenCV
- **部署平台**: Railway

## 📁 项目结构

```
study1-random-1-10-main/
├── app_railway.py              # 主应用文件
├── design_functions.py         # 设计功能模块
├── fabric_texture.py          # 面料纹理模块
├── svg_utils.py              # SVG处理工具
├── requirements_railway.txt   # Python依赖
├── Procfile                  # Railway部署配置
├── railway.json              # Railway配置文件
├── run.py                    # 启动脚本
├── deploy_check.py           # 部署检查脚本
├── white_shirt.png          # 基础T恤图像
└── README_RAILWAY.md        # 部署说明
```

## 🚀 Railway部署步骤

### 1. 准备工作

#### 1.1 检查部署文件
运行部署检查脚本：
```bash
python deploy_check.py
```

确保所有文件都存在且配置正确。

#### 1.2 配置API密钥
在`design_functions.py`中更新API密钥：
```python
API_KEYS = [
    "your-openai-api-key-1",
    "your-openai-api-key-2",
    # ... 更多密钥
]

DASHSCOPE_API_KEY = "your-dashscope-api-key"
```

### 2. 部署到Railway

#### 2.1 创建Railway账户
1. 访问 [Railway.app](https://railway.app)
2. 使用GitHub账户登录

#### 2.2 连接GitHub仓库
1. 点击"New Project"
2. 选择"Deploy from GitHub repo"
3. 选择包含此代码的GitHub仓库

#### 2.3 配置环境变量
在Railway项目设置中添加以下环境变量：
```
PORT=8000
STREAMLIT_SERVER_PORT=8000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

#### 2.4 部署设置
- Railway会自动检测到Procfile
- 使用requirements_railway.txt安装依赖
- 部署完成后会获得一个公共URL

### 3. 本地测试

在部署前，可以在本地测试：

```bash
# 安装依赖
pip install -r requirements_railway.txt

# 运行应用
streamlit run app_railway.py
```

或者使用启动脚本：
```bash
python run.py
```

## 🔧 自定义配置

### 修改设计数量范围
在`app_railway.py`中修改：
```python
def get_random_design_count():
    """随机生成1-10个设计数量"""
    return random.randint(1, 10)  # 修改这里的范围
```

### 添加新的面料类型
在`fabric_texture.py`中添加新的面料类型和纹理。

### 自定义API端点
在`design_functions.py`中修改API配置：
```python
BASE_URL = "your-api-endpoint"
GPT4O_MINI_BASE_URL = "your-gpt-api-endpoint"
```

## 🐛 故障排除

### 常见问题

#### 1. 依赖安装失败
**症状**: 部署时出现依赖错误
**解决方案**:
- 检查`requirements_railway.txt`中的版本兼容性
- 确保所有依赖都列在requirements文件中
- 查看Railway构建日志

#### 2. 图像处理错误
**症状**: 无法加载或处理图像
**解决方案**:
- 确保`white_shirt.png`文件存在
- 检查PIL和OpenCV安装
- 验证图像文件格式

#### 3. API调用失败
**症状**: AI功能无法正常工作
**解决方案**:
- 验证API密钥配置
- 检查网络连接
- 确认API配额充足

#### 4. 端口配置问题
**症状**: 应用无法访问
**解决方案**:
- 确保PORT环境变量设置正确
- 检查Railway端口配置
- 验证防火墙设置

### 日志查看

在Railway控制台中可以查看：
- 构建日志
- 应用日志
- 错误信息

### 性能优化

1. **减少API调用**: 使用多个API密钥轮询
2. **图像缓存**: 实现图像缓存机制
3. **并发控制**: 限制同时生成的设计数量

## 📊 监控和维护

### 健康检查
定期检查应用状态：
- 响应时间
- 错误率
- API调用成功率

### 更新维护
- 定期更新依赖包
- 监控API配额使用情况
- 备份重要配置

## 📞 支持

### 获取帮助
1. 查看Railway部署日志
2. 检查环境变量配置
3. 验证API密钥有效性
4. 确认依赖包版本兼容性

### 联系信息
- 项目GitHub Issues
- Railway支持文档
- Streamlit社区论坛

## 📄 许可证

MIT License - 详见LICENSE文件

---

**🎉 恭喜！您的AI T恤设计生成器已成功部署到Railway！** 