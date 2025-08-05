# AI服装设计实验 - Railway部署指南

## 项目概述
这是一个AI服装设计消费者行为实验的Streamlit应用，用于研究AI推荐水平对AI创造力的影响。

## 部署到Railway

### 1. 准备工作
- 确保所有依赖在`requirements.txt`中列出
- 检查Railway配置文件已创建：`railway.toml`和`nixpacks.toml`
- 验证环境变量配置

### 2. GitHub仓库设置
```bash
git init
git add .
git commit -m "Initial commit for Railway deployment"
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

### 3. Railway部署步骤
1. 访问 [Railway.app](https://railway.app)
2. 使用GitHub账号登录
3. 点击"New Project" -> "Deploy from GitHub repo"
4. 选择您的GitHub仓库
5. Railway会自动检测到Streamlit应用并开始部署
6. 配置环境变量（见下方）
7. 等待部署完成

### 4. 环境变量配置
在Railway项目设置中添加以下环境变量：
- `OPENAI_API_KEY`: OpenAI API密钥
- `OPENAI_BASE_URL`: API基础URL（默认：https://api.deepbricks.ai/v1/）
- `DASHSCOPE_API_KEY`: 阿里云DashScope API密钥（可选）

### 5. 自动部署配置
- Railway会自动检测到`railway.toml`配置文件
- 每次推送到main分支时，Railway会自动重新部署
- 健康检查已配置在`/_stcore/health`端点

### 6. 应用访问
部署完成后，Railway会提供一个公开的URL，格式通常为：
`https://your-app-name.up.railway.app`

## 配置文件说明

### railway.toml
```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/_stcore/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[variables]
NIXPACKS_PYTHON_VERSION = "3.11"
```

### nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python311", "cairo", "pango", "gdk-pixbuf", "libffi", "shared-mime-info"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.fileWatcherType none --browser.gatherUsageStats false"
```

## 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

## 故障排除

### 常见问题
1. **依赖安装失败**
   - 检查`requirements.txt`中的版本兼容性
   - 确保系统依赖在`nixpacks.toml`中正确配置

2. **应用启动失败**
   - 检查Railway日志中的错误信息
   - 确保端口配置正确（使用$PORT环境变量）

3. **API密钥问题**
   - 在Railway项目设置中正确配置所有环境变量
   - 确保API密钥有效且权限正确

4. **内存不足**
   - Railway提供的免费计划有内存限制
   - 考虑升级到付费计划或优化应用内存使用

### 监控和日志
- Railway提供实时日志查看功能
- 可以在项目仪表板中监控应用状态
- 设置了健康检查以确保应用正常运行

## Railway优势
- 零配置部署：自动检测Streamlit应用
- GitHub集成：每次提交自动部署
- 免费额度：适合小型项目和测试
- 简单易用：无需复杂的Docker配置
- 实时日志：便于调试和监控 