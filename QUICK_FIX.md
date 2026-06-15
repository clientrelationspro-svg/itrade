# 快速修复询价保存问题

## 问题
新增询价时，不填目标价无法保存（500错误）。

## 根本原因
数据库表 `inquiries` 的 `target_price` 和 `quantity` 字段设置了 `NOT NULL` 约束。

## 快速修复方案

### 方案A：调用手动迁移API（推荐）

等待Render部署完成后（约2-3分钟），执行以下命令：

```bash
# 1. 获取 token
TOKEN=$(curl -s -X POST https://ai-trade-platform-api.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# 2. 调用手动迁移API
curl -X POST https://ai-trade-platform-api.onrender.com/api/admin/migrate-inquiries \
  -H "Authorization: Bearer $TOKEN"

# 期望响应：
# {"status":"success","message":"迁移成功：inquiries 表的 quantity 和 target_price 列已设置为可空"}
```

### 方案B：在Render Shell中执行Python脚本

如果方案A失败，可以在Render的Shell中执行以下Python脚本：

```python
import asyncpg
import os

async def migrate():
    # 从环境变量获取数据库URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not found")
        return
    
    # 连接数据库
    conn = await asyncpg.connect(db_url)
    
    # 执行迁移
    try:
        await conn.execute("""
            ALTER TABLE inquiries 
            ALTER COLUMN quantity DROP NOT NULL,
            ALTER COLUMN target_price DROP NOT NULL
        """)
        print("✓ 迁移成功")
    except Exception as e:
        print(f"✗ 迁移失败: {e}")
    
    await conn.close()

import asyncio
asyncio.run(migrate())
```

### 方案C：使用pgAdmin或psql手动执行SQL

1. 获取Render PostgreSQL连接信息
2. 使用任何PostgreSQL客户端连接
3. 执行以下SQL：

```sql
ALTER TABLE inquiries 
ALTER COLUMN quantity DROP NOT NULL,
ALTER COLUMN target_price DROP NOT NULL;
```

## 验证修复是否成功

执行以下API测试：

```bash
# 1. 登录
TOKEN=$(curl -s -X POST https://ai-trade-platform-api.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. 测试创建询价（不填目标价）
curl -X POST https://ai-trade-platform-api.onrender.com/api/inquiries \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"customer_id":"test","product_id":"test","currency":"USD"}'

# 期望响应：201 Created + 询价数据
# 如果还是500错误，说明迁移没有成功
```

## 联系开发者
如果以上方案都无法解决，请联系开发者进行深度调试。
