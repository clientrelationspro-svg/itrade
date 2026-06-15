import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Integer, Float, Numeric, Boolean,
    DateTime, Date, ForeignKey, Enum as SAEnum, JSON, Index
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


def gen_uuid():
    return str(uuid.uuid4())


def now():
    return datetime.utcnow()


# ─── Enums ───

class RecordStatus(str, enum.Enum):
    ACTIVE = "active"
    DELETED = "deleted"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    VIEWER = "viewer"


class OrderStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    IN_PRODUCTION = "in_production"
    INSPECTING = "inspecting"
    SHIPPING = "shipping"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"


class InspectionStatus(str, enum.Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    REWORK = "rework"


class ShippingStatus(str, enum.Enum):
    PENDING = "pending"
    LOADED = "loaded"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"
    CLEARED = "cleared"


class DocumentCategory(str, enum.Enum):
    INVOICE = "invoice"
    BILL_OF_LADING = "bill_of_lading"
    CERTIFICATE = "certificate"
    CONTRACT = "contract"
    INSPECTION = "inspection"
    OTHER = "other"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ─── User ───

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="operator")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)


# ─── Customer ───

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    name_en = Column(String(200))
    country = Column(String(100))
    contact_person = Column(String(100))
    email = Column(String(120))
    phone = Column(String(50))
    address = Column(Text)
    tax_id = Column(String(100))
    credit_rating = Column(String(20), default="medium")
    credit_score = Column(Integer, default=700)
    notes = Column(Text)
    tags = Column(JSON, default=list)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    orders = relationship("Order", back_populates="customer")
    documents = relationship("Document", back_populates="customer")


# ─── Supplier ───

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    name_en = Column(String(200))
    country = Column(String(100))
    contact_person = Column(String(100))
    email = Column(String(120))
    phone = Column(String(50))
    address = Column(Text)
    factory_address = Column(Text)
    main_products = Column(Text)
    certifications = Column(JSON, default=list)
    rating = Column(Integer, default=3)
    notes = Column(Text)
    tags = Column(JSON, default=list)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    products = relationship("Product", back_populates="supplier")


# ─── Product ───

class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    name_en = Column(String(200))
    category = Column(String(100))
    specification = Column(Text)
    unit = Column(String(20))
    hs_code = Column(String(50), index=True)
    hs_code_recommended = Column(String(50))
    supplier_id = Column(String(36), ForeignKey("suppliers.id"))
    moq = Column(Numeric(14, 2))
    price_range = Column(String(100))
    images = Column(JSON, default=list)
    notes = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    supplier = relationship("Supplier", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    inquiries = relationship("Inquiry", back_populates="product")


# ─── Inquiry ───

class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    customer_id = Column(String(36), ForeignKey("customers.id"))
    product_id = Column(String(36), ForeignKey("products.id"))
    quantity = Column(Numeric(14, 2))
    unit = Column(String(20))
    target_price = Column(Numeric(14, 2))
    currency = Column(String(10), default="USD")
    supplier_quotes = Column(JSON, default=list)
    ai_analysis = Column(Text)
    valid_until = Column(Date)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    product = relationship("Product", back_populates="inquiries")


# ─── Contract ───

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    contract_no = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"))
    supplier_id = Column(String(36), ForeignKey("suppliers.id"))
    amount = Column(Numeric(14, 2))
    currency = Column(String(10), default="USD")
    sign_date = Column(Date)
    expiry_date = Column(Date)
    delivery_date = Column(Date)
    key_terms = Column(Text)
    ai_extracted_terms = Column(JSON, default=dict)
    payment_terms = Column(Text)
    attachments = Column(JSON, default=list)
    notes = Column(Text)
    status = Column(String(20), default="active")
    risk_level = Column(String(20), default="low")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    orders = relationship("Order", back_populates="contract")


# ─── Order ───

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    order_no = Column(String(100), unique=True, nullable=False, index=True, default=lambda: f"ORD-{uuid.uuid4().hex[:8].upper()}")
    customer_id = Column(String(36), ForeignKey("customers.id"))
    contract_id = Column(String(36), ForeignKey("contracts.id"))
    total_amount = Column(Numeric(14, 2))
    currency = Column(String(10), default="USD")
    status = Column(String(20), default="draft")
    production_deadline = Column(Date)
    shipping_deadline = Column(Date)
    delivery_deadline = Column(Date)
    ai_risk_alert = Column(String(20), default="low")
    notes = Column(Text)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    customer = relationship("Customer", back_populates="orders")
    contract = relationship("Contract", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="order")
    shipments = relationship("Shipment", back_populates="order")
    payments = relationship("Payment", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"))
    product_name = Column(String(200))
    specification = Column(Text)
    quantity = Column(Numeric(14, 2))
    unit = Column(String(20))
    unit_price = Column(Numeric(14, 2))
    total_price = Column(Numeric(14, 2))
    created_at = Column(DateTime, default=now)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# ─── Inspection ───

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"))
    inspection_date = Column(Date)
    inspector = Column(String(100))
    company = Column(String(200))
    result = Column(String(20), default="pending")
    ai_result = Column(String(20))
    ai_anomalies = Column(JSON, default=list)
    defects = Column(Text)
    report_url = Column(Text)
    attachments = Column(JSON, default=list)
    notes = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    order = relationship("Order", back_populates="inspections")


# ─── Shipment ───

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"))
    vessel_name = Column(String(200))
    voyage_no = Column(String(100))
    container_no = Column(String(200))
    bl_no = Column(String(100), index=True)
    etd = Column(Date)
    eta = Column(Date)
    port_of_loading = Column(String(200))
    port_of_discharge = Column(String(200))
    ai_extracted_data = Column(JSON, default=dict)
    attachments = Column(JSON, default=list)
    status = Column(String(20), default="pending")
    notes = Column(Text)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    order = relationship("Order", back_populates="shipments")


# ─── Payment ───

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"))
    receivable = Column(Numeric(14, 2))
    received = Column(Numeric(14, 2))
    outstanding = Column(Numeric(14, 2))
    status = Column(String(20), default="unpaid")
    due_date = Column(Date)
    received_date = Column(Date)
    payment_method = Column(String(50))
    bank_info = Column(Text)
    ai_credit_assessment = Column(Text)
    notes = Column(JSON, default=list)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    order = relationship("Order", back_populates="payments")


# ─── Document ───

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    filename = Column(String(255), nullable=False)
    category = Column(String(50))
    ai_category = Column(String(50))
    ai_confidence = Column(Float)
    related_module = Column(String(50))
    related_id = Column(String(36))
    customer_id = Column(String(36), ForeignKey("customers.id"))
    file_path = Column(Text)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    ocr_text = Column(Text)
    ai_extracted_data = Column(JSON, default=dict)
    ai_embedding = Column(JSON)
    tags = Column(JSON, default=list)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    customer = relationship("Customer", back_populates="documents")


# ─── Operation Log ───

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    module = Column(String(50))
    record_id = Column(String(100))
    action = Column(String(50))
    detail = Column(JSON, default=dict)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=now, index=True)


# ─── System Settings ───

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    module = Column(String(100), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    __table_args__ = (
        Index("ix_settings_module_key", "module", "key", unique=True),
    )
