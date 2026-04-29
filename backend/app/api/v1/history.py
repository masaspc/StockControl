from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionResponse

router = APIRouter()


@router.get("", response_model=List[TransactionResponse])
async def list_history(
    from_: Optional[datetime] = Query(None, alias="from"),
    to: Optional[datetime] = None,
    item_id: Optional[int] = None,
    operator_id: Optional[int] = None,
    type: Optional[str] = None,
    limit: int = 200,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> List[TransactionResponse]:
    stmt = select(Transaction)
    if from_:
        stmt = stmt.where(Transaction.created_at >= from_)
    if to:
        stmt = stmt.where(Transaction.created_at <= to)
    if item_id:
        stmt = stmt.where(Transaction.item_id == item_id)
    if operator_id:
        stmt = stmt.where(Transaction.operator_id == operator_id)
    if type:
        stmt = stmt.where(Transaction.tx_type == type)
    stmt = stmt.order_by(Transaction.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return [TransactionResponse.model_validate(t) for t in result.scalars().all()]
