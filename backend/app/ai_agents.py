"""
AI Agents - 各业务场景的 AI 智能代理
"""
import json
import logging
from typing import Optional
from app.ai_service import ai_service

logger = logging.getLogger(__name__)


class AIAgents:
    """业务 AI Agent 集合"""

    # ─── OCR 智能填充 Agent ───

    @staticmethod
    async def ocr_fill_form(
        image_data: bytes,
        module: str,
        mime_type: str = "image/png",
    ) -> dict:
        """上传图片/PDF，自动识别并填充表单字段"""
        field_configs = {
            "customer": ["公司名称", "联系人", "邮箱", "电话", "地址", "税号", "国家"],
            "supplier": ["公司名称", "联系人", "邮箱", "电话", "地址", "工厂地址", "主营产品"],
            "product": ["产品名称", "规格", "型号", "HS编码", "单位", "单价范围"],
            "contract": ["合同编号", "甲方", "乙方", "金额", "签订日期", "到期日", "付款条款"],
            "shipment": ["船名", "航次", "提单号", "集装箱号", "ETD", "ETA", "装货港", "卸货港"],
            "inspection": ["检验日期", "检验机构", "检验结果", "缺陷描述", "批号"],
            "payment": ["应收金额", "已收金额", "应付日期", "付款方式", "银行信息"],
        }
        fields = field_configs.get(module, ["文本内容"])
        result = await ai_service.vision_extract_fields(image_data, fields, mime_type)
        # 解析 AI 响应，提取实际内容
        try:
            content = result["choices"][0]["message"]["content"]
            parsed = AIAgents._parse_json(content)
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse OCR result: {e}, raw result: {result}")
            return {"error": "Failed to parse AI response", "raw": result}

    # ─── HS 编码推荐 Agent ───

    @staticmethod
    async def recommend_hs_code(product_name: str, description: str = "") -> dict:
        """根据产品名称推荐 HS 编码"""
        messages = [
            {"role": "system", "content": "你是一个HS编码专家。请直接返回JSON格式，不要包含任何其他内容。"},
            {"role": "user", "content": f"为以下产品推荐HS编码(6位数字)：\n产品名: {product_name}\n描述: {description}\n\n请返回: {{\"hs_code\":\"090421\",\"chapter\":\"第9章\",\"confidence\":\"high\",\"reason\":\"分类依据\"}}"},
        ]
        resp = await ai_service.chat_daily(messages, temperature=0.1, max_tokens=200)
        content = resp["choices"][0]["message"]["content"]
        return AIAgents._parse_json(content)

    # ─── 合同解析 Agent ───

    @staticmethod
    async def parse_contract(contract_text: str) -> dict:
        """智能解析合同关键条款"""
        messages = [
            {"role": "system", "content": "你是合同分析专家。直接返回JSON对象，不要markdown包裹。"},
            {"role": "user", "content": f"""从以下合同提取信息，返回JSON：
{contract_text[:10000]}

返回格式（直接返回JSON）:
{{"甲方":"公司名","乙方":"公司名","金额":0,"币种":"USD","签订日期":"","交货日期":"","付款条款":"","风险等级":"low/medium/high","风险提示":"","关键条款":""}}"""}
        ]
        resp = await ai_service.chat_complex(messages, temperature=0.2)
        content = resp["choices"][0]["message"]["content"]
        raw = AIAgents._parse_json(content)
        # Normalize to expected format
        return {
            "parties": {"甲方": raw.get("甲方", ""), "乙方": raw.get("乙方", "")},
            "amount": {"金额": raw.get("金额", 0), "币种": raw.get("币种", "USD")},
            "dates": {"签订日期": raw.get("签订日期", ""), "交货日期": raw.get("交货日期", ""), "到期日": raw.get("到期日", "")},
            "payment_terms": raw.get("付款条款", ""),
            "key_clauses": [raw.get("关键条款", "")] if raw.get("关键条款") else [],
            "risk_flags": [raw.get("风险提示", "")] if raw.get("风险提示") else [],
            "risk_level": raw.get("风险等级", "low"),
        }

    # ─── 报价对比分析 Agent ───

    @staticmethod
    async def compare_quotes(quotes: list[dict]) -> dict:
        """多供应商报价智能对比分析"""
        messages = [{
            "role": "user",
            "content": f"""请分析以下供应商报价，给出对比分析和推荐：
{json.dumps(quotes, ensure_ascii=False, indent=2)}

返回JSON：
{{
    "rankings": [{{"supplier": "", "score": 0, "reasons": []}}],
    "best_choice": {{"supplier": "", "reasons": ""}},
    "price_analysis": "",
    "risk_warnings": [],
    "negotiation_tips": ""
}}"""
        }]
        resp = await ai_service.chat_complex(messages, temperature=0.3)
        content = resp["choices"][0]["message"]["content"]
        return AIAgents._parse_json(content)

    # ─── 订单风险预警 Agent ───

    @staticmethod
    async def assess_order_risk(order_data: dict) -> dict:
        """订单智能风险预警"""
        messages = [{
            "role": "user",
            "content": f"""评估以下外贸订单的风险等级：
{json.dumps(order_data, ensure_ascii=False)}

返回JSON：
{{
    "risk_level": "low/medium/high/critical",
    "risk_factors": [],
    "suggestions": [],
    "production_risk": "评估",
    "payment_risk": "评估",
    "logistics_risk": "评估",
    "overall_score": 85
}}"""
        }]
        resp = await ai_service.chat_complex(messages, temperature=0.3)
        content = resp["choices"][0]["message"]["content"]
        return AIAgents._parse_json(content)

    # ─── 收款信用评估 Agent ───

    @staticmethod
    async def assess_credit(customer_data: dict, payment_history: list[dict]) -> dict:
        """客户信用评估"""
        messages = [{
            "role": "user",
            "content": f"""根据客户信息和历史付款记录，评估客户信用：
客户: {json.dumps(customer_data, ensure_ascii=False)}
历史付款: {json.dumps(payment_history, ensure_ascii=False)}

返回JSON：
{{
    "credit_score": 750,
    "credit_rating": "low/medium/high/critical",
    "recommended_terms": "",
    "risk_factors": [],
    "payment_prediction": "预计收款时间节点"
}}"""
        }]
        resp = await ai_service.chat_complex(messages, temperature=0.3)
        content = resp["choices"][0]["message"]["content"]
        return AIAgents._parse_json(content)

    # ─── 智能翻译 Agent ───

    @staticmethod
    async def translate(text: str, target_lang: str = "en", source_lang: str = "auto") -> str:
        """中英互译"""
        lang_map = {"en": "英文", "zh": "中文"}
        target = lang_map.get(target_lang, target_lang)
        messages = [{
            "role": "user",
            "content": f"请将以下文本翻译为{target}，保持专业外贸术语准确：\n{text}"
        }]
        resp = await ai_service.chat_daily(messages, temperature=0.3)
        return resp["choices"][0]["message"]["content"]

    # ─── 智能报告生成 Agent ───

    @staticmethod
    async def generate_report(report_type: str, data: dict) -> str:
        """生成业务报告"""
        prompts = {
            "daily": "生成外贸日报摘要",
            "weekly": "生成本周业务周报，包含订单、收款、出货统计",
            "monthly": "生成月度经营分析报告，含趋势图表数据",
            "customer": "生成客户分析报告",
        }
        instruction = prompts.get(report_type, "生成业务报告")
        messages = [{
            "role": "user",
            "content": f"{instruction}：\n{json.dumps(data, ensure_ascii=False)}"
        }]
        resp = await ai_service.chat_daily(messages, temperature=0.5, max_tokens=4096)
        return resp["choices"][0]["message"]["content"]

    # ─── 单据数据一致性比对 Agent ───

    @staticmethod
    async def verify_documents(doc1_data: dict, doc2_data: dict) -> dict:
        """比对提单与发票等单据数据一致性"""
        messages = [{
            "role": "user",
            "content": f"""请比对以下两份单据数据，检查一致性：
单据A: {json.dumps(doc1_data, ensure_ascii=False)}
单据B: {json.dumps(doc2_data, ensure_ascii=False)}

返回JSON：
{{
    "is_consistent": true/false,
    "differences": [{{"field": "", "value_a": "", "value_b": "", "severity": "critical/warning/info"}}],
    "summary": ""
}}"""
        }]
        resp = await ai_service.chat_complex(messages, temperature=0.2)
        content = resp["choices"][0]["message"]["content"]
        return AIAgents._parse_json(content)

    # ─── 自然语言查询理解 Agent ───

    @staticmethod
    async def parse_nl_query(query: str) -> dict:
        """将自然语言查询转化为结构化搜索条件"""
        messages = [{
            "role": "user",
            "content": f"""将以下自然语言外贸查询转化为结构化搜索参数：
查询: "{query}"

返回JSON：
{{
    "intent": "search_customer/search_product/search_order/compare/analyze",
    "filters": {{"field": "value"}},
    "sort_by": "",
    "date_range": {{"start": "", "end": ""}},
    "keywords": []
}}"""
        }]
        resp = await ai_service.chat_daily(messages, temperature=0.2)
        content = resp["choices"][0]["message"]["content"]
        return AIAgents._parse_json(content)

    # ─── Helpers ───

    @staticmethod
    def _parse_json(content: str) -> dict:
        """从 AI 响应中提取 JSON（多策略解析）"""
        import re
        # 策略1: 直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        # 策略2: 从 markdown code block 提取
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # 策略3: 查找所有 JSON 对象，尝试每个，选字段最多的
        candidates = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        best = None
        for c in candidates:
            try:
                obj = json.loads(c)
                if isinstance(obj, dict) and (best is None or len(obj) > len(best)):
                    best = obj
            except json.JSONDecodeError:
                continue
        if best:
            return best
        # 策略4: 贪婪匹配最后一个完整 JSON 对象
        for m in re.finditer(r'\{[^}]*\}', content):
            try:
                obj = json.loads(m.group())
                if isinstance(obj, dict) and len(obj) >= 1:
                    return obj
            except json.JSONDecodeError:
                continue
        return {"raw_response": content, "error": "Failed to parse JSON"}


ai_agents = AIAgents()
