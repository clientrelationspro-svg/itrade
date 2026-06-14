# 🚀 一键部署指南

## 📋 前置准备

### 1. 注册账号
- ✅ **GitHub**: https://github.com (已有仓库)
- ✅ **Vercel**: https://vercel.com (用 GitHub 登录)
- ✅ **Render**: https://render.com (用 GitHub 登录)

### 2. 准备 API Key
- ✅ **SiliconFlow API Key**: `sk-tkmklxuruwxdqbuqzpcqucbzbcjwomvxuzcththgmwjtpxdz`

---

## 🌐 步骤 1：部署前端到 Vercel（5 分钟）

### 方法 A：网页界面（推荐）

1. **访问 Vercel**: https://vercel.com/dashboard
2. **导入项目**: 点击 **"Add New..."** → **"Project"**
3. **选择仓库**: `clientrelationspro-svg/itrade`
4. **配置项目**:
   - **Project Name**: `ai-trade-platform`
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. **Environment Variables** (展开 "Environment Variables"):
   ```
   Name: VITE_API_URL
   Value: https://ai-trade-platform-api.onrender.com
   ```
   (这个 URL 后面部署后端时会获得，先填个占位符)
6. **点击 "Deploy"**

**⏳ 等待 2-3 分钟...**

**✅ 部署成功后获得**:
- **前端 URL**: `https://ai-trade-platform.vercel.app`
- **记录这个 URL**，后面配置后端 CORS 需要

---

### 方法 B：使用 Vercel CLI（高级）

```bash
# 1. 登录 Vercel
vercel login

# 2. 部署前端
cd frontend
vercel --prod

# 按提示操作...
```

---

## 🔧 步骤 2：部署后端到 Render（10 分钟）

### 1. 创建 PostgreSQL 数据库

1. **访问 Render**: https://dashboard.render.com
2. **创建数据库**: 点击 **"New +"** → **"PostgreSQL"**
3. **配置数据库**:
   - **Name**: `ai-trade-db`
   - **Database**: `ai_trade`
   - **User**: `ai_trade_user`
   - **Plan**: `Free` (免费额度)
4. **点击 "Create Database"**

**⏳ 等待数据库创建...**

**✅ 创建成功后**:
- 复制 **"Internal Database URL"** (格式: `postgresql://user:pass@host:5432/db`)
- **记录这个 URL**，后面配置后端需要

---

### 2. 创建 Web Service（后端）

1. **创建服务**: 点击 **"New +"** → **"Web Service"**
2. **连接仓库**: 选择 `clientrelationspro-svg/itrade`
3. **配置服务**:
   - **Name**: `ai-trade-platform-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: 
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: `Free` (750 小时/月，会休眠)
4. **Environment Variables** (展开 "Advanced" → "Add Environment Variable"):
   ```
   Name: SILICONFLOW_API_KEY
   Value: sk-tkmklxuruwxdqbuqzpcqucbzbcjwomvxuzcththgmwjtpxdz
   ```
   ```
   Name: DATABASE_URL
   Value: <粘贴刚才复制的 Internal Database URL>
   ```
   ```
   Name: AI_MODEL_VISION
   Value: Qwen/Qwen3-VL-8B-Instruct
   ```
5. **点击 "Create Web Service"**

**⏳ 等待 5-10 分钟（首次部署较慢）...**

**✅ 部署成功后获得**:
- **后端 URL**: `https://ai-trade-platform-api.onrender.com`
- **记录这个 URL**

---

## 🔗 步骤 3：连接前端和后端

### 1. 更新前端环境变量

1. **访问 Vercel**: https://vercel.com/dashboard
2. **选择项目**: `ai-trade-platform`
3. **设置**: 点击 **"Settings"** → **"Environment Variables"**
4. **修改 `VITE_API_URL`**:
   ```
   Value: https://ai-trade-platform-api.onrender.com
   ```
5. **保存** → **"Redeploy"**

---

### 2. 配置后端 CORS（允许前端访问）

**方法 A：通过 Render 环境变量（推荐）**

