from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ─── Common ───

class PaginatedParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list


class SearchParams(BaseModel):
    keyword: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ─── Auth ───

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Customer ───

class CustomerCreate(BaseModel):
    name: str
    name_en: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = []


class CustomerUpdate(CustomerCreate):
    pass


class CustomerResponse(CustomerCreate):
    id: str
    code: str
    credit_rating: Optional[str] = None
    credit_score: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── Supplier ───

class SupplierCreate(BaseModel):
    name: str
    name_en: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    factory_address: Optional[str] = None
    main_products: Optional[str] = None
    certifications: Optional[List[str]] = []
    rating: Optional[int] = 3
    notes: Optional[str] = None
    tags: Optional[List[str]] = []


class SupplierUpdate(SupplierCreate):
    pass


class SupplierResponse(SupplierCreate):
    id: str
    code: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── Product ───

class ProductCreate(BaseModel):
    name: str
    name_en: Optional[str] = None
    category: Optional[str] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    hs_code: Optional[str] = None
    hs_code_recommended: Optional[str] = None
    supplier_id: Optional[str] = None
    moq: Optional[Decimal] = None
    price_range: Optional[str] = None
    images: Optional[List[str]] = []
    notes: Optional[str] = None


class ProductUpdate(ProductCreate):
    pass


class ProductResponse(ProductCreate):
    id: str
    code: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── Inquiry ───

class InquiryCreate(BaseModel):
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    target_price: Optional[Decimal] = None
    currency: str = "USD"
    supplier_quotes: Optional[List[dict]] = []
    valid_until: Optional[date] = None


class InquiryUpdate(InquiryCreate):
    ai_analysis: Optional[str] = None


class InquiryResponse(InquiryCreate):
    id: str
    ai_analysis: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── Contract ───

class ContractCreate(BaseModel):
    contract_no: str
    title: str
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: str = "USD"
    sign_date: Optional[date] = None
    expiry_date: Optional[date] = None
    delivery_date: Optional[date] = None
    key_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    attachments: Optional[List[str]] = []
    notes: Optional[str] = None


class ContractUpdate(ContractCreate):
    ai_extracted_terms: Optional[dict] = None
    risk_level: Optional[str] = None


class ContractResponse(ContractCreate):
    id: str
    ai_extracted_terms: Optional[dict] = None
    risk_level: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── Order ───

class OrderItemCreate(BaseModel):
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    specification: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None


class OrderCreate(BaseModel):
    customer_id: Optional[str] = None
    contract_id: Optional[str] = None
    total_amount: Optional[Decimal] = None
    currency: str = "USD"
    status: Optional[str] = "draft"
    production_deadline: Optional[date] = None
    shipping_deadline: Optional[date] = None
    delivery_deadline: Optional[date] = None
    notes: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = []


class OrderUpdate(OrderCreate):
    ai_risk_alert: Optional[str] = None


class OrderResponse(OrderCreate):
    id: str
    order_no: str
    ai_risk_alert: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── Inspection ───

class InspectionCreate(BaseModel):
    order_id: Optional[str] = None
    inspection_date: Optional[date] = None
    inspector: Optional[str] = None
    company: Optional[str] = None
    result: Optional[str] = "pending"
    defects: Optional[str] = None
    report_url: Optional[str] = None
    attachments: Optional[List[str]] = []
    notes: Optional[str] = None


class InspectionUpdate(InspectionCreate):
    ai_result: Optional[str] = None
    ai_anomalies: Optional[List[dict]] = None


class InspectionResponse(InspectionCreate):
    id: str
    ai_result: Optional[str] = None
    ai_anomalies: Optional[List[dict]] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── Shipment ───

class ShipmentCreate(BaseModel):
    order_id: Optional[str] = None
    vessel_name: Optional[str] = None
    voyage_no: Optional[str] = None
    container_no: Optional[str] = None
    bl_no: Optional[str] = None
    etd: Optional[date] = None
    eta: Optional[date] = None
    port_of_loading: Optional[str] = None
    port_of_discharge: Optional[str] = None
    attachments: Optional[List[str]] = []
    notes: Optional[str] = None


class ShipmentUpdate(ShipmentCreate):
    ai_extracted_data: Optional[dict] = None
    status: Optional[str] = None


class ShipmentResponse(ShipmentCreate):
    id: str
    ai_extracted_data: Optional[dict] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── Payment ───

class PaymentCreate(BaseModel):
    order_id: Optional[str] = None
    receivable: Optional[Decimal] = None
    received: Optional[Decimal] = None
    outstanding: Optional[Decimal] = None
    due_date: Optional[date] = None
    received_date: Optional[date] = None
    payment_method: Optional[str] = None
    bank_info: Optional[str] = None
    notes: Optional[List[dict]] = []


class PaymentUpdate(PaymentCreate):
    status: Optional[str] = None
    ai_credit_assessment: Optional[str] = None


class PaymentResponse(PaymentCreate):
    id: str
    status: str
    ai_credit_assessment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── Document ───

class DocumentCreate(BaseModel):
    filename: str
    category: Optional[str] = None
    related_module: Optional[str] = None
    related_id: Optional[str] = None
    customer_id: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    ocr_text: Optional[str] = None
    tags: Optional[List[str]] = []


class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    category: Optional[str] = None
    ai_category: Optional[str] = None
    ai_confidence: Optional[float] = None
    related_module: Optional[str] = None
    related_id: Optional[str] = None
    customer_id: Optional[str] = None
    ocr_text: Optional[str] = None
    ai_extracted_data: Optional[dict] = None
    tags: Optional[List[str]] = None


class DocumentResponse(BaseModel):
    id: str
    filename: str
    category: Optional[str] = None
    ai_category: Optional[str] = None
    ai_confidence: Optional[float] = None
    related_module: Optional[str] = None
    related_id: Optional[str] = None
    customer_id: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    ocr_text: Optional[str] = None
    ai_extracted_data: Optional[dict] = None
    tags: Optional[List[str]] = None
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


# ─── System Setting ───

class SettingCreate(BaseModel):
    module: str
    key: str
    value: str
    description: Optional[str] = None


class SettingResponse(SettingCreate):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ─── AI Endpoints ───

class AIOCRRequest(BaseModel):
    module: str = Field(description="目标模块: customer/supplier/product/contract/shipment/inspection/payment")
    prompt: Optional[str] = None


class AITranslateRequest(BaseModel):
    text: str
    target_lang: str = "en"
    source_lang: str = "auto"


class AIHSRecommendRequest(BaseModel):
    product_name: str
    description: str = ""


class AICompareQuotesRequest(BaseModel):
    quotes: List[dict]


class AICreditRequest(BaseModel):
    customer_id: str


class AIRiskRequest(BaseModel):
    order_id: str


class AISearchRequest(BaseModel):
    query: str


class AIReportRequest(BaseModel):
    report_type: str = "weekly"
    data: Optional[dict] = None


class AIExtractTextRequest(BaseModel):
    module: str
    prompt: Optional[str] = None
