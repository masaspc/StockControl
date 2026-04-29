from fastapi import APIRouter

from app.api.v1 import (
    auth,
    dashboard,
    history,
    items,
    locations,
    orders,
    serials,
    stocks,
    stocktake,
    suppliers,
    transactions,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(serials.router, prefix="/serials", tags=["serials"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(stocktake.router, prefix="/stocktake", tags=["stocktake"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
