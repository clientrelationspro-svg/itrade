# AI 外贸工作平台

基于硅基流动 SiliconCloud 开源模型的全栈智能外贸业务管理系统。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vite + Pinia + ECharts |
| 后端 | Python FastAPI + SQLAlchemy + PostgreSQL |
| AI | SiliconCloud API (Qwen2.5 / DeepSeek-V2.5 / BGE / SD3.5) |

## 功能模块

| 模块 | AI 增强功能 |
|------|------------|
| 看板 Dashboard | 收入预测、异常检测 |
| 客户管理 | OCR 名片识别自动建档 |
| 供应商管理 | OCR 资料自动建档 |
| 产品管理 | HS 编码智能推荐 |
| 询价管理 | 多供应商报价对比分析 |
| 合同管理 | OCR 解析 + 风险提示 + 到期提醒 |
| 订单管理 | 智能风险预警 |
| 验货管理 | 报告 OCR + 异常检测 |
| 装运管理 | 提单/发票 OCR + 数据一致性比对 |
| 收付款管理 | 信用评估 + 回款预测 |
| 文档管理 | AI 自动分类 + 全文搜索 |

## 快速开始

### 前置条件
- Docker & Docker Compose
- SiliconFlow API Key ([获取地址](https://siliconflow.cn))

### 启动

```bash
# 1. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 填入你的 SILICONFLOW_API_KEY

# 2. 启动所有服务
docker-compose up -d

# 3. 访问
# 前端: http://localhost:5173
# API文档: http://localhost:8000/docs
# 默认账号: admin / admin123
```

### 本地开发

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 项目结构

```
├── docker-compose.yml
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 主应用
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接
│   │   ├── models.py         # 数据模型 (14个表)
│   │   ├── schemas.py        # Pydantic 验证
│   │   ├── ai_service.py     # SiliconFlow AI 服务封装
│   │   ├── ai_agents.py      # 业务 AI Agent
│   │   └── routers/
│   │       ├── auth.py       # 认证路由
│   │       ├── crud.py       # 通用 CRUD 路由工厂
│   │       └── ai.py         # AI 功能路由
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.js           # Vue 入口
│   │   ├── App.vue
│   │   ├── router/           # 路由配置
│   │   ├── api/              # API 封装
│   │   ├── composables/      # 组合式函数
│   │   ├── layouts/          # 布局组件
│   │   ├── views/            # 页面组件 (12个)
│   │   └── styles/           # 全局样式
│   ├── package.json
│   └── Dockerfile
└── docs/
    └── siliconflow-ai-architecture.md  # AI架构文档
```

## AI 模型成本

| 模型 | 月费用 |
|------|--------|
| Qwen2.5-7B-Instruct | **免费** |
| Qwen2.5-VL-72B-Instruct | ~$5-15 |
| DeepSeek-V2.5 | ~$3-8 |
| BAAI/bge-large | < $1 |
| **合计** | **~$10-25/月** |
