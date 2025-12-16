from __future__ import annotations
from typing import TYPE_CHECKING, List
"""
User Feature Models
Saved searches, templates, comparisons, and preferences
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class UserPreferences(Base):
    """
    Individual user settings and preferences.
    Separate from OrganizationSettings to allow user-level customization.
    """
    __tablename__ = "user_preferences"

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    
    # Notification Preferences
    email_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    websocket_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_on_job_complete: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_on_negotiation_reply: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_on_price_drop: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Display Preferences
    theme: Mapped[str] = mapped_column(String(20), default="dark", nullable=False)  # "dark", "light", "auto"
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    default_currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    
    # Search Preferences
    preferred_vendors: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)  # ["amazon", "bestbuy"]
    default_max_price: Mapped[float] = mapped_column(Float, nullable=True)
    default_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Dashboard Preferences
    dashboard_layout: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example: {"widgets": ["recent_jobs", "price_alerts", "negotiations"], "layout": "grid"}
    
    # Privacy & Data
    share_analytics: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="preferences")  # type: ignore

    def __repr__(self) -> str:
        return f"<UserPreferences user_id={self.user_id}>"


class SearchTemplate(Base):
    """
    Reusable search query templates.
    Enables users to save common searches like "Monthly Laptop Purchase".
    """
    __tablename__ = "search_templates"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Template Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # "Monthly Laptop Purchase"
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Query Template (Supports variables)
    query_template: Mapped[str] = mapped_column(Text, nullable=False)
    # Example: "Find {product_type} under ${max_price} with {min_rating}+ rating"
    
    # Default Filters
    default_filters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example: {"max_price": 2000, "min_rating": 4.0, "vendors": ["amazon"]}
    
    # Variables (For UI form generation)
    template_variables: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    # Example: [{"name": "product_type", "type": "text"}, {"name": "max_price", "type": "number"}]
    
    # Sharing
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Share with organization?
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Usage Stats
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="search_templates")  # type: ignore

    def __repr__(self) -> str:
        return f"<SearchTemplate {self.name}>"


class ComparisonSet(Base):
    """
    Saves product comparisons for later review.
    Enables side-by-side analysis of scraped products.
    """
    __tablename__ = "comparison_sets"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Comparison Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # "Laptops - March 2025"
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Products to Compare
    product_ids: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)  # List of UUIDs
    
    # Comparison Criteria (Weights for scoring)
    criteria: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example: {"price": 0.4, "rating": 0.3, "specs.ram": 0.3}
    
    # Decision
    winner_product_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)  # User's final choice
    decision_notes: Mapped[str] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # Sharing
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    share_token: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)  # For public sharing
    
    # Collaboration
    notes: Mapped[str] = mapped_column(Text, nullable=True)  # Team discussion notes
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="comparison_sets")  # type: ignore

    def __repr__(self) -> str:
        return f"<ComparisonSet {self.name}>"

