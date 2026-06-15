# 修复询价保存问题 - 完整指南

## 问题描述
新增询价时，如果不填目标价（target_price）或数量（quantity），保存失败（500错误）。

## 问题根源
数据库表 `inquiries` 的 `target_price` 和 `quantity` 字段设置了 `NOT NULL` 约束，导致无法插入 NULL 值。

## 解决方案

### 方案1：自动迁移（推荐）
代码已推送，Render 会自动部署后端。部署完成后，后端会在启动时自动执行数据库迁移。

**等待时间**：约 2-3 分钟

**验证步骤**：
1. 清除浏览器缓存（Cmd+Shift+R）
2. 重新登录
3. 新增询价，不填目标价
4. 如果成功保存，说明自动迁移成功

### 方案2：手动执行 SQL（如果方案1失败）
如果自动迁移失败，需要手动连接 Render 的 PostgreSQL 数据库执行 SQL。

#### 步骤1：获取数据库连接信息
1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 找到你的 PostgreSQL 数据库服务
3. 复制 "Internal Database URL" 或 "External Database URL"

#### 步骤2：执行 SQL
使用 psql 或任何 PostgreSQL 客户端连接数据库，执行以下 SQL：

```sql
-- 修改表结构：允许 target_price 和 quantity 为空
ALTER TABLE inquiries 
ALTER COLUMN quantity DROP NOT NULL,
ALTER COLUMN target_price DROP NOT NULL;

-- 验证修改结果
SELECT column_name, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'inquiries' 
AND column_name IN ('quantity', 'target_price');
```

期望结果：
```
 column_name   | is_nullable
---------------+-------------
 quantity      | YES
 target_price  | YES
```

### 方案3：前端临时规避（不推荐）
如果以上方案都无法执行，可以强制前端填写目标价（添加表单验证）。

但这不是根本解决方案，因为数据库中这些字段应该允许为空。

## 代码修改说明

### 1. 后端修改
- `backend/app/models.py`：为 `Inquiry.quantity` 和 `Inquiry.target_price` 添加 `nullable=True`
- `backend/app/main.py`：在 `lifespan` 函数中添加数据库迁移逻辑

### 2. 前端修改
- `frontend/src/views/InquiryList.vue`：在 `save` 函数中清理空值，避免发送 `null` 到后端

## 测试步骤

1. **测试不填目标价**：
   - 新增询价
   - 不填写目标价
   - 点击保存
   - 期望：成功保存

2. **测试填写目标价**：
   - 新增询价
   - 填写目标价（如 100.5）
   - 点击保存
   - 期望：成功保存

3. **测试修改询价**：
   - 编辑已有询价
   - 清空目标价
   - 点击保存
   - 期望：成功保存

## 常见问题

### Q1: 自动迁移失败后怎么办？
A: 按照"方案2"手动执行 SQL。

### Q2: 如何确认数据库迁移是否成功？
A: 执行以下 SQL 验证：
```sql
SELECT column_name, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'inquiries' 
AND column_name IN ('quantity', 'target_price');
```

### Q3: 修改后前端还需要清理空值吗？
A: 需要。虽然数据库已经允许 NULL，但前端清理空值是一个好习惯，可以避免不必要的错误。

## 联系人
如果有任何问题，请联系开发者。
