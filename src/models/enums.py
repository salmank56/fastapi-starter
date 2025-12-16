"""
Enums for type safety across the application
"""
from enum import Enum


class JobStatus(str, Enum):
    """Status of AI agent search jobs"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NegotiationStatus(str, Enum):
    """Status of vendor negotiations"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    SENT = "sent"
    VENDOR_REPLIED = "vendor_replied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class UserRole(str, Enum):
    """User roles for RBAC"""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class MediaType(str, Enum):
    """Types of media files stored"""
    SCREENSHOT = "screenshot"
    PDF_PURCHASE_ORDER = "pdf_purchase_order"
    EMAIL_ATTACHMENT = "email_attachment"
    PRODUCT_IMAGE = "product_image"
    EXPORT_CSV = "export_csv"


class NotificationType(str, Enum):
    """Types of user notifications"""
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    NEGOTIATION_REPLY = "negotiation_reply"
    NEGOTIATION_ACCEPTED = "negotiation_accepted"
    PURCHASE_ORDER_READY = "purchase_order_ready"
    PRICE_DROP_ALERT = "price_drop_alert"
    SYSTEM_ALERT = "system_alert"


class WebhookSource(str, Enum):
    """External webhook sources"""
    GMAIL = "gmail"
    SENDGRID = "sendgrid"
    STRIPE = "stripe"
    CUSTOM = "custom"


class EmailTemplateType(str, Enum):
    """Types of email templates for negotiator agent"""
    INITIAL_CONTACT = "initial_contact"
    FOLLOW_UP = "follow_up"
    PRICE_NEGOTIATION = "price_negotiation"
    BULK_DISCOUNT_REQUEST = "bulk_discount_request"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"

