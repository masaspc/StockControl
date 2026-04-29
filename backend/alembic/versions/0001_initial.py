"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-29

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("maker", sa.String(100)),
        sa.Column("model_no", sa.String(100)),
        sa.Column("manage_type", sa.String(20), nullable=False),
        sa.Column("unit", sa.String(20), server_default="個"),
        sa.Column("order_point", sa.Integer, server_default="0"),
        sa.Column("order_unit", sa.Integer, server_default="1"),
        sa.Column("barcode", sa.String(100)),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "manage_type IN ('serial', 'quantity')", name="items_manage_type_check"
        ),
    )

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("loc_type", sa.String(20), nullable=False),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("locations.id", ondelete="SET NULL")),
        sa.Column("site_id", sa.Integer, sa.ForeignKey("locations.id", ondelete="SET NULL")),
        sa.Column("manager_id", sa.Integer),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "loc_type IN ('site','area','shelf','vehicle','person','customer')",
            name="locations_loc_type_check",
        ),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ad_account", sa.String(100), unique=True, nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(200)),
        sa.Column("password_hash", sa.String(255)),
        sa.Column("role", sa.String(20), nullable=False, server_default="viewer"),
        sa.Column("site_id", sa.Integer, sa.ForeignKey("locations.id", ondelete="SET NULL")),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("last_login", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "role IN ('admin','manager','operator','viewer')", name="users_role_check"
        ),
    )

    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("contact", sa.String(100)),
        sa.Column("email", sa.String(200)),
        sa.Column("phone", sa.String(50)),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "stocks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.Integer, sa.ForeignKey("locations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Integer, server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("quantity >= 0", name="stocks_quantity_nonneg"),
        sa.UniqueConstraint("item_id", "location_id", name="uq_stocks_item_location"),
    )
    op.create_index("idx_stocks_item_location", "stocks", ["item_id", "location_id"])

    op.create_table(
        "serial_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("serial_no", sa.String(100), unique=True, nullable=False),
        sa.Column("mac_address", sa.String(17)),
        sa.Column("location_id", sa.Integer, sa.ForeignKey("locations.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_stock"),
        sa.Column("condition", sa.String(20), server_default="normal"),
        sa.Column("received_at", sa.Date),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('in_stock','checked_out','disposed','lost')",
            name="serial_items_status_check",
        ),
        sa.CheckConstraint(
            "condition IN ('normal','damaged','repair_needed')",
            name="serial_items_condition_check",
        ),
    )
    op.create_index("idx_serial_items_serial_no", "serial_items", ["serial_no"])
    op.create_index("idx_serial_items_location", "serial_items", ["location_id"])
    op.create_index("idx_serial_items_status", "serial_items", ["status"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tx_type", sa.String(20), nullable=False),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("items.id"), nullable=False),
        sa.Column("serial_item_id", sa.Integer, sa.ForeignKey("serial_items.id")),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("from_location_id", sa.Integer, sa.ForeignKey("locations.id")),
        sa.Column("to_location_id", sa.Integer, sa.ForeignKey("locations.id")),
        sa.Column("operator_id", sa.Integer, nullable=False),
        sa.Column("note", sa.Text),
        sa.Column("work_order_no", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "tx_type IN ('in','out','return','transfer','adjust')",
            name="transactions_tx_type_check",
        ),
    )
    op.create_index("idx_transactions_item_id", "transactions", ["item_id"])
    op.create_index("idx_transactions_created_at", "transactions", [sa.text("created_at DESC")])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_no", sa.String(50), unique=True, nullable=False),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("items.id"), nullable=False),
        sa.Column("supplier_id", sa.Integer, sa.ForeignKey("suppliers.id")),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("requested_by", sa.Integer),
        sa.Column("approved_by", sa.Integer),
        sa.Column("ordered_at", sa.Date),
        sa.Column("expected_at", sa.Date),
        sa.Column("note", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('draft','pending','approved','ordered','partial','completed','cancelled')",
            name="orders_status_check",
        ),
    )

    op.create_table(
        "alert_settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("items.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("order_point", sa.Integer, nullable=False, server_default="0"),
        sa.Column("notify_to", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("last_notified_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "stocktake_sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("location_id", sa.Integer, sa.ForeignKey("locations.id")),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("started_by", sa.Integer, nullable=False),
        sa.Column("note", sa.Text),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "status IN ('open','closed','cancelled')",
            name="stocktake_sessions_status_check",
        ),
    )

    op.create_table(
        "stocktake_records",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("stocktake_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer, sa.ForeignKey("items.id"), nullable=False),
        sa.Column("location_id", sa.Integer, sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("expected_qty", sa.Integer, server_default="0"),
        sa.Column("counted_qty", sa.Integer, server_default="0"),
        sa.Column("note", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("stocktake_records")
    op.drop_table("stocktake_sessions")
    op.drop_table("alert_settings")
    op.drop_table("orders")
    op.drop_index("idx_transactions_created_at", table_name="transactions")
    op.drop_index("idx_transactions_item_id", table_name="transactions")
    op.drop_table("transactions")
    op.drop_index("idx_serial_items_status", table_name="serial_items")
    op.drop_index("idx_serial_items_location", table_name="serial_items")
    op.drop_index("idx_serial_items_serial_no", table_name="serial_items")
    op.drop_table("serial_items")
    op.drop_index("idx_stocks_item_location", table_name="stocks")
    op.drop_table("stocks")
    op.drop_table("suppliers")
    op.drop_table("users")
    op.drop_table("locations")
    op.drop_table("items")
