# 🛠️ Railway 502错误修复指南

## 🔍 问题诊断

你遇到的502错误通常是因为以下原因：

1. **端口绑定问题** - Railway无法正确路由到应用端口
2. **Streamlit配置问题** - 应用启动了但无法接受HTTP请求
3. **健康检查失败** - Railway无法验证应用是否正常运行

## 🚀 解决方案

### 方法1：使用修复后的run.py（推荐）

已经修复的配置：
- `run.py` - 改进了端口配置
- `railway.json` - 添加了健康检查配置

### 方法2：直接使用Streamlit启动

如果方法1不工作，可以尝试：

1. **替换Procfile内容**：
```
web: streamlit run app_railway.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false
```

2. **或者使用备选启动脚本**：
```
web: python railway_start.py
```

### 方法3：环境变量检查

在Railway项目设置中确保以下环境变量：

- `PORT` - Railway自动设置，不需要手动配置
- `STREAMLIT_SERVER_HEADLESS` = `true`
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS` = `false`

## 🔧 部署步骤

1. **提交修复**：
```bash
git add .
git commit -m "修复Railway 502错误"
git push origin main
```

2. **重新部署**：
   - 在Railway控制台点击 "Redeploy"
   - 或推送代码触发自动部署

3. **查看日志**：
   - 在Railway控制台查看部署日志
   - 确认应用显示"External URL"地址而不是"0.0.0.0"

## 🎯 预期结果

修复后，你应该看到：
```
🚀 启动AI T恤设计生成器...
📡 端口: [Railway分配的端口]
🌐 地址: 0.0.0.0

You can now view your Streamlit app in your browser.
URL: http://0.0.0.0:[端口]
```

## 🆘 如果仍然有问题

1. **检查Railway日志**是否有错误消息
2. **尝试本地测试**：
```bash
PORT=8000 python run.py
```
3. **使用备选Procfile**：
```bash
# 备份当前Procfile
mv Procfile Procfile.backup
# 使用备选Procfile
mv Procfile.alternative Procfile
# 提交并重新部署
git add . && git commit -m "使用备选Procfile" && git push
```

## 📞 调试命令

```bash
# 检查端口是否正确绑定
netstat -tlnp | grep :8000

# 测试应用是否响应
curl -I http://localhost:8000

# 检查Streamlit配置
streamlit config show
```