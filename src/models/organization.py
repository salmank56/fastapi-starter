"""
Organization and Settings Models
Supports multi-tenancy and per-org configuration
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Integer, Boolean, DateTime, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base

if TYPE_CHECKING:
    from .auth import User, APIKey
    from .agent import SearchJob
    from .audit import AuditLog, UsageLog


class Organization(Base):
    """
    Multi-tenant organization model.
    Each company/team is an organization with its own users and settings.
    """
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Contact & Billing
    contact_email: Mapped[str] = mapped_column(String(255), nullable=True)
    billing_email: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Subscription & Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subscription_tier: Mapped[str] = mapped_column(String(50), default="free", nullable=False)  # free, pro, enterprise
    trial_ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization")  # type: ignore
    settings: Mapped["OrganizationSettings"] = relationship("OrganizationSettings", back_populates="organization", uselist=False)  # type: ignore
    api_keys: Mapped[List["APIKey"]] = relationship("APIKey", back_populates="organization")  # type: ignore
    search_jobs: Mapped[List["SearchJob"]] = relationship("SearchJob", back_populates="organization")  # type: ignore
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="organization")  # type: ignore
    usage_logs: Mapped[List["UsageLog"]] = relationship("UsageLog", back_populates="organization")  # type: ignore

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"


class OrganizationSettings(Base):
    """
    Encrypted API keys, usage quotas, and agent behavior configuration per organization.
    CRITICAL: API keys should be encrypted at rest using Fernet or AWS KMS.
    """
    __tablename__ = "organization_settings"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True, index=True)

    # Encrypted API Credentials (Store encrypted, decrypt on read)
    openai_api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=True)
    pinecone_api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=True)
    pinecone_environment: Mapped[str] = mapped_column(String(100), nullable=True)
    pinecone_index_name: Mapped[str] = mapped_column(String(100), nullable=True)
    gmail_oauth_token_encrypted: Mapped[str] = mapped_column(Text, nullable=True)
    sendgrid_api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=True)

    # Usage Limits (Prevent runaway costs)
    max_searches_per_month: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    max_products_per_search: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    max_concurrent_jobs: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    monthly_budget_usd: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    
    # Current Usage (Reset monthly)
    current_searches_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_spend_this_month: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    usage_reset_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Agent Behavior Configuration
    default_scraping_timeout: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # seconds
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    enable_auto_negotiation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enable_price_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Vendor Preferences
    allowed_vendors: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)  # ["amazon.com", "bestbuy.com"]
    blocked_vendors: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    
    # Custom Preferences (Flexible JSONB)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="settings")  # type: ignore

    def __repr__(self) -> str:
        return f"<OrganizationSettings org_id={self.organization_id}>"

