"""
Database Module for Smart Ticket System

Handles all database operations including:
- Connection management
- CRUD operations for tickets
- Query helpers
- Transaction management

This module provides a clean interface to the SQLite database,
abstracting away the SQL details from the rest of the application.
"""

import sqlite3
from contextlib import contextmanager
import logging
from config import DATABASE_NAME

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures connections are properly closed even if errors occur.

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # ... perform database operations
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def create_ticket(title, description, user_name, user_email):
    """
    Create a new ticket in the database.

    Args:
        title: Ticket title
        description: Ticket description
        user_name: Name of the user submitting the ticket
        user_email: Email of the user

    Returns:
        int: ID of the newly created ticket
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tickets (title, description, user_name, user_email, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (title, description, user_name, user_email))
        ticket_id = cursor.lastrowid
        logger.info(f"Created ticket {ticket_id} for user {user_name}")
        return ticket_id


def get_ticket_by_id(ticket_id):
    """
    Retrieve a ticket by its ID.

    Args:
        ticket_id: ID of the ticket

    Returns:
        dict: Ticket data or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_ticket_department(ticket_id, department, confidence_score):
    """
    Update the department assignment and confidence score for a ticket.

    Args:
        ticket_id: ID of the ticket
        department: Department name
        confidence_score: AI confidence score (0-100)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tickets
                SET department = ?, confidence_score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (department, confidence_score, ticket_id))
            logger.info(f"Updated ticket {ticket_id} department to {department}")
            return True
    except Exception as e:
        logger.error(f"Error updating ticket {ticket_id} department: {e}")
        return False


def update_ticket_status(ticket_id, status):
    """
    Update the status of a ticket.

    Args:
        ticket_id: ID of the ticket
        status: New status (pending, in_progress, resolved)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tickets
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, ticket_id))
            logger.info(f"Updated ticket {ticket_id} status to {status}")
            return True
    except Exception as e:
        logger.error(f"Error updating ticket {ticket_id} status: {e}")
        return False


def get_tickets_by_department(department, status_filter=None):
    """
    Get all tickets for a specific department.

    Args:
        department: Department name
        status_filter: Optional status filter

    Returns:
        list: List of ticket dictionaries
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if status_filter:
            cursor.execute('''
                SELECT * FROM tickets
                WHERE department = ? AND status = ?
                ORDER BY created_at DESC
            ''', (department, status_filter))
        else:
            cursor.execute('''
                SELECT * FROM tickets
                WHERE department = ?
                ORDER BY created_at DESC
            ''', (department,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_all_tickets():
    """
    Get all tickets from the database.

    Returns:
        list: List of all ticket dictionaries
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tickets ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_ticket_statistics():
    """
    Get summary statistics for all tickets.

    Returns:
        dict: Statistics including total count, by department, by status, etc.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total tickets
        cursor.execute('SELECT COUNT(*) as count FROM tickets')
        total_tickets = cursor.fetchone()['count']

        # By department
        cursor.execute('''
            SELECT department, COUNT(*) as count
            FROM tickets
            GROUP BY department
        ''')
        by_department = {row['department']: row['count'] for row in cursor.fetchall()}

        # By status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM tickets
            GROUP BY status
        ''')
        by_status = {row['status']: row['count'] for row in cursor.fetchall()}

        # Average confidence score
        cursor.execute('SELECT AVG(confidence_score) as avg_confidence FROM tickets')
        avg_confidence = cursor.fetchone()['avg_confidence'] or 0

        return {
            'total_tickets': total_tickets,
            'by_department': by_department,
            'by_status': by_status,
            'average_confidence': round(avg_confidence, 2)
        }


def ticket_exists(ticket_id):
    """
    Check if a ticket exists in the database.

    Args:
        ticket_id: ID of the ticket

    Returns:
        bool: True if ticket exists, False otherwise
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM tickets WHERE id = ?', (ticket_id,))
        return cursor.fetchone() is not None
