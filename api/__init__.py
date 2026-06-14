# Vercel Functions - 后端 API
# 使用 Vercel Python Functions 运行 FastAPI 应用

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建简化版 FastAPI 应用
app = FastAPI(title="AI 外贸工作平台 API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "AI 外贸工作平台 API",
        "version": "1.0.0",
        "status": "running on Vercel Functions"
    }

@app.get("/api/health")
def health():
    return {"status": "healthy"}

# 认证 API
@app.post("/api/auth/login")
def login(username: str, password: str):
    # 简化版登录（实际应该连接数据库）
    if username == "admin" and password == "admin123":
        return {
            "access_token": "demo-token",
            "token_type": "bearer",
            "user": {
                "username": "admin",
                "name": "管理员",
                "role": "admin"
            }
        }
    return {"error": "用户名或密码错误"}

# 客户 API（简化版）
@app.get("/api/customers")
def get_customers():
    return {
        "items": [],
        "total": 0,
        "page": 1,
        "pageSize": 20
    }

@app.get("/api/products")
def get_products():
    return {
        "items": [],
        "total": 0,
        "page": 1,
        "pageSize": 20
    }
