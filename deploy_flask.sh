#!/bin/bash

# Flask版本快速部署脚本
echo "🚀 开始部署Flask版本..."

# 1. 备份原始配置
echo "📦 备份Streamlit配置..."
mv Procfile Procfile.streamlit.backup 2>/dev/null || echo "Procfile已备份"
mv requirements.txt requirements_streamlit.backup 2>/dev/null || echo "requirements.txt已备份"

# 2. 启用Flask配置
echo "⚙️ 启用Flask配置..."
cp Procfile.flask Procfile
cp requirements_flask.txt requirements.txt

# 3. 检查必要文件
echo "🔍 检查必要文件..."
FILES_TO_CHECK=(
    "app_flask.py"
    "design_functions_flask.py"
    "fabric_texture.py"
    "svg_utils.py"
    "white_shirt.png"
    "templates/index.html"
    "templates/base.html"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 缺失"
        exit 1
    fi
done

# 4. 创建必要目录
echo "📁 创建目录结构..."
mkdir -p uploads generated static/css static/js static/images

# 5. 显示部署信息
echo ""
echo "🎉 Flask版本配置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 提交到Git:"
echo "   git add ."
echo "   git commit -m \"转换为Flask应用 - 脱离Streamlit\""
echo "   git push origin main"
echo ""
echo "2. Railway将自动重新部署"
echo ""
echo "3. 访问您的应用:"
echo "   - 主页: https://your-app.up.railway.app/"
echo "   - 测试: https://your-app.up.railway.app/test"
echo ""
echo "🔧 本地测试命令:"
echo "   python app_flask.py"
echo ""

# 6. 可选：显示配置对比
echo "📊 配置对比:"
echo "┌─────────────────┬─────────────────┬─────────────────┐"
echo "│      特性       │   Streamlit版   │   Flask版       │"
echo "├─────────────────┼─────────────────┼─────────────────┤"
echo "│   502错误问题   │       有        │       无        │"
echo "│   响应式设计    │      有限       │      完整       │"
echo "│   部署稳定性    │      一般       │      优秀       │"
echo "│   自定义UI      │      受限       │      完全       │"
echo "│   移动支持      │      基础       │      优化       │"
echo "│   性能         │      中等       │      高性能      │"
echo "└─────────────────┴─────────────────┴─────────────────┘"
echo ""
echo "✨ Flask版本的优势:"
echo "   - 解决所有502错误问题"
echo "   - 现代响应式界面"  
echo "   - 更好的移动设备支持"
echo "   - 标准HTTP服务器，稳定可靠"
echo "   - 完全控制用户界面和体验"
echo ""

echo "🚀 准备就绪！现在可以部署到Railway了。"