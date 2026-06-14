# Vercel Serverless Function - 认证 API

from http.server import BaseHTTPRequestHandler
import json
import hashlib
import jwt
import os
from datetime import datetime, timedelta

# 简化版用户数据库（实际应该使用真实数据库）
USERS = {
    "admin": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "name": "管理员",
        "role": "admin"
    }
}

SECRET_KEY = os.getenv("JWT_SECRET", "ai-trade-platform-secret-key")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            username = data.get("username")
            password = data.get("password")
            
            # 验证用户
            if username in USERS:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if USERS[username]["password"] == hashed_password:
                    # 生成 JWT token
                    payload = {
                        "sub": username,
                        "name": USERS[username]["name"],
                        "role": USERS[username]["role"],
                        "exp": datetime.utcnow() + timedelta(days=7)
                    }
                    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "access_token": token,
                        "token_type": "bearer",
                        "user": {
                            "username": username,
                            "name": USERS[username]["name"],
                            "role": USERS[username]["role"]
                        }
                    }).encode())
                    return
            
            # 认证失败
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "detail": "用户名或密码错误"
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "detail": str(e)
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
