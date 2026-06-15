# Cloudflare D1 数据库配置

## 1. 创建 D1 数据库

```bash
# 安装 Wrangler CLI
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 创建 D1 数据库
wrangler d1 create ai-trade-db

# 输出示例:
# ✅ Created database 'ai-trade-db' with database_id: 'xxxx-xxxx-xxxx-xxxx'
```

## 2. 初始化数据库表结构

```bash
# 执行 SQL 初始化
wrangler d1 execute ai-trade-db --file=cloudflare/schema.sql
```

## 3. 配置后端连接 D1

在后端 `.env` 中设置：
```
DATABASE_URL=sqlite+aiosqlite:///./ai_trade.db  # 本地开发
# Cloudflare D1 通过 HTTP API 访问（需要通过 Worker 代理）
```

## 4. 创建 Worker 代理 API

```bash
# 创建 Worker 项目
wrangler init ai-trade-api-worker

# 部署 Worker
wrangler deploy
```

## 5. D1 HTTP API 端点

```
GET  https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/d1/database/{DATABASE_ID}/query
POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/d1/database/{DATABASE_ID}/query
```

需要在 Header 中携带 API Token。
