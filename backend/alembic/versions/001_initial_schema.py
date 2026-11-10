"""Initial schema — all core tables and junction tables

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. roles
    # ------------------------------------------------------------------
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_roles_id", "roles", ["id"])
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    # ------------------------------------------------------------------
    # 2. users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role_id", "users", ["role_id"])

    # ------------------------------------------------------------------
    # 3. audience_members
    # ------------------------------------------------------------------
    op.create_table(
        "audience_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column(
            "preferred_language", sa.String(length=10), nullable=False, server_default="en"
        ),
        sa.Column("consent_status", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audience_members_id", "audience_members", ["id"])
    op.create_index("ix_audience_members_email", "audience_members", ["email"])

    # ------------------------------------------------------------------
    # 4. segments
    # ------------------------------------------------------------------
    op.create_table(
        "segments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("filter_criteria", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_segments_id", "segments", ["id"])
    op.create_index("ix_segments_name", "segments", ["name"])

    # ------------------------------------------------------------------
    # 5. campaigns
    # ------------------------------------------------------------------
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="draft"
        ),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_campaigns_id", "campaigns", ["id"])
    op.create_index("ix_campaigns_name", "campaigns", ["name"])
    op.create_index("ix_campaigns_status", "campaigns", ["status"])

    # ------------------------------------------------------------------
    # 6. templates
    # ------------------------------------------------------------------
    op.create_table(
        "templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column(
            "language", sa.String(length=10), nullable=False, server_default="en"
        ),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_templates_id", "templates", ["id"])
    op.create_index("ix_templates_name", "templates", ["name"])
    op.create_index("ix_templates_channel", "templates", ["channel"])

    # ------------------------------------------------------------------
    # 7. messages
    # ------------------------------------------------------------------
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("audience_member_id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=True),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["audience_member_id"], ["audience_members.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["template_id"], ["templates.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_id", "messages", ["id"])
    op.create_index("ix_messages_campaign_id", "messages", ["campaign_id"])
    op.create_index("ix_messages_audience_member_id", "messages", ["audience_member_id"])
    op.create_index("ix_messages_template_id", "messages", ["template_id"])
    op.create_index("ix_messages_status", "messages", ["status"])

    # ------------------------------------------------------------------
    # 8. delivery_logs
    # ------------------------------------------------------------------
    op.create_table(
        "delivery_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("delivery_status", sa.String(length=20), nullable=False),
        sa.Column("error_details", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_delivery_logs_id", "delivery_logs", ["id"])
    op.create_index("ix_delivery_logs_message_id", "delivery_logs", ["message_id"])
    op.create_index("ix_delivery_logs_delivery_status", "delivery_logs", ["delivery_status"])

    # ------------------------------------------------------------------
    # 9. feedback
    # ------------------------------------------------------------------
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("audience_member_id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_feedback_rating_range"),
        sa.ForeignKeyConstraint(
            ["audience_member_id"], ["audience_members.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedback_id", "feedback", ["id"])
    op.create_index("ix_feedback_audience_member_id", "feedback", ["audience_member_id"])
    op.create_index("ix_feedback_campaign_id", "feedback", ["campaign_id"])

    # ------------------------------------------------------------------
    # 10. segment_members  (junction: segments ↔ audience_members)
    # ------------------------------------------------------------------
    op.create_table(
        "segment_members",
        sa.Column("segment_id", sa.Integer(), nullable=False),
        sa.Column("audience_member_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["segment_id"], ["segments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["audience_member_id"], ["audience_members.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("segment_id", "audience_member_id"),
    )

    # ------------------------------------------------------------------
    # 11. campaign_segments  (junction: campaigns ↔ segments)
    # ------------------------------------------------------------------
    op.create_table(
        "campaign_segments",
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("segment_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["segment_id"], ["segments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("campaign_id", "segment_id"),
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("campaign_segments")
    op.drop_table("segment_members")
    op.drop_index("ix_feedback_campaign_id", table_name="feedback")
    op.drop_index("ix_feedback_audience_member_id", table_name="feedback")
    op.drop_index("ix_feedback_id", table_name="feedback")
    op.drop_table("feedback")
    op.drop_index("ix_delivery_logs_delivery_status", table_name="delivery_logs")
    op.drop_index("ix_delivery_logs_message_id", table_name="delivery_logs")
    op.drop_index("ix_delivery_logs_id", table_name="delivery_logs")
    op.drop_table("delivery_logs")
    op.drop_index("ix_messages_status", table_name="messages")
    op.drop_index("ix_messages_template_id", table_name="messages")
    op.drop_index("ix_messages_audience_member_id", table_name="messages")
    op.drop_index("ix_messages_campaign_id", table_name="messages")
    op.drop_index("ix_messages_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_templates_channel", table_name="templates")
    op.drop_index("ix_templates_name", table_name="templates")
    op.drop_index("ix_templates_id", table_name="templates")
    op.drop_table("templates")
    op.drop_index("ix_campaigns_status", table_name="campaigns")
    op.drop_index("ix_campaigns_name", table_name="campaigns")
    op.drop_index("ix_campaigns_id", table_name="campaigns")
    op.drop_table("campaigns")
    op.drop_index("ix_segments_name", table_name="segments")
    op.drop_index("ix_segments_id", table_name="segments")
    op.drop_table("segments")
    op.drop_index("ix_audience_members_email", table_name="audience_members")
    op.drop_index("ix_audience_members_id", table_name="audience_members")
    op.drop_table("audience_members")
    op.drop_index("ix_users_role_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_index("ix_roles_id", table_name="roles")
    op.drop_table("roles")
