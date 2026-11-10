"""
Auth router — registration, login, token verification, role seeding.

Endpoints:
  POST  /auth/register   — Create a new user account
  POST  /auth/login      — Authenticate and return JWT + user info
  GET   /auth/me         — Return current user from JWT (protected)
  GET   /auth/roles      — List available roles for the registration dropdown
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    RoleResponse,
    UserResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── JWT configuration ─────────────────────────────────────────────────────────

ALGORITHM      = "HS256"
ACCESS_EXPIRE  = timedelta(hours=8)   # tokens valid for 8 hours

_bearer_scheme = HTTPBearer(auto_error=False)


def _create_access_token(user_id: int, email: str, role: Optional[str]) -> str:
    """Create a signed JWT containing user_id, email, and role."""
    payload = {
        "sub":   str(user_id),
        "email": email,
        "role":  role or "",
        "exp":   datetime.now(timezone.utc) + ACCESS_EXPIRE,
        "iat":   datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict:
    """Decode and verify a JWT. Raises HTTPException 401 on failure."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise ValueError("missing sub")
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — extracts and validates the Bearer token,
    returns the authenticated User ORM object.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = _decode_token(credentials.credentials)
    user_id = int(payload["sub"])

    try:
        user = db.query(User).filter(User.id == user_id).first()
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    return user


# ── Default roles ─────────────────────────────────────────────────────────────

DEFAULT_ROLES = [
    {"name": "Admin",              "description": "Full platform administrator access"},
    {"name": "Campaign Manager",   "description": "Create and manage campaigns"},
    {"name": "Communication Team", "description": "Manage messages and audience communication"},
]

RESTRICTED_ROLES = {"Admin"}

FALLBACK_ROLES = [
    RoleResponse(id=1, name="Campaign Manager",   description="Create and manage campaigns"),
    RoleResponse(id=2, name="Communication Team", description="Manage messages and audience communication"),
]

# ── Password helpers ──────────────────────────────────────────────────────────

def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── Role seeding ──────────────────────────────────────────────────────────────

def seed_roles(db: Session) -> None:
    """Idempotently insert default roles. Safe to run on every startup."""
    for role_data in DEFAULT_ROLES:
        if not db.query(Role).filter(Role.name == role_data["name"]).first():
            db.add(Role(name=role_data["name"], description=role_data["description"]))
    db.commit()
    logger.info("Default roles seeded.")


# ── GET /auth/roles ───────────────────────────────────────────────────────────

@router.get(
    "/roles",
    response_model=List[RoleResponse],
    summary="List roles available for registration",
)
def list_roles(db: Session = Depends(get_db)):
    try:
        roles = (
            db.query(Role)
            .filter(Role.name.not_in(RESTRICTED_ROLES))
            .order_by(Role.name)
            .all()
        )
        return roles if roles else FALLBACK_ROLES
    except OperationalError:
        logger.warning("/auth/roles — DB unreachable, returning fallback.")
        return FALLBACK_ROLES
    except SQLAlchemyError as exc:
        logger.error("/auth/roles DB error: %s", exc)
        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ── POST /auth/register ───────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create account. Password hashed with bcrypt; never stored or returned as plain text."""

    if payload.role in RESTRICTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected role cannot be assigned during public registration.",
        )

    try:
        role_obj = db.query(Role).filter(Role.name == payload.role).first()
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    if not role_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{payload.role}' is not valid. Please select a valid role.",
        )

    normalised_email = payload.email.lower().strip()
    try:
        if db.query(User).filter(User.email == normalised_email).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    hashed_pw = _hash_password(payload.password)

    new_user = User(
        name=payload.name.strip(),
        email=normalised_email,
        phone=payload.phone.strip(),
        organization_name=payload.organization_name.strip(),
        password_hash=hashed_pw,
        role_id=role_obj.id,
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    except OperationalError:
        db.rollback()
        raise HTTPException(status_code=503, detail="Database unavailable.")
    except Exception as exc:
        db.rollback()
        logger.error("Registration error: %s", exc)
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

    logger.info("Registered user id=%d email=%s role=%s", new_user.id, new_user.email, role_obj.name)

    return RegisterResponse(
        message="Registration successful",
        user=UserResponse(
            id=new_user.id, name=new_user.name, email=new_user.email,
            phone=new_user.phone, organization_name=new_user.organization_name,
            role=role_obj.name,
        ),
    )


# ── POST /auth/login ──────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and receive a JWT access token",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email and password.
    Returns a signed JWT access token valid for 8 hours.
    Token type: Bearer — include in Authorization header for protected routes.
    """
    normalised_email = payload.email.lower().strip()

    try:
        user = db.query(User).filter(User.email == normalised_email).first()
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    # Vague error — does not reveal whether email or password was wrong
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    role_name = user.role.name if user.role else None
    token = _create_access_token(user.id, user.email, role_name)

    logger.info("User login: id=%d email=%s", user.id, user.email)

    return LoginResponse(
        message="Login successful",
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id, name=user.name, email=user.email,
            phone=user.phone, organization_name=user.organization_name,
            role=role_name,
        ),
    )


# ── GET /auth/me ──────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
    description="Returns the profile of the user identified by the Bearer JWT token.",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Protected endpoint — requires a valid Bearer token from POST /auth/login."""
    role_name = current_user.role.name if current_user.role else None
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        organization_name=current_user.organization_name,
        role=role_name,
    )
