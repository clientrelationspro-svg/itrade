# SiliconFlow AI Technology Architecture Overview
# 硅基流动 AI 技术架构总览

> **平台说明**: 全部 AI 功能基于硅基流动 SiliconCloud 平台的开源模型服务，通过统一 RESTful API 调用。不使用任何商业模型（如 GPT-4V），全部采用硅基流动平台提供的高性价比开源模型。

---

## 0.1 硅基流动模型选型表 / SiliconFlow Model Selection Guide

| AI能力 / AI Capability | 选用模型 / Selected Model | 模型特点 / Model Features | 费用参考 / Cost Reference | 应用场景 / Application Scenarios |
|---|---|---|---|---|
| **文本生成—日常** | `Qwen/Qwen2.5-7B-Instruct` | 32K 上下文，中英文优秀 | 免费（限速） | 智能填充、推荐、翻译、报告生成 |
| **文本生成—复杂任务** | `deepseek-ai/DeepSeek-V2.5` | 236B MoE，推理能力极强 | 低成本 | 智能合同解析、复杂报表生成、数据分析 |
| **视觉识别(OCR)** | `Qwen/Qwen2.5-VL-72B-Instruct` | 72B 可视语言模型，图片理解极强 | 低成本 | 发票识别、提单识别、合同 OCR、认证书识别 |
| **向量嵌入** | `BAAI/bge-large-zh-v1.5` | 1024 维，中文优化 | 极低 | 自然语言搜索、智能推荐、相似度匹配 |
| **向量嵌入(英文)** | `BAAI/bge-large-en-v1.5` | 1024 维，英文优化 | 极低 | 英文文档搜索、国际客户匹配 |
| **图片生成** | `stabilityai/stable-diffusion-3.5-large` | 高质量绘图生成 | 低成本 | 产品图片生成、包装设计案例 |

---

## 0.2 模型详细参数 / Model Detailed Parameters

### 文本生成 / Text Generation

#### Qwen/Qwen2.5-7B-Instruct (日常任务)
- **上下文窗口**: 32K tokens
- **语言支持**: 中文、英文及多语言
- **适用场景**: 
  - 外贸邮件智能填充与润色
  - 产品描述翻译（中英互译）
  - 客户询盘智能推荐回复
  - 日报/周报自动生成
- **API 调用限制**: 免费额度，存在速率限制

#### DeepSeek-V2.5 (复杂任务)
- **架构**: 236B MoE (Mixture of Experts)
- **推理能力**: 极强的逻辑推理与深度分析
- **适用场景**:
  - 外贸合同条款智能解析
  - 复杂财务报表与报关单分析
  - 市场趋势数据分析与预测
  - 多维度客户画像分析
- **API 调用限制**: 低成本按量计费

### 视觉识别 / Visual Recognition (OCR)

#### Qwen/Qwen2.5-VL-72B-Instruct
- **参数量**: 72B
- **能力**: 图片理解 + 文字识别 + 视觉问答
- **适用场景**:
  - 发票 (Invoice) 自动识别与提取
  - 提单 (Bill of Lading) 信息提取
  - 外贸合同扫描件 OCR
  - 产品认证证书识别
  - 包装标签信息读取
- **API 调用限制**: 低成本按量计费

### 向量嵌入 / Vector Embedding

#### BAAI/bge-large-zh-v1.5 (中文)
- **向量维度**: 1024
- **中文优化**: 针对中文语义深度优化
- **适用场景**:
  - 中文产品目录语义搜索
  - 客户需求智能匹配
  - 相似客户发现
  - 知识库检索增强生成 (RAG)

#### BAAI/bge-large-en-v1.5 (英文)
- **向量维度**: 1024
- **英文优化**: 针对英文语义深度优化
- **适用场景**:
  - 英文产品文档搜索
  - 国际客户需求匹配
  - 跨境贸易知识检索
  - 英文合同条款相似度比对

### 图片生成 / Image Generation

#### stabilityai/stable-diffusion-3.5-large
- **输出**: 高质量图片生成
- **适用场景**:
  - 外贸产品展示图生成
  - 包装设计方案预览
  - 营销素材制作
  - 产品目录图片优化
- **API 调用限制**: 低成本按量计费

---

## 0.3 API 配置概要 / API Configuration Summary

### SiliconCloud API 基础信息

| 配置项 / Config Item | 值 / Value |
|---|---|
| **API 基础 URL** | `https://api.siliconflow.cn/v1` |
| **认证方式** | Bearer Token (API Key) |
| **请求格式** | OpenAI 兼容格式 |
| **HTTP Method** | POST |

### 各模型 API Endpoint

| 能力 | Endpoint | Model ID |
|---|---|---|
| 文本生成 | `/v1/chat/completions` | `Qwen/Qwen2.5-7B-Instruct` |
| 文本生成 | `/v1/chat/completions` | `deepseek-ai/DeepSeek-V2.5` |
| 视觉识别 | `/v1/chat/completions` | `Qwen/Qwen2.5-VL-72B-Instruct` |
| 向量嵌入 | `/v1/embeddings` | `BAAI/bge-large-zh-v1.5` |
| 向量嵌入 | `/v1/embeddings` | `BAAI/bge-large-en-v1.5` |
| 图片生成 | `/v1/images/generations` | `stabilityai/stable-diffusion-3.5-large` |

---

## 0.4 外贸场景能力路由 / Foreign Trade Scenario Routing

```
                    ┌─────────────────────────────┐
                    │     用户输入 / User Input     │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │        场景识别 Router        │
                    └─────────────┬───────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  文本理解/生成   │   │  文档/图片 OCR   │   │  搜索/推荐匹配   │
│ Qwen2.5-7B      │   │ Qwen2.5-VL-72B  │   │ BGE v1.5        │
│ DeepSeek-V2.5   │   │                 │   │                 │
└─────────────────┘   └─────────────────┘   └─────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │      结果汇总 & 格式化输出      │
                    └─────────────────────────────┘
```

---

## 0.5 选型原则 / Selection Principles

1. **成本优先**: 优先使用免费模型（`Qwen2.5-7B-Instruct`），复杂任务降级至 DeepSeek-V2.5
2. **场景适配**: 根据具体外贸业务场景自动选择最匹配的模型
3. **容错降级**: 模型不可用时自动切换备用模型
4. **异步处理**: 大批量任务（如批量 OCR）采用异步队列处理
5. **结果缓存**: 相同输入的结果进行缓存，减少重复 API 调用

---

> 📅 文档创建日期: 2026-06-14
> 🏗️ 项目: AI 外贸工作平台
