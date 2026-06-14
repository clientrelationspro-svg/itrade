"""
SiliconFlow AI Service - 硅基流动 AI 服务层
所有 AI 功能通过统一接口调用 SiliconCloud API
"""
import base64
import json
import logging
from typing import Optional, AsyncGenerator
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SiliconFlowAIService:
    """硅基流动 AI 服务统一封装"""

    def __init__(self):
        self.base_url = settings.SILICONFLOW_BASE_URL
        self.api_key = settings.SILICONFLOW_API_KEY
        self.is_configured = bool(self.api_key and self.api_key.startswith("sk-"))

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _mock_chat_response(self, content: str) -> dict:
        return {
            "choices": [{"message": {"content": content}}],
            "usage": {"total_tokens": 0},
        }

    async def _check_configured(self):
        if not self.is_configured:
            raise RuntimeError(
                "SiliconFlow API Key 未配置。请在 backend/.env 中设置 SILICONFLOW_API_KEY"
            )

    # ═══════════════════════════════════════════════
    # 文本生成 - 日常任务 (Qwen2.5-7B-Instruct, 免费)
    # ═══════════════════════════════════════════════

    async def chat_daily(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> dict:
        """日常文本生成：智能填充、翻译、推荐、报告"""
        return await self._chat_completion(
            model=settings.AI_MODEL_DAILY,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def chat_daily_stream(
        self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 2048
    ) -> AsyncGenerator[str, None]:
        """流式日常文本生成"""
        async for chunk in self._chat_completion_stream(
            model=settings.AI_MODEL_DAILY,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk

    # ═══════════════════════════════════════════════
    # 文本生成 - 复杂任务 (DeepSeek-V2.5, 低成本)
    # ═══════════════════════════════════════════════

    async def chat_complex(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict:
        """复杂任务：合同解析、报表生成、数据分析（不可用时自动降级到免费模型）"""
        try:
            return await self._chat_completion(
                model=settings.AI_MODEL_COMPLEX,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            logger.warning(f"DeepSeek-V2.5 unavailable ({e}), falling back to Qwen2.5-7B")
            return await self._chat_completion(
                model=settings.AI_MODEL_DAILY,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    # ═══════════════════════════════════════════════
    # 视觉识别 OCR (Qwen2.5-VL-72B-Instruct, 低成本)
    # ═══════════════════════════════════════════════

    async def vision_ocr(
        self,
        image_data: bytes,
        prompt: str = "请识别并提取图片中的所有文字信息，以JSON格式返回。",
        mime_type: str = "image/png",
    ) -> dict:
        """图片 OCR 识别：发票、提单、合同、认证书"""
        image_b64 = base64.b64encode(image_data).decode("utf-8")
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_b64}"
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        return await self._chat_completion(
            model=settings.AI_MODEL_VISION,
            messages=messages,
            temperature=0.1,
            max_tokens=4096,
        )

    async def vision_extract_fields(
        self,
        image_data: bytes,
        fields: list[str],
        mime_type: str = "image/png",
    ) -> dict:
        """从图片中提取指定字段信息"""
        prompt = f"""请从该图片中提取以下字段信息，以JSON格式返回：
{json.dumps(fields, ensure_ascii=False)}

返回格式: {{"字段名": "提取值", ...}}
如果某字段无法识别，值设为 null。"""
        return await self.vision_ocr(image_data, prompt, mime_type)

    # ═══════════════════════════════════════════════
    # 向量嵌入 (BGE-large-zh/en-v1.5, 极低成本)
    # ═══════════════════════════════════════════════

    async def embed_texts(
        self, texts: list[str], lang: str = "zh"
    ) -> list[list[float]]:
        """文本向量嵌入"""
        model = settings.AI_MODEL_EMBED_ZH if lang == "zh" else settings.AI_MODEL_EMBED_EN
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                headers=self._get_headers(),
                json={
                    "model": model,
                    "input": texts,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

    async def embed_text(self, text: str, lang: str = "zh") -> list[float]:
        """单文本向量嵌入"""
        embeddings = await self.embed_texts([text], lang)
        return embeddings[0]

    # ═══════════════════════════════════════════════
    # 图片生成 (SD3.5-large, 低成本)
    # ═══════════════════════════════════════════════

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
    ) -> list[str]:
        """生成产品图片、包装设计"""
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/image/generations",
                headers=self._get_headers(),
                json={
                    "model": settings.AI_MODEL_IMAGE,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                    "num_images": num_images,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return [img.get("url") or img.get("b64_json", "") for img in data.get("data", [])]

    # ═══════════════════════════════════════════════
    # 底层调用
    # ═══════════════════════════════════════════════

    async def _chat_completion(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> dict:
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"SiliconFlow API error: {error_detail}")
            raise RuntimeError(f"AI API 调用失败: {error_detail}")
        except Exception as e:
            logger.error(f"Chat completion error: {e}", exc_info=True)
            raise

    async def _chat_completion_stream(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue


# 单例
ai_service = SiliconFlowAIService()
