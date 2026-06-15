"""
AI 智能路由 - 所有 AI 增强功能端点
包含：OCR识别、翻译、HS推荐、合同解析、报价对比、风险预警、
       信用评估、网站分析、自然语言搜索、报告生成、文档分类、
       智能网络搜索、API配置管理
"""
import uuid
import os
import json as _json
import logging
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.ai_service import ai_service
from app.ai_agents import ai_agents
from app.schemas import *
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/ai", tags=["AI 智能"])


# ═══════════════════════════════════════
# OCR 智能识别 - 上传图片/PDF 自动提取
# ═══════════════════════════════════════

@router.post("/ocr/extract")
async def ai_ocr_extract(
    file: UploadFile = File(...),
    module: str = Form(description="目标模块: customer/supplier/product/contract/shipment/inspection/payment"),
    prompt: str = Form(None),
):
    """上传文件，AI 自动识别并提取字段信息"""
    try:
        contents = await file.read()

        if module == "ocr_text":
            result = await ai_service.vision_ocr(
                contents,
                prompt or "请提取该文档中的所有文字信息。",
                file.content_type or "image/png",
            )
            return {
                "text": result["choices"][0]["message"]["content"],
                "raw": result,
            }

        result = await ai_agents.ocr_fill_form(contents, module, file.content_type or "image/png")
        return result
    except Exception as e:
        logger.error(f"OCR extract error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI 识别失败: {str(e)}")


@router.post("/ocr/extract-fields")
async def ai_ocr_extract_fields(
    file: UploadFile = File(...),
    fields: str = Form(description="JSON array of field names to extract"),
    prompt: str = Form(None),
):
    """从图片中提取指定字段"""
    try:
        field_list = _json.loads(fields)
        contents = await file.read()
        result = await ai_service.vision_extract_fields(
            contents, field_list, file.content_type or "image/png"
        )
        content = result["choices"][0]["message"]["content"]
        parsed = ai_agents._parse_json(content)
        return parsed
    except Exception as e:
        logger.error(f"OCR extract-fields error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI 识别失败: {str(e)}")


# ═══════════════════════════════════════
# 智能填充
# ═══════════════════════════════════════

@router.post("/smart-fill")
async def ai_smart_fill(request: AIOCRRequest):
    """根据已有数据，AI 智能填充缺失字段"""
    messages = [{
        "role": "user",
        "content": f"""根据上下文，智能填充{request.module}模块的以下信息：
{request.prompt or '请推测可能的相关信息'}

返回JSON格式。"""
    }]
    result = await ai_service.chat_daily(messages, temperature=0.3)
    return {"result": result["choices"][0]["message"]["content"]}


# ═══════════════════════════════════════
# 翻译
# ═══════════════════════════════════════

@router.post("/translate")
async def ai_translate(request: AITranslateRequest):
    """中英互译"""
    result = await ai_agents.translate(request.text, request.target_lang, request.source_lang)
    return {"translated": result}


# ═══════════════════════════════════════
# HS 编码推荐
# ═══════════════════════════════════════

@router.post("/hs-recommend")
async def ai_hs_recommend(request: AIHSRecommendRequest):
    """推荐 HS 编码"""
    result = await ai_agents.recommend_hs_code(request.product_name, request.description)
    return result


# ═══════════════════════════════════════
# 合同解析
# ═══════════════════════════════════════

class ContractParseRequest(BaseModel):
    contract_text: str


@router.post("/contract/parse")
async def ai_contract_parse(request: ContractParseRequest):
    """智能解析合同文本"""
    result = await ai_agents.parse_contract(request.contract_text)
    return result


@router.post("/contract/parse-file")
async def ai_contract_parse_file(file: UploadFile = File(...)):
    """上传合同文件，智能解析"""
    contents = await file.read()
    ocr_result = await ai_service.vision_ocr(
        contents,
        "请提取该合同文件的完整文本内容。",
        file.content_type or "application/pdf",
    )
    text = ocr_result["choices"][0]["message"]["content"]
    result = await ai_agents.parse_contract(text)
    result["raw_text"] = text
    return result


