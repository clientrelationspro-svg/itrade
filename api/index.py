from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import jwt
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 简化版用户数据库
USERS = {
    "admin": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "name": "管理员",
        "role": "admin"
    }
}

SECRET_KEY = "ai-trade-platform-secret-2024"

@app.get("/")
def root():
    return {"name": "AI 外贸工作平台 API", "version": "1.0.0", "status": "running on Vercel"}

@app.post("/api/auth/login")
def login(data: dict):
    username = data.get("username")
    password = data.get("password")
    
    if username in USERS:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if USERS[username]["password"] == hashed_password:
            payload = {
                "sub": username,
                "name": USERS[username]["name"],
                "role": USERS[username]["role"],
                "exp": datetime.utcnow() + timedelta(days=7)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "username": username,
                    "name": USERS[username]["name"],
                    "role": USERS[username]["role"]
                }
            }
    
    return {"detail": "用户名或密码错误"}, 401

@app.get("/api/customers")
def get_customers():
    return {"items": [], "total": 0, "page": 1, "pageSize": 20}

@app.get("/api/products")
def get_products():
    return {"items": [], "total": 0, "page": 1, "pageSize": 20}
