# AI T-shirt Design Generator - Railway Deployment

这是一个基于Streamlit的AI T恤设计生成器，可以部署到Railway平台。

## 功能特点

- 🎲 随机生成1-10个T恤设计
- 🎨 AI驱动的设计建议和颜色选择
- 👕 面料纹理应用
- 🖼️ 透明背景logo生成
- 📱 响应式界面设计

## Railway部署步骤

### 1. 准备代码

确保以下文件存在于项目根目录：
- `app_railway.py` - 主应用文件
- `design_functions.py` - 设计功能模块
- `fabric_texture.py` - 面料纹理模块
- `svg_utils.py` - SVG处理工具
- `requirements_railway.txt` - Python依赖
- `Procfile` - Railway部署配置
- `railway.json` - Railway配置文件
- `white_shirt.png` - 基础T恤图像

### 2. 部署到Railway

1. **创建Railway账户**
   - 访问 [Railway.app](https://railway.app)
   - 使用GitHub账户登录

2. **连接GitHub仓库**
   - 点击"New Project"
   - 选择"Deploy from GitHub repo"
   - 选择包含此代码的GitHub仓库

3. **配置环境变量**
   在Railway项目设置中添加以下环境变量：
   ```
   PORT=8000
   ```

4. **部署设置**
   - Railway会自动检测到Procfile
   - 使用requirements_railway.txt安装依赖
   - 部署完成后会获得一个公共URL

### 3. 自定义配置

#### 修改API密钥
在`design_functions.py`中更新API密钥：
```python
API_KEYS = [
    "your-api-key-1",
    "your-api-key-2",
    # ... 更多密钥
]
```

#### 环境变量配置
可以在Railway项目设置中添加以下环境变量：
```
OPENAI_API_KEY=your-openai-key
DASHSCOPE_API_KEY=your-dashscope-key
```

### 4. 本地测试

在部署前，可以在本地测试：

```bash
# 安装依赖
pip install -r requirements_railway.txt

# 运行应用
streamlit run app_railway.py
```

### 5. 故障排除

#### 常见问题

1. **依赖安装失败**
   - 确保使用`requirements_railway.txt`
   - 检查Python版本兼容性

2. **图像处理错误**
   - 确保`white_shirt.png`文件存在
   - 检查PIL和OpenCV安装

3. **API调用失败**
   - 验证API密钥配置
   - 检查网络连接

#### 日志查看
在Railway控制台中可以查看应用日志，帮助诊断问题。

## 技术栈

- **前端**: Streamlit
- **AI服务**: OpenAI GPT-4o-mini, DashScope
- **图像处理**: Pillow, OpenCV
- **部署平台**: Railway

## 许可证

MIT License

## 支持

如有问题，请检查：
1. Railway部署日志
2. 环境变量配置
3. API密钥有效性
4. 依赖包版本兼容性 