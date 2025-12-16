"""
Base enums and shared types
"""
from enum import Enum


class JobStatus(str, Enum):
    """Status of agent search jobs"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NegotiationStatus(str, Enum):
    """Status of vendor negotiation workflow"""
    DRAFT = "draft"
    SENT = "sent"
    VENDOR_REPLIED = "vendor_replied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AgentType(str, Enum):
    """Types of AI agents in the system"""
    ORCHESTRATOR = "orchestrator"
    SCRAPER = "scraper"
    ANALYST = "analyst"
    NEGOTIATOR = "negotiator"
    REPORTER = "reporter"

