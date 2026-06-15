"""
通用 CRUD 路由工厂 - 为所有模块生成标准 RESTful API
遵循说明书标准列表页/编辑页/软删除设计
"""
import uuid
from typing import Type, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, cast, String
from app.database import get_db
from app.models import RecordStatus


def create_crud_router(
    prefix: str,
    model: Type,
    create_schema: Type,
    update_schema: Type,
    response_schema: Type,
    tags: list[str],
    search_fields: list[str] = None,
    require_auth: bool = True,
) -> APIRouter:
    """通用 CRUD 路由工厂"""

    router = APIRouter(prefix=f"/api/{prefix}", tags=tags, redirect_slashes=False)

    model_name = model.__name__

    # 可选的认证依赖
    dependencies = []
    if require_auth:
        try:
            from app.routers.auth import get_current_user
            dependencies = [Depends(get_current_user)]
        except ImportError:
            pass

    @router.get("", response_model=dict, dependencies=dependencies)
    async def list_items(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        keyword: str = Query(None),
        status: str = Query(None),
        date_from: Optional[str] = Query(None),
        date_to: Optional[str] = Query(None),
        sort_by: str = Query("created_at"),
        sort_order: str = Query("desc"),
        db: AsyncSession = Depends(get_db),
    ):
        """标准列表页 - 支持搜索/筛选/分页/排序"""
        query = select(model)

        # 软删除过滤
        if hasattr(model, "status"):
            if status:
                query = query.where(model.status == status)
            elif status != "all":
                query = query.where(model.status == RecordStatus.ACTIVE)

        # 关键词搜索
        if keyword and search_fields:
            conditions = []
            for field in search_fields:
                col = getattr(model, field, None)
                if col:
                    conditions.append(cast(col, String).ilike(f"%{keyword}%"))
            if conditions:
                query = query.where(or_(*conditions))

        # 日期筛选
        if date_from and hasattr(model, "created_at"):
            query = query.where(model.created_at >= date_from)
        if date_to and hasattr(model, "created_at"):
            query = query.where(model.created_at <= date_to)

        # 排序
        sort_col = getattr(model, sort_by, model.created_at if hasattr(model, "created_at") else None)
        if sort_col:
            if sort_order == "desc":
                query = query.order_by(sort_col.desc())
            else:
                query = query.order_by(sort_col.asc())

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()

        # 序列化
        serialized = []
        for item in items:
            d = {}
            for col in item.__table__.columns:
                val = getattr(item, col.name)
                d[col.name] = str(val) if isinstance(val, (uuid.UUID,)) else val
            serialized.append(d)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": serialized,
        }

    @router.get("/{item_id}", dependencies=dependencies)
    async def get_item(item_id: str, db: AsyncSession = Depends(get_db)):
        """获取单个记录"""
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return {"detail": f"{model_name} not found"}
        d = {}
        for col in item.__table__.columns:
            val = getattr(item, col.name)
            d[col.name] = str(val) if isinstance(val, (uuid.UUID,)) else val
        return d

    @router.post("", status_code=201, dependencies=dependencies)
    async def create_item(data: create_schema, db: AsyncSession = Depends(get_db)):
        """新增记录"""
        try:
            data_dict = {}
            for k, v in data.dict(exclude_unset=True).items():
                if v == "" or v == []:
                    data_dict[k] = None
                else:
                    data_dict[k] = v

            if hasattr(model, "order_no"):
                data_dict.setdefault("order_no", f"ORD-{uuid.uuid4().hex[:8].upper()}")
            if hasattr(model, "contract_no"):
                data_dict.setdefault("contract_no", f"CTR-{uuid.uuid4().hex[:8].upper()}")
            if hasattr(model, "code"):
                data_dict.setdefault("code", f"{prefix.upper()[:3]}-{uuid.uuid4().hex[:8].upper()}")

            item = model(**data_dict)
            db.add(item)
            await db.flush()
            await db.refresh(item)
            d = {}
            for col in item.__table__.columns:
                val = getattr(item, col.name)
                d[col.name] = str(val) if isinstance(val, (uuid.UUID,)) else val
            return d
        except Exception as e:
            raise

    @router.put("/{item_id}", dependencies=dependencies)
    async def update_item(item_id: str, data: update_schema, db: AsyncSession = Depends(get_db)):
        """编辑记录"""
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return {"detail": f"{model_name} not found"}
        for key, value in data.dict(exclude_unset=True).items():
            if value == "" or value == []:
                setattr(item, key, None)
            else:
                setattr(item, key, value)
        await db.flush()
        await db.refresh(item)
        d = {}
        for col in item.__table__.columns:
            val = getattr(item, col.name)
            d[col.name] = str(val) if isinstance(val, (uuid.UUID,)) else val
        return d

    @router.delete("/{item_id}", dependencies=dependencies)
    async def delete_item(item_id: str, permanent: bool = False, db: AsyncSession = Depends(get_db)):
        """软删除（默认）或永久删除"""
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return {"detail": f"{model_name} not found"}
        if permanent:
            await db.delete(item)
            return {"detail": "Permanently deleted"}
        if hasattr(model, "status"):
            item.status = RecordStatus.DELETED
        return {"detail": "Moved to recycle bin"}

    @router.post("/{item_id}/restore", dependencies=dependencies)
    async def restore_item(item_id: str, db: AsyncSession = Depends(get_db)):
        """从回收站还原"""
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return {"detail": f"{model_name} not found"}
        if hasattr(model, "status"):
            item.status = RecordStatus.ACTIVE
        return {"detail": "Restored"}

    @router.post("/batch-delete", dependencies=dependencies)
    async def batch_delete(ids: list[str], db: AsyncSession = Depends(get_db)):
        """批量软删除"""
        result = await db.execute(select(model).where(model.id.in_(ids)))
        items = result.scalars().all()
        for item in items:
            if hasattr(model, "status"):
                item.status = RecordStatus.DELETED
        return {"detail": f"Deleted {len(items)} items"}

    return router
