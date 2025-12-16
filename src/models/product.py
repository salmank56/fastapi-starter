from __future__ import annotations
from typing import TYPE_CHECKING, List
"""
Product & Vendor Models
E-commerce data with RAG integration
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Float, DateTime, Text, JSON, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base
from .enums import MediaType


class Vendor(Base):
    """
    E-commerce vendors (Amazon, BestBuy, etc.)
    Stores contact info for the Negotiator Agent.
    """
    __tablename__ = "vendors"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Vendor Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # "Amazon", "Best Buy"
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)  # "amazon"
    domain: Mapped[str] = mapped_column(String(255), nullable=False)  # "amazon.com"
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Contact Information (For Negotiator Agent)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=True)
    support_email: Mapped[str] = mapped_column(String(255), nullable=True)
    procurement_email: Mapped[str] = mapped_column(String(255), nullable=True)  # B2B contact
    
    # Vendor Metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scraping_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    average_response_time_hours: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Configuration
    scraper_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example: {"selector_price": ".a-price", "requires_login": false, "rate_limit_delay": 2}
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="vendor")  # type: ignore

    def __repr__(self) -> str:
        return f"<Vendor {self.name}>"


class Product(Base):
    """
    Normalized product data extracted by GPT-4o Vision.
    Supports RAG with vector_id for semantic search.
    """
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    search_job_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("search_jobs.id"), nullable=False, index=True)
    vendor_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True, index=True)
    
    # Product Identity
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=True)  # Vendor SKU
    url: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Pricing
    price: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    original_price: Mapped[float] = mapped_column(Float, nullable=True)  # Before discount
    discount_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Price History (For trend analysis)
    price_history: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    # Example: [{"price": 1999, "timestamp": "2025-12-15T10:00:00Z"}, ...]
    
    # Availability
    availability_status: Mapped[str] = mapped_column(String(100), nullable=False)  # "In Stock", "Backordered", "Out of Stock"
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Product Details
    brand: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=True)  # 4.5
    review_count: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # FLEXIBLE SPECS: GPT-4o dumps JSON here
    # Laptop: {"ram": "16GB", "processor": "M3", "storage": "512GB SSD"}
    # Chair: {"material": "Mesh", "weight_capacity": "300lbs", "warranty": "5 years"}
    specs: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    # AI Extraction Metadata
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)  # 0.0-1.0, GPT-4o extraction confidence
    raw_extraction_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # Full GPT-4o response
    
    # Evidence (The Screenshot taken by Playwright)
    screenshot_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # RAG Integration: The ID of the vector in Pinecone
    vector_id: Mapped[str] = mapped_column(String(100), nullable=True, unique=True, index=True)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=True)  # "text-embedding-3-small"
    
    # Scraping Metadata
    last_scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    scrape_attempt_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    search_job: Mapped["SearchJob"] = relationship("SearchJob", back_populates="products")  # type: ignore
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="products")  # type: ignore
    negotiations: Mapped[List["Negotiation"]] = relationship("Negotiation", back_populates="product")  # type: ignore

    def __repr__(self) -> str:
        return f"<Product {self.title[:30]}... ${self.price}>"


class MediaFile(Base):
    """
    Centralized file tracking for screenshots, PDFs, exports.
    Supports S3, local storage, or any cloud storage.
    """
    __tablename__ = "media_files"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # File Identity
    file_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # MediaType enum
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)  # S3 key or local path
    public_url: Mapped[str] = mapped_column(Text, nullable=True)  # Signed URL or public URL
    
    # File Metadata
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)  # "image/png", "application/pdf"
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=True)  # SHA256 for integrity
    
    # Polymorphic Relationship (Can link to Product, PurchaseOrder, etc.)
    related_entity_type: Mapped[str] = mapped_column(String(50), nullable=True)  # "product", "purchase_order"
    related_entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Ownership
    uploaded_by: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Lifecycle
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)  # Auto-delete temp files
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<MediaFile {self.file_type}: {self.original_filename}>"

