"""
Database Initialization Script for Smart Ticket System

This script creates the SQLite database and the necessary tables.
Run this once before starting the application.
"""

import sqlite3
from datetime import datetime

def init_database():
    """
    Initialize the SQLite database with the tickets table.

    This function creates the database structure for the monolithic
    ticket management system.
    """
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # Create tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            user_name TEXT NOT NULL,
            user_email TEXT NOT NULL,
            department TEXT,
            confidence_score INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create index on department for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_department
        ON tickets(department)
    ''')

    # Create index on status for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_status
        ON tickets(status)
    ''')

    conn.commit()
    conn.close()

    print("✓ Database initialized successfully!")
    print("✓ Created 'tickets' table with proper indexes")
    print("✓ Database file: tickets.db")

if __name__ == '__main__':
    init_database()
