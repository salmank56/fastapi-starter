#!/usr/bin/env python3
"""
Setup script for AI Procurement System database schema
Run this after starting PostgreSQL to create all tables
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("=" * 60)
    print("🚀 AI Procurement System - Schema Setup")
    print("=" * 60)
    
    # Step 1: Check environment
    print("\n1️⃣  Checking environment...")
    try:
        from src.core.config import settings
        print(f"   ✅ Config loaded")
        print(f"   📍 Database: {settings.POSTGRESQL_SERVER}:{settings.POSTGRESQL_PORT}/{settings.POSTGRESQL_DB}")
    except Exception as e:
        print(f"   ❌ Error loading config: {e}")
        print("\n   💡 Make sure you have a .env file with:")
        print("      POSTGRESQL_USER=postgres")
        print("      POSTGRESQL_PASSWORD=yourpassword")
        print("      POSTGRESQL_SERVER=localhost")
        print("      POSTGRESQL_PORT=5432")
        print("      POSTGRESQL_DB=ai_procurement")
        return False
    
    # Step 2: Test database connection
    print("\n2️⃣  Testing database connection...")
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"   ✅ Connected to PostgreSQL")
            print(f"   📦 Version: {version[:50]}...")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n   💡 Make sure PostgreSQL is running:")
        print("      docker run -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16-alpine")
        return False
    
    # Step 3: Load all models
    print("\n3️⃣  Loading database models...")
    try:
        from src.models import (
            Organization, OrganizationSettings,
            User, RefreshToken, APIKey,
            UserPreferences, SearchTemplate, ComparisonSet,
            SearchJob, AgentLog,
            Vendor, Product, MediaFile,
            Negotiation, PurchaseOrder, EmailTemplate,
            Notification, WebhookEvent,
            AuditLog, UsageLog
        )
        models = [
            Organization, OrganizationSettings,
            User, RefreshToken, APIKey,
            UserPreferences, SearchTemplate, ComparisonSet,
            SearchJob, AgentLog,
            Vendor, Product, MediaFile,
            Negotiation, PurchaseOrder, EmailTemplate,
            Notification, WebhookEvent,
            AuditLog, UsageLog
        ]
        print(f"   ✅ Loaded {len(models)} models successfully")
        for model in models:
            print(f"      • {model.__tablename__}")
    except Exception as e:
        print(f"   ❌ Error loading models: {e}")
        return False
    
    # Step 4: Check encryption key
    print("\n4️⃣  Checking security configuration...")
    try:
        from src.core.security import EncryptionManager
        encryption = EncryptionManager()
        test_text = "test"
        encrypted = encryption.encrypt(test_text)
        decrypted = encryption.decrypt(encrypted)
        assert decrypted == test_text
        print("   ✅ Encryption key configured correctly")
    except Exception as e:
        print(f"   ⚠️  Warning: Encryption not configured: {e}")
        print("\n   💡 Generate an encryption key:")
        print("      python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
        print("   💡 Add to .env:")
        print("      ENCRYPTION_KEY=<your_generated_key>")
    
    # Step 5: Instructions for migration
    print("\n5️⃣  Next steps:")
    print("   Run these commands to create the database tables:")
    print()
    print("   # Generate migration:")
    print("   alembic revision --autogenerate -m \"Create full AI procurement schema\"")
    print()
    print("   # Apply migration:")
    print("   alembic upgrade head")
    print()
    print("   # Verify tables:")
    print("   psql -U postgres -d ai_procurement -c '\\dt'")
    
    print("\n" + "=" * 60)
    print("✅ Setup check complete!")
    print("=" * 60)
    print()
    print("📚 Documentation:")
    print("   • Full schema: src/models/README.md")
    print("   • Summary: SCHEMA_COMPLETE.md")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



