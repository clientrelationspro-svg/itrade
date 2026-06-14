#!/bin/bash

# AI 外贸工作平台 - 后端自动部署脚本
# 这个脚本会自动将后端部署到 Render

echo "🚀 AI 外贸工作平台 - 后端自动部署"
echo "======================================"
echo ""

# 检查是否已安装 Render CLI
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI 未安装"
    echo "正在安装 Render CLI..."
    echo ""
    echo "请访问 https://render.com/docs/cli 安装 Render CLI"
    echo ""
    echo "或者使用以下命令安装："
    echo "  brew install render"
    echo ""
    exit 1
fi

echo "✅ Render CLI 已安装"
echo ""

# 登录 Render
echo "📋 步骤 1：登录 Render"
echo "请在浏览器中完成登录..."
render login

# 创建后端服务
echo ""
echo "📋 步骤 2：创建后端服务"
echo "服务名称: ai-trade-platform-api"
echo "环境: Python 3"
echo "构建命令: pip install -r requirements.txt"
echo "启动命令: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo ""

# 使用 Render Blueprint 部署（从 render.yaml）
echo "📋 步骤 3：从 Blueprint 部署"
echo "正在读取 render.yaml 配置..."

# 部署到 Render
render blueprint apply

echo ""
echo "✅ 后端部署完成！"
echo ""
echo "📊 部署信息："
echo "  后端 URL: https://ai-trade-platform-api.onrender.com"
echo "  API 文档: https://ai-trade-platform-api.onrender.com/docs"
echo ""
echo "📋 下一步："
echo "  1. 等待后端部署完成（5-10 分钟）"
echo "  2. 前端环境变量将自动更新"
echo "  3. 前端将自动重新部署"
echo ""
echo "🔧 配置前端环境变量..."
echo "  正在更新 Vercel 环境变量..."

# 更新 Vercel 环境变量
vercel env add VITE_API_URL production https://ai-trade-platform-api.onrender.com --token vcp_015YVgsR8OEH5eWgf8XrFIuhzeb7YJADRRFuTtEvdYWwh6tVeD3yIqGq

echo ""
echo "✅ 前端环境变量已更新"
echo ""
echo "🎉 部署完成！"
echo ""
echo "📊 完整部署信息："
echo "  前端 URL: https://frontend-q6aop25ra-alexfang-s-projects.vercel.app"
echo "  后端 URL: https://ai-trade-platform-api.onrender.com"
echo "  登录账号: admin / admin123"
echo ""
