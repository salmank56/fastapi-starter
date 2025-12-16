from __future__ import annotations
from typing import TYPE_CHECKING, List
"""
Audit & Usage Tracking Models
Compliance, debugging, and billing infrastructure
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class AuditLog(Base):
    """
    Comprehensive audit trail for compliance and debugging.
    Tracks all critical actions with before/after state.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)  # Nullable for system actions
    
    # Action Details
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Examples: "user.login", "user.logout", "search_job.created", "purchase_order.approved", "settings.updated"
    
    # Entity Information
    entity_type: Mapped[str] = mapped_column(String(50), nullable=True, index=True)  # "User", "PurchaseOrder", "OrganizationSettings"
    entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # State Changes (For rollback and debugging)
    changes: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example: {"before": {"status": "draft"}, "after": {"status": "sent"}}
    
    # Additional Context
    description: Mapped[str] = mapped_column(Text, nullable=True)  # Human-readable description
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # Flexible extra data (renamed from metadata)
    
    # Request Context
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # IPv6 compatible
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    request_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)  # For tracing
    
    # Result
    success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="audit_logs")  # type: ignore

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by user={self.user_id}>"

    # Composite index for common queries
    __table_args__ = (
        Index("ix_audit_org_action_time", "organization_id", "action", "timestamp"),
    )


class UsageLog(Base):
    """
    Granular resource usage tracking for billing and rate limiting.
    Enables cost attribution per organization and user.
    """
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Resource Type
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Examples: "openai_api_call", "pinecone_query", "scrape_job", "vector_upsert", "email_sent"
    
    # Resource Details
    resource_name: Mapped[str] = mapped_column(String(100), nullable=True)  # "gpt-4o-mini", "text-embedding-3-small"
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # Tokens, API calls, etc.
    unit: Mapped[str] = mapped_column(String(20), nullable=True)  # "tokens", "requests", "emails"
    
    # Cost Tracking
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    # Related Entity (For attribution)
    related_entity_type: Mapped[str] = mapped_column(String(50), nullable=True)  # "search_job", "negotiation"
    related_entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Extra Data (Flexible for different resource types, renamed from metadata to avoid SQLAlchemy reserved word)
    extra_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example for OpenAI: {"model": "gpt-4o-mini", "input_tokens": 500, "output_tokens": 150, "latency_ms": 1200}
    # Example for Scraper: {"url": "amazon.com/...", "duration_ms": 3500, "success": true}
    
    # Billing Period (For easy aggregation)
    billing_period: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # "2025-12" (YYYY-MM format)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="usage_logs")  # type: ignore

    def __repr__(self) -> str:
        return f"<UsageLog {self.resource_type} cost=${self.cost_usd}>"

    # Composite indexes for fast aggregation queries
    __table_args__ = (
        Index("ix_usage_org_period", "organization_id", "billing_period"),
        Index("ix_usage_org_resource_time", "organization_id", "resource_type", "timestamp"),
    )

