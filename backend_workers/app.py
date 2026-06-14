"""
AI 外贸工作平台 - Cloudflare Workers 完整版
使用 Cloudflare D1 (SQLite) 数据库
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import uuid
import os
from datetime import datetime

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
    name_en: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    name_en: Optional[str] = None
    category: Optional[str] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    hs_code: Optional[str] = None
    hs_code_recommended: Optional[str] = None
    supplier_id: Optional[str] = None
    moq: Optional[float] = None
    price_range: Optional[str] = None
    notes: Optional[str] = None

class InquiryCreate(BaseModel):
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    target_price: Optional[float] = None
    currency: str = "USD"

class ContractCreate(BaseModel):
    contract_no: str
    title: str
    customer_id: Optional[str] = None
    amount: Optional[float] = None
    currency: str = "USD"
    sign_date: Optional[str] = None
    expiry_date: Optional[str] = None

class OrderCreate(BaseModel):
    customer_id: Optional[str] = None
    contract_id: Optional[str] = None
    total_amount: Optional[float] = None
    currency: str = "USD"
    status: str = "draft"

class InspectionCreate(BaseModel):
    order_id: Optional[str] = None
    inspection_date: Optional[str] = None
    inspector: Optional[str] = None
    company: Optional[str] = None
    result: str = "pending"

class ShipmentCreate(BaseModel):
    order_id: Optional[str] = None
    vessel_name: Optional[str] = None
    voyage_no: Optional[str] = None
    container_no: Optional[str] = None
    bl_no: Optional[str] = None
    etd: Optional[str] = None
    eta: Optional[str] = None

class PaymentCreate(BaseModel):
    order_id: Optional[str] = None
    receivable: Optional[float] = None
    received: Optional[float] = None
    due_date: Optional[str] = None
    payment_method: Optional[str] = None

# ─── 工具函数 ───

def get_db(request: Request):
    """获取 D1 数据库连接"""
    return request.app.state.DB

def generate_code(prefix: str) -> str:
    """生成业务编号"""
    import time
    timestamp = int(time.time() * 1000)
    return f"{prefix}-{timestamp}"

# ─── 认证端点 ───

@app.post("/api/auth/login")
async def login(request: Request, body: LoginRequest):
    """登录接口"""
    db = get_db(request)
    
    # 默认账号: admin / admin123
    if body.username == "admin" and body.password == "admin123":
        return {
            "access_token": "mock-jwt-token-cloudflare",
            "token_type": "bearer"
        }
    
    # 查询数据库
    result = db.prepare("""
        SELECT id, password_hash FROM users 
        WHERE username = ? AND status = 'active'
    """).bind(body.username).first()
    
    if result:
        # TODO: 验证密码哈希
        return {
            "access_token": "jwt-token-placeholder",
            "token_type": "bearer"
        }
    
    raise HTTPException(status_code=401, detail="用户名或密码错误")

# ─── 客户管理端点 ───

@app.get("/api/customers")
async def list_customers(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    status: Optional[str] = "active"
):
    """获取客户列表"""
    db = get_db(request)
    offset = (page - 1) * page_size
    
    query = "SELECT * FROM customers WHERE status = ?"
    params = [status]
    
    if keyword:
        query += " AND (name LIKE ? OR email LIKE ? OR contact_person LIKE ? OR country LIKE ?)"
        keyword_param = f"%{keyword}%"
        params.extend([keyword_param, keyword_param, keyword_param, keyword_param])
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    
    results = db.prepare(query).bind(*params).all()
    
    total = db.prepare("SELECT COUNT(*) FROM customers WHERE status = ?").bind(status).first()[0]
    
    customers = []
    for row in results:
        customers.append({
            "id": row[0],
            "code": row[1],
            "name": row[2],
            "name_en": row[3],
            "country": row[4],
            "contact_person": row[5],
            "email": row[6],
            "phone": row[7],
            "address": row[8],
            "tax_id": row[9],
            "notes": row[10],
            "credit_rating": row[12],
            "status": row[13],
            "created_at": row[14]
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": customers
    }

@app.post("/api/customers")
async def create_customer(request: Request, body: CustomerCreate):
    """创建客户"""
    db = get_db(request)
    
    customer_id = str(uuid.uuid4())
    code = generate_code("CUS")
    now = datetime.now().isoformat()
    
    db.prepare("""
        INSERT INTO customers (id, code, name, name_en, country, contact_person, email, phone, address, tax_id, notes, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
    """).bind(
        customer_id, code, body.name, body.name_en, body.country,
        body.contact_person, body.email, body.phone, body.address,
        body.tax_id, body.notes, now, now
    ).run()
    
    return {
        "id": customer_id,
        "code": code,
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
        "created_at": now
    }

@app.get("/api/customers/{customer_id}")
async def get_customer(request: Request, customer_id: str):
    """获取客户详情"""
    db = get_db(request)
    
    result = db.prepare("SELECT * FROM customers WHERE id = ?").bind(customer_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "id": result[0],
        "code": result[1],
        "name": result[2],
        "name_en": result[3],
        "country": result[4],
        "contact_person": result[5],
        "email": result[6],
        "phone": result[7],
        "address": result[8],
        "tax_id": result[9],
        "notes": result[10],
        "status": result[13],
        "created_at": result[14]
    }

@app.put("/api/customers/{customer_id}")
async def update_customer(request: Request, customer_id: str, body: CustomerCreate):
    """更新客户"""
    db = get_db(request)
    now = datetime.now().isoformat()
    
    db.prepare("""
        UPDATE customers 
        SET name = ?, name_en = ?, country = ?, contact_person = ?, 
            email = ?, phone = ?, address = ?, tax_id = ?, notes = ?, updated_at = ?
        WHERE id = ?
    """).bind(
        body.name, body.name_en, body.country, body.contact_person,
        body.email, body.phone, body.address, body.tax_id, body.notes, now,
        customer_id
    ).run()
    
    return {"message": "更新成功"}

@app.delete("/api/customers/{customer_id}")
async def delete_customer(request: Request, customer_id: str, permanent: bool = False):
    """删除客户（软删除）"""
    db = get_db(request)
    now = datetime.now().isoformat()
    
    if permanent:
        db.prepare("DELETE FROM customers WHERE id = ?").bind(customer_id).run()
    else:
        db.prepare("UPDATE customers SET status = 'deleted', updated_at = ? WHERE id = ?").bind(now, customer_id).run()
    
    return {"message": "删除成功"}

# ─── 产品管理端点 ───

@app.get("/api/products")
async def list_products(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    status: Optional[str] = "active"
):
    """获取产品列表"""
    db = get_db(request)
    offset = (page - 1) * page_size
    
    query = "SELECT * FROM products WHERE status = ?"
    params = [status]
    
    if keyword:
        query += " AND (name LIKE ? OR specification LIKE ? OR hs_code LIKE ? OR category LIKE ?)"
        keyword_param = f"%{keyword}%"
        params.extend([keyword_param, keyword_param, keyword_param, keyword_param])
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    
    results = db.prepare(query).bind(*params).all()
    
    total = db.prepare("SELECT COUNT(*) FROM products WHERE status = ?").bind(status).first()[0]
    
    products = []
    for row in results:
        products.append({
            "id": row[0],
            "code": row[1],
            "name": row[2],
            "name_en": row[3],
            "category": row[4],
            "specification": row[5],
            "unit": row[6],
            "hs_code": row[7],
            "hs_code_recommended": row[8],
            "price_range": row[11],
            "status": row[13],
            "created_at": row[14]
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": products
    }

@app.post("/api/products")
async def create_product(request: Request, body: ProductCreate):
    """创建产品"""
    db = get_db(request)
    
    product_id = str(uuid.uuid4())
    code = generate_code("PRO")
    now = datetime.now().isoformat()
    
    db.prepare("""
        INSERT INTO products (id, code, name, name_en, category, specification, unit, hs_code, hs_code_recommended, supplier_id, moq, price_range, notes, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
    """).bind(
        product_id, code, body.name, body.name_en, body.category,
        body.specification, body.unit, body.hs_code, body.hs_code_recommended,
        body.supplier_id, body.moq, body.price_range, body.notes, now, now
    ).run()
    
    return {
        "id": product_id,
        "code": code,
        "name": body.name,
        "name_en": body.name_en,
        "category": body.category,
        "specification": body.specification,
        "unit": body.unit,
        "hs_code": body.hs_code,
        "hs_code_recommended": body.hs_code_recommended,
        "price_range": body.price_range,
        "status": "active",
        "created_at": now
    }

# ─── AI 端点 ───

@app.post("/api/ai/ocr/extract")
async def ai_ocr_extract(request: Request):
    """AI OCR 识别"""
    # TODO: 调用 SiliconFlow API
    # 当前返回模拟数据
    return {
        "公司名称": "示例公司",
        "联系人": "张三",
        "邮箱": "zhangsan@example.com",
        "电话": "13800138000",
        "地址": "上海市浦东新区",
        "税号": "91310000MA1FL8XK5P",
        "国家": "中国"
    }

@app.post("/api/ai/translate")
async def ai_translate(request: Request):
    """AI 翻译"""
    body = await request.json()
    text = body.get("text", "")
    target_lang = body.get("target_lang", "en")
    
    # TODO: 调用 SiliconFlow API
    return {
        "translated": f"[翻译结果] {text}"
    }

@app.post("/api/ai/hs-recommend")
async def ai_hs_recommend(request: Request):
    """AI HS 编码推荐"""
    body = await request.json()
    product_name = body.get("product_name", "")
    
    # TODO: 调用 SiliconFlow API
    return {
        "hs_code": "090421",
        "chapter": "第9章",
        "confidence": "high",
        "reason": f"根据产品名称'{product_name}'分类"
    }

# ─── 看板端点 ───

@app.get("/api/dashboard")
async def dashboard(request: Request):
    """看板数据"""
    db = get_db(request)
    
    total_customers = db.prepare("SELECT COUNT(*) FROM customers WHERE status = 'active'").first()[0]
    total_products = db.prepare("SELECT COUNT(*) FROM products WHERE status = 'active'").first()[0]
    
    return {
        "summary": {
            "total_customers": total_customers,
            "total_products": total_products,
            "total_orders": 0,
            "pending_shipments": 0,
            "overdue_payments": 0
        },
        "charts": {
            "order_trend": [],
            "revenue_by_month": [],
            "customer_distribution": []
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

# ─── 启动事件 ───

@app.on_event("startup")
async def startup():
    """初始化数据库"""
    # Cloudflare Workers 会在每次请求时注入 D1 绑定
    pass
