#!/bin/bash

# 测试后端 API
BASE_URL="https://ai-trade-platform-api.onrender.com"

echo "测试后端 API..."
echo ""

# 测试 1: 根路径
echo "1. 测试根路径:"
curl -s "$BASE_URL/" | python3 -m json.tool 2>&1
echo ""

# 测试 2: 登录（应该返回 401 或 400，而不是 500）
echo "2. 测试登录 API:"
curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | python3 -m json.tool 2>&1
echo ""

# 测试 3: 检查后端日志（通过访问一个不存在的路径）
echo "3. 测试 404 处理:"
curl -s "$BASE_URL/nonexistent" 2>&1
echo ""

echo "测试完成！"
