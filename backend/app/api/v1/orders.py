from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.item import Item
from app.models.order import Order
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.common import Message
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.order_service import generate_order_no
from app.utils.pdf import render_purchase_order_pdf

router = APIRouter()


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> List[OrderResponse]:
    stmt = select(Order)
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    stmt = stmt.order_by(Order.created_at.desc())
    result = await db.execute(stmt)
    return [OrderResponse.model_validate(o) for o in result.scalars().all()]


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_min_role("manager")),
) -> OrderResponse:
    order_no = await generate_order_no(db)
    order = Order(
        order_no=order_no,
        item_id=payload.item_id,
        supplier_id=payload.supplier_id,
        quantity=payload.quantity,
        expected_at=payload.expected_at,
        note=payload.note,
        status="pending",
        requested_by=user.id,
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> OrderResponse:
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="発注が見つかりません")
    return OrderResponse.model_validate(order)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    payload: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> OrderResponse:
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="発注が見つかりません")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(order, k, v)
    await db.flush()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/approve", response_model=OrderResponse)
async def approve_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_min_role("admin")),
) -> OrderResponse:
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="発注が見つかりません")
    if order.status not in ("draft", "pending"):
        raise HTTPException(status_code=400, detail="承認できないステータスです")
    order.status = "approved"
    order.approved_by = user.id
    order.ordered_at = date.today()
    await db.flush()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/complete", response_model=OrderResponse)
async def complete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> OrderResponse:
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="発注が見つかりません")
    order.status = "completed"
    await db.flush()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


@router.get("/{order_id}/pdf")
async def download_order_pdf(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> Response:
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="発注が見つかりません")
    item = await db.get(Item, order.item_id)
    supplier = await db.get(Supplier, order.supplier_id) if order.supplier_id else None
    pdf_bytes = render_purchase_order_pdf(
        order_no=order.order_no,
        supplier_name=supplier.name if supplier else None,
        item_code=item.code if item else "",
        item_name=item.name if item else "",
        quantity=order.quantity,
        unit=item.unit if item else "",
        expected_at=order.expected_at,
        note=order.note,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{order.order_no}.pdf"',
        },
    )
