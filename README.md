# AI服装设计实验平台

这是一个基于Streamlit构建的AI服装设计消费者行为实验平台，用于研究AI推荐水平对AI创造力的影响。

## 功能特性

- 🎨 **AI服装设计**: 集成OpenAI API进行智能设计生成
- 👕 **交互式设计界面**: 支持用户自定义和预设设计元素
- 📊 **实验数据收集**: 完整的用户行为和偏好数据采集
- 🔄 **多实验组支持**: 支持不同AI推荐水平的对比实验
- 🎯 **响应式UI**: 优化的用户界面和交互体验

## 快速部署到Railway

### 一键部署
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/railway-template)

### 手动部署步骤

1. **Fork此仓库**到您的GitHub账号

2. **登录Railway**
   - 访问 [Railway.app](https://railway.app)
   - 使用GitHub账号登录

3. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择您fork的仓库

4. **配置环境变量**
   在Railway项目设置中添加：
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_BASE_URL=https://api.deepbricks.ai/v1/
   DASHSCOPE_API_KEY=your_dashscope_api_key_here  # 可选
   ```

5. **等待部署完成**
   - Railway会自动检测配置并开始部署
   - 部署完成后会提供访问URL

## 本地开发

### 环境要求
- Python 3.11+
- 系统依赖：cairo, pango, gdk-pixbuf, libffi

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env_example.txt .env
# 编辑.env文件，填入您的API密钥

# 运行应用
streamlit run app.py
```

## 项目结构

```
├── app.py                     # 主应用文件
├── railway.toml              # Railway部署配置
├── nixpacks.toml             # Nixpacks构建配置
├── requirements.txt          # Python依赖
├── packages.txt              # 系统依赖
├── env_example.txt           # 环境变量示例
├── DEPLOYMENT.md             # 详细部署指南
├── experiment_data.csv       # 实验数据存储
├── fabric_texture.py         # 面料纹理处理
├── svg_utils.py              # SVG工具函数
├── welcome_page.py           # 欢迎页面
├── survey_page.py            # 调研页面
├── high_no_explanation.py    # 高推荐级别（无解释）
├── high_with_explanation.py  # 高推荐级别（有解释）
├── low_no_explanation.py     # 低推荐级别（无解释）
├── low_with_explanation.py   # 低推荐级别（有解释）
└── white_shirt.png          # 基础衬衫图片
```

## 实验组说明

本平台支持四种实验设置：
1. **AI定制组** - 低推荐级别，无AI解释
2. **AI设计组** - 低推荐级别，有AI解释  
3. **AI创作组** - 高推荐级别，有AI解释
4. **研究组1** - 高推荐级别，无AI解释

## 技术栈

- **前端框架**: Streamlit
- **AI集成**: OpenAI API, 阿里云DashScope
- **图像处理**: Pillow, OpenCV, Cairo
- **数据处理**: Pandas, NumPy
- **部署平台**: Railway

## 环境变量说明

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 是 |
| `OPENAI_BASE_URL` | OpenAI API基础URL | 否 |
| `DASHSCOPE_API_KEY` | 阿里云DashScope API密钥 | 否 |
| `PORT` | 应用端口（Railway自动设置） | 否 |

## 故障排除

### 常见问题
1. **依赖安装失败**: 检查系统依赖是否正确安装
2. **API调用失败**: 验证API密钥是否正确配置
3. **内存不足**: 考虑升级Railway计划或优化代码

### 获取帮助
- 查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 获取详细部署指南
- 检查Railway项目日志获取错误信息
- 提交Issue报告问题

## 许可证

本项目仅用于学术研究目的。

## 贡献

欢迎提交Pull Request和Issue来改进项目。