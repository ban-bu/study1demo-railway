# 🚀 Railway部署指南

## 📋 部署前检查

运行以下命令确保所有配置正确：

```bash
python railway_deploy_check.py
```

如果所有检查都通过，就可以开始部署了。

## 🚀 Railway部署步骤

### 1. 准备GitHub仓库

确保以下文件都在您的GitHub仓库中：

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
├── white_shirt.png          # 基础T恤图像
└── README_RAILWAY.md        # 部署说明
```

### 2. 创建Railway账户

1. 访问 [Railway.app](https://railway.app)
2. 使用GitHub账户登录
3. 点击"Start a New Project"

### 3. 连接GitHub仓库

1. 选择"Deploy from GitHub repo"
2. 选择包含此代码的GitHub仓库
3. 点击"Deploy Now"

### 4. 配置环境变量（可选）

在Railway项目设置中可以添加以下环境变量：

```
# Railway自动设置
PORT=8000

# 可选的环境变量
STREAMLIT_SERVER_PORT=8000
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 5. 等待部署完成

Railway会自动：
- 检测到Procfile
- 安装requirements_railway.txt中的依赖
- 运行run.py启动脚本
- 分配一个公共URL

## 🔧 故障排除

### 常见问题

#### 1. "Starting Container" 然后 "Stopping Container"

**原因**: 应用启动失败
**解决方案**:
- 检查Railway日志
- 确保所有依赖都正确安装
- 验证PORT环境变量设置

#### 2. 端口绑定错误

**原因**: 应用没有正确监听Railway分配的端口
**解决方案**:
- 确保run.py正确读取PORT环境变量
- 检查Procfile配置

#### 3. 依赖安装失败

**原因**: 某些依赖在Railway环境中不可用
**解决方案**:
- 检查requirements_railway.txt
- 移除不必要的依赖
- 使用兼容的版本

### 查看日志

在Railway控制台中：
1. 点击项目
2. 选择"Deployments"
3. 点击最新的部署
4. 查看"Logs"标签

### 重新部署

如果部署失败：
1. 修复问题
2. 推送代码到GitHub
3. Railway会自动重新部署

## 📊 部署验证

部署成功后，您应该看到：

1. **Railway状态**: "Deployed"
2. **公共URL**: 类似 `https://your-app-name.railway.app`
3. **应用功能**:
   - 页面正常加载
   - 可以输入设计关键词
   - 可以生成T恤设计

## 🎯 功能测试

部署完成后，测试以下功能：

1. **基本页面加载**
   - 访问Railway提供的URL
   - 确认页面标题为"AI T-shirt Design Generator"

2. **设计生成功能**
   - 输入关键词（如：casual, sport, vintage）
   - 点击"🎲 Randomize & Generate Designs"
   - 等待1-10个设计生成

3. **AI功能验证**
   - 检查日志中是否有DashScope或OpenAI调用
   - 确认生成的是AI设计的logo而不是简单几何图形

## 📞 支持

如果遇到问题：

1. **检查Railway日志**: 查看详细的错误信息
2. **验证配置**: 运行`python railway_deploy_check.py`
3. **本地测试**: 确保本地运行正常
4. **Railway文档**: 参考[Railway官方文档](https://docs.railway.app/)

## 🎉 成功部署

部署成功后，您将获得：
- 一个公共可访问的URL
- 自动扩展的云服务
- 完整的AI T恤设计生成功能
- 支持多用户同时使用

---

**🎊 恭喜！您的AI T恤设计生成器已成功部署到Railway！** 