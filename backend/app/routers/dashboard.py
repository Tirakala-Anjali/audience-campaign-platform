"""
Dashboard router — aggregated statistics for the dashboard page.

GET /dashboard/stats  — Returns role-aware statistics (JWT required)

Role behaviour:
  Admin / Campaign Manager  → campaign-focused stats
  Communication Team        → audience/message-focused stats
  (All roles see the full stats object; the frontend picks what to display)
"""
import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audience_member import AudienceMember
from app.models.campaign import Campaign
from app.models.message import Message
from app.models.user import User
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ── Response schemas ──────────────────────────────────────────────────────────

class CampaignStatusCount(BaseModel):
    status: str
    count: int


class RecentCampaign(BaseModel):
    id: int
    name: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    # Common
    user_role: str
    total_registered_users: int

    # Campaign-focused (all roles)
    total_campaigns: int
    active_campaigns: int
    draft_campaigns: int
    paused_campaigns: int
    completed_campaigns: int
    cancelled_campaigns: int
    status_breakdown: List[CampaignStatusCount]
    recent_campaigns: List[RecentCampaign]

    # Audience / Communication-focused
    total_audience_members: int
    consented_audience_members: int
    total_messages_sent: int


# ── GET /dashboard/stats ──────────────────────────────────────────────────────

@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Get role-aware dashboard statistics",
)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch dashboard statistics from the database.
    Returns the same schema for all roles; the frontend selects
    which cards to display based on the user_role field.
    """
    try:
        # ── Campaign counts ───────────────────────────────────────────────────
        total_campaigns = db.query(func.count(Campaign.id)).scalar() or 0

        status_rows = (
            db.query(Campaign.status, func.count(Campaign.id).label("cnt"))
            .group_by(Campaign.status)
            .all()
        )
        status_map: Dict[str, int] = {row.status: row.cnt for row in status_rows}

        active_campaigns    = status_map.get("active",    0)
        draft_campaigns     = status_map.get("draft",     0)
        paused_campaigns    = status_map.get("paused",    0)
        completed_campaigns = status_map.get("completed", 0)
        cancelled_campaigns = status_map.get("cancelled", 0)

        status_breakdown = [
            CampaignStatusCount(status=s, count=c)
            for s, c in sorted(status_map.items())
        ]

        # ── Audience / Communication stats ────────────────────────────────────
        total_audience_members = db.query(func.count(AudienceMember.id)).scalar() or 0

        consented_audience_members = (
            db.query(func.count(AudienceMember.id))
            .filter(AudienceMember.consent_status == True)   # noqa: E712
            .scalar() or 0
        )

        total_messages_sent = db.query(func.count(Message.id)).scalar() or 0

        # ── Registered users ──────────────────────────────────────────────────
        total_registered_users = db.query(func.count(User.id)).scalar() or 0

        # ── Recent campaigns ──────────────────────────────────────────────────
        recent_rows = (
            db.query(Campaign)
            .order_by(Campaign.created_at.desc())
            .limit(5)
            .all()
        )
        recent_campaigns = [
            RecentCampaign(
                id=c.id,
                name=c.name,
                status=c.status,
                created_at=c.created_at.isoformat() if c.created_at else "",
            )
            for c in recent_rows
        ]

        # ── Determine role name ───────────────────────────────────────────────
        user_role = current_user.role.name if current_user.role else "Unknown"

    except OperationalError as exc:
        logger.error("DB error in /dashboard/stats: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is currently unavailable. Please try again shortly.",
        )
    except SQLAlchemyError as exc:
        logger.error("DB query error in /dashboard/stats: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics.",
        )

    logger.debug(
        "Dashboard stats: role=%s campaigns=%d audience=%d messages=%d",
        user_role, total_campaigns, total_audience_members, total_messages_sent,
    )

    return DashboardStats(
        user_role=user_role,
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        draft_campaigns=draft_campaigns,
        paused_campaigns=paused_campaigns,
        completed_campaigns=completed_campaigns,
        cancelled_campaigns=cancelled_campaigns,
        status_breakdown=status_breakdown,
        recent_campaigns=recent_campaigns,
        total_audience_members=total_audience_members,
        consented_audience_members=consented_audience_members,
        total_messages_sent=total_messages_sent,
        total_registered_users=total_registered_users,
    )
