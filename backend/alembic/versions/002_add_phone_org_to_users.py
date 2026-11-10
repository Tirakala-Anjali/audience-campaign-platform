"""Add phone and organization_name to users table

Revision ID: 002
Revises: 001
Create Date: 2025-01-02 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add phone column — nullable so existing rows are unaffected
    op.add_column(
        "users",
        sa.Column("phone", sa.String(length=30), nullable=True),
    )
    # Add organization_name column — nullable so existing rows are unaffected
    op.add_column(
        "users",
        sa.Column("organization_name", sa.String(length=150), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "organization_name")
    op.drop_column("users", "phone")
