"""Add spec fields: audience demographics, campaign type/priority/channels, template category/tags

Revision ID: 003
Revises: 002
Create Date: 2025-01-03 00:00:00.000000
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── audience_members: add demographic fields ──────────────────────────────
    op.add_column("audience_members", sa.Column("age",               sa.Integer(),     nullable=True))
    op.add_column("audience_members", sa.Column("gender",            sa.String(20),    nullable=True))
    op.add_column("audience_members", sa.Column("city",              sa.String(100),   nullable=True))
    op.add_column("audience_members", sa.Column("state",             sa.String(100),   nullable=True))
    op.add_column("audience_members", sa.Column("occupation",        sa.String(100),   nullable=True))
    op.add_column("audience_members", sa.Column("department",        sa.String(100),   nullable=True))
    op.add_column("audience_members", sa.Column("organization",      sa.String(150),   nullable=True))
    op.add_column("audience_members", sa.Column("preferred_channel", sa.String(20),    nullable=True))

    # ── campaigns: add spec fields ────────────────────────────────────────────
    op.add_column("campaigns", sa.Column("campaign_type", sa.String(50),   nullable=True))
    op.add_column("campaigns", sa.Column("objective",     sa.String(255),  nullable=True))
    op.add_column("campaigns", sa.Column("channels",      sa.JSON(),       nullable=True))
    op.add_column("campaigns", sa.Column("priority",      sa.String(20),   nullable=False, server_default="medium"))
    op.add_column("campaigns", sa.Column("creator_id",    sa.Integer(),    nullable=True))
    op.create_foreign_key("fk_campaigns_creator_id", "campaigns", "users", ["creator_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_campaigns_creator_id", "campaigns", ["creator_id"])

    # ── templates: add spec fields ────────────────────────────────────────────
    op.add_column("templates", sa.Column("category",     sa.String(50),  nullable=True))
    op.add_column("templates", sa.Column("placeholders", sa.JSON(),      nullable=True))
    op.add_column("templates", sa.Column("tags",         sa.JSON(),      nullable=True))


def downgrade() -> None:
    # templates
    op.drop_column("templates", "tags")
    op.drop_column("templates", "placeholders")
    op.drop_column("templates", "category")

    # campaigns
    op.drop_index("ix_campaigns_creator_id", table_name="campaigns")
    op.drop_constraint("fk_campaigns_creator_id", "campaigns", type_="foreignkey")
    op.drop_column("campaigns", "creator_id")
    op.drop_column("campaigns", "priority")
    op.drop_column("campaigns", "channels")
    op.drop_column("campaigns", "objective")
    op.drop_column("campaigns", "campaign_type")

    # audience_members
    op.drop_column("audience_members", "preferred_channel")
    op.drop_column("audience_members", "organization")
    op.drop_column("audience_members", "department")
    op.drop_column("audience_members", "occupation")
    op.drop_column("audience_members", "state")
    op.drop_column("audience_members", "city")
    op.drop_column("audience_members", "gender")
    op.drop_column("audience_members", "age")
