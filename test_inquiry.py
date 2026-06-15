#!/usr/bin/env python3
"""
测试脚本：验证询价功能（不填目标价）
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_inquiry_without_target_price():
    """测试不填目标价创建询价"""
    print("=== 测试1: 不填目标价创建询价 ===")
    
    # 先登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✓ 登录成功")
            
            # 创建询价（不填目标价）
            headers = {"Authorization": f"Bearer {token}"}
            inquiry_data = {
                "customer_id": "test-customer-id",
                "product_id": "test-product-id",
                "quantity": None,
                "target_price": None,
                "currency": "USD"
            }
            
            response = requests.post(f"{BASE_URL}/inquiries", json=inquiry_data, headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            
            if response.status_code == 200:
                print("✓ 测试通过：不填目标价成功创建询价")
                return True
            else:
                print("✗ 测试失败")
                return False
        else:
            print(f"✗ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 测试异常: {str(e)}")
        return False

def test_inquiry_with_target_price():
    """测试填写目标价创建询价"""
    print("\n=== 测试2: 填写目标价创建询价 ===")
    
    try:
        # 先登录获取token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            
            # 创建询价（填写目标价）
            headers = {"Authorization": f"Bearer {token}"}
            inquiry_data = {
                "customer_id": "test-customer-id",
                "product_id": "test-product-id",
                "quantity": 100,
                "target_price": 50.5,
                "currency": "USD"
            }
            
            response = requests.post(f"{BASE_URL}/inquiries", json=inquiry_data, headers=headers)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            
            if response.status_code == 200:
                print("✓ 测试通过：填写目标价成功创建询价")
                return True
            else:
                print("✗ 测试失败")
                return False
        else:
            print(f"✗ 登录失败: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试询价功能...\n")
    
    # 注意：需要先启动后端服务
    print("请确保后端服务已启动 (cd backend && python3 -m uvicorn app.main:app --reload)")
    print("按Enter键继续...")
    input()
    
    result1 = test_inquiry_without_target_price()
    result2 = test_inquiry_with_target_price()
    
    print("\n" + "="*50)
    if result1 and result2:
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败，请检查后端日志")
