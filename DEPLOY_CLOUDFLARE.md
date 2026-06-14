# 🌩️ 部署到 Cloudflare Workers

## 📋 方案说明

**Cloudflare Workers** 提供免费的 Python Workers 运行时，可以部署 FastAPI 应用。

### 优势
- ✅ **免费额度慷慨**：每天 100,000 请求
- ✅ **全球边缘网络**：延迟低
- ✅ **无需数据库**：使用 D1 (SQLite) 或 KV
- ✅ **自动 HTTPS**

### 限制
- ⚠️ **无状态**：不能使用传统数据库（需用 D1）
- ⚠️ **运行时间限制**：每次请求最多 30 秒
- ⚠️ **需要适配代码**：当前 FastAPI 代码需简化

---

## 🚀 部署步骤

### 1️⃣ 安装 Wrangler CLI

```bash
npm install -g wrangler
# 或
pnpm add -g wrangler
```

### 2️⃣ 登录 Cloudflare

```bash
wrangler login
```

浏览器会自动打开，登录你的 Cloudflare 账号。

### 3️⃣ 创建 D1 数据库（可选）

如果需要数据库：

```bash
# 创建数据库
wrangler d1 create ai-trade-db

# 记下输出的 database_id，填入 wrangler.toml
```

### 4️⃣ 配置 `wrangler.toml`

编辑 `wrangler.toml`，填入你的账号信息：

```toml
name = "ai-trade-platform-api"
type = "python-worker"
account_id = "你的 Cloudflare Account ID"  # 在 Cloudflare Dashboard 首页可以找到
workers_dev = true
compatibility_date = "2024-06-14"

# D1 数据库（如果需要）
[[d1_databases]]
binding = "DB"
database_name = "ai-trade-db"
database_id = "你的 database_id"

# 环境变量
[vars]
SILICONFLOW_API_KEY = "sk-tkmklxuruwxdqbuqzpcqucbzbcjwomvxuzcththgmwjtpxdz"
AI_MODEL_VISION = "Qwen/Qwen3-VL-8B-Instruct"
```

### 5️⃣ 部署后端

```bash
cd /Users/mima0000/CodeBuddy/ai外贸工作平台

# 部署到 Cloudflare Workers
wrangler deploy backend_workers/main.py --config wrangler.toml
```

**部署成功后会输出**：
```
✅ Successfully deployed to:
   https://ai-trade-platform-api.your-subdomain.workers.dev
```

---

## 🔗 连接前端和后端

### 1. 更新前端环境变量

编辑 `frontend/.env.production`：

```bash
VITE_API_URL=https://ai-trade-platform-api.your-subdomain.workers.dev
```

### 2. 重新构建并部署前端

```bash
cd frontend
pnpm run build
# 然后重新部署到 Vercel
vercel --prod
```

或者在 Vercel Dashboard 中更新环境变量后触发重新部署。

---

## 🧪 测试部署

### 1. 测试后端

访问：`https://ai-trade-platform-api.your-subdomain.workers.dev/docs`

应该能看到 FastAPI 的 Swagger UI 文档。

### 2. 测试登录

在 Swagger UI 中测试 `/api/auth/login` 端点。

### 3. 测试前端

访问你的 Vercel 前端 URL，尝试登录。

---

## ⚠️ 重要说明

### 当前状态：演示版本

`backend_workers/main.py` 是一个**简化演示版本**，包含：
- ✅ 登录接口
- ✅ 客户列表（演示数据）
- ✅ 创建客户（演示）
- ✅ AI OCR 识别（演示）
- ✅ AI 翻译（演示）
- ✅ AI HS 编码推荐（演示）

**不包含**：
- ❌ 完整的 14 个数据模型
- ❌ 数据库 CRUD 操作
- ❌ 文件上传功能
- ❌ AI 视觉识别（需要调用外部 API）

### 完整适配需要

要将完整的 FastAPI 应用部署到 Cloudflare Workers，需要：

1. **重写数据库层**：使用 Cloudflare D1 代替 PostgreSQL
2. **适配文件上传**：使用 R2 存储代替本地上传
3. **重写 AI 调用**：确保 `aiohttp` 调用 SiliconFlow API 在 Workers 中可用
4. **处理环境变量**：使用 Wrangler 的 `vars` 配置

**预计时间**：2-3 小时

---

## 💡 推荐方案

### 如果你想要...

**✅ 快速上线（1 小时内）**：
- 使用 **Render.com** 部署完整版本（已有部署指南 `DEPLOYMENT.md`）
- 免费额度足够个人使用

**✅ 完全免费 + 全球加速**：
- 继续完成 Cloudflare Workers 适配
- 需要 2-3 小时重写后端

**✅ 最简单**：
- 使用 **Railway.app** 或 **Fly.io** 部署 Docker 容器
- 直接支持当前代码，无需修改

---

## 📞 下一步

请告诉我你想要哪个方案：

1. **继续 Cloudflare 适配**（我帮你完成完整的代码重写）
2. **切换到 Render.com**（按照 `DEPLOYMENT.md` 部署完整版本）
3. **使用 Railway/Fly**（我帮你配置 Docker 部署）

或者，如果你只是想要一个**能用的演示版本**，当前的 `backend_workers/main.py` 已经可以部署并测试基本功能了！
