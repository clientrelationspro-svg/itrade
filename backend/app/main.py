"""
AI 外贸工作平台 - FastAPI 主应用
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.config import get_settings
from app.database import init_db, async_session
from app.routers import crud, ai, auth
from app import models, schemas

settings = get_settings()

# Ensure upload directory exists before app starts
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 执行数据库迁移
    async with async_session() as session:
        try:
            # 检查并执行数据库迁移
            
            # 1. 修改 inquiries 表的列约束允许 NULL
            try:
                # 先检查列是否允许 NULL
                result = await session.execute(text("""
                    SELECT column_name, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = 'inquiries' 
                    AND column_name IN ('quantity', 'target_price')
                """))
                columns = result.fetchall()
                
                # 如果 quantity 列不可空，执行 ALTER TABLE
                quantity_nullable = any(col[0] == 'quantity' and col[1] == 'YES' for col in columns)
                target_price_nullable = any(col[0] == 'target_price' and col[1] == 'YES' for col in columns)
                
                if not quantity_nullable or not target_price_nullable:
                    await session.execute(text("""
                        ALTER TABLE inquiries 
                        ALTER COLUMN quantity DROP NOT NULL,
                        ALTER COLUMN target_price DROP NOT NULL
                    """))
                    await session.commit()
                    print("✓ 数据库迁移成功：inquiries 表的 quantity 和 target_price 列已设置为可空")
                else:
                    print("ℹ 数据库迁移跳过：inquiries 表的列已经可空")
                    
            except Exception as e:
                await session.rollback()
                print(f"⚠ 数据库迁移失败（将在下次启动时重试）：{str(e)}")
            
        except Exception as e:
            print(f"⚠ 数据库迁移检查失败：{str(e)}")
    
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (uploads)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ─── Auth Router ───
app.include_router(auth.router)

# ─── Business CRUD Routers ───
app.include_router(crud.create_crud_router(
    prefix="customers", model=models.Customer,
    create_schema=schemas.CustomerCreate, update_schema=schemas.CustomerUpdate,
    response_schema=schemas.CustomerResponse, tags=["客户管理"],
    search_fields=["name", "name_en", "email", "phone", "contact_person", "country"],
))

app.include_router(crud.create_crud_router(
    prefix="suppliers", model=models.Supplier,
    create_schema=schemas.SupplierCreate, update_schema=schemas.SupplierUpdate,
    response_schema=schemas.SupplierResponse, tags=["供应商管理"],
    search_fields=["name", "name_en", "email", "phone", "country", "main_products"],
))

app.include_router(crud.create_crud_router(
    prefix="products", model=models.Product,
    create_schema=schemas.ProductCreate, update_schema=schemas.ProductUpdate,
    response_schema=schemas.ProductResponse, tags=["产品管理"],
    search_fields=["name", "name_en", "specification", "hs_code", "category"],
))

app.include_router(crud.create_crud_router(
    prefix="inquiries", model=models.Inquiry,
    create_schema=schemas.InquiryCreate, update_schema=schemas.InquiryUpdate,
    response_schema=schemas.InquiryResponse, tags=["询价管理"],
    search_fields=[],
))

app.include_router(crud.create_crud_router(
    prefix="contracts", model=models.Contract,
    create_schema=schemas.ContractCreate, update_schema=schemas.ContractUpdate,
    response_schema=schemas.ContractResponse, tags=["合同管理"],
    search_fields=["contract_no", "title", "key_terms"],
))

app.include_router(crud.create_crud_router(
    prefix="orders", model=models.Order,
    create_schema=schemas.OrderCreate, update_schema=schemas.OrderUpdate,
    response_schema=schemas.OrderResponse, tags=["订单管理"],
    search_fields=["order_no", "notes"],
))

app.include_router(crud.create_crud_router(
    prefix="inspections", model=models.Inspection,
    create_schema=schemas.InspectionCreate, update_schema=schemas.InspectionUpdate,
    response_schema=schemas.InspectionResponse, tags=["验货管理"],
    search_fields=["inspector", "company", "defects"],
))

app.include_router(crud.create_crud_router(
    prefix="shipments", model=models.Shipment,
    create_schema=schemas.ShipmentCreate, update_schema=schemas.ShipmentUpdate,
    response_schema=schemas.ShipmentResponse, tags=["装运管理"],
    search_fields=["vessel_name", "voyage_no", "bl_no", "container_no"],
))

app.include_router(crud.create_crud_router(
    prefix="payments", model=models.Payment,
    create_schema=schemas.PaymentCreate, update_schema=schemas.PaymentUpdate,
    response_schema=schemas.PaymentResponse, tags=["收付款管理"],
    search_fields=["payment_method", "bank_info"],
))

app.include_router(crud.create_crud_router(
    prefix="documents", model=models.Document,
    create_schema=schemas.DocumentCreate,
    update_schema=schemas.DocumentUpdate,
    response_schema=schemas.DocumentResponse, tags=["文档管理"],
    search_fields=["filename", "ocr_text"],
))

app.include_router(crud.create_crud_router(
    prefix="settings", model=models.SystemSetting,
    create_schema=schemas.SettingCreate, update_schema=schemas.SettingCreate,
    response_schema=schemas.SettingResponse, tags=["系统设置"],
    search_fields=["module", "key", "description"],
))

# ─── AI Router ───
app.include_router(ai.router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.post("/api/admin/migrate-inquiries")
async def migrate_inquiries(db: AsyncSession = Depends(get_db)):
    """手动触发数据库迁移：修改 inquiries 表允许 NULL"""
    try:
        # 执行迁移
        await db.execute(text("""
            ALTER TABLE inquiries 
            ALTER COLUMN quantity DROP NOT NULL,
            ALTER COLUMN target_price DROP NOT NULL
        """))
        await db.commit()
        return {"status": "success", "message": "迁移成功：inquiries 表的 quantity 和 target_price 列已设置为可空"}
    except Exception as e:
        await db.rollback()
        return {"status": "error", "message": str(e)}


@app.get("/api/dashboard")
async def dashboard():
    """看板概览"""
    return {
        "summary": {
            "total_orders": 0,
            "total_revenue": 0,
            "pending_shipments": 0,
            "overdue_payments": 0,
        },
        "charts": {
            "order_trend": [],
            "revenue_by_month": [],
            "customer_distribution": [],
        },
        "alerts": [],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
