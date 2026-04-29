from __future__ import annotations

from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_min_role
from app.models.item import Item
from app.models.serial_item import SerialItem
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import (
    InTxRequest,
    OutTxRequest,
    ReturnTxRequest,
    TransactionResponse,
    TransferTxRequest,
)
from app.services.alert_service import check_and_notify
from app.services.stock_service import adjust_quantity

router = APIRouter()


async def _ensure_item(db: AsyncSession, item_id: int) -> Item:
    item = await db.get(Item, item_id)
    if not item or not item.is_active:
        raise HTTPException(status_code=404, detail="品目が見つかりません")
    return item


@router.post("/in", response_model=List[TransactionResponse])
async def transaction_in(
    payload: InTxRequest,
    bg: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_min_role("manager")),
) -> List[TransactionResponse]:
    item = await _ensure_item(db, payload.item_id)
    txs: List[Transaction] = []

    if item.manage_type == "serial":
        if not payload.serial_nos:
            raise HTTPException(status_code=400, detail="シリアル番号リストが必要です")
        macs = payload.mac_addresses or []
        for idx, sn in enumerate(payload.serial_nos):
            existing = await db.execute(
                select(SerialItem).where(SerialItem.serial_no == sn)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=409, detail=f"シリアル '{sn}' は既に登録済みです")
            si = SerialItem(
                item_id=item.id,
                serial_no=sn,
                mac_address=macs[idx] if idx < len(macs) else None,
                location_id=payload.to_location_id,
                status="in_stock",
                received_at=date.today(),
            )
            db.add(si)
            await db.flush()
            tx = Transaction(
                tx_type="in",
                item_id=item.id,
                serial_item_id=si.id,
                quantity=1,
                to_location_id=payload.to_location_id,
                operator_id=user.id,
                note=payload.note,
                work_order_no=payload.work_order_no,
            )
            db.add(tx)
            txs.append(tx)
    else:
        await adjust_quantity(db, item.id, payload.to_location_id, +payload.quantity)
        tx = Transaction(
            tx_type="in",
            item_id=item.id,
            quantity=payload.quantity,
            to_location_id=payload.to_location_id,
            operator_id=user.id,
            note=payload.note,
            work_order_no=payload.work_order_no,
        )
        db.add(tx)
        txs.append(tx)

    await db.flush()
    return [TransactionResponse.model_validate(t) for t in txs]


@router.post("/out", response_model=TransactionResponse)
async def transaction_out(
    payload: OutTxRequest,
    bg: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_min_role("operator")),
) -> TransactionResponse:
    item = await _ensure_item(db, payload.item_id)

    if item.manage_type == "serial":
        if not payload.serial_item_id:
            raise HTTPException(status_code=400, detail="シリアル品IDが必要です")
        si = await db.get(SerialItem, payload.serial_item_id)
        if not si or si.status != "in_stock":
            raise HTTPException(status_code=400, detail="シリアル品が出庫可能な状態ではありません")
        si.status = "checked_out"
        si.location_id = payload.to_location_id
        tx = Transaction(
            tx_type="out",
            item_id=item.id,
            serial_item_id=si.id,
            quantity=1,
            from_location_id=payload.from_location_id,
            to_location_id=payload.to_location_id,
            operator_id=user.id,
            note=payload.note,
            work_order_no=payload.work_order_no,
        )
        db.add(tx)
    else:
        await adjust_quantity(db, item.id, payload.from_location_id, -payload.quantity)
        tx = Transaction(
            tx_type="out",
            item_id=item.id,
            quantity=payload.quantity,
            from_location_id=payload.from_location_id,
            to_location_id=payload.to_location_id,
            operator_id=user.id,
            note=payload.note,
            work_order_no=payload.work_order_no,
        )
        db.add(tx)

    await db.flush()
    bg.add_task(check_and_notify, item.id)
    return TransactionResponse.model_validate(tx)


@router.post("/return", response_model=TransactionResponse)
async def transaction_return(
    payload: ReturnTxRequest,
    bg: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_min_role("operator")),
) -> TransactionResponse:
    item = await _ensure_item(db, payload.item_id)

    if item.manage_type == "serial":
        if not payload.serial_item_id:
            raise HTTPException(status_code=400, detail="シリアル品IDが必要です")
        si = await db.get(SerialItem, payload.serial_item_id)
        if not si:
            raise HTTPException(status_code=404, detail="シリアル品が見つかりません")
        si.status = "in_stock"
        si.location_id = payload.to_location_id
        tx = Transaction(
            tx_type="return",
            item_id=item.id,
            serial_item_id=si.id,
            quantity=1,
            from_location_id=payload.from_location_id,
            to_location_id=payload.to_location_id,
            operator_id=user.id,
            note=payload.note,
        )
        db.add(tx)
    else:
        await adjust_quantity(db, item.id, payload.to_location_id, +payload.quantity)
        tx = Transaction(
            tx_type="return",
            item_id=item.id,
            quantity=payload.quantity,
            from_location_id=payload.from_location_id,
            to_location_id=payload.to_location_id,
            operator_id=user.id,
            note=payload.note,
        )
        db.add(tx)

    await db.flush()
    bg.add_task(check_and_notify, item.id)
    return TransactionResponse.model_validate(tx)


@router.post("/transfer", response_model=TransactionResponse)
async def transaction_transfer(
    payload: TransferTxRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_min_role("manager")),
) -> TransactionResponse:
    item = await _ensure_item(db, payload.item_id)
    if item.manage_type == "quantity":
        await adjust_quantity(db, item.id, payload.from_location_id, -payload.quantity)
        await adjust_quantity(db, item.id, payload.to_location_id, +payload.quantity)
    tx = Transaction(
        tx_type="transfer",
        item_id=item.id,
        quantity=payload.quantity,
        from_location_id=payload.from_location_id,
        to_location_id=payload.to_location_id,
        operator_id=user.id,
        note=payload.note,
    )
    db.add(tx)
    await db.flush()
    return TransactionResponse.model_validate(tx)


@router.get("", response_model=List[TransactionResponse])
async def list_transactions(
    from_: Optional[datetime] = Query(None, alias="from"),
    to: Optional[datetime] = None,
    item_id: Optional[int] = None,
    operator_id: Optional[int] = None,
    type: Optional[str] = None,
    limit: int = 100,
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


@router.get("/{tx_id}", response_model=TransactionResponse)
async def get_transaction(
    tx_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_min_role("manager")),
) -> TransactionResponse:
    tx = await db.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="取引が見つかりません")
    return TransactionResponse.model_validate(tx)
