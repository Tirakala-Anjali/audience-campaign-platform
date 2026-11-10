"""
Templates router — CRUD for message templates.
All endpoints require JWT authentication.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.template import Template
from app.models.user import User
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/templates", tags=["Templates"])

# ── Schemas ───────────────────────────────────────────────────────────────────

class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    channel: str = Field(..., max_length=20)        # email | sms | push | whatsapp
    language: str = Field("en", max_length=10)
    subject: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1)
    placeholders: Optional[List[str]] = None        # ["name", "company", "date"]
    tags: Optional[List[str]] = None                # ["welcome", "promo"]


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    channel: Optional[str] = Field(None, max_length=20)
    language: Optional[str] = Field(None, max_length=10)
    subject: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    placeholders: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class TemplateRead(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    channel: str
    language: str
    subject: Optional[str] = None
    content: str
    placeholders: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    model_config = {"from_attributes": True}


# ── GET /templates ────────────────────────────────────────────────────────────

@router.get("", response_model=List[TemplateRead], summary="List templates")
def list_templates(
    channel: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Template)
    if channel:  q = q.filter(Template.channel == channel)
    if language: q = q.filter(Template.language == language)
    return q.order_by(Template.created_at.desc()).all()


# ── POST /templates ───────────────────────────────────────────────────────────

@router.post("", response_model=TemplateRead, status_code=201, summary="Create template")
def create_template(
    payload: TemplateCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    tmpl = Template(
        name=payload.name, category=payload.category, channel=payload.channel,
        language=payload.language, subject=payload.subject, content=payload.content,
        placeholders=payload.placeholders, tags=payload.tags,
    )
    db.add(tmpl); db.commit(); db.refresh(tmpl)
    logger.info("Template created: id=%d name=%s channel=%s", tmpl.id, tmpl.name, tmpl.channel)
    return tmpl


# ── GET /templates/{id} ───────────────────────────────────────────────────────

@router.get("/{template_id}", response_model=TemplateRead, summary="Get template")
def get_template(template_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t: raise HTTPException(status_code=404, detail="Template not found.")
    return t


# ── PUT /templates/{id} ───────────────────────────────────────────────────────

@router.put("/{template_id}", response_model=TemplateRead, summary="Update template")
def update_template(
    template_id: int, payload: TemplateUpdate,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t: raise HTTPException(status_code=404, detail="Template not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit(); db.refresh(t)
    return t


# ── DELETE /templates/{id} ────────────────────────────────────────────────────

@router.delete("/{template_id}", status_code=204, summary="Delete template")
def delete_template(template_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t: raise HTTPException(status_code=404, detail="Template not found.")
    db.delete(t); db.commit()
