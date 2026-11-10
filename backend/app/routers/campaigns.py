"""
Campaigns router — full CRUD with spec fields.
Emergency campaigns are automatically assigned 'high' priority.
All endpoints require a valid JWT Bearer token.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.campaign import Campaign
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.campaign_schemas import CampaignCreate, CampaignRead, CampaignUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


def _get_campaign_or_404(campaign_id: int, db: Session) -> Campaign:
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found.")
    return c


# ── GET /campaigns ────────────────────────────────────────────────────────────

@router.get("", response_model=List[CampaignRead], summary="List all campaigns")
def list_campaigns(
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(Campaign).order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()


# ── POST /campaigns ───────────────────────────────────────────────────────────

@router.post("", response_model=CampaignRead, status_code=201, summary="Create a campaign")
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Emergency campaigns always get 'high' priority
    priority = payload.priority.value
    if payload.campaign_type and "emergency" in payload.campaign_type.lower():
        priority = "high"
    if priority == "emergency":
        priority = "high"

    campaign = Campaign(
        name=payload.name.strip(),
        description=payload.description,
        campaign_type=payload.campaign_type,
        objective=payload.objective,
        channels=payload.channels,
        status=payload.status.value,
        priority=priority,
        start_at=payload.start_at,
        end_at=payload.end_at,
        creator_id=current_user.id,
    )
    try:
        db.add(campaign); db.commit(); db.refresh(campaign)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Create campaign error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create campaign.")
    logger.info("Campaign created: id=%d name=%s priority=%s", campaign.id, campaign.name, priority)
    return campaign


# ── GET /campaigns/{id} ───────────────────────────────────────────────────────

@router.get("/{campaign_id}", response_model=CampaignRead, summary="Get campaign by ID")
def get_campaign(campaign_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return _get_campaign_or_404(campaign_id, db)


# ── PUT /campaigns/{id} ───────────────────────────────────────────────────────

@router.put("/{campaign_id}", response_model=CampaignRead, summary="Update campaign")
def update_campaign(
    campaign_id: int, payload: CampaignUpdate,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    campaign = _get_campaign_or_404(campaign_id, db)
    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        if value is not None and hasattr(value, 'value'):
            setattr(campaign, field, value.value)
        else:
            setattr(campaign, field, value)

    # Re-enforce emergency priority
    ctype = getattr(campaign, 'campaign_type', '') or ''
    if 'emergency' in ctype.lower():
        campaign.priority = 'high'

    try:
        db.commit(); db.refresh(campaign)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update campaign.")
    return campaign


# ── DELETE /campaigns/{id} ────────────────────────────────────────────────────

@router.delete("/{campaign_id}", status_code=204, summary="Delete campaign")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    campaign = _get_campaign_or_404(campaign_id, db)
    try:
        db.delete(campaign); db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete campaign.")
