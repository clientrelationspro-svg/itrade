# 客户网站 AI 解析功能 - 部署指南

## 功能说明
在客户管理界面添加了"客户网站"字段，用户可以通过点击"AI 解析"按钮，自动分析网站内容并填充客户信息（公司名称、联系人、邮箱、电话、地址等）。

## 部署步骤

### 1. 安装新的后端依赖
```bash
cd backend
pip install requests beautifulsoup4 lxml
```

或者如果使用 requirements.txt：
```bash
pip install -r backend/requirements.txt
```

### 2. 数据库迁移
连接到你的数据库，执行以下 SQL 命令：

**PostgreSQL:**
```sql
ALTER TABLE customers ADD COLUMN IF NOT EXISTS website VARCHAR(200);
```

**SQLite:**
```sql
ALTER TABLE customers ADD COLUMN website VARCHAR(200);
```

你可以直接使用项目中的 SQL 脚本：
```bash
psql -U your_user -d your_database -f ADD_WEBSITE_FIELD.sql
```

### 3. 重启后端服务
```bash
# 如果使用 Render.com 部署
# 推送代码后会自动重启

# 如果手动部署
pkill -f "uvicorn app.main:app"
# 然后重新启动
```

### 4. 前端部署
前端代码已自动适配，无需额外操作。如果使用静态部署，重新构建并上传即可：
```bash
cd frontend
npm run build
# 上传 dist/ 目录到你的静态服务器
```

## 功能使用说明

1. 进入"客户管理"页面
2. 点击"新增客户"或编辑现有客户
3. 在表单中找到"客户网站"字段
4. 输入客户网站 URL（例如：https://www.example.com）
5. 点击旁边的"AI 解析"按钮
6. 等待 AI 分析完成（按钮会显示加载状态）
7. 核对自动填充的信息，确认无误后保存

## 注意事项

1. **网络连接**：后端服务器需要能够访问外网，以便爬取网站内容
2. **AI 模型**：确保已正确配置 AI 服务（OpenAI 或兼容 API）
3. **网站访问失败**：如果网站无法访问或超时，系统会提示错误信息
4. **数据核对**：AI 分析结果需要人工核对，确保准确性

## 故障排查

### 问题：点击"AI 解析"无反应
- 检查是否已输入网站 URL
- 检查浏览器控制台是否有错误
- 检查后端日志

### 问题：AI 分析失败
- 检查后端是否安装了 `requests` 和 `beautifulsoup4`
- 检查后端日志查看详细错误
- 确认网站 URL 是否正确，网站是否可访问

### 问题：数据库错误
- 确认已执行数据库迁移 SQL
- 检查 `customers` 表是否有 `website` 字段

## 技术实现

### 后端
- 路由：`/api/ai/website/analyze` (POST)
- 功能：爬取网站内容，使用 AI 提取客户信息
- 文件：`backend/app/routers/ai.py`

### 前端
- 界面：在客户表单中添加网站字段和 AI 解析按钮
- API 调用：使用 `aiAPI.websiteAnalyze()` 调用后端接口
- 文件：`frontend/src/views/CustomerList.vue`, `frontend/src/api/index.js`

## 后续优化建议

1. 添加网站内容缓存，避免重复爬取
2. 支持更多语言的网站分析
3. 添加解析进度显示
4. 支持批量网站分析
