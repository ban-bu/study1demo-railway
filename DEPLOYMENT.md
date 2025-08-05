# Railway 部署说明

## 文件说明

- `high_no_explanation_optimized.py` - 优化后的主应用文件
- `fabric_texture.py` - 面料纹理生成模块
- `requirements_optimized.txt` - 优化后的依赖文件
- `railway.toml` - Railway部署配置
- `Procfile` - 备选启动配置
- `.env.example` - 环境变量示例

## 部署步骤

1. 在Railway平台创建新项目
2. 连接GitHub仓库或直接上传代码
3. 设置环境变量：
   - `OPENAI_API_KEY_1` - OpenAI API密钥1
   - `OPENAI_API_KEY_2` - OpenAI API密钥2（可选）
   - `OPENAI_API_KEY_3` - OpenAI API密钥3（可选）
   - `DASHSCOPE_API_KEY` - DashScope API密钥
4. Railway会自动检测并使用railway.toml配置进行部署

## 注意事项

- 确保所有API密钥都已正确设置
- 应用会自动在Railway分配的端口上运行
- 支持多个OpenAI API密钥轮询使用，提高稳定性