# 🚀 Render 后端部署 - 简化操作指南

## 📋 你需要在打开的 Render 页面上完成以下操作

### 步骤 1：创建 PostgreSQL 数据库（2 分钟）

1. **在 Render 页面**：点击左侧 **"PostgreSQL"** → **"New PostgreSQL"**
2. **填写配置**：
   - **Name**: `ai-trade-db`
   - **Database**: `ai_trade`
   - **User**: `ai_trade_user`
   - **Plan**: 选择 **"Free"**
3. **点击 "Create Database"**
4. **等待创建完成**（约 1 分钟）
5. **复制数据库连接信息**：
   - 找到 **"Internal Database URL"**（格式：`postgresql://user:pass@host:5432/db`）
   - **复制这个 URL**，后面需要用到

---

### 步骤 2：创建后端 Web Service（3 分钟）

1. **在 Render 页面**：点击左侧 **"Web Services"** → **"New Web Service"**
2. **连接 GitHub 仓库**：
   - 选择 **"Connect a repository"**
   - 选择 **"clientrelationspro-svg/itrade"**
   - 点击 **"Connect"**
3. **填写配置**：
   - **Name**: `ai-trade-platform-api`
   - **Root Directory**: 输入 `backend`
   - **Runtime**: 选择 `Python 3`
   - **Build Command**: 输入 `pip install -r requirements.txt`
   - **Start Command**: 输入：
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: 选择 **"Free"**（750 小时/月，会休眠）
4. **展开 "Advanced" → "Add Environment Variable"**：
   添加以下 3 个环境变量：

   | Key | Value |
   |-----|-------|
   | `SILICONFLOW_API_KEY` | `sk-tkmklxuruwxdqbuqzpcqucbzbcjwomvxuzcththgmwjtpxdz` |
   | `DATABASE_URL` | `<粘贴刚才复制的 Internal Database URL>` |
   | `AI_MODEL_VISION` | `Qwen/Qwen3-VL-8B-Instruct` |

5. **点击 "Create Web Service"**

---

### 步骤 3：等待部署完成（5-10 分钟）

- Render 会自动开始构建和部署
- 你可以在 **"Events"** 标签页查看部署进度
- 首次部署可能需要 5-10 分钟（需要安装依赖）
- **部署成功后**，你会看到：
  - **"Service Status"**: `Live`
  - **"URL"**: `https://ai-trade-platform-api.onrender.com`

---

### 步骤 4：测试后端（1 分钟）

1. **访问 API 文档**：
   - 打开：`https://ai-trade-platform-api.onrender.com/docs`
   - 应该能看到 FastAPI 的 Swagger 文档页面
2. **测试登录接口**：
   - 展开 `/api/auth/login` 端点
   - 点击 **"Try it out"**
   - 输入：
     ```json
     {
       "username": "admin",
       "password": "admin123"
     }
     ```
   - 点击 **"Execute"**
   - 应该返回 JWT token

---

## ✅ 部署完成检查清单

- [ ] PostgreSQL 数据库已创建
- [ ] 后端 Web Service 已创建
- [ ] `SILICONFLOW_API_KEY` 环境变量已配置
- [ ] `DATABASE_URL` 环境变量已配置
- [ ] 后端部署成功（Service Status: Live）
- [ ] 访问 `/docs` 能看到 API 文档
- [ ] 登录接口测试成功

---

## 🌐 下一步：连接前端和后端

后端部署成功后，需要配置前端的环境变量：

1. **访问 Vercel**: https://vercel.com/dashboard
2. **选择前端项目**: `frontend` 或 `ai-trade-platform`
3. **设置环境变量**:
   - **Settings** → **Environment Variables**
   - 修改 `VITE_API_URL` 的值为：
     ```
     https://ai-trade-platform-api.onrender.com
     ```
4. **保存并重新部署**：
   - **Deployments** → 最新部署 → **"Redeploy"**

---

## 🎉 完成！

部署成功后，你可以：

- **访问前端**: `https://frontend-j3gqodj1g-alexfang-s-projects.vercel.app`
- **登录账号**: `admin` / `admin123`
- **测试 AI 功能**: 新增客户 → AI 识别
- **查看后端 API**: `https://ai-trade-platform-api.onrender.com/docs`

---

## 💡 注意事项

1. **Render 免费版会休眠**：
   - 15 分钟无活动后，服务会进入休眠状态
   - 下次访问时需要等待 30-60 秒唤醒
   - 这是免费版的限制

2. **数据库免费版限制**：
   - 1 GB 存储空间
   - 100 个连接数

3. **查看日志**：
   - 在 Render 控制台 → 你的服务 → **"Logs"** 标签页
   - 可以查看后端运行日志和错误

---

## 🆘 需要帮助？

如果遇到问题，请告诉我：
- 错误截图
- Render 日志内容
- 具体的错误信息

我会帮你解决！
