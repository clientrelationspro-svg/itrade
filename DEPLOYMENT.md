# 部署指南

## 方案选择

### 方案 1：前后端分离部署（推荐）
- **前端**：Vercel (免费)
- **后端**：Render (免费额度) 或 Railway ($5/月)
- **数据库**：PostgreSQL (Render 免费额度 或 Supabase 免费)

### 方案 2：Docker 部署
- 使用 `docker-compose.yml` 在 VPS 上部署
- 适合有服务器的场景

---

## 方案 1：前后端分离部署

### 1. 前端部署 (Vercel)

#### 步骤：
1. 访问 [vercel.com](https://vercel.com)
2. 导入 GitHub 仓库：`clientrelationspro-svg/itrade`
3. 配置：
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variables**:
     ```
     VITE_API_URL=https://your-backend.onrender.com
     ```

4. 点击 **Deploy**

#### 自定义域名（可选）：
- 在 Vercel 项目设置中添加域名
- 修改 `frontend/vite.config.js` 的 API 代理配置

---

### 2. 后端部署 (Render)

#### 步骤：
1. 访问 [render.com](https://render.com)
2. 创建 **Web Service**：
   - **Repository**: `clientrelationspro-svg/itrade`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**:
   ```
   SILICONFLOW_API_KEY=sk-tkmklxuruwxdqbuqzpcqucbzbcjwomvxuzcththgmwjtpxdz
   DATABASE_URL=<PostgreSQL 连接字符串>
   AI_MODEL_VISION=Qwen/Qwen3-VL-8B-Instruct
   ```

4. 创建 **PostgreSQL** 数据库（Render 免费额度）：
   - 在 Render 控制台创建数据库
   - 复制 **Internal Database URL** 到 Web Service 的环境变量

5. 点击 **Create Web Service**

---

### 3. 数据库初始化

部署后，访问后端 API 文档：
```
https://your-backend.onrender.com/docs
```

手动触发数据库初始化（第一次访问会自动创建表）。

---

## 方案 2：Docker 部署（VPS）

### 1. 准备服务器
- 推荐：DigitalOcean / Vultr / Linode
- 配置：1 CPU, 1GB RAM, 25GB SSD ($5-10/月)

### 2. 安装 Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 3. 部署
```bash
# 1. 克隆仓库
git clone https://github.com/clientrelationspro-svg/itrade.git
cd itrade

# 2. 配置环境变量
cp backend/.env.example backend/.env
nano backend/.env  # 填入你的 API Key

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

访问：
- 前端：`http://your-server-ip:5173`
- 后端 API：`http://your-server-ip:8000`

---

## 环境变量清单

### 后端 (.env)
```bash
# 必需
SILICONFLOW_API_KEY=<你的 API Key>

# 可选（有默认值）
AI_MODEL_VISION=Qwen/Qwen3-VL-8B-Instruct
DATABASE_URL=<PostgreSQL 连接字符串>
```

### 前端 (.env.production)
```bash
VITE_API_URL=https://your-backend.onrender.com
```

---

## 常见问题

### Q1: 前端无法连接后端？
**A**: 检查 CORS 配置。在 `backend/app/main.py` 中添加：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q2: SiliconFlow API 调用失败？
**A**: 
1. 检查 API Key 是否正确
2. 确认模型名称（可在 [siliconflow.cn](https://siliconflow.cn) 查看可用模型）
3. 查看后端日志：`render.com` → 你的服务 → Logs

### Q3: 数据库迁移？
**A**: 当前使用 SQLAlchemy 自动创建表。生产环境建议使用 Alembic：
```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "init"
alembic upgrade head
```

---

## 成本估算

| 服务 | 免费方案 | 付费方案 |
|------|----------|----------|
| **前端 (Vercel)** | ✅ 免费（带宽 100GB/月） | $20/月（团队版） |
| **后端 (Render)** | ✅ 免费（750 小时/月，需休眠） | $7/月（不休眠） |
| **数据库 (Render PostgreSQL)** | ✅ 免费（1GB 存储） | $7/月（10GB） |
| **AI API (SiliconFlow)** | - | ~$10-25/月 |
| **合计** | **$0/月**（有限制） | **$24-39/月** |

---

## 下一步

1. ✅ 前端部署到 Vercel
2. ✅ 后端部署到 Render
3. ✅ 配置自定义域名（可选）
4. ✅ 设置 CI/CD 自动部署（Vercel 和 Render 自动支持）
5. ✅ 配置监控和日志（如 Sentry）

---

## 快速部署检查清单

- [ ] SiliconFlow API Key 已配置
- [ ] 后端数据库已创建并连接
- [ ] 前端 API URL 已指向后端
- [ ] CORS 已配置允许前端域名
- [ ] 后端健康检查和日志正常
- [ ] 测试 AI 功能（OCR、翻译等）
