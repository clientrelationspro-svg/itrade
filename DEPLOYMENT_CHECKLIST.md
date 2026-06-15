# 客户网站 AI 解析功能 - 部署检查清单

## 🔍 排查步骤

### 1. 检查 Render.com 部署状态

1. 登录 [Render.com](https://dashboard.render.com)
2. 找到你的后端服务（通常名为 `ai-trade-platform-api` 或类似）
3. 查看部署状态：
   - ✅ **Live** - 部署成功
   - ⚠️ **Build Failed** - 构建失败，点击查看日志
   - ⏳ **Building** - 正在构建中，请等待

### 2. 查看构建日志

如果部署失败，查看构建日志中的错误信息：

**常见错误：**
- `ModuleNotFoundError: No module named 'requests'` - 依赖未安装
- `ModuleNotFoundError: No module named 'bs4'` - beautifulsoup4 未安装
- 语法错误 - 检查代码

**解决方法：**
确保 `backend/requirements.txt` 包含所有依赖：
```
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

### 3. 测试 API 端点

部署成功后，测试 API 是否可访问：

```bash
# 测试网站分析 API
curl -X POST "https://ai-trade-platform-api.onrender.com/api/ai/website/analyze" \
  -H "Content-Type: application/json" \
  -d '{"website_url": "https://example.com"}'
```

**预期结果：**
- ✅ 返回 JSON 数据（包含 name, email 等字段）
- ❌ `{"detail":"Not Found"}` - 路由未注册或部署未成功
- ❌ `{"detail":"Internal Server Error"}` - 服务器错误，查看日志

### 4. 执行数据库迁移

**必须执行！** 否则客户数据无法保存网站字段。

连接到你的数据库，执行：
```sql
ALTER TABLE customers ADD COLUMN IF NOT EXISTS website VARCHAR(200);
```

**如果使用 Render.com PostgreSQL：**
1. 在 Render.com 控制台点击你的 PostgreSQL 实例
2. 点击 "Connect" 标签
3. 使用提供的命令连接数据库
4. 执行上面的 SQL

### 5. 清除浏览器缓存

前端更新后，需要清除浏览器缓存：

- **Chrome/Edge:** `Ctrl+Shift+R` (Windows) 或 `Cmd+Shift+R` (Mac)
- **Firefox:** `Ctrl+F5` (Windows) 或 `Cmd+Shift+R` (Mac)

或者：
1. 按 `F12` 打开开发者工具
2. 右键点击"刷新"按钮
3. 选择"清空缓存并硬性重新加载"

### 6. 验证前端界面

清除缓存后，进入客户管理页面：

1. 点击"新增客户"或编辑现有客户
2. 在表单中查找"客户网站"字段
3. 确认旁边有"AI 解析"按钮

**如果看不到：**
- 检查浏览器控制台是否有错误（`F12` -> `Console` 标签）
- 确认前端已正确构建和部署

---

## 🧪 功能测试

### 测试 1: 手动输入网站

1. 新增客户
2. 输入客户网站（如：`https://www.apple.com`）
3. 点击"AI 解析"
4. **预期结果：** 表单自动填充公司信息

### 测试 2: 空网站 URL

1. 不输入网站 URL
2. 点击"AI 解析"
3. **预期结果：** 提示"请先输入客户网站 URL"

### 测试 3: 无效 URL

1. 输入无效 URL（如：`https://invalid-url-test-12345.com`）
2. 点击"AI 解析"
3. **预期结果：** 提示"无法访问网站"

---

## 📋 常见问题

### Q1: API 返回 "Not Found"

**原因：**
- 部署未成功
- 路由未正确注册

**解决：**
1. 检查 Render.com 部署状态
2. 查看构建日志是否有错误
3. 确认代码已正确推送

### Q2: 前端看不到"客户网站"字段

**原因：**
- 浏览器缓存了旧版本
- 前端未正确构建

**解决：**
1. 清除浏览器缓存（`Ctrl+Shift+R`）
2. 重新构建前端：`cd frontend && npm run build`
3. 确认 `dist/` 目录已更新

### Q3: 点击"AI 解析"无反应

**原因：**
- JavaScript 错误
- API 调用失败

**解决：**
1. 按 `F12` 打开开发者工具
2. 查看 `Console` 标签是否有错误
3. 查看 `Network` 标签，确认 API 请求是否发送

### Q4: AI 分析失败

**原因：**
- 后端无法访问外网
- AI 服务未正确配置
- 网站内容无法解析

**解决：**
1. 检查后端服务器网络权限
2. 查看 Render.com 服务日志
3. 尝试使用其他网站 URL 测试

---

## 📞 获取帮助

如果以上步骤都无法解决问题：

1. **查看 Render.com 日志：**
   - 进入 Render.com 控制台
   - 点击你的后端服务
   - 点击 "Logs" 标签
   - 查看最近的错误日志

2. **提供以下信息：**
   - Render.com 部署状态
   - 构建日志中的错误信息
   - 浏览器控制台错误
   - API 测试的返回结果

---

## ✅ 部署成功标志

当以下功能都正常工作时，说明部署成功：

- [ ] 前端显示"客户网站"字段和"AI 解析"按钮
- [ ] 点击"AI 解析"后按钮显示加载状态
- [ ] API 返回有效的 JSON 数据
- [ ] 表单成功自动填充
- [ ] 客户数据成功保存到数据库

---

**当前进度：**
- ✅ 代码已开发完成
- ✅ 代码已推送到 GitHub
- ⏳ 等待 Render.com 部署完成
- ⏳ 需要执行数据库迁移
- ⏳ 需要测试功能
