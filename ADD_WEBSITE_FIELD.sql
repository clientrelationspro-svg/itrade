-- 添加 website 字段到 customers 表
ALTER TABLE customers ADD COLUMN IF NOT EXISTS website VARCHAR(200);
