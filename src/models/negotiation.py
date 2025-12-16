from __future__ import annotations
from typing import TYPE_CHECKING, List
"""
Negotiation & Procurement Models
AI negotiator agent email tracking and purchase orders
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base
from .enums import NegotiationStatus, EmailTemplateType


class Negotiation(Base):
    """
    Tracks the AI 'Negotiator' Agent's email conversations with vendors.
    Supports state machine workflow: DRAFT → SENT → REPLIED → ACCEPTED/REJECTED
    """
    __tablename__ = "negotiations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_by: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Negotiation State
    status: Mapped[str] = mapped_column(String(50), default=NegotiationStatus.DRAFT.value, nullable=False, index=True)
    
    # Pricing
    original_price: Mapped[float] = mapped_column(Float, nullable=False)
    target_price: Mapped[float] = mapped_column(Float, nullable=False)  # The price we WANT
    current_offer_price: Mapped[float] = mapped_column(Float, nullable=True)  # The price vendor offered
    final_price: Mapped[float] = mapped_column(Float, nullable=True)  # Agreed price
    discount_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Quantity & Terms
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    payment_terms: Mapped[str] = mapped_column(String(100), nullable=True)  # "Net 30", "Upfront"
    delivery_timeline_days: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Email Threading
    email_thread_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)  # Gmail API Thread ID
    email_subject: Mapped[str] = mapped_column(String(500), nullable=True)
    email_sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_email_content: Mapped[dict] = mapped_column(JSON, nullable=True)  # Store HTML/text of last email
    
    # Vendor Interaction
    vendor_contact_email: Mapped[str] = mapped_column(String(255), nullable=True)
    vendor_contact_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_vendor_response_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Automation Settings
    auto_follow_up_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    next_follow_up_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    max_follow_ups: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # Human-in-the-Loop
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Internal Notes
    notes: Mapped[str] = mapped_column(Text, nullable=True)  # Team collaboration notes
    ai_strategy: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # Agent's negotiation strategy
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Negotiation deadline

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="negotiations")  # type: ignore
    user: Mapped["User"] = relationship("User", back_populates="negotiations", foreign_keys=[user_id])  # type: ignore
    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="negotiation")  # type: ignore

    def __repr__(self) -> str:
        return f"<Negotiation {self.id} status={self.status}>"


class PurchaseOrder(Base):
    """
    The final output generated for the human to review and approve.
    Can be exported as PDF for signing.
    """
    __tablename__ = "purchase_orders"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    negotiation_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("negotiations.id"), nullable=False, index=True)
    
    # PO Details
    po_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # "PO-2025-001"
    
    # Line Items
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Costs
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    shipping_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Terms
    payment_terms: Mapped[str] = mapped_column(String(100), nullable=True)
    delivery_address: Mapped[dict] = mapped_column(JSON, nullable=True)
    expected_delivery_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Approval Workflow
    approved_by_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Document Generation
    generated_pdf_url: Mapped[str] = mapped_column(String(500), nullable=True)
    signed_pdf_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Status
    is_sent_to_vendor: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Additional Data
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    po_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # Renamed from 'metadata' to avoid SQLAlchemy reserved word
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    negotiation: Mapped["Negotiation"] = relationship("Negotiation", back_populates="purchase_orders")  # type: ignore

    def __repr__(self) -> str:
        return f"<PurchaseOrder {self.po_number}>"


class EmailTemplate(Base):
    """
    Prompt templates for the Negotiator AI Agent.
    Allows customization of negotiation strategies.
    """
    __tablename__ = "email_templates"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Template Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # "Bulk Discount Request"
    template_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # EmailTemplateType enum
    
    # Template Content (Supports Jinja2 variables)
    subject_template: Mapped[str] = mapped_column(String(500), nullable=False)
    # Example: "Bulk Purchase Inquiry - {{product_name}}"
    
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    # Example: "Dear {{vendor_name}},\n\nWe are interested in purchasing {{quantity}} units..."
    
    # Template Variables (Documentation)
    available_variables: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    # Example: ["product_name", "quantity", "target_price", "vendor_name"]
    
    # Configuration
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tone: Mapped[str] = mapped_column(String(50), nullable=True)  # "professional", "friendly", "assertive"
    
    # Usage Stats
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, nullable=True)  # % of negotiations that succeeded
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<EmailTemplate {self.name}>"

