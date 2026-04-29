from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class TxBase(BaseModel):
    item_id: int
    quantity: int = Field(1, ge=1)
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    note: Optional[str] = None
    work_order_no: Optional[str] = None


class InTxRequest(TxBase):
    """入庫: to_location_id 必須。シリアル管理品目はserial_nosで一括登録"""

    to_location_id: int
    serial_nos: Optional[List[str]] = None
    mac_addresses: Optional[List[str]] = None


class OutTxRequest(TxBase):
    """出庫: from_location_id 必須"""

    from_location_id: int
    to_location_id: Optional[int] = None
    serial_item_id: Optional[int] = None


class ReturnTxRequest(TxBase):
    """返却: 持出し中のシリアルを戻す or 数量管理品目を戻す"""

    to_location_id: int
    serial_item_id: Optional[int] = None


class TransferTxRequest(TxBase):
    from_location_id: int
    to_location_id: int


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tx_type: str
    item_id: int
    serial_item_id: Optional[int] = None
    quantity: int
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    operator_id: int
    note: Optional[str] = None
    work_order_no: Optional[str] = None
    created_at: datetime
