"""
Authentication models for user management and multiple auth methods
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid
from datetime import datetime, timedelta
from .database import Base


class AuthMethod(str, Enum):
    """Authentication methods supported"""
    EMAIL_PASSWORD = "email_password"
    GOOGLE_OAUTH = "google_oauth"
    AADHAAR = "aadhaar"
    OTP_SMS = "otp_sms"
    OTP_EMAIL = "otp_email"


class UserRole(str, Enum):
    """User roles"""
    CITIZEN = "citizen"
    ADMIN = "admin"
    MODERATOR = "moderator"


class User(Base):
    """User model with multiple authentication methods"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Basic user info
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(15), unique=True, index=True, nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(201), nullable=False)  # computed field
    
    # Authentication
    password_hash = Column(String(255), nullable=True)  # null for OAuth users
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CITIZEN)
    
    # Aadhaar info (encrypted)
    aadhaar_number_hash = Column(String(255), nullable=True)
    aadhaar_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    auth_methods = relationship("UserAuthMethod", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    otp_attempts = relationship("OTPAttempt", back_populates="user", cascade="all, delete-orphan")


class UserAuthMethod(Base):
    """Track which authentication methods a user has enabled"""
    __tablename__ = "user_auth_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    method = Column(SQLEnum(AuthMethod), nullable=False)
    
    # Method-specific data (encrypted)
    provider_id = Column(String(255), nullable=True)  # Google ID, etc.
    provider_data = Column(Text, nullable=True)  # JSON data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="auth_methods")


class UserSession(Base):
    """User session management"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True, nullable=True)
    
    # Session metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class OTPAttempt(Base):
    """OTP verification attempts"""
    __tablename__ = "otp_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null for pre-registration
    contact = Column(String(255), nullable=False)  # email or phone
    contact_type = Column(SQLEnum(AuthMethod), nullable=False)  # OTP_SMS or OTP_EMAIL
    
    # OTP data
    otp_code = Column(String(10), nullable=False)
    otp_hash = Column(String(255), nullable=False)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="otp_attempts")


class PasswordReset(Base):
    """Password reset tokens"""
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)


class LoginAttempt(Base):
    """Track login attempts for security"""
    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(15), nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    
    # Attempt result
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    
    # Timestamps
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())


# Helper functions for token generation and validation
def generate_session_token() -> str:
    """Generate a secure session token"""
    return str(uuid.uuid4())


def generate_refresh_token() -> str:
    """Generate a secure refresh token"""
    return str(uuid.uuid4())


def generate_otp_code() -> str:
    """Generate a 6-digit OTP code"""
    import random
    return f"{random.randint(100000, 999999)}"


def get_token_expiry(hours: int = 24) -> datetime:
    """Get token expiry datetime"""
    return datetime.utcnow() + timedelta(hours=hours)


def get_otp_expiry(minutes: int = 10) -> datetime:
    """Get OTP expiry datetime"""
    return datetime.utcnow() + timedelta(minutes=minutes)
