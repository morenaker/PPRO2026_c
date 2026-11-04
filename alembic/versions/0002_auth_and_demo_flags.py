"""app_user a příznak is_demo

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

DEMO_TABLES = ("patient", "doctor", "procedure", "appointment")


def upgrade() -> None:
    op.create_table(
        "app_user",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("password_hash", sa.String(200), nullable=False),
        sa.UniqueConstraint("username", name="uq_app_user_username"),
        sa.CheckConstraint("role IN ('admin', 'reception')", name="ck_app_user_role_values"),
    )
    for table in DEMO_TABLES:
        op.add_column(table, sa.Column("is_demo", sa.Boolean, nullable=False, server_default=sa.false()))


def downgrade() -> None:
    for table in DEMO_TABLES:
        op.drop_column(table, "is_demo")
    op.drop_table("app_user")
