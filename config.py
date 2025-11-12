"""
Configuration Module for Smart Ticket System

Contains all application constants and configuration settings.
This centralized configuration makes it easy to modify settings
without searching through the entire codebase.
"""

# Database Configuration
DATABASE_NAME = 'tickets.db'

# Department Configuration
DEPARTMENTS = [
    'IT Support',
    'HR',
    'Facilities',
    'Finance',
    'General'
]

# Ticket Status Options
TICKET_STATUSES = [
    'pending',
    'in_progress',
    'resolved'
]

# AI Configuration
AI_MAX_RETRIES = 3
AI_RETRY_DELAY = 2  # seconds
AI_DEFAULT_CONFIDENCE = 70  # Default confidence if not provided by AI
AI_FALLBACK_CONFIDENCE = 30  # Confidence when AI fails and we use fallback

# Flask Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = True

# Logging Configuration
LOG_LEVEL = 'INFO'
