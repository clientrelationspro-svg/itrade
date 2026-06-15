-- 修复询价表结构：允许 target_price 和 quantity 为空
-- 在 Render 的 PostgreSQL 数据库执行此 SQL

-- 方案1：使用 ALTER TABLE（推荐）
ALTER TABLE inquiries 
ALTER COLUMN quantity DROP NOT NULL,
ALTER COLUMN target_price DROP NOT NULL;

-- 验证修改结果
SELECT column_name, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'inquiries' 
AND column_name IN ('quantity', 'target_price');

-- 期望结果：
-- column_name   | is_nullable
-- --------------|-------------
-- quantity      | YES
-- target_price  | YES
