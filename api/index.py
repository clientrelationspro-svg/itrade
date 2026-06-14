# Vercel Serverless Function - 后端 API 入口
# 使用 Vercel Python Functions 运行 FastAPI 应用

import sys
import os

# 添加后端目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 安装依赖（Vercel Functions 会自动安装 requirements.txt）

try:
    # 导入 FastAPI 应用
    from app.main import app
    
    # Vercel Functions handler
    def handler(request, response):
        # 将请求转发到 FastAPI 应用
        return app

except Exception as e:
    # 如果导入失败，返回一个简单的错误应用
    from fastapi import FastAPI
    error_app = FastAPI()
    
    @error_app.get("/")
    def root():
        return {
            "error": "Backend import failed",
            "message": str(e),
            "help": "Please check backend dependencies and configuration"
        }
    
    def handler(request, response):
        return error_app
