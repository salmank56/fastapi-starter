"""
AI Procurement System - Database Models
Complete schema for production-ready multi-agent e-procurement platform
"""

# Import all models so Alembic can discover them
from .enums import *
from .organization import Organization, OrganizationSettings
from .auth import User, RefreshToken, APIKey
from .user_features import UserPreferences, SearchTemplate, ComparisonSet
from .agent import SearchJob, AgentLog
from .product import Vendor, Product, MediaFile
from .negotiation import Negotiation, PurchaseOrder, EmailTemplate
from .notification import Notification, WebhookEvent
from .audit import AuditLog, UsageLog

__all__ = [
    # Enums
    "JobStatus",
    "NegotiationStatus",
    "UserRole",
    "MediaType",
    "NotificationType",
    "WebhookSource",
    # Core Models
    "Organization",
    "OrganizationSettings",
    "User",
    "RefreshToken",
    "APIKey",
    "UserPreferences",
    "SearchTemplate",
    "ComparisonSet",
    "SearchJob",
    "AgentLog",
    "Vendor",
    "Product",
    "MediaFile",
    "Negotiation",
    "PurchaseOrder",
    "EmailTemplate",
    "Notification",
    "WebhookEvent",
    "AuditLog",
    "UsageLog",
]
