#!/bin/bash

# AI 外贸工作平台 - 修复后的 Render 部署脚本
# 使用方法：bash deploy-render-fixed.sh <Render API Key>

set -e

if [ -z "$1" ]; then
    echo "❌ 请提供 Render API Key"
    echo ""
    echo "📝 获取 API Key 步骤："
    echo "  1. 访问：https://dashboard.render.com/u/settings?add-api-key"
    echo "  2. 点击 'Create API Key'"
    echo "  3. 复制 API Key（以 rnd_ 开头）"
    echo ""
    echo "然后运行："
    echo "  bash deploy-render-fixed.sh <粘贴你的 API Key>"
    exit 1
fi

RENDER_API_KEY=$1
RENDER_API="https://api.render.com/v1"
OWNER_ID="tea-d8nabui8qa3s73eu0dig"

echo "🚀 AI 外贸工作平台 - Render 部署（修复版）"
echo "======================================"
echo ""

# 1. 创建 PostgreSQL 数据库
echo "📦 步骤 1/3：创建 PostgreSQL 数据库..."
DB_RESPONSE=$(curl -s -X POST "${RENDER_API}/postgres" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"ai-trade-db\",
    \"ownerId\": \"${OWNER_ID}\",
    \"plan\": \"free\",
    \"version\": \"16\",
    \"databaseName\": \"ai_trade\",
    \"databaseUser\": \"ai_trade_user\"
  }")

echo "API 响应：$DB_RESPONSE"

# 检查是否成功
if echo "$DB_RESPONSE" | grep -q "\"id\""; then
    DB_ID=$(echo "$DB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
    echo "✅ 数据库创建成功！ID: $DB_ID"
else
    echo "⚠️  数据库可能已存在或创建失败"
    echo "响应：$DB_RESPONSE"
    echo ""
    echo "请手动在 Render Dashboard 检查是否已存在 'ai-trade-db' 数据库"
    echo "如果存在，请获取数据库连接字符串并继续..."
    echo ""
    echo "按 Enter 继续，或 Ctrl+C 退出："
    read
fi

echo ""
echo "⏳ 等待数据库就绪（约 2 分钟）..."
sleep 10

# 2. 获取数据库连接字符串（需要从 Dashboard 手动获取）
echo ""
echo "📋 步骤 2/3：获取数据库连接字符串"
echo "======================================"
echo "请在 Render Dashboard 中："
echo "  1. 打开 https://dashboard.render.com"
echo "  2. 点击 'ai-trade-db' 数据库"
echo "  3. 找到 'Internal Database URL'（内部连接字符串）"
echo "  4. 复制这个 URL"
echo ""
echo "然后粘贴数据库连接字符串（Internal Database URL）："
read -r DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
    echo "❌ 数据库连接字符串不能为空"
    exit 1
fi

echo "✅ 数据库连接字符串已获取"
echo ""

# 3. 创建后端 Web Service
echo "🌐 步骤 3/3：创建后端 Web Service..."
SERVICE_RESPONSE=$(curl -s -X POST "${RENDER_API}/services" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"ai-trade-platform-api\",
    \"ownerId\": \"${OWNER_ID}\",
    \"type\": \"web_service\",
    \"repo\": \"https://github.com/clientrelationspro-svg/itrade\",
    \"branch\": \"main\",
    \"rootDir\": \"backend\",
    \"env\": \"python\",
    \"plan\": \"free\",
    \"buildCommand\": \"pip install -r requirements.txt\",
    \"startCommand\": \"uvicorn app.main:app --host 0.0.0.0 --port \\\$PORT\",
    \"envVars\": [
      {\"key\": \"SILICONFLOW_API_KEY\", \"value\": \"sk-tkmklxuruwxdqbuqzpcqucbzbcjwomvxuzcththgmwjtpxdz\"},
      {\"key\": \"DATABASE_URL\", \"value\": \"${DATABASE_URL}\"},
      {\"key\": \"AI_MODEL_VISION\", \"value\": \"Qwen/Qwen3-VL-8B-Instruct\"},
      {\"key\": \"JWT_SECRET\", \"value\": \"ai-trade-platform-secret-2024\"}
    ]
  }")

echo "API 响应：$SERVICE_RESPONSE"

# 检查是否成功
if echo "$SERVICE_RESPONSE" | grep -q "\"id\""; then
    SERVICE_ID=$(echo "$SERVICE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
    echo "✅ 后端服务创建成功！ID: $SERVICE_ID"
else
    echo "⚠️  后端服务可能已存在或创建失败"
    echo "响应：$SERVICE_RESPONSE"
    echo ""
    echo "请手动在 Render Dashboard 检查是否已存在 'ai-trade-platform-api' 服务"
fi

echo ""
echo "🎉 部署完成！"
echo "======================================"
echo ""
echo "📊 部署信息："
echo "  前端 URL: https://frontend-ten-teal-98.vercel.app"
echo "  后端 URL: https://ai-trade-platform-api.onrender.com"
echo "  API 文档: https://ai-trade-platform-api.onrender.com/docs"
echo ""
echo "⏳ 下一步："
echo "  1. 等待后端部署完成（约 5-10 分钟）"
echo "     在 https://dashboard.render.com 查看进度"
echo "  2. 配置前端环境变量："
echo "     - 访问：https://vercel.com/dashboard"
echo "     - 选择前端项目"
echo "     - Settings → Environment Variables"
echo "     - 添加/修改 VITE_API_URL 为："
echo "       https://ai-trade-platform-api.onrender.com"
echo "     - 保存并 Redeploy"
echo "  3. 测试访问："
echo "     前端：https://frontend-ten-teal-98.vercel.app"
echo "     默认账号：admin / admin123"
echo ""
echo "✅ 部署脚本执行完成！"
