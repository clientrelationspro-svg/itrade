#!/usr/bin/env python3
"""
数据库迁移脚本：修改 inquiries 表允许 target_price 和 quantity 为 NULL
"""
import asyncpg
import os

# 从环境变量或配置中获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ai_trade")

async def migrate():
    """执行数据库迁移"""
    # 解析数据库URL
    if "postgresql://" in DATABASE_URL:
        url = DATABASE_URL.replace("postgresql://", "")
    elif "postgresql+asyncpg://" in DATABASE_URL:
        url = DATABASE_URL.replace("postgresql+asyncpg://", "")
    else:
        print(f"不支持的数据库URL: {DATABASE_URL}")
        return
    
    # 解析用户名、密码、主机、端口、数据库名
    try:
        user_pass, host_db = url.split("@")
        user, password = user_pass.split(":")
        host_port, database = host_db.split("/")
        host = host_port.split(":")[0]
        port = int(host_port.split(":")[1]) if ":" in host_port else 5432
    except:
        print(f"无法解析数据库URL: {url}")
        return
    
    print(f"连接到数据库: {host}:{port}/{database}")
    
    try:
        # 连接数据库
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        # 执行迁移
        print("执行迁移: ALTER TABLE inquiries ...")
        try:
            await conn.execute("""
                ALTER TABLE inquiries 
                ALTER COLUMN quantity DROP NOT NULL,
                ALTER COLUMN target_price DROP NOT NULL
            """)
            print("✓ 迁移成功：quantity 和 target_price 已设置为可空")
        except Exception as e:
            if "already" in str(e).lower() or "does not exist" in str(e).lower():
                print(f"ℹ 跳过（可能已完成）: {e}")
            else:
                print(f"✗ 迁移失败: {e}")
                raise
        
        # 验证迁移
        print("\n验证迁移结果...")
        columns = await conn.fetch("""
            SELECT column_name, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'inquiries' 
            AND column_name IN ('quantity', 'target_price')
        """)
        
        for col in columns:
            nullable = "可空" if col['is_nullable'] == 'YES' else "不可空"
            print(f"  {col['column_name']}: {nullable}")
        
        await conn.close()
        print("\n✓ 迁移完成！")
        
    except Exception as e:
        print(f"\n✗ 数据库连接失败: {e}")
        print("\n请手动执行以下SQL：")
        print("""
ALTER TABLE inquiries 
ALTER COLUMN quantity DROP NOT NULL,
ALTER COLUMN target_price DROP NOT NULL;
        """)

if __name__ == "__main__":
    import asyncio
    asyncio.run(migrate())
