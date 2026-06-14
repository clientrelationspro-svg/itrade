#!/bin/bash

# AI 外贸工作平台 - 后端自动部署到 Render
# 使用方法：
# 1. 在 https://dashboard.render.com/u/settings?add-api-key 创建 API Key
# 2. 运行：bash deploy-backend.sh <你的 Render API Key>

set -e

if [ -z "$1" ]; then
    echo "❌ 请提供 Render API Key"
    echo "使用方法：bash deploy-backend.sh <Render API Key>"
    echo ""
    echo "获取 API Key："
    echo "  1. 访问 https://dashboard.render.com/u/settings?add-api-key"
    echo "  2. 点击 'Create API Key'"
    echo "  3. 复制 API Key"
    exit 1
fi

RENDER_API_KEY=$1
RENDER_API="https://api.render.com/v1"

echo "🚀 开始自动部署后端到 Render..."
echo "======================================"

# 1. 创建 PostgreSQL 数据库
echo ""
echo "📦 步骤 1：创建 PostgreSQL 数据库..."
DB_RESPONSE=$(curl -s -X POST "${RENDER_API}/databases" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ai-trade-db",
    "databaseName": "ai_trade",
    "user": "ai_trade_user",
    "plan": "free",
    "version": "16"
  }')

# 检查是否成功
if echo "$DB_RESPONSE" | grep -q "id"; then
    DB_ID=$(echo "$DB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    echo "✅ 数据库创建成功！ID: $DB_ID"
    echo "⏳ 等待数据库就绪（约 2 分钟）..."
else
    echo "❌ 数据库创建失败："
    echo "$DB_RESPONSE"
    exit 1
fi

# 等待数据库就绪
echo "   等待中..."
sleep 10

# 获取数据库连接字符串
echo ""
echo "📋 步骤 2：获取数据库连接信息..."
DB_DETAIL=$(curl -s -X GET "${RENDER_API}/databases/${DB_ID}" \
  -H "Authorization: Bearer ${RENDER_API_KEY}")

INTERNAL_URL=$(echo "$DB_DETAIL" | python3 -c "import sys, json; print(json.load(sys.stdin).get('internalConnectionString', ''))")

if [ -z "$INTERNAL_URL" ]; then
    echo "❌ 无法获取数据库连接字符串"
    echo "请手动在 Render Dashboard 查看"
    exit 1
fi

echo "✅ 数据库连接字符串已获取"

# 2. 创建 Web Service
echo ""
echo "🌐 步骤 3：创建后端 Web Service..."
SERVICE_RESPONSE=$(curl -s -X POST "${RENDER_API}/services" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"ai-trade-platform-api\",
    \"type\": \"web_service\",
    \"repo\": \"https://github.com/clientrelationspro-svg/itrade\",
    \"branch\": \"main\",
    \"rootDir\": \"backend\",
    \"env\": \"python\",
    \"plan\": \"free\",
    \"buildCommand\": \"pip install -r requirements.txt\",
    \"startCommand\": \"uvicorn app.main:app --host 0.0.0.0 --port \\$PORT\",
    \"envVars\": [
      {\"key\": \"SILICONFLOW_API_KEY\", \"value\": \"sk-tkmklxuruwxdqbuqzpcqucbzbcjwomvxuzcththgmwjtpxdz\"},
      {\"key\": \"DATABASE_URL\", \"value\": \"${INTERNAL_URL}\"},
      {\"key\": \"AI_MODEL_VISION\", \"value\": \"Qwen/Qwen3-VL-8B-Instruct\"}
    ]
  }")

# 检查是否成功
if echo "$SERVICE_RESPONSE" | grep -q "id"; then
    SERVICE_ID=$(echo "$SERVICE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
    SERVICE_URL=$(echo "$SERVICE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['serviceDetails']['url'])" 2>/dev/null || echo "https://ai-trade-platform-api.onrender.com")
    echo "✅ 后端服务创建成功！"
    echo "   ID: $SERVICE_ID"
    echo "   URL: $SERVICE_URL"
else
    echo "❌ 后端服务创建失败："
    echo "$SERVICE_RESPONSE"
    exit 1
fi

echo ""
echo "⏳ 等待部署完成（约 5-10 分钟）..."
echo "   你可以在 https://dashboard.render.com 查看部署进度"

# 3. 输出结果
echo ""
echo "🎉 部署完成！"
echo "======================================"
echo ""
echo "📊 部署信息："
echo "   前端 URL: https://frontend-j3gqodj1g-alexfang-s-projects.vercel.app"
echo "   后端 URL: $SERVICE_URL"
echo "   API 文档: ${SERVICE_URL}/docs"
echo ""
echo "📋 下一步："
echo "   1. 等待后端部署完成（5-10 分钟）"
echo "   2. 配置 CORS（允许前端域名访问）"
echo "   3. 测试前端登录和功能"
echo ""
echo "🔧 配置 CORS："
echo "   在 backend/app/main.py 中添加："
echo "   app.add_middleware("
echo "       CORSMiddleware,"
echo "       allow_origins=['https://frontend-j3gqodj1g-alexfang-s-projects.vercel.app'],"
echo "       allow_credentials=True,"
echo "       allow_methods=['*'],"
echo "       allow_headers=['*'],"
echo "   )"
echo ""
echo "   然后提交并推送代码，Render 会自动重新部署。"
