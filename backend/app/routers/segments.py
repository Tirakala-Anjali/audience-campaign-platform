"""
Segments router — CRUD + preview + members.
All endpoints require JWT authentication.
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audience_member import AudienceMember
from app.models.segment import Segment
from app.models.user import User
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/segments", tags=["Segments"])

# ── Schemas ───────────────────────────────────────────────────────────────────

class SegmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    filter_criteria: Optional[Dict[str, Any]] = Field(
        None,
        description='Filter rules, e.g. {"operator":"AND","rules":[{"field":"city","op":"eq","value":"Mumbai"}]}'
    )


class SegmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    filter_criteria: Optional[Dict[str, Any]] = None


class SegmentRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    filter_criteria: Optional[Dict[str, Any]] = None
    model_config = {"from_attributes": True}


class PreviewRequest(BaseModel):
    name: Optional[str] = None
    filter_criteria: Optional[Dict[str, Any]] = None


class PreviewResponse(BaseModel):
    matching_count: int
    sample: List[Dict[str, Any]]


# ── Filter engine ─────────────────────────────────────────────────────────────

ALLOWED_FIELDS = {
    "age", "gender", "city", "state", "occupation", "department",
    "preferred_language", "preferred_channel", "consent_status", "organization",
}
ALLOWED_OPS = {"eq", "ne", "gt", "lt", "gte", "lte", "contains", "in"}


def _apply_filter_criteria(q, criteria: Optional[Dict[str, Any]]):
    """
    Apply filter_criteria dict to a query.
    Format: {"operator": "AND"|"OR", "rules": [{"field": str, "op": str, "value": any}]}
    Returns the filtered query.
    """
    if not criteria:
        return q

    rules = criteria.get("rules", [])
    op = criteria.get("operator", "AND").upper()
    conditions = []

    for rule in rules:
        field = rule.get("field", "")
        operation = rule.get("op", "eq")
        value = rule.get("value")

        if field not in ALLOWED_FIELDS:
            continue
        if operation not in ALLOWED_OPS:
            continue

        col = getattr(AudienceMember, field, None)
        if col is None:
            continue

        if operation == "eq":
            conditions.append(col == value)
        elif operation == "ne":
            conditions.append(col != value)
        elif operation == "gt":
            conditions.append(col > value)
        elif operation == "lt":
            conditions.append(col < value)
        elif operation == "gte":
            conditions.append(col >= value)
        elif operation == "lte":
            conditions.append(col <= value)
        elif operation == "contains":
            conditions.append(col.ilike(f"%{value}%"))
        elif operation == "in":
            if isinstance(value, list):
                conditions.append(col.in_(value))

    if not conditions:
        return q

    from sqlalchemy import and_, or_ as sql_or
    combiner = and_ if op == "AND" else sql_or
    return q.filter(combiner(*conditions))


# ── GET /segments ─────────────────────────────────────────────────────────────

@router.get("", response_model=List[SegmentRead], summary="List segments")
def list_segments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Segment).order_by(Segment.created_at.desc()).all()


# ── POST /segments ────────────────────────────────────────────────────────────

@router.post("", response_model=SegmentRead, status_code=201, summary="Create segment")
def create_segment(payload: SegmentCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    seg = Segment(name=payload.name, description=payload.description,
                  filter_criteria=payload.filter_criteria)
    db.add(seg); db.commit(); db.refresh(seg)
    logger.info("Segment created: id=%d name=%s", seg.id, seg.name)
    return seg


# ── GET /segments/{id} ────────────────────────────────────────────────────────

@router.get("/{segment_id}", response_model=SegmentRead, summary="Get segment")
def get_segment(segment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    seg = db.query(Segment).filter(Segment.id == segment_id).first()
    if not seg: raise HTTPException(status_code=404, detail="Segment not found.")
    return seg


# ── PUT /segments/{id} ────────────────────────────────────────────────────────

@router.put("/{segment_id}", response_model=SegmentRead, summary="Update segment")
def update_segment(segment_id: int, payload: SegmentUpdate,
                   db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    seg = db.query(Segment).filter(Segment.id == segment_id).first()
    if not seg: raise HTTPException(status_code=404, detail="Segment not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(seg, k, v)
    db.commit(); db.refresh(seg)
    return seg


# ── DELETE /segments/{id} ─────────────────────────────────────────────────────

@router.delete("/{segment_id}", status_code=204, summary="Delete segment")
def delete_segment(segment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    seg = db.query(Segment).filter(Segment.id == segment_id).first()
    if not seg: raise HTTPException(status_code=404, detail="Segment not found.")
    db.delete(seg); db.commit()


# ── POST /segments/preview ────────────────────────────────────────────────────

@router.post("/preview", response_model=PreviewResponse, summary="Preview matching members")
def preview_segment(payload: PreviewRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    q = db.query(AudienceMember)
    q = _apply_filter_criteria(q, payload.filter_criteria)
    count = q.count()
    sample_rows = q.limit(5).all()
    sample = [{"id": m.id, "name": m.name, "email": m.email,
               "city": m.city, "gender": m.gender, "consent": m.consent_status}
              for m in sample_rows]
    return PreviewResponse(matching_count=count, sample=sample)


# ── GET /segments/{id}/members ────────────────────────────────────────────────

@router.get("/{segment_id}/members", summary="Get segment members")
def get_segment_members(segment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    seg = db.query(Segment).filter(Segment.id == segment_id).first()
    if not seg: raise HTTPException(status_code=404, detail="Segment not found.")
    q = db.query(AudienceMember)
    q = _apply_filter_criteria(q, seg.filter_criteria)
    members = q.all()
    return {"segment_id": segment_id, "segment_name": seg.name,
            "member_count": len(members),
            "members": [{"id": m.id, "name": m.name, "email": m.email} for m in members]}
