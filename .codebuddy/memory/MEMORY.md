# Project Memory - AI 外贸工作平台

## 项目概述
AI 外贸工作平台，基于硅基流动 SiliconCloud 平台的开源模型服务构建。

## 技术架构
- 全部 AI 功能通过 SiliconCloud RESTful API 调用，不使用商业模型
- 模型选型文档位于: `docs/siliconflow-ai-architecture.md`

## 核心模型
| 能力 | 模型 |
|------|------|
| 日常文本生成 | Qwen/Qwen2.5-7B-Instruct (免费) |
| 复杂任务 | deepseek-ai/DeepSeek-V2.5 |
| 视觉识别 OCR | Qwen/Qwen2.5-VL-72B-Instruct |
| 中文向量嵌入 | BAAI/bge-large-zh-v1.5 |
| 英文向量嵌入 | BAAI/bge-large-en-v1.5 |
| 图片生成 | stabilityai/stable-diffusion-3.5-large |

## 技术栈
- 前端: Vue 3 + Element Plus + Vite + Pinia + ECharts
- 后端: Python FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL + pgvector
- AI: SiliconCloud API 统一封装 (app/ai_service.py)，业务 Agent (app/ai_agents.py)
- 部署: Docker Compose (PG16 + Redis + Backend + Frontend)

## 项目结构
- `backend/app/main.py` - FastAPI 入口，注册所有路由
- `backend/app/models.py` - 14 个数据模型 (User/Customer/Supplier/Product/Inquiry/Contract/Order/OrderItem/Inspection/Shipment/Payment/Document/OperationLog/SystemSetting)
- `backend/app/routers/crud.py` - 通用 CRUD 路由工厂，支持搜索/分页/软删除/批量操作
- `backend/app/routers/ai.py` - 15+ AI 端点 (OCR/翻译/HS推荐/合同解析/报价对比/风险预警/信用评估/自然语言搜索/文档分类等)
- `frontend/src/composables/useCrud.js` - 通用 CRUD 组合式函数
- `frontend/src/views/` - 12 个页面组件，每个包含标准列表页 + 编辑弹窗 + AI 智能面板

## 项目约定
- 文档存放于 `docs/` 目录
- 配置文档使用中英双语
- 所有删除操作默认为软删除 (status='deleted')
- AI 识别结果采用"人在环中"模式，用户确认后写入数据库
- 前端代理 `/api` → `localhost:8000`，`/uploads` → `localhost:8000`
