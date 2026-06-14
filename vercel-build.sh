#!/bin/bash
set -e

echo "🚀 开始构建前端..."
cd frontend

echo "📦 安装依赖..."
npm install

echo "🔨 构建生产版本..."
npm run build

echo "✅ 构建完成！"
ls -lah dist/
