# Project Memory - AI 外贸工作平台

## 项目概述
AI 外贸工作平台，基于硅基流动 SiliconCloud 平台的开源模型服务构建。

## 技术架构
- 全部 AI 功能通过 SiliconCloud RESTful API 调用，不使用商业模型
- 模型选型文档位于: `docs/siliconflow-ai-architecture.md`

## 核心模型
| 能力 | 模型 |
|------|------|
| 日常文本生成 | Qwen/Qwen2.5-7B-Instruct (免费) |
| 复杂任务 | deepseek-ai/DeepSeek-V2.5 |
| 视觉识别 OCR | Qwen/Qwen2.5-VL-72B-Instruct |
| 中文向量嵌入 | BAAI/bge-large-zh-v1.5 |
| 英文向量嵌入 | BAAI/bge-large-en-v1.5 |
| 图片生成 | stabilityai/stable-diffusion-3.5-large |

## 项目约定
- 文档存放于 `docs/` 目录
- 配置文档使用中英双语
