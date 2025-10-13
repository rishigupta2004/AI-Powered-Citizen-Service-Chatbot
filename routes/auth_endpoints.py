"""
Authentication API endpoints with multiple auth methods
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets
import json
import re
from pydantic import BaseModel, EmailStr, validator

from core.database import SessionLocal, get_db
from core.auth_models import (
    User, UserAuthMethod, UserSession, OTPAttempt, PasswordReset, LoginAttempt,
    AuthMethod, UserRole, generate_session_token, generate_refresh_token,
    generate_otp_code, get_token_expiry, get_otp_expiry
)

# Security scheme
security = HTTPBearer()

# Router
router = APIRouter(prefix="/auth", tags=["Authentication"])


# Pydantic models for requests/responses
class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    method: AuthMethod = AuthMethod.EMAIL_PASSWORD

    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v


class SignupRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    first_name: str
    last_name: str
    method: AuthMethod = AuthMethod.EMAIL_PASSWORD

    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class OTPRequest(BaseModel):
    contact: str
    contact_type: AuthMethod
    purpose: str = "login"  # login, signup, reset_password


class OTPVerifyRequest(BaseModel):
    contact: str
    otp_code: str
    contact_type: AuthMethod


class GoogleAuthRequest(BaseModel):
    access_token: str
    id_token: Optional[str] = None


class AadhaarAuthRequest(BaseModel):
    aadhaar_number: str
    otp_code: str
    name: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: int
    uuid: str
    email: Optional[str]
    phone: Optional[str]
    first_name: str
    last_name: str
    full_name: str
    is_verified: bool
    role: str
    created_at: datetime


# Utility functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def hash_aadhaar(aadhaar: str) -> str:
    """Hash Aadhaar number for storage"""
    return hashlib.sha256(aadhaar.encode()).hexdigest()


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def create_user_session(db: Session, user_id: int, request: Request) -> UserSession:
    """Create a new user session"""
    session_token = generate_session_token()
    refresh_token = generate_refresh_token()
    
    session = UserSession(
        user_id=user_id,
        session_token=session_token,
        refresh_token=refresh_token,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        expires_at=get_token_expiry(24)  # 24 hours
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def log_login_attempt(db: Session, email: Optional[str], phone: Optional[str], 
                     request: Request, success: bool, failure_reason: Optional[str] = None):
    """Log login attempt for security"""
    attempt = LoginAttempt(
        email=email,
        phone=phone,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        success=success,
        failure_reason=failure_reason
    )
    db.add(attempt)
    db.commit()


# Authentication endpoints
@router.post("/register", response_model=AuthResponse)
async def register(request: SignupRequest, req: Request, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        or_(
            and_(User.email == request.email, User.email.isnot(None)),
            and_(User.phone == request.phone, User.phone.isnot(None))
        )
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exists"
        )
    
    # Create new user
    password_hash = hash_password(request.password)
    full_name = f"{request.first_name} {request.last_name}"
    
    user = User(
        email=request.email,
        phone=request.phone,
        first_name=request.first_name,
        last_name=request.last_name,
        full_name=full_name,
        password_hash=password_hash,
        is_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add auth method
    auth_method = UserAuthMethod(
        user_id=user.id,
        method=request.method
    )
    db.add(auth_method)
    db.commit()
    
    # Create session
    session = create_user_session(db, user.id, req)
    
    # Log successful registration
    log_login_attempt(db, request.email, request.phone, req, True)
    
    return AuthResponse(
        access_token=session.session_token,
        refresh_token=session.refresh_token,
        expires_in=86400,  # 24 hours
        user={
            "id": user.id,
            "uuid": user.uuid,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "role": user.role.value
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    """Login with email/phone and password"""
    # Find user
    user = db.query(User).filter(
        or_(
            and_(User.email == request.email, User.email.isnot(None)),
            and_(User.phone == request.phone, User.phone.isnot(None))
        )
    ).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        log_login_attempt(db, request.email, request.phone, req, False, "Invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/phone or password"
        )
    
    if not user.is_active:
        log_login_attempt(db, request.email, request.phone, req, False, "Account disabled")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create session
    session = create_user_session(db, user.id, req)
    
    # Log successful login
    log_login_attempt(db, request.email, request.phone, req, True)
    
    return AuthResponse(
        access_token=session.session_token,
        refresh_token=session.refresh_token,
        expires_in=86400,  # 24 hours
        user={
            "id": user.id,
            "uuid": user.uuid,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "role": user.role.value
        }
    )


@router.post("/otp/send")
async def send_otp(request: OTPRequest, db: Session = Depends(get_db)):
    """Send OTP to email or phone"""
    # Generate OTP
    otp_code = generate_otp_code()
    otp_hash = hash_password(otp_code)
    
    # Create OTP attempt record
    otp_attempt = OTPAttempt(
        contact=request.contact,
        contact_type=request.contact_type,
        otp_code=otp_code,
        otp_hash=otp_hash,
        expires_at=get_otp_expiry(10)  # 10 minutes
    )
    
    db.add(otp_attempt)
    db.commit()
    
    # In a real implementation, send OTP via SMS/Email
    # For now, return the OTP for testing
    return {
        "message": "OTP sent successfully",
        "otp": otp_code,  # Remove this in production
        "expires_in": 600  # 10 minutes
    }


@router.post("/otp/verify", response_model=AuthResponse)
async def verify_otp(request: OTPVerifyRequest, req: Request, db: Session = Depends(get_db)):
    """Verify OTP and login/register"""
    # Find valid OTP attempt
    otp_attempt = db.query(OTPAttempt).filter(
        and_(
            OTPAttempt.contact == request.contact,
            OTPAttempt.contact_type == request.contact_type,
            OTPAttempt.expires_at > datetime.utcnow(),
            OTPAttempt.attempts < OTPAttempt.max_attempts,
            OTPAttempt.is_verified == False
        )
    ).first()
    
    if not otp_attempt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Verify OTP
    if not verify_password(request.otp_code, otp_attempt.otp_hash):
        otp_attempt.attempts += 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code"
        )
    
    # Mark OTP as verified
    otp_attempt.is_verified = True
    otp_attempt.verified_at = datetime.utcnow()
    db.commit()
    
    # Find or create user
    user = db.query(User).filter(
        or_(
            and_(User.email == request.contact, User.email.isnot(None)),
            and_(User.phone == request.contact, User.phone.isnot(None))
        )
    ).first()
    
    if not user:
        # Create new user for OTP registration
        full_name = "User"  # Default name, can be updated later
        
        user = User(
            email=request.contact if request.contact_type == AuthMethod.OTP_EMAIL else None,
            phone=request.contact if request.contact_type == AuthMethod.OTP_SMS else None,
            first_name="User",
            last_name="",
            full_name=full_name,
            is_verified=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Add OTP auth method
        auth_method = UserAuthMethod(
            user_id=user.id,
            method=request.contact_type
        )
        db.add(auth_method)
        db.commit()
    
    # Create session
    session = create_user_session(db, user.id, req)
    
    return AuthResponse(
        access_token=session.session_token,
        refresh_token=session.refresh_token,
        expires_in=86400,  # 24 hours
        user={
            "id": user.id,
            "uuid": user.uuid,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "role": user.role.value
        }
    )


@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, req: Request, db: Session = Depends(get_db)):
    """Google OAuth authentication"""
    # In a real implementation, verify the Google token
    # For now, simulate Google user data
    google_user_data = {
        "email": "user@gmail.com",  # Extract from token
        "name": "Google User",
        "given_name": "Google",
        "family_name": "User",
        "sub": "google_user_id"
    }
    
    # Find existing user
    user = db.query(User).filter(User.email == google_user_data["email"]).first()
    
    if not user:
        # Create new user
        user = User(
            email=google_user_data["email"],
            first_name=google_user_data["given_name"],
            last_name=google_user_data["family_name"],
            full_name=google_user_data["name"],
            is_verified=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Add Google auth method
        auth_method = UserAuthMethod(
            user_id=user.id,
            method=AuthMethod.GOOGLE_OAUTH,
            provider_id=google_user_data["sub"],
            provider_data=json.dumps(google_user_data)
        )
        db.add(auth_method)
        db.commit()
    
    # Create session
    session = create_user_session(db, user.id, req)
    
    return AuthResponse(
        access_token=session.session_token,
        refresh_token=session.refresh_token,
        expires_in=86400,  # 24 hours
        user={
            "id": user.id,
            "uuid": user.uuid,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "role": user.role.value
        }
    )


@router.post("/aadhaar", response_model=AuthResponse)
async def aadhaar_auth(request: AadhaarAuthRequest, req: Request, db: Session = Depends(get_db)):
    """Aadhaar-based authentication"""
    # In a real implementation, verify Aadhaar with UIDAI
    # For now, simulate Aadhaar verification
    aadhaar_hash = hash_aadhaar(request.aadhaar_number)
    
    # Find user by Aadhaar hash
    user = db.query(User).filter(User.aadhaar_number_hash == aadhaar_hash).first()
    
    if not user:
        # Create new user with Aadhaar
        full_name = request.name or "Aadhaar User"
        name_parts = full_name.split(" ", 1)
        
        user = User(
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else "",
            full_name=full_name,
            aadhaar_number_hash=aadhaar_hash,
            aadhaar_verified=True,
            is_verified=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Add Aadhaar auth method
        auth_method = UserAuthMethod(
            user_id=user.id,
            method=AuthMethod.AADHAAR
        )
        db.add(auth_method)
        db.commit()
    
    # Create session
    session = create_user_session(db, user.id, req)
    
    return AuthResponse(
        access_token=session.session_token,
        refresh_token=session.refresh_token,
        expires_in=86400,  # 24 hours
        user={
            "id": user.id,
            "uuid": user.uuid,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "role": user.role.value
        }
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest, req: Request, db: Session = Depends(get_db)):
    """Refresh access token"""
    session = db.query(UserSession).filter(
        and_(
            UserSession.refresh_token == request.refresh_token,
            UserSession.expires_at > datetime.utcnow()
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new session
    new_session = create_user_session(db, session.user_id, req)
    
    # Invalidate old session
    db.delete(session)
    db.commit()
    
    user = db.query(User).filter(User.id == new_session.user_id).first()
    
    return AuthResponse(
        access_token=new_session.session_token,
        refresh_token=new_session.refresh_token,
        expires_in=86400,  # 24 hours
        user={
            "id": user.id,
            "uuid": user.uuid,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "role": user.role.value
        }
    )


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), 
                db: Session = Depends(get_db)):
    """Logout and invalidate session"""
    session = db.query(UserSession).filter(
        UserSession.session_token == credentials.credentials
    ).first()
    
    if session:
        db.delete(session)
        db.commit()
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                          db: Session = Depends(get_db)):
    """Get current user information"""
    session = db.query(UserSession).filter(
        and_(
            UserSession.session_token == credentials.credentials,
            UserSession.expires_at > datetime.utcnow()
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        uuid=user.uuid,
        email=user.email,
        phone=user.phone,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        is_verified=user.is_verified,
        role=user.role.value,
        created_at=user.created_at
    )


# Dependency to get current user
async def get_current_user_dependency(credentials: HTTPAuthorizationCredentials = Depends(security),
                                     db: Session = Depends(get_db)) -> User:
    """Dependency to get current authenticated user"""
    session = db.query(UserSession).filter(
        and_(
            UserSession.session_token == credentials.credentials,
            UserSession.expires_at > datetime.utcnow()
        )
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