1. **访问 Render**: https://dashboard.render.com
2. **选择后端服务**: `ai-trade-platform-api`
3. **Environment Variables**: 点击 **"Environment"** → **"Add Environment Variable"**
4. **添加变量**:
   ```
   Name: CORS_ORIGINS
   Value: https://ai-trade-platform.vercel.app
   ```
5. **保存** → **"Manual Deploy"** → **"Deploy latest commit"**

**方法 B：修改代码（更灵活）**

在 `backend/app/main.py` 中添加：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-trade-platform.vercel.app",  # 你的前端 URL
        "http://localhost:5173",  # 本地开发
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

然后提交并推送：
```bash
git add backend/app/main.py
git commit -m "配置 CORS"
git push
```

Render 会自动重新部署。

---

## ✅ 步骤 4：测试部署

### 1. 访问前端
打开浏览器，访问：
```
https://ai-trade-platform.vercel.app
```

### 2. 测试登录
- **默认账号**: `admin` / `admin123`
- （如果登录失败，检查后端日志）

### 3. 测试 AI 功能
- 进入 **客户管理** → **新增客户**
- 点击 **"AI 智能识别填充"**
- 上传名片图片
- 检查是否能正常识别

### 4. 检查后端健康状态
访问：
```
https://ai-trade-platform-api.onrender.com/docs
```

应该能看到 FastAPI 的 Swagger 文档。

---

## 🐛 常见问题

### Q1: 前端无法连接后端？
**检查**:
1. CORS 配置是否正确
2. `VITE_API_URL` 环境变量是否正确
3. 后端服务是否正在运行（Render 免费版会休眠）

**解决**:
- 访问后端 URL 唤醒服务
- 检查 Render 日志

---

### Q2: AI 功能不可用？
**检查**:
1. `SILICONFLOW_API_KEY` 环境变量是否正确
2. 后端日志是否有 API 调用错误
3. SiliconFlow 账户余额是否充足

**解决**:
- 访问 https://siliconflow.cn 检查 API Key 和余额
- 查看后端日志：`render.com` → 你的服务 → **"Logs"**

---

### Q3: 数据库迁移？
当前使用 SQLAlchemy 自动创建表。如果修改了模型，需要手动处理：

**本地开发**:
```bash
cd backend
rm ai_trade.db  # 删除旧数据库
python -m uvicorn app.main:app  # 自动创建新表
```

**生产环境**（推荐用 Alembic）:
```bash
pip install alembic
alembic init migrations
# 配置 alembic.ini 和 migrations/env.py
alembic revision --autogenerate -m "init"
alembic upgrade head
```

---

## 📊 部署检查清单

- [ ] 前端已部署到 Vercel
- [ ] 后端已部署到 Render
- [ ] PostgreSQL 数据库已创建
- [ ] `SILICONFLOW_API_KEY` 已配置
- [ ] `DATABASE_URL` 已配置
- [ ] `VITE_API_URL` 已配置（指向后端）
- [ ] CORS 已配置（允许前端域名）
- [ ] 测试登录功能
- [ ] 测试 AI 识别功能
- [ ] 检查后端日志无错误

---

## 🎉 完成！

部署成功后，你将获得：

**前端**: `https://ai-trade-platform.vercel.app`
- ✅ 全球 CDN 加速
- ✅ 自动 HTTPS
- ✅ 每次 Git push 自动部署

**后端**: `https://ai-trade-platform-api.onrender.com`
- ✅ 免费托管（750 小时/月）
- ✅ 自动部署
- ⚠️ 免费版会休眠（15 分钟无活动）

**成本**: 
- ✅ 托管费用：**$0/月**（使用免费额度）
- 💰 AI API 费用：**~$10-25/月**

---

## 📞 需要帮助？

1. **Vercel 文档**: https://vercel.com/docs
2. **Render 文档**: https://render.com/docs
3. **项目 Issues**: https://github.com/clientrelationspro-svg/itrade/issues
4. **SiliconFlow 文档**: https://siliconflow.cn/docs

---

## 🚀 快速部署（如果你信任我）

运行以下命令（需要已登录 Vercel CLI）：

```bash
cd /Users/mima0000/CodeBuddy/ai外贸工作平台
bash deploy.sh
```

然后根据提示操作...

---

**祝你部署顺利！** 🎊
