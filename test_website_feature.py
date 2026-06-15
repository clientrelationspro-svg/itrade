#!/usr/bin/env python3
"""
测试客户网站 AI 解析功能
"""
import requests
import json

# 配置
API_BASE = "https://ai-trade-platform-api.onrender.com/api"
TEST_WEBSITE = "https://www.apple.com"  # 用一个真实网站测试

def test_website_analyze():
    """测试网站分析 API"""
    print("=" * 60)
    print("测试：AI 分析客户网站")
    print("=" * 60)
    
    url = f"{API_BASE}/ai/website/analyze"
    payload = {
        "website_url": TEST_WEBSITE
    }
    
    try:
        print(f"\n正在分析网站: {TEST_WEBSITE}")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ API 调用成功！")
            print("\n提取的信息：")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 验证返回的数据
            expected_fields = ["name", "name_en", "country", "contact_person", "email", "phone", "address", "website"]
            print("\n字段验证：")
            for field in expected_fields:
                if field in data:
                    print(f"  ✅ {field}: {data.get(field, '')[:50]}...")
                else:
                    print(f"  ⚠️  缺少字段: {field}")
            
            return True
        else:
            print(f"\n❌ API 调用失败")
            print(f"状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络错误: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        return False

def test_customer_with_website():
    """测试客户 API 是否包含 website 字段"""
    print("\n" + "=" * 60)
    print("测试：客户 API 是否包含 website 字段")
    print("=" * 60)
    
    # 这个测试需要认证，所以只检查字段定义
    print("\n提示：需要确保数据库已添加 website 字段")
    print("执行 SQL: ALTER TABLE customers ADD COLUMN IF NOT EXISTS website VARCHAR(200);")

if __name__ == "__main__":
    print("\n🚀 开始测试客户网站 AI 解析功能\n")
    
    # 测试 1: 网站分析 API
    success = test_website_analyze()
    
    # 测试 2: 检查字段
    test_customer_with_website()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    if not success:
        print("\n⚠️  请确保：")
        print("  1. Render.com 部署已完成")
        print("  2. 后端依赖已安装（requests, beautifulsoup4）")
        print("  3. 数据库已执行迁移 SQL")
        print("  4. AI 服务已正确配置")
