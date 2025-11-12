"""
Smart Ticket System - Main Application

MONOLITHIC ARCHITECTURE:
This application demonstrates a monolithic architecture where all components
(ticket submission, AI categorization, department routing, and dashboard)
are part of a single application but organized into separate modules.

ARCHITECTURE BENEFITS:
+ Simple deployment (single application)
+ Easy development and debugging
+ Shared database connections
+ No network latency between components
+ Atomic transactions across features
+ Straightforward testing

ARCHITECTURE TRADE-OFFS:
- Scaling requires scaling entire app
- All components deployed together
- Tight coupling between modules
- Single point of failure

FUTURE MIGRATION PATH:
The modular structure (separate files for database, AI, routing) makes it
easier to migrate to microservices if needed. Each module could become
its own service with minimal refactoring.

File Structure:
- app.py: Main Flask application and API routes (this file)
- config.py: Configuration constants
- database.py: Database operations
- ai_categorization.py: AI categorization logic
- routing.py: Department routing logic
- init_db.py: Database initialization
"""

from flask import Flask, request, jsonify
import logging
import os
import sqlite3

# Import our modules
from config import (
    DEPARTMENTS,
    TICKET_STATUSES,
    FLASK_HOST,
    FLASK_PORT,
    FLASK_DEBUG,
    LOG_LEVEL,
    DATABASE_NAME
)
from database import (
    create_ticket,
    get_ticket_by_id,
    update_ticket_status,
    get_tickets_by_department,
    get_all_tickets,
    get_ticket_statistics,
    ticket_exists
)
from ai_categorization import categorize_ticket
from routing import route_ticket_to_department, get_routing_statistics
from init_db import init_database

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


# ============================================================================
# DATABASE AUTO-INITIALIZATION
# ============================================================================

