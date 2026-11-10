"""
Models package — import every model here so that:
  1. Alembic autogenerate can discover all tables.
  2. SQLAlchemy relationship resolution works at startup.
"""

from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

# ---------------------------------------------------------------------------
# Junction tables (many-to-many, no extra columns needed)
# ---------------------------------------------------------------------------

# Segment ↔ AudienceMember
segment_members = Table(
    "segment_members",
    Base.metadata,
    Column(
        "segment_id",
        Integer,
        ForeignKey("segments.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "audience_member_id",
        Integer,
        ForeignKey("audience_members.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)

# Campaign ↔ Segment
campaign_segments = Table(
    "campaign_segments",
    Base.metadata,
    Column(
        "campaign_id",
        Integer,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "segment_id",
        Integer,
        ForeignKey("segments.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)

# ---------------------------------------------------------------------------
# ORM model imports — order matters (parents before children)
# ---------------------------------------------------------------------------

from app.models.role import Role  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
from app.models.audience_member import AudienceMember  # noqa: E402, F401
from app.models.segment import Segment  # noqa: E402, F401
from app.models.campaign import Campaign  # noqa: E402, F401
from app.models.template import Template  # noqa: E402, F401
from app.models.message import Message  # noqa: E402, F401
from app.models.delivery_log import DeliveryLog  # noqa: E402, F401
from app.models.feedback import Feedback  # noqa: E402, F401

__all__ = [
    "Role",
    "User",
    "AudienceMember",
    "Segment",
    "Campaign",
    "Template",
    "Message",
    "DeliveryLog",
    "Feedback",
    "segment_members",
    "campaign_segments",
]
