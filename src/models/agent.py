from __future__ import annotations
from typing import TYPE_CHECKING, List
"""
Agent Workflow Models
LangGraph orchestration state management
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base
from .enums import JobStatus


class SearchJob(Base):
    """
    Represents a user request like 'Find MacBook Pro M3 under $2000'.
    The LangGraph Orchestrator reads from this table to manage workflow state.
    """
    __tablename__ = "search_jobs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Search Query
    query_text: Mapped[str] = mapped_column(Text, nullable=False)  # The raw user prompt
    refined_query: Mapped[str] = mapped_column(Text, nullable=True)  # LLM-refined query
    
    # Job Configuration
    filters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example: {"max_price": 2000, "min_rating": 4.0, "brands": ["Apple", "Dell"]}
    
    # Workflow Status
    status: Mapped[str] = mapped_column(String(50), default=JobStatus.PENDING.value, nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # For job queue ordering
    
    # Progress Tracking
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_step: Mapped[str] = mapped_column(String(100), nullable=True)  # "scraping_amazon", "analyzing_results"
    
    # Results Summary
    products_found_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vendors_searched_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Error Handling
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Cost Tracking
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # Timing
    estimated_completion_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="search_jobs")  # type: ignore
    user: Mapped["User"] = relationship("User", back_populates="search_jobs")  # type: ignore
    agent_logs: Mapped[List["AgentLog"]] = relationship("AgentLog", back_populates="search_job", cascade="all, delete-orphan")  # type: ignore
    products: Mapped[List["Product"]] = relationship("Product", back_populates="search_job")  # type: ignore

    def __repr__(self) -> str:
        return f"<SearchJob {self.id} status={self.status}>"


class AgentLog(Base):
    """
    Stores the 'Thought Process' of the AI agents.
    Frontend polls this table to show the real-time 'Terminal' view.
    
    Example logs:
    - "ScraperAgent: Navigating to Amazon.com..."
    - "VisionAgent: Extracting price from screenshot..."
    - "AnalystAgent: Creating embeddings for 12 products..."
    """
    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    search_job_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("search_jobs.id"), nullable=False, index=True)
    
    # Log Details
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)  # Sequence in the workflow
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)  # "ScraperAgent", "AnalystAgent", "OrchestratorAgent"
    action: Mapped[str] = mapped_column(Text, nullable=False)  # Human-readable action description
    
    # Technical Details (For debugging)
    log_level: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)  # INFO, WARNING, ERROR
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)  # How long this step took
    
    # Flexible Debug Data
    metadata_log: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example: {"url": "amazon.com/product/123", "tokens_used": 500, "screenshot_path": "/tmp/img.png"}
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    search_job: Mapped["SearchJob"] = relationship("SearchJob", back_populates="agent_logs")  # type: ignore

    def __repr__(self) -> str:
        return f"<AgentLog {self.agent_name}: {self.action[:30]}...>"

