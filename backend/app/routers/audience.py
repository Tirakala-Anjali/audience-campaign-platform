"""
Audience router — CRUD, stats, and CSV import for audience members.
All endpoints require JWT authentication.
"""
import csv, io, logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audience_member import AudienceMember
from app.models.user import User
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/audience", tags=["Audience"])

# ── Schemas ───────────────────────────────────────────────────────────────────

class AudienceMemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=150)
    preferred_language: str = Field("en", max_length=10)
    preferred_channel: Optional[str] = Field(None, max_length=20)
    consent_status: bool = False


class AudienceMemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=150)
    preferred_language: Optional[str] = Field(None, max_length=10)
    preferred_channel: Optional[str] = Field(None, max_length=20)
    consent_status: Optional[bool] = None


class AudienceMemberRead(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    department: Optional[str] = None
    organization: Optional[str] = None
    preferred_language: str
    preferred_channel: Optional[str] = None
    consent_status: bool
    model_config = {"from_attributes": True}


class AudienceListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AudienceMemberRead]


class AudienceStats(BaseModel):
    total: int
    consented: int
    consent_rate_pct: float
    by_channel: dict
    by_language: dict
    by_gender: dict


class ImportResult(BaseModel):
    imported: int
    skipped: int
    errors: List[str]


# ── GET /audience/stats ───────────────────────────────────────────────────────

@router.get("/stats", response_model=AudienceStats, summary="Audience statistics")
def get_audience_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    total = db.query(func.count(AudienceMember.id)).scalar() or 0
    consented = db.query(func.count(AudienceMember.id)).filter(
        AudienceMember.consent_status == True).scalar() or 0   # noqa: E712

    # Group-by channel
    channel_rows = db.query(AudienceMember.preferred_channel,
                            func.count(AudienceMember.id)).group_by(
        AudienceMember.preferred_channel).all()
    by_channel = {(r[0] or "unset"): r[1] for r in channel_rows}

    lang_rows = db.query(AudienceMember.preferred_language,
                         func.count(AudienceMember.id)).group_by(
        AudienceMember.preferred_language).all()
    by_language = {(r[0] or "en"): r[1] for r in lang_rows}

    gender_rows = db.query(AudienceMember.gender,
                           func.count(AudienceMember.id)).group_by(
        AudienceMember.gender).all()
    by_gender = {(r[0] or "unspecified"): r[1] for r in gender_rows}

    return AudienceStats(
        total=total,
        consented=consented,
        consent_rate_pct=round((consented / total * 100), 1) if total else 0.0,
        by_channel=by_channel,
        by_language=by_language,
        by_gender=by_gender,
    )


# ── GET /audience ─────────────────────────────────────────────────────────────

@router.get("", response_model=AudienceListResponse, summary="List audience members")
def list_audience(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search name or email"),
    city: Optional[str] = None,
    state: Optional[str] = None,
    gender: Optional[str] = None,
    consent: Optional[bool] = None,
    language: Optional[str] = None,
    channel: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(AudienceMember)
    if search:
        q = q.filter(or_(
            AudienceMember.name.ilike(f"%{search}%"),
            AudienceMember.email.ilike(f"%{search}%"),
        ))
    if city:     q = q.filter(AudienceMember.city.ilike(f"%{city}%"))
    if state:    q = q.filter(AudienceMember.state.ilike(f"%{state}%"))
    if gender:   q = q.filter(AudienceMember.gender == gender)
    if consent is not None: q = q.filter(AudienceMember.consent_status == consent)
    if language: q = q.filter(AudienceMember.preferred_language == language)
    if channel:  q = q.filter(AudienceMember.preferred_channel == channel)

    total = q.count()
    items = q.order_by(AudienceMember.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    return AudienceListResponse(total=total, page=page, page_size=page_size, items=items)


# ── POST /audience ────────────────────────────────────────────────────────────

@router.post("", response_model=AudienceMemberRead, status_code=201, summary="Create audience member")
def create_member(
    payload: AudienceMemberCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    normalised = payload.email.lower().strip()
    if db.query(AudienceMember).filter(AudienceMember.email == normalised).first():
        raise HTTPException(status_code=409, detail="An audience member with this email already exists.")

    member = AudienceMember(
        **{k: v for k, v in payload.model_dump().items() if k != "email"},
        email=normalised,
    )
    try:
        db.add(member); db.commit(); db.refresh(member)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Duplicate email.")
    return member


# ── GET /audience/{id} ────────────────────────────────────────────────────────

@router.get("/{member_id}", response_model=AudienceMemberRead, summary="Get audience member")
def get_member(member_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    m = db.query(AudienceMember).filter(AudienceMember.id == member_id).first()
    if not m: raise HTTPException(status_code=404, detail="Audience member not found.")
    return m


# ── PUT /audience/{id} ────────────────────────────────────────────────────────

@router.put("/{member_id}", response_model=AudienceMemberRead, summary="Update audience member")
def update_member(
    member_id: int, payload: AudienceMemberUpdate,
    db: Session = Depends(get_db), _: User = Depends(get_current_user),
):
    m = db.query(AudienceMember).filter(AudienceMember.id == member_id).first()
    if not m: raise HTTPException(status_code=404, detail="Audience member not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    db.commit(); db.refresh(m)
    return m


# ── DELETE /audience/{id} ─────────────────────────────────────────────────────

@router.delete("/{member_id}", status_code=204, summary="Delete audience member")
def delete_member(member_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    m = db.query(AudienceMember).filter(AudienceMember.id == member_id).first()
    if not m: raise HTTPException(status_code=404, detail="Audience member not found.")
    db.delete(m); db.commit()


# ── POST /audience/import ─────────────────────────────────────────────────────

@router.post("/import", response_model=ImportResult, summary="Bulk CSV import")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))

    imported = 0; skipped = 0; errors = []
    REQUIRED = {"name", "email"}

    for i, row in enumerate(reader, start=2):
        row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
        missing = REQUIRED - set(row.keys())
        if missing:
            errors.append(f"Row {i}: missing columns {missing}")
            skipped += 1; continue

        email = row.get("email", "").lower().strip()
        name  = row.get("name", "").strip()
        if not email or not name:
            errors.append(f"Row {i}: empty name or email"); skipped += 1; continue

        if db.query(AudienceMember).filter(AudienceMember.email == email).first():
            errors.append(f"Row {i}: duplicate email {email}"); skipped += 1; continue

        def safe_int(v):
            try: return int(v) if v else None
            except: return None

        member = AudienceMember(
            name=name, email=email,
            phone=row.get("phone") or None,
            age=safe_int(row.get("age")),
            gender=row.get("gender") or None,
            city=row.get("city") or None,
            state=row.get("state") or None,
            occupation=row.get("occupation") or None,
            department=row.get("department") or None,
            organization=row.get("organization") or None,
            preferred_language=row.get("preferred_language") or "en",
            preferred_channel=row.get("preferred_channel") or None,
            consent_status=row.get("consent_status","").lower() in ("true","1","yes"),
        )
        db.add(member); imported += 1

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error("CSV import commit failed: %s", exc)
        raise HTTPException(status_code=500, detail="Import failed. Please check your file.")

    return ImportResult(imported=imported, skipped=skipped, errors=errors[:50])
