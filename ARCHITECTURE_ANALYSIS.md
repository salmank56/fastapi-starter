# AI-Powered Procurement System - Architecture Analysis

## Executive Summary
**Verdict: Your schema is 85% production-ready, but you need additional dependencies and minor schema enhancements.**

---

## ✅ What Your Schema Gets RIGHT (Senior-Level Thinking)

### 1. **Hybrid Data Model (JSONB for Flexibility)**
```python
specs: Dict = Field(default={}, sa_column=Column(JSON))
```
**Why This is Elite:**
- You correctly identified that product attributes are polymorphic (Laptop ≠ Chair specs)
- Using PostgreSQL JSONB allows:
  - Schema flexibility without migrations
  - Native JSON querying: `WHERE specs->>'ram' = '16GB'`
  - AI agents can dump unstructured data directly

### 2. **Agent State Persistence (AgentLog)**
This is the **killer feature** that separates your app from basic scrapers.
- Stores the "thought process" of LangGraph agents
- Enables real-time "Terminal UI" in the frontend
- Provides audit trail for debugging agent decisions

### 3. **Separation of Concerns (Postgres + Pinecone)**
```python
vector_id: Optional[str] = None  # Link to Pinecone
```
**Architecture Pattern:** You're implementing the **hybrid search pattern**:
- Postgres = Transactional data (prices, orders)
- Pinecone = Semantic search (finding "budget gaming laptops")

### 4. **Multi-Tenancy Ready (Organization Model)**
Even though Phase 0 doesn't need it, you're thinking ahead for B2B SaaS scalability.

---

## 🚨 CRITICAL GAPS IN YOUR CURRENT SETUP

### **Missing Dependencies (Add to requirements.in)**

Your current `requirements.in` is missing 70% of what you need:

```plaintext
# ============= CURRENT (Basic Stack) =============
fastapi
uvicorn[standard]
pydantic
pydantic-settings
sqlmodel
sqlalchemy
psycopg2-binary
requests
playwright
python-multipart
alembic

# ============= MISSING (Critical for Your App) =============

# --- AI/LLM Stack ---
openai>=1.0.0                    # GPT-4o Vision API
langchain>=0.3.0                 # RAG framework
langchain-openai                 # OpenAI integrations
langgraph>=0.2.0                 # Agent orchestration (MOST IMPORTANT)
langchain-community              # Additional tools

# --- Vector Database ---
pinecone-client>=3.0.0           # Semantic search
tiktoken                         # Token counting for embeddings

# --- Async Task Queue ---
celery[redis]>=5.4.0             # Background jobs
redis>=5.0.0                     # Message broker
flower                           # Celery monitoring UI

# --- WebSocket (Real-time Updates) ---
python-socketio                  # WebSocket support
# (uvicorn[standard] already includes websockets)

# --- Email Integration ---
google-api-python-client         # Gmail API
google-auth-httplib2
google-auth-oauthlib

# --- PDF Generation (Purchase Orders) ---
reportlab                        # Or use weasyprint for HTML->PDF
pypdf                            # PDF manipulation

# --- Screenshot Storage ---
boto3                            # AWS S3 (or use Cloudinary)
python-magic                     # File type detection

# --- Data Validation & Serialization ---
pydantic[email]                  # Email validation
python-jose[cryptography]        # JWT tokens
passlib[bcrypt]                  # Password hashing

# --- Monitoring & Logging ---
structlog                        # Structured logging
sentry-sdk[fastapi]              # Error tracking

# --- Development Tools ---
pytest                           # Testing
pytest-asyncio                   # Async tests
httpx                            # HTTP client for tests
faker                            # Test data generation
```

---

## 📊 SCHEMA ENHANCEMENTS NEEDED

### **1. Missing: WebSocket Session Management**

Your schema doesn't track WebSocket connections for real-time updates.

**Add This Model:**

```python
class WebSocketSession(SQLModel, table=True):
    """
    Tracks active WebSocket connections per user.
    When a SearchJob updates, we know which connections to notify.
    """
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    connection_id: str  # Unique socket ID from Socket.IO
    is_active: bool = Field(default=True)
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_ping: datetime = Field(default_factory=datetime.utcnow)
```

**Why:** Your frontend needs to know WHERE to push updates when an agent finishes.

---

### **2. Missing: Rate Limiting & Cost Tracking**

Your app calls expensive APIs (OpenAI, Playwright). You need quotas.

**Add This Model:**

```python
class APIUsage(SQLModel, table=True):
    """
    Tracks API costs per user/org for billing and rate limiting.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id")
    
    service: str  # "openai_gpt4o", "pinecone_query"
    tokens_used: int = Field(default=0)
    cost_usd: float = Field(default=0.0)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # For rate limiting
    class Config:
        indexes = [
            ("organization_id", "service", "timestamp")
        ]
```

---

### **3. Schema Bug Fix: Foreign Key Casing**

