"""
AI 外贸工作平台 - Cloudflare Workers 版本
使用 Cloudflare Workers + D1 (SQLite) 部署
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

app = FastAPI(title="AI 外贸工作平台 API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 数据模型 ───

class LoginRequest(BaseModel):
    username: str
    password: str

class CustomerCreate(BaseModel):
    name: str
    name_en: str = None
    country: str = None
    contact_person: str = None
    email: str = None
    phone: str = None
    address: str = None
    tax_id: str = None
    notes: str = None

# ─── 认证端点 ───

@app.post("/api/auth/login")
async def login(request: Request, body: LoginRequest):
    """登录接口（简化版，实际应连接数据库）"""
    if body.username == "admin" and body.password == "admin123":
        return {
            "access_token": "mock-jwt-token-for-cloudflare",
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="用户名或密码错误")

# ─── 客户管理端点 ───

@app.get("/api/customers")
async def list_customers(request: Request, page: int = 1, page_size: int = 20):
    """获取客户列表（演示数据）"""
    return {
        "total": 1,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": "1",
                "code": "CUS-001",
                "name": "演示客户",
                "name_en": "Demo Customer",
                "country": "中国",
                "contact_person": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "status": "active",
                "created_at": "2024-01-01T00:00:00"
            }
        ]
    }

@app.post("/api/customers")
async def create_customer(request: Request, body: CustomerCreate):
    """创建客户"""
    return {
        "id": "new-id",
        "code": "CUS-002",
        "name": body.name,
        "name_en": body.name_en,
        "country": body.country,
        "contact_person": body.contact_person,
        "email": body.email,
        "phone": body.phone,
        "address": body.address,
        "tax_id": body.tax_id,
        "notes": body.notes,
        "status": "active",
        "created_at": "2024-01-01T00:00:00"
    }

# ─── AI 端点 ───

@app.post("/api/ai/ocr/extract")
async def ai_ocr_extract(request: Request):
    """AI OCR 识别（演示）"""
    return {
        "公司名称": "示例公司",
        "联系人": "李四",
        "邮箱": "lisi@example.com",
        "电话": "13900139000",
        "地址": "上海市浦东新区",
        "税号": "91310000MA1FL8XK5P",
        "国家": "中国"
    }

@app.post("/api/ai/translate")
async def ai_translate(request: Request):
    """AI 翻译（演示）"""
    body = await request.json()
    return {
        "translated": f"[翻译结果] {body.get('text', '')}"
    }

@app.post("/api/ai/hs-recommend")
async def ai_hs_recommend(request: Request):
    """AI HS 编码推荐（演示）"""
    return {
        "hs_code": "090421",
        "chapter": "第9章",
        "confidence": "high",
        "reason": "根据产品名称分类"
    }

# ─── 看板端点 ───

@app.get("/api/dashboard")
async def dashboard():
    """看板数据"""
    return {
        "summary": {
            "total_orders": 10,
            "total_revenue": 50000,
            "pending_shipments": 3,
            "overdue_payments": 1
        },
        "charts": {
            "order_trend": [
                {"month": "2024-01", "count": 5},
                {"month": "2024-02", "count": 8}
            ],
            "revenue_by_month": [
                {"month": "2024-01", "amount": 20000},
                {"month": "2024-02", "amount": 30000}
            ]
        },
        "alerts": []
    }

# ─── 根路径 ───

@app.get("/")
async def root():
    return {
        "name": "AI 外贸工作平台 API",
        "version": "1.0.0",
        "docs": "/docs",
        "deployed_on": "Cloudflare Workers"
    }
