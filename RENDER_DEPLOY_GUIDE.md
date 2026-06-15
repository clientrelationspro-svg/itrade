# Render.com 部署指南 - 不使用 Docker

## 问题
Render.com 尝试使用 Docker 构建，但找不到 Dockerfile。

## 解决方案

### 方案 1: 在 Render.com 控制台手动配置（推荐）

1. **登录 Render.com**
   - 访问 https://dashboard.render.com

2. **删除现有的后端服务**（如果有）
   - 点击你的后端服务
   - 点击 "Settings" -> "Delete Service"

3. **创建新的 Web Service**
   - 点击 "New +" -> "Web Service"
   - 连接 GitHub 仓库：`clientrelationspro-svg/itrade`
   - 配置：
     - **Name**: `ai-trade-platform-api`
     - **Environment**: `Python 3`
     - **Region**: 选择离你最近的区域
     - **Branch**: `main`
     - **Root Directory**: `backend`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   
4. **添加环境变量**
   - 点击 "Environment" 标签
   - 添加：
     - `DATABASE_URL` - 从数据库实例选择（先创建 PostgreSQL 数据库）
     - `AI_API_KEY` - 你的 AI API Key
     - `AI_API_BASE` - AI API 地址（可选）
     - `SECRET_KEY` - 随机字符串
     - `UPLOAD_DIR` - `./uploads`

5. **创建 PostgreSQL 数据库**（如果还没有）
   - 点击 "New +" -> "PostgreSQL"
   - Name: `ai-trade-db`
   - Plan: Free
   - 创建后，回到 Web Service 配置，连接数据库

6. **部署**
   - 点击 "Create Web Service"
   - Render.com 会自动构建和部署

---

### 方案 2: 使用 render.yaml（需要删除后重新连接）

1. **删除仓库中的 render.yaml**
   ```bash
   git rm render.yaml
   git commit -m "Remove render.yaml to use manual config"
   git push origin main
   ```

2. **在 Render.com 控制台手动创建服务**（参考方案 1）

---

### 方案 3: 修复 Docker 部署

如果你想使用 Docker 部署：

1. **确保 Dockerfile 在正确位置**
   - 将 `backend/Dockerfile` 移动到 `backend/Dockerfile`（已完成）
   - 确保 `render.yaml` 中的 `dockerfilePath` 正确

2. **更新 render.yaml**
   ```yaml
   services:
     - type: web
       name: ai-trade-platform-api
       env: docker
       plan: free
       branch: main
       repo: https://github.com/clientrelationspro-svg/itrade
       rootDir: backend
       dockerfilePath: ./Dockerfile
   ```

3. **推送更新**
   ```bash
   git add backend/Dockerfile render.yaml
   git commit -m "Add Dockerfile for backend"
   git push origin main
   ```

---

## 推荐方案

**使用方案 1（手动配置）**，因为：
- ✅ 更简单，不需要 Dockerfile
- ✅ Render.com 会自动处理 Python 环境
- ✅ 更容易调试构建问题

---

## 快速部署步骤（方案 1）

### 1. 删除 `render.yaml`（避免自动检测）

```bash
cd /Users/mima0000/CodeBuddy/ai外贸工作平台
git rm render.yaml
git commit -m "Remove render.yaml for manual deployment"
git push origin main
```

### 2. 在 Render.com 创建 Web Service

参考上面的"方案 1"步骤。

### 3. 执行数据库迁移

部署成功后，连接到数据库执行：
```sql
ALTER TABLE customers ADD COLUMN IF NOT EXISTS website VARCHAR(200);
```

### 4. 测试

访问 `https://<your-service-name>.onrender.com/docs` 查看 API 文档。

---

## 当前建议

**先删除 `render.yaml`，然后在 Render.com 手动创建服务。**

需要我帮你删除 `render.yaml` 并推送吗？