```python
# ❌ WRONG (SQLModel is case-sensitive for table names)
job_id: UUID = Field(foreign_key="searchjob.id")

# ✅ CORRECT
job_id: UUID = Field(foreign_key="searchjob.id")
```

**Fix:** SQLModel auto-generates table names as lowercase. Update all FKs:
- `"searchjob.id"` (not `"SearchJob.id"`)
- `"agentlog.id"` (not `"AgentLog.id"`)

---

### **4. Missing: File Storage References**

Your schema stores `screenshot_url` but doesn't track WHERE screenshots are stored.

**Add This Field to Product:**

```python
class Product(SQLModel, table=True):
    # ... existing fields ...
    
    screenshot_url: Optional[str] = None
    screenshot_storage_key: Optional[str] = None  # S3 key or path
    raw_html_snapshot: Optional[str] = None  # For debugging scraper issues
```

---

### **5. Missing: Agent Configuration**

Your `SearchJob` has `filters` but no way to configure WHICH agents to use.

**Enhance SearchJob:**

```python
class SearchJob(SQLModel, table=True):
    # ... existing fields ...
    
    # Agent Configuration
    target_websites: List[str] = Field(default=["amazon", "bestbuy"], sa_column=Column(JSON))
    max_results: int = Field(default=20)
    enable_negotiation: bool = Field(default=False)  # User can disable auto-email
    
    # Performance Tracking
    total_execution_time_seconds: Optional[float] = None
    num_products_found: int = Field(default=0)
```

---

## 🏗️ ARCHITECTURAL RECOMMENDATIONS

### **Issue 1: Your Current Database Setup is SQLAlchemy 1.x Style**

**Problem:** You're using `declarative_base()` (old style) but your schema uses SQLModel (modern).

**Fix Required in `src/core/database.py`:**

```python
# ❌ CURRENT (SQLAlchemy ORM - incompatible with SQLModel)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# ✅ NEW (SQLModel compatible)
from sqlmodel import create_engine, Session, SQLModel

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=True if settings.ENVIRONMENT == "local" else False,
    pool_pre_ping=True,  # Handles DB connection drops
)

def init_db():
    """Call this on startup to create all tables"""
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session
```

---

### **Issue 2: No Redis Configuration**

Your app needs Redis for Celery. Add to `config.py`:

```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    # Redis (for Celery + Caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str  # e.g., "us-east1-gcp"
    PINECONE_INDEX_NAME: str = "procurement-products"
    
    # Gmail API (for negotiation emails)
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
```

---

### **Issue 3: No Celery Setup**

Create `src/core/celery_app.py`:

```python
from celery import Celery
from .config import settings

celery_app = Celery(
    "procurement_agent",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["src.agents"])
```

---

## 📋 MISSING COMPONENTS CHECKLIST

| Component | Status | Priority | Notes |
|-----------|--------|----------|-------|
| LangGraph Orchestrator | ❌ Missing | **P0** | Core agent logic |
| Celery Tasks | ❌ Missing | **P0** | Async scraping |
| Playwright Scraper | ❌ Missing | **P0** | Phase 1 deliverable |
| Pinecone Integration | ❌ Missing | **P1** | RAG search |
| WebSocket Handler | ❌ Missing | **P1** | Real-time updates |
| Gmail API Integration | ❌ Missing | **P2** | Phase 5 feature |
| PDF Generator (PO) | ❌ Missing | **P2** | Phase 5 feature |
| Auth System (JWT) | ❌ Missing | **P1** | User login |
| S3/Storage Setup | ❌ Missing | **P1** | Screenshot hosting |

---

## 🎯 FINAL VERDICT

### **Schema Grade: A- (Excellent foundation)**
**Strong Points:**
- ✅ Agent state management
- ✅ Flexible JSONB storage
- ✅ Multi-tenancy ready
- ✅ Negotiation state machine

**Needs:**
- Add `WebSocketSession` model
- Add `APIUsage` model for cost tracking
- Fix foreign key casing
- Enhance `SearchJob` with agent config

### **Dependency Grade: D (Critical gaps)**
**Missing:**
- 🚨 `langgraph` (no orchestrator = no AI agents)
- 🚨 `celery[redis]` (scraping will block HTTP)
- 🚨 `openai` (no GPT-4o = no vision scraper)
- 🚨 `pinecone-client` (no vector search)

---

## 📝 IMMEDIATE NEXT STEPS

1. **Update dependencies** (I'll do this for you)
2. **Refactor database.py** to use SQLModel properly
3. **Implement the enhanced schema** with missing models
4. **Create Celery worker setup**
5. **Build Phase 1: Vision Scraper** as a Celery task

---

**Would you like me to:**
1. ✅ Update `requirements.in` with ALL missing dependencies?
2. ✅ Refactor your database setup to be SQLModel-native?
3. ✅ Create the enhanced schema file with all models?
4. ✅ Set up the Celery worker architecture?

**Let me know which to tackle first, or I'll do all 4 in sequence.**

