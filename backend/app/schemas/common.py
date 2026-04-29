from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagination(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = 1
    page_size: int = 50


class Message(BaseModel):
    message: str
