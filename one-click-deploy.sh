#!/bin/bash

# AI 外贸工作平台 - 一键部署脚本
# 使用方法：
# 1. 在 https://dashboard.render.com/u/settings?add-api-key 创建 API Key
# 2. 运行：bash one-click-deploy.sh <Render API Key>

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
    echo "  bash one-click-deploy.sh <粘贴你的 API Key>"
    exit 1
fi

RENDER_API_KEY=$1
RENDER_API="https://api.render.com/v1"

echo "🚀 AI 外贸工作平台 - 一键部署"
echo "======================================"
echo ""

# 1. 验证 API Key
echo "🔐 验证 API Key..."
VALIDATE=$(curl -s -X GET "${RENDER_API}/services?limit=1" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Accept: application/json")

if echo "$VALIDATE" | grep -q "error"; then
    echo "❌ API Key 无效！"
    echo "$VALIDATE"
    exit 1
fi
echo "✅ API Key 验证通过"
echo ""

# 2. 创建 PostgreSQL 数据库
echo "🗄️  步骤 1/3：创建 PostgreSQL 数据库..."
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

DB_ID=$(echo "$DB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")

if [ -z "$DB_ID" ]; then
    echo "❌ 数据库创建失败！"
    echo "$DB_RESPONSE"
    exit 1
fi

echo "✅ 数据库创建成功！ID: $DB_ID"
echo "⏳ 等待数据库就绪（约 2 分钟）..."
echo "   （你可以在 https://dashboard.render.com 查看进度）"
sleep 10
echo ""

# 3. 获取数据库连接字符串
echo "🔗 获取数据库连接字符串..."
DB_DETAIL=$(curl -s -X GET "${RENDER_API}/databases/${DB_ID}" \
  -H "Authorization: Bearer ${RENDER_API_KEY}")

INTERNAL_URL=$(echo "$DB_DETAIL" | python3 -c "import sys, json; print(json.load(sys.stdin).get('internalConnectionString', ''))" 2>/dev/null || echo "")

if [ -z "$INTERNAL_URL" ]; then
    echo "⚠️  无法自动获取数据库连接字符串"
    echo "请手动在 Render Dashboard 复制 'Internal Database URL'"
    echo "然后运行："
    echo "  bash configure-db.sh <数据库URL>"
    exit 1
fi

echo "✅ 数据库连接字符串已获取"
echo ""

# 4. 创建后端 Web Service
echo "🌐 步骤 2/3：创建后端 Web Service..."
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

SERVICE_ID=$(echo "$SERVICE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")

if [ -z "$SERVICE_ID" ]; then
    echo "❌ 后端服务创建失败！"
    echo "$SERVICE_RESPONSE"
    exit 1
fi

echo "✅ 后端服务创建成功！ID: $SERVICE_ID"
echo ""

# 5. 获取后端 URL
echo "🔗 获取后端服务 URL..."
SERVICE_DETAIL=$(curl -s -X GET "${RENDER_API}/services/${SERVICE_ID}" \
  -H "Authorization: Bearer ${RENDER_API_KEY}")

BACKEND_URL=$(echo "$SERVICE_DETAIL" | python3 -c "import sys, json; print(json.load(sys.stdin).get('serviceDetails', {}).get('url', ''))" 2>/dev/null || echo "https://ai-trade-platform-api.onrender.com")

if [ -z "$BACKEND_URL" ]; then
    BACKEND_URL="https://ai-trade-platform-api.onrender.com"
fi

echo "✅ 后端 URL: $BACKEND_URL"
echo ""

# 6. 输出结果
echo "🎉 部署完成！"
echo "======================================"
echo ""
echo "📊 部署信息："
echo "  前端 URL: https://frontend-j3gqodj1g-alexfang-s-projects.vercel.app"
echo "  后端 URL: $BACKEND_URL"
echo "  API 文档: ${BACKEND_URL}/docs"
echo ""
echo "⏳ 下一步："
echo "  1. 等待后端部署完成（约 5-10 分钟）"
echo "     在 https://dashboard.render.com 查看进度"
echo "  2. 配置前端环境变量："
echo "     - 访问：https://vercel.com/dashboard"
echo "     - 选择前端项目"
echo "     - Settings → Environment Variables"
echo "     - 修改 VITE_API_URL 为：${BACKEND_URL}"
echo "     - 保存并 Redeploy"
echo "  3. 测试访问："
echo "     前端：https://frontend-j3gqodj1g-alexfang-s-projects.vercel.app"
echo "     默认账号：admin / admin123"
echo ""
echo "✅ 部署脚本执行完成！"
echo ""
echo "📖 详细指南："
echo "  - DEPLOY_STEPS.md"
echo "  - RENDER_DEPLOY_GUIDE.md"