# ═══════════════════════════════════════
# 报价对比
# ═══════════════════════════════════════

@router.post("/compare-quotes")
async def ai_compare_quotes(request: AICompareQuotesRequest):
    """多供应商报价对比分析"""
    result = await ai_agents.compare_quotes(request.quotes)
    return result


# ═══════════════════════════════════════
# 订单风险预警
# ═══════════════════════════════════════

@router.post("/order/risk")
async def ai_order_risk(request: AIRiskRequest, db: AsyncSession = Depends(get_db)):
    """订单智能风险预警"""
    from app.models import Order
    result = await db.execute(select(Order).where(Order.id == request.order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Order not found")

    order_data = {
        "order_no": order.order_no,
        "total_amount": str(order.total_amount) if order.total_amount else None,
        "status": order.status if order.status else None,
        "delivery_deadline": str(order.delivery_deadline) if order.delivery_deadline else None,
        "notes": order.notes,
    }
    assessment = await ai_agents.assess_order_risk(order_data)
    order.ai_risk_alert = assessment.get("risk_level", "low")
    await db.flush()
    return assessment


# ═══════════════════════════════════════
# 信用评估
# ═══════════════════════════════════════

@router.post("/credit/assess")
async def ai_credit_assess(request: AICreditRequest, db: AsyncSession = Depends(get_db)):
    """客户信用评估"""
    from app.models import Customer, Payment, Order
    c_result = await db.execute(select(Customer).where(Customer.id == request.customer_id))
    customer = c_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(404, "Customer not found")

    customer_data = {
        "name": customer.name,
        "country": customer.country,
        "credit_rating": customer.credit_rating if customer.credit_rating else None,
    }

    p_result = await db.execute(
        select(Payment).join(Order, Payment.order_id == Order.id)
        .where(Order.customer_id == request.customer_id)
    )
    payments = p_result.scalars().all()
    payment_history = [
        {
            "receivable": str(p.receivable) if p.receivable else None,
            "received": str(p.received) if p.received else None,
            "status": p.status if p.status else None,
            "due_date": str(p.due_date) if p.due_date else None,
        }
        for p in payments
    ]

    assessment = await ai_agents.assess_credit(customer_data, payment_history)
    return assessment


# ═══════════════════════════════════════
# 网站分析 - 自动提取客户信息
# ═══════════════════════════════════════

class WebsiteAnalyzeRequest(BaseModel):
    website_url: str
    fields: list[str] = ["name", "name_en", "country", "contact_person", "email", "phone", "address"]


@router.post("/website/analyze")
async def ai_website_analyze(request: WebsiteAnalyzeRequest):
    """分析客户网站，自动提取客户信息"""
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(request.website_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)[:5000]

        prompt = f"""请分析以下公司网站内容，提取关键信息并以 JSON 格式返回。

需要提取的字段：{', '.join(request.fields)}

网站内容：
{text_content}

请严格按照以下 JSON 格式返回，不要包含其他内容：
{{
    "name": "公司名称",
    "name_en": "公司英文名称",
    "country": "所在国家",
    "contact_person": "联系人姓名",
    "email": "联系邮箱",
    "phone": "联系电话",
    "address": "公司地址",
    "website": "{request.website_url}"
}}

如果某个字段无法提取，请设置为空字符串。"""

        messages = [{"role": "user", "content": prompt}]
        result = await ai_service.chat_daily(messages, temperature=0.3)
        content = result["choices"][0]["message"]["content"]

        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()

        parsed = _json.loads(json_str)
        return parsed

    except requests.RequestException as e:
        logger.error(f"网站访问失败: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"无法访问网站: {str(e)}")
    except _json.JSONDecodeError as e:
        logger.error(f"AI 响应解析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI 分析结果解析失败")
    except Exception as e:
        logger.error(f"网站分析错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"网站分析失败: {str(e)}")


# ═══════════════════════════════════════
# 智能网络搜索 - 搜索公司/产品信息
# ═══════════════════════════════════════

class WebSearchRequest(BaseModel):
    query: str = Field(description="搜索关键词")
    search_type: str = Field(default="company", description="搜索类型: company/product/hs_code/trade_policy")
    fields: list[str] = Field(default=[], description="需要提取的字段")


@router.post("/web-search")
async def ai_web_search(request: WebSearchRequest):
    """智能网络搜索 - 利用 AI 搜索并解析公司/产品/HS编码/贸易政策信息"""
    try:
        import requests
        from bs4 import BeautifulSoup

        # 使用 DuckDuckGo 搜索（无需 API Key）
        search_url = "https://html.duckduckgo.com/html/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        resp = requests.post(search_url, data={"q": request.query}, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 提取搜索结果摘要
        results = []
        for item in soup.select('.result')[:5]:
            title_el = item.select_one('.result__title')
            snippet_el = item.select_one('.result__snippet')
            link_el = item.select_one('.result__url')
            if title_el and snippet_el:
                results.append({
                    "title": title_el.get_text(strip=True),
                    "snippet": snippet_el.get_text(strip=True),
                    "url": link_el.get_text(strip=True) if link_el else "",
                })

        if not results:
            return {"query": request.query, "results": [], "extracted": {}, "note": "未找到搜索结果"}

        # 构建搜索结果摘要文本
        search_summary = "\n\n".join([
            f"标题: {r['title']}\n摘要: {r['snippet']}\nURL: {r['url']}"
            for r in results
        ])

        # 用 AI 解析搜索结果
        fields_str = ", ".join(request.fields) if request.fields else "公司名称, 国家, 联系人, 邮箱, 电话, 地址"
        type_prompts = {
            "company": f"从以下搜索结果中提取公司信息，返回JSON: {{\"name\":\"\",\"country\":\"\",\"industry\":\"\",\"description\":\"\",\"website\":\"\",\"email\":\"\",\"phone\":\"\"}}",
            "product": f"从以下搜索结果中提取产品信息，返回JSON: {{\"name\":\"\",\"hs_code\":\"\",\"specification\":\"\",\"price_range\":\"\",\"supplier\":\"\",\"category\":\"\"}}",
            "hs_code": f"从以下搜索结果中确定HS编码，返回JSON: {{\"hs_code\":\"\",\"chapter\":\"\",\"description\":\"\",\"confidence\":\"\",\"note\":\"\"}}",
            "trade_policy": f"从以下搜索结果中提取贸易政策信息，返回JSON: {{\"policy_title\":\"\",\"country\":\"\",\"effective_date\":\"\",\"summary\":\"\",\"impact\":\"\",\"source\":\"\"}}",
        }

        prompt = type_prompts.get(request.search_type, type_prompts["company"])
        messages = [{
            "role": "user",
            "content": f"""请从以下网络搜索结果中，提取与"{request.query}"相关的关键信息。

{prompt}

搜索结果：
{search_summary[:4000]}

只返回JSON格式，不要包含其他内容。如果某字段无法确定，设为空字符串。"""
        }]

        result = await ai_service.chat_daily(messages, temperature=0.3, max_tokens=2048)
        content = result["choices"][0]["message"]["content"]
        extracted = ai_agents._parse_json(content)

        return {
            "query": request.query,
            "search_type": request.search_type,
            "results": results,
            "extracted": extracted,
        }

    except Exception as e:
        logger.error(f"Web search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"网络搜索失败: {str(e)}")


# ═══════════════════════════════════════
# 自然语言搜索
# ═══════════════════════════════════════

@router.post("/search")
async def ai_natural_search(request: AISearchRequest):
    """自然语言搜索（语义理解）"""
    parsed = await ai_agents.parse_nl_query(request.query)
    return {
        "query": request.query,
        "parsed": parsed,
        "note": "Use parsed.filters for structured search"
    }


# ═══════════════════════════════════════
# 报告生成
# ═══════════════════════════════════════

@router.post("/report")
async def ai_generate_report(request: AIReportRequest):
    """AI 生成业务报告"""
    result = await ai_agents.generate_report(request.report_type, request.data or {})
    return {"report": result}


# ═══════════════════════════════════════
# 文本生成（通用对话）
# ═══════════════════════════════════════

@router.post("/chat")
async def ai_chat(messages: list[dict], model_type: str = "daily"):
    """通用 AI 对话"""
    if model_type == "complex":
        result = await ai_service.chat_complex(messages)
    else:
        result = await ai_service.chat_daily(messages)
    return result


# ═══════════════════════════════════════
# 流式对话
# ═══════════════════════════════════════

@router.post("/chat/stream")
async def ai_chat_stream(messages: list[dict], model_type: str = "daily"):
    """流式 AI 对话"""
    async def generate():
        async for chunk in ai_service.chat_daily_stream(messages):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ═══════════════════════════════════════
# 文档分类
# ═══════════════════════════════════════

@router.post("/document/classify")
async def ai_document_classify(file: UploadFile = File(...)):
    """AI 自动分类文档类型（发票/提单/认证书/合同）"""
    contents = await file.read()
    ocr_result = await ai_service.vision_ocr(
        contents,
        "请判断该文档的类型：invoice(发票), bill_of_lading(提单), certificate(认证书), contract(合同), inspection(检验报告), other(其他)。只返回类型。",
        file.content_type or "image/png",
    )
    text = ocr_result["choices"][0]["message"]["content"].strip().lower()
    return {"category": text, "confidence": 0.9}


# ═══════════════════════════════════════
# 文档一致性验证
# ═══════════════════════════════════════

@router.post("/document/verify")
async def ai_document_verify(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
):
    """比对两份单据数据一致性"""
    content_a = await file_a.read()
    content_b = await file_b.read()

    ocr_a = await ai_service.vision_ocr(content_a, "提取该单据的关键信息为JSON格式。")
    ocr_b = await ai_service.vision_ocr(content_b, "提取该单据的关键信息为JSON格式。")

    result = await ai_agents.verify_documents(
        {"content": ocr_a["choices"][0]["message"]["content"]},
        {"content": ocr_b["choices"][0]["message"]["content"]},
    )
    return result


# ═══════════════════════════════════════
# 向量嵌入
# ═══════════════════════════════════════

class EmbedRequest(BaseModel):
    texts: list[str]
    lang: str = "zh"


@router.post("/embed")
async def ai_embed(request: EmbedRequest):
    """文本向量嵌入"""
    embeddings = await ai_service.embed_texts(request.texts, request.lang)
    return {"embeddings": embeddings, "dimensions": len(embeddings[0]) if embeddings else 0}


# ═══════════════════════════════════════
# 图片生成
# ═══════════════════════════════════════

@router.post("/image/generate")
async def ai_image_generate(
    prompt: str = Form(...),
    negative_prompt: str = Form(""),
    width: int = Form(1024),
    height: int = Form(1024),
):
    """AI 图片生成"""
    images = await ai_service.generate_image(prompt, negative_prompt, width, height)
    return {"images": images}


# ═══════════════════════════════════════
# API 配置状态检查
# ═══════════════════════════════════════

@router.get("/config/status")
async def ai_config_status():
    """检查 AI API 配置状态"""
    return {
        "is_configured": ai_service.is_configured,
        "api_key_masked": (settings.SILICONFLOW_API_KEY[:10] + "..." + settings.SILICONFLOW_API_KEY[-4:])
            if settings.SILICONFLOW_API_KEY else "",
        "base_url": settings.SILICONFLOW_BASE_URL,
        "models": {
            "daily": settings.AI_MODEL_DAILY,
            "complex": settings.AI_MODEL_COMPLEX,
            "vision": settings.AI_MODEL_VISION,
            "embed_zh": settings.AI_MODEL_EMBED_ZH,
            "embed_en": settings.AI_MODEL_EMBED_EN,
            "image": settings.AI_MODEL_IMAGE,
        }
    }
