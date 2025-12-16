"""
Security utilities for encryption, password hashing, and token generation
"""
import os
import secrets
from typing import Optional
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from passlib.context import CryptContext


# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


# API Key Encryption/Decryption
class EncryptionManager:
    """
    Manages encryption/decryption of sensitive data like API keys.
    
    CRITICAL: The ENCRYPTION_KEY must be:
    1. Stored in environment variables
    2. Generated using Fernet.generate_key()
    3. NEVER committed to git
    4. Backed up securely (losing it means losing all encrypted data)
    
    Usage:
        encryption = EncryptionManager()
        encrypted = encryption.encrypt("sk-openai-api-key-123")
        decrypted = encryption.decrypt(encrypted)
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize with encryption key from environment or parameter.
        
        To generate a new key:
        >>> from cryptography.fernet import Fernet
        >>> print(Fernet.generate_key().decode())
        """
        key = encryption_key or os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError(
                "ENCRYPTION_KEY not found. Generate one with: "
                "python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string"""
        if not plaintext:
            return ""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        """Decrypt a string"""
        if not encrypted:
            return ""
        return self.cipher.decrypt(encrypted.encode()).decode()


# Token Generation
def generate_api_key(prefix: str = "sk") -> tuple[str, str]:
    """
    Generate a secure API key with prefix.
    
    Returns:
        (full_key, key_hash): The full key to show to user once, and the hash to store in DB
    
    Example:
        >>> full_key, key_hash = generate_api_key("sk_live")
        >>> # Show full_key to user: "sk_live_abc123def456..."
        >>> # Store key_hash in database
    """
    random_part = secrets.token_urlsafe(32)
    full_key = f"{prefix}_{random_part}"
    key_hash = pwd_context.hash(full_key)
    return full_key, key_hash


def verify_api_key(plain_key: str, key_hash: str) -> bool:
    """Verify an API key against its hash"""
    return pwd_context.verify(plain_key, key_hash)


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token (for share links, etc.)"""
    return secrets.token_urlsafe(length)


# JWT Token Utilities (Placeholder - implement with python-jose)
def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    TODO: Implement with python-jose:
    from jose import jwt
    
    to_encode = {"sub": user_id, "exp": datetime.utcnow() + expires_delta}
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    """
    raise NotImplementedError("Implement JWT with python-jose")


def create_refresh_token() -> str:
    """Generate a secure refresh token"""
    return secrets.token_urlsafe(64)


# Example Usage
if __name__ == "__main__":
    # Generate encryption key
    print("Generate ENCRYPTION_KEY and add to .env:")
    print(Fernet.generate_key().decode())
    
    print("\n" + "="*60)
    
    # Test password hashing
    password = "MySecurePassword123!"
    hashed = hash_password(password)
    print(f"Password: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verified: {verify_password(password, hashed)}")
    
    print("\n" + "="*60)
    
    # Test API key generation
    full_key, key_hash = generate_api_key("sk_test")
    print(f"Generated API Key: {full_key}")
    print(f"Key Hash (store in DB): {key_hash[:50]}...")
    print(f"Verification: {verify_api_key(full_key, key_hash)}")



