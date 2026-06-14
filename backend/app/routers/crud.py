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


def _like_filter(column, keyword: str):
    return column.ilike(f"%{keyword}%")


def create_crud_router(
    prefix: str,
    model: Type,
    create_schema: Type,
    update_schema: Type,
    response_schema: Type,
    tags: list[str],
    search_fields: list[str] = None,
) -> APIRouter:
    """通用 CRUD 路由工厂"""

    router = APIRouter(prefix=f"/api/{prefix}", tags=tags, redirect_slashes=False)

    model_name = model.__name__

    @router.get("", response_model=dict)
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

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [response_schema.from_orm(item).dict() for item in items],
        }

    @router.get("/{item_id}", response_model=response_schema)
    async def get_item(item_id: str, db: AsyncSession = Depends(get_db)):
        """获取单个记录"""
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return {"detail": f"{model_name} not found"}
        return item

    @router.post("", response_model=response_schema, status_code=201)
    async def create_item(data: create_schema, db: AsyncSession = Depends(get_db)):
        """新增记录"""
        # 清理数据：空字符串和空列表 → None
        data_dict = {}
        for k, v in data.dict(exclude_unset=True).items():
            if v == "" or v == []:
                data_dict[k] = None
            else:
                data_dict[k] = v
        item = model(**data_dict)
        # Auto-generate code
        if hasattr(model, "code") and not getattr(item, "code", None):
            item.code = f"{prefix.upper()[:3]}-{uuid.uuid4().hex[:8].upper()}"
        if hasattr(model, "order_no") and not getattr(item, "order_no", None):
            item.order_no = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        if hasattr(model, "contract_no") and not getattr(item, "contract_no", None):
            item.contract_no = f"CTR-{uuid.uuid4().hex[:8].upper()}"
        db.add(item)
        await db.flush()
        await db.refresh(item)
        return item

    @router.put("/{item_id}", response_model=response_schema)
    async def update_item(item_id: str, data: update_schema, db: AsyncSession = Depends(get_db)):
        """编辑记录"""
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return {"detail": f"{model_name} not found"}
        for key, value in data.dict(exclude_unset=True).items():
            # 清理：空字符串/空列表 → None
            if value == "" or value == []:
                setattr(item, key, None)
            else:
                setattr(item, key, value)
        await db.flush()
        await db.refresh(item)
        return item

    @router.delete("/{item_id}")
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

    @router.post("/{item_id}/restore")
    async def restore_item(item_id: str, db: AsyncSession = Depends(get_db)):
        """从回收站还原"""
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            return {"detail": f"{model_name} not found"}
        if hasattr(model, "status"):
            item.status = RecordStatus.ACTIVE
        return {"detail": "Restored"}

    @router.post("/batch-delete")
    async def batch_delete(ids: list[str], db: AsyncSession = Depends(get_db)):
        """批量软删除"""
        result = await db.execute(select(model).where(model.id.in_(ids)))
        items = result.scalars().all()
        for item in items:
            if hasattr(model, "status"):
                item.status = RecordStatus.DELETED
        return {"detail": f"Deleted {len(items)} items"}

    return router
