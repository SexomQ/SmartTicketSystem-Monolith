"""
Department Routing Module for Smart Ticket System

Handles the routing of tickets to appropriate departments.
This module acts as the bridge between AI categorization and
the department queues.

In a monolithic architecture, this is straightforward - just
update the database. In a microservices architecture, this
would involve:
- Publishing events to message queues
- Notifying department services
- Managing distributed state
"""

import logging
from database import update_ticket_department
from config import DEPARTMENTS

logger = logging.getLogger(__name__)


def route_ticket_to_department(ticket_id, department, confidence_score):
    """
    Route a ticket to the appropriate department.

    This function assigns a ticket to a department queue based on
    the AI categorization result.

    Args:
        ticket_id: ID of the ticket to route
        department: Department name (must be valid)
        confidence_score: AI confidence score (0-100)

    Returns:
        bool: True if routing was successful, False otherwise

    Raises:
        ValueError: If department is invalid
    """
    # Validate department
    if department not in DEPARTMENTS:
        logger.error(f"Invalid department: {department}")
        raise ValueError(f"Invalid department. Must be one of: {', '.join(DEPARTMENTS)}")

    # Validate confidence score
    if not isinstance(confidence_score, (int, float)) or confidence_score < 0 or confidence_score > 100:
        logger.error(f"Invalid confidence score: {confidence_score}")
        raise ValueError("Confidence score must be between 0 and 100")

    # Update the ticket in the database
    success = update_ticket_department(ticket_id, department, confidence_score)

    if success:
        logger.info(f"Successfully routed ticket {ticket_id} to {department} department")
        return True
    else:
        logger.error(f"Failed to route ticket {ticket_id} to {department}")
        return False


def reroute_ticket(ticket_id, new_department, confidence_score):
    """
    Reroute a ticket to a different department.

    This can be used when:
    - Manual override is needed
    - AI categorization was incorrect
    - Business rules change

    Args:
        ticket_id: ID of the ticket to reroute
        new_department: New department name
        confidence_score: Updated confidence score

    Returns:
        bool: True if rerouting was successful, False otherwise
    """
    logger.info(f"Rerouting ticket {ticket_id} to {new_department}")
    return route_ticket_to_department(ticket_id, new_department, confidence_score)


def get_routing_statistics():
    """
    Get statistics about ticket routing.

    Returns statistics that can help understand routing patterns
    and AI accuracy.

    Returns:
        dict: Routing statistics
    """
    from database import get_ticket_statistics

    stats = get_ticket_statistics()

    # Add routing-specific information
    routing_stats = {
        'department_distribution': stats['by_department'],
        'average_confidence': stats['average_confidence'],
        'total_routed': stats['total_tickets']
    }

    # Calculate distribution percentages
    total = stats['total_tickets']
    if total > 0:
        routing_stats['department_percentages'] = {
            dept: round((count / total) * 100, 2)
            for dept, count in stats['by_department'].items()
        }
    else:
        routing_stats['department_percentages'] = {}

    return routing_stats


def validate_routing_rules():
    """
    Validate that routing configuration is correct.

    This is useful for system health checks and startup validation.

    Returns:
        dict: Validation results
    """
    issues = []

    # Check that departments are defined
    if not DEPARTMENTS or len(DEPARTMENTS) == 0:
        issues.append("No departments defined")

    # Check for duplicate departments
    if len(DEPARTMENTS) != len(set(DEPARTMENTS)):
        issues.append("Duplicate departments found")

    # Check that all departments have valid names
    for dept in DEPARTMENTS:
        if not isinstance(dept, str) or not dept.strip():
            issues.append(f"Invalid department name: {dept}")

    is_valid = len(issues) == 0

    return {
        'is_valid': is_valid,
        'departments_count': len(DEPARTMENTS),
        'departments': DEPARTMENTS,
        'issues': issues
    }
