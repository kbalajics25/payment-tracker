import secrets
import os

class Config:
    """Application configuration"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    
    # Database configuration
    DATABASE_PATH = 'database.db'
    BACKUP_DIR = 'backups'
    EXPORT_DIR = 'exports'
    
    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Application settings
    TRANSACTIONS_PER_PAGE = 20
    BACKUP_RETENTION_DAYS = 30
    
    # Currency symbol
    CURRENCY_SYMBOL = '₹'