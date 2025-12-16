from __future__ import annotations
from typing import TYPE_CHECKING, List
"""
Notification & Webhook Models
Real-time user notifications and external event handling
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Text, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base
from .enums import NotificationType, WebhookSource


class Notification(Base):
    """
    User-facing notifications for the frontend.
    Supports real-time updates via WebSocket or polling.
    """
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification Content
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # NotificationType enum
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Action & Navigation
    link: Mapped[str] = mapped_column(String(500), nullable=True)  # Deep link to the UI: "/jobs/abc-123"
    action_label: Mapped[str] = mapped_column(String(100), nullable=True)  # "View Results", "Approve"
    
    # Related Entity (Polymorphic link)
    related_entity_type: Mapped[str] = mapped_column(String(50), nullable=True)  # "search_job", "negotiation"
    related_entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Status
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Priority
    priority: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)  # "low", "normal", "high", "urgent"
    
    # Delivery Channels
    sent_via_websocket: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_via_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Expiration
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Auto-hide old notifications
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")  # type: ignore

    def __repr__(self) -> str:
        return f"<Notification {self.type}: {self.title}>"


class WebhookEvent(Base):
    """
    Tracks incoming webhooks from external services (Gmail, SendGrid, Stripe).
    Ensures idempotency and enables event replay.
    """
    __tablename__ = "webhook_events"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Event Source
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # WebhookSource enum
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # "email.received", "payment.succeeded"
    
    # External Reference (For deduplication)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # Gmail message ID or SendGrid event ID
    
    # Raw Payload
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    headers: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # HTTP headers for debugging
    
    # Processing Status
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    processing_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processing_error: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Related Entity (If matched)
    negotiation_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("negotiations.id"), nullable=True, index=True)
    matched_entity_type: Mapped[str] = mapped_column(String(50), nullable=True)
    matched_entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Metadata
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # Source IP
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Timestamp from the external service

    def __repr__(self) -> str:
        return f"<WebhookEvent {self.source}:{self.event_type}>"

