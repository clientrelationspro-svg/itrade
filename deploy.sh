#!/bin/bash

# AI 外贸工作平台 - 自动部署脚本
# 使用说明：
# 1. 首次使用需要登录 Vercel：vercel login
# 2. 首次使用需要登录 Render：在 render.com 创建账号并连接 GitHub
# 3. 运行此脚本：bash deploy.sh

set -e  # 遇到错误立即退出

echo "🚀 AI 外贸工作平台 - 自动部署脚本"
echo "======================================"

# 检查必要工具
echo "📦 检查必要工具..."
which git || (echo "❌ Git 未安装" && exit 1)
which vercel || (echo "❌ Vercel CLI 未安装，运行：npm i -g vercel" && exit 1)
echo "✅ 工具检查通过"

# 1. 检查 Git 状态
echo ""
echo "📋 检查 Git 状态..."
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  有未提交的更改，是否继续？(y/n)"
    read -r response
    if [[ "$response" != "y" ]]; then
        echo "❌ 部署已取消"
        exit 1
    fi
fi
echo "✅ Git 状态正常"

# 2. 部署前端到 Vercel
echo ""
echo "🌐 部署前端到 Vercel..."
cd frontend

# 检查是否已登录 Vercel
if ! vercel whoami &>/dev/null; then
    echo "❌ 请先登录 Vercel："
    echo "   运行：vercel login"
    exit 1
fi

# 部署到 Vercel
echo "📤 开始部署前端..."
vercel --prod --yes || (echo "❌ 前端部署失败" && exit 1)
echo "✅ 前端部署成功！"
cd ..

# 3. 提示后端部署
echo ""
echo "🔧 后端部署（需要手动操作）"
echo "======================================"
echo "请访问 Render.com 完成后端部署："
echo "1. 访问 https://render.com"
echo "2. 点击 'New +' → 'Web Service'"
echo "3. 连接 GitHub 仓库：clientrelationspro-svg/itrade"
echo "4. 配置："
echo "   - Root Directory: backend"
echo "   - Runtime: Python 3"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo "5. 添加环境变量（见 DEPLOYMENT.md）"
echo "6. 创建 PostgreSQL 数据库并复制连接字符串"
echo ""
echo "详细步骤请查看 DEPLOYMENT.md"
echo ""
echo "⏳ 部署完成后，请运行："
echo "   bash test-deployment.sh <前端URL> <后端URL>"
echo ""
echo "🎉 部署脚本执行完成！"
echo ""
echo "📊 部署信息"
echo "======================================"
echo "前端 URL: 查看上方 Vercel 部署输出"
echo "后端部署指南: DEPLOYMENT.md"
echo "GitHub 仓库: https://github.com/clientrelationspro-svg/itrade"