def ensure_database_initialized():
    """
    Check if the database has been initialized and initialize it if needed.

    This function checks if:
    1. The database file exists
    2. The required 'tickets' table exists

    If either check fails, it automatically initializes the database.
    """
    db_needs_init = False

    # Check if database file exists
    if not os.path.exists(DATABASE_NAME):
        logger.info(f"Database file '{DATABASE_NAME}' not found. Initializing database...")
        db_needs_init = True
    else:
        # Check if tickets table exists
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
            if cursor.fetchone() is None:
                logger.info("Database exists but 'tickets' table not found. Initializing database...")
                db_needs_init = True
            conn.close()
        except Exception as e:
            logger.warning(f"Error checking database: {e}. Initializing database...")
            db_needs_init = True

    # Initialize database if needed
    if db_needs_init:
        try:
            init_database()
            logger.info("✓ Database initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise


# Ensure database is initialized on startup
ensure_database_initialized()


# ============================================================================
# TICKET SUBMISSION ENDPOINTS
# ============================================================================

@app.route('/api/tickets', methods=['POST'])
def create_new_ticket():
    """
    Create a new support ticket.

    This endpoint handles the complete ticket creation workflow:
    1. Validate input data
    2. Create ticket in database
    3. Categorize using AI
    4. Route to appropriate department

    Request Body:
        {
            "title": "Ticket title",
            "description": "Detailed description",
            "user_name": "User name",
            "user_email": "user@example.com"
        }

    Returns:
        201: {
            "success": true,
            "ticket_id": 123,
            "department": "IT Support",
            "confidence_score": 85,
            "message": "Ticket created successfully"
        }
        400: Validation error
        500: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['title', 'description', 'user_name', 'user_email']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        title = data['title'].strip()
        description = data['description'].strip()
        user_name = data['user_name'].strip()
        user_email = data['user_email'].strip()

        # Basic validation
        if len(title) < 3:
            return jsonify({
                'success': False,
                'error': 'Title must be at least 3 characters'
            }), 400

        if len(description) < 10:
            return jsonify({
                'success': False,
                'error': 'Description must be at least 10 characters'
            }), 400

        # Step 1: Create ticket in database
        ticket_id = create_ticket(title, description, user_name, user_email)
        logger.info(f"Created ticket {ticket_id} for {user_name}")

        # Step 2: AI Categorization
        department, confidence_score = categorize_ticket(title, description)
        logger.info(f"Ticket {ticket_id} categorized as {department} ({confidence_score}%)")

        # Step 3: Route to department
        route_ticket_to_department(ticket_id, department, confidence_score)
        logger.info(f"Ticket {ticket_id} routed to {department}")

        return jsonify({
            'success': True,
            'ticket_id': ticket_id,
            'department': department,
            'confidence_score': confidence_score,
            'status': 'pending',
            'message': 'Ticket created and categorized successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating ticket: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """
    Get details of a specific ticket.

    Args:
        ticket_id: Ticket ID from URL path

    Returns:
        200: Ticket data
        404: Ticket not found
        500: Server error
    """
    try:
        ticket = get_ticket_by_id(ticket_id)

        if ticket is None:
            return jsonify({
                'success': False,
                'error': 'Ticket not found'
            }), 404

        return jsonify({
            'success': True,
            'ticket': ticket
        }), 200

    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/tickets', methods=['GET'])
def get_all_tickets_route():
    """
    Get all tickets in the system.

    Returns:
        200: List of all tickets
        500: Server error
    """
    try:
        tickets = get_all_tickets()

        return jsonify({
            'success': True,
            'count': len(tickets),
            'tickets': tickets
        }), 200

    except Exception as e:
        logger.error(f"Error fetching all tickets: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# TICKET STATUS MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/tickets/<int:ticket_id>/status', methods=['PUT'])
def update_status(ticket_id):
    """
    Update the status of a ticket.

    Request Body:
        {
            "status": "in_progress" | "resolved" | "pending"
        }

    Returns:
        200: Status updated
        400: Invalid status
        404: Ticket not found
        500: Server error
    """
    try:
        data = request.get_json()

        if 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: status'
            }), 400

        new_status = data['status']

        if new_status not in TICKET_STATUSES:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(TICKET_STATUSES)}'
            }), 400

        # Check if ticket exists
        if not ticket_exists(ticket_id):
            return jsonify({
                'success': False,
                'error': 'Ticket not found'
            }), 404

        # Update status
        success = update_ticket_status(ticket_id, new_status)

        if success:
            return jsonify({
                'success': True,
                'message': f'Ticket status updated to {new_status}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update ticket status'
            }), 500

    except Exception as e:
        logger.error(f"Error updating ticket {ticket_id} status: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# DEPARTMENT DASHBOARD ENDPOINTS
# ============================================================================

@app.route('/api/departments/<department>/tickets', methods=['GET'])
def get_department_tickets_route(department):
    """
    Get all tickets for a specific department.

    Query Parameters:
        status: Filter by status (optional)

    Returns:
        200: List of tickets
        400: Invalid department
        500: Server error
    """
    try:
        # Validate department
        if department not in DEPARTMENTS:
            return jsonify({
                'success': False,
                'error': f'Invalid department. Must be one of: {", ".join(DEPARTMENTS)}'
            }), 400

        status_filter = request.args.get('status')

        # Validate status filter if provided
        if status_filter and status_filter not in TICKET_STATUSES:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(TICKET_STATUSES)}'
            }), 400

        # Get tickets
        tickets = get_tickets_by_department(department, status_filter)

        return jsonify({
            'success': True,
            'department': department,
            'status_filter': status_filter,
            'ticket_count': len(tickets),
            'tickets': tickets
        }), 200

    except Exception as e:
        logger.error(f"Error fetching tickets for {department}: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """
    Get summary statistics for the dashboard.

    Returns comprehensive statistics including:
    - Total tickets
    - Distribution by department
    - Distribution by status
    - Average confidence scores

    Returns:
        200: Dashboard summary data
        500: Server error
    """
    try:
        stats = get_ticket_statistics()

        return jsonify({
            'success': True,
            'summary': stats
        }), 200

    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/dashboard/routing', methods=['GET'])
def get_routing_stats():
    """
    Get routing statistics.

    Returns statistics about how tickets are being routed
    and the effectiveness of the AI categorization.

    Returns:
        200: Routing statistics
        500: Server error
    """
    try:
        stats = get_routing_statistics()

        return jsonify({
            'success': True,
            'routing_stats': stats
        }), 200

    except Exception as e:
        logger.error(f"Error fetching routing stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


# ============================================================================
# SYSTEM INFORMATION ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        200: System is healthy
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Smart Ticket System',
        'architecture': 'monolithic',
        'version': '1.0.0'
    }), 200


@app.route('/api/departments', methods=['GET'])
def get_departments_list():
    """
    Get list of available departments.

    Returns:
        200: List of departments
    """
    return jsonify({
        'success': True,
        'departments': DEPARTMENTS
    }), 200


@app.route('/api/statuses', methods=['GET'])
def get_statuses_list():
    """
    Get list of available ticket statuses.

    Returns:
        200: List of statuses
    """
    return jsonify({
        'success': True,
        'statuses': TICKET_STATUSES
    }), 200


@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint with API information.
    """
    return jsonify({
        'service': 'Smart Ticket System',
        'architecture': 'monolithic',
        'version': '1.0.0',
        'endpoints': {
            'tickets': {
                'POST /api/tickets': 'Create a new ticket',
                'GET /api/tickets': 'Get all tickets',
                'GET /api/tickets/<id>': 'Get specific ticket',
                'PUT /api/tickets/<id>/status': 'Update ticket status'
            },
            'departments': {
                'GET /api/departments': 'List all departments',
                'GET /api/departments/<dept>/tickets': 'Get tickets by department'
            },
            'dashboard': {
                'GET /api/dashboard/summary': 'Get dashboard summary',
                'GET /api/dashboard/routing': 'Get routing statistics'
            },
            'system': {
                'GET /api/health': 'Health check',
                'GET /api/statuses': 'List ticket statuses'
            }
        }
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Smart Ticket System - Monolithic Architecture")
    logger.info("=" * 60)
    logger.info(f"Available Departments: {', '.join(DEPARTMENTS)}")
    logger.info(f"Ticket Statuses: {', '.join(TICKET_STATUSES)}")
    logger.info("")
    logger.info("Database: Auto-initialization enabled")
    logger.info(f"Starting server on {FLASK_HOST}:{FLASK_PORT}")
    logger.info("=" * 60)

    # Run the application
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
