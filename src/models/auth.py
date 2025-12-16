from __future__ import annotations
from typing import TYPE_CHECKING, List
"""
Authentication & Authorization Models
Handles users, JWT tokens, and API keys
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base
from .enums import UserRole


class User(Base):
    """
    Core user model with RBAC and security features.
    Replaces the old user.py model with production-ready fields.
    """
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    
    # Authorization
    role: Mapped[str] = mapped_column(String(50), default=UserRole.MEMBER.value, nullable=False)
    
    # Account Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    locked_until: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_login_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_login_ip: Mapped[str] = mapped_column(String(45), nullable=True)  # IPv6 compatible
    password_changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")  # type: ignore
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")  # type: ignore
    preferences: Mapped["UserPreferences"] = relationship("UserPreferences", back_populates="user", uselist=False)  # type: ignore
    search_jobs: Mapped[List["SearchJob"]] = relationship("SearchJob", back_populates="user")  # type: ignore
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user")  # type: ignore
    search_templates: Mapped[List["SearchTemplate"]] = relationship("SearchTemplate", back_populates="user")  # type: ignore
    comparison_sets: Mapped[List["ComparisonSet"]] = relationship("ComparisonSet", back_populates="user")  # type: ignore
    negotiations: Mapped[List["Negotiation"]] = relationship("Negotiation", back_populates="user")  # type: ignore

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class RefreshToken(Base):
    """
    JWT refresh token tracking for secure auth.
    Allows token revocation and rotation.
    """
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Security
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Device Tracking
    device_info: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # User-Agent, IP, etc.
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")  # type: ignore

    def __repr__(self) -> str:
        return f"<RefreshToken user_id={self.user_id}>"


class APIKey(Base):
    """
    API keys for programmatic access.
    Supports scoped permissions and usage tracking.
    """
    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    created_by_user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Key Details
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # "Production Key", "CI/CD Key"
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # "sk_live_abc123" (first 10 chars)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)  # SHA256 hash
    
    # Permissions
    scopes: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)  # ["search:read", "search:write", "products:read"]
    
    # Status & Limits
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    
    # Usage Tracking
    last_used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Expiration
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="api_keys")  # type: ignore

    def __repr__(self) -> str:
        return f"<APIKey {self.name}>"

