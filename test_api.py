"""
API Test Script for Smart Ticket System

This script tests all API endpoints to ensure they are working correctly.
Run this after starting the Flask application to verify all routes.

Usage:
    python test_api.py
"""

import requests
import json
import sys
import time
import io

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 60  # seconds

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")

def print_test(test_name):
    """Print test name"""
    print(f"\n{Colors.CYAN}Testing: {test_name}{Colors.RESET}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.YELLOW}  {message}{Colors.RESET}")

def print_response(response):
    """Print formatted response data"""
    try:
        data = response.json()
        print(f"{Colors.YELLOW}  Response: {json.dumps(data, indent=2)}{Colors.RESET}")
    except:
        print(f"{Colors.YELLOW}  Response: {response.text}{Colors.RESET}")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "total": 0
}

def run_test(test_name, method, endpoint, expected_status, data=None, validate_fn=None):
    """
    Run a single API test

    Args:
        test_name: Name of the test
        method: HTTP method (GET, POST, PUT, etc.)
        endpoint: API endpoint (e.g., '/api/health')
        expected_status: Expected HTTP status code
        data: Request body data (for POST/PUT)
        validate_fn: Optional function to validate response data

    Returns:
        Response object or None if test failed
    """
    global test_results
    test_results["total"] += 1

    print_test(f"{method} {endpoint}")

    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=TIMEOUT)
        else:
            print_error(f"Unsupported HTTP method: {method}")
            test_results["failed"] += 1
            return None

        # Check status code
        if response.status_code == expected_status:
            print_success(f"Status code: {response.status_code} (Expected: {expected_status})")
        else:
            print_error(f"Status code: {response.status_code} (Expected: {expected_status})")
            print_response(response)
            test_results["failed"] += 1
            return None

        # Validate response data if validation function provided
        if validate_fn:
            try:
                response_data = response.json()
                if validate_fn(response_data):
                    print_success("Response validation passed")
                else:
                    print_error("Response validation failed")
                    print_response(response)
                    test_results["failed"] += 1
                    return None
            except Exception as e:
                print_error(f"Validation error: {str(e)}")
                print_response(response)
                test_results["failed"] += 1
                return None

        print_success(f"Test passed: {test_name}")
        test_results["passed"] += 1
        print_response(response)
        return response

    except requests.exceptions.ConnectionError:
        print_error(f"Connection failed. Is the server running at {BASE_URL}?")
        test_results["failed"] += 1
        return None
    except requests.exceptions.Timeout:
        print_error(f"Request timeout after {TIMEOUT} seconds")
        test_results["failed"] += 1
        return None
    except Exception as e:
        print_error(f"Test error: {str(e)}")
        test_results["failed"] += 1
        return None

def main():
    """Main test execution"""
    print_header("SMART TICKET SYSTEM - API TEST SUITE")
    print(f"Base URL: {BASE_URL}")
    print(f"Timeout: {TIMEOUT}s")

    # Track created ticket ID for later tests
    ticket_id = None

    # ========================================================================
    # 1. SYSTEM HEALTH & INFO ENDPOINTS
    # ========================================================================
    print_header("1. SYSTEM HEALTH & INFO ENDPOINTS")

    # Test health endpoint
    run_test(
        "Health Check",
        "GET",
        "/api/health",
        200,
        validate_fn=lambda r: r.get("status") == "healthy"
    )

    # Test root endpoint
    run_test(
        "Root Endpoint",
        "GET",
        "/",
        200,
        validate_fn=lambda r: "service" in r and "endpoints" in r
    )

    # Test departments list
    run_test(
        "List Departments",
        "GET",
        "/api/departments",
        200,
        validate_fn=lambda r: r.get("success") == True and "departments" in r
    )

    # Test statuses list
    run_test(
        "List Ticket Statuses",
        "GET",
        "/api/statuses",
        200,
        validate_fn=lambda r: r.get("success") == True and "statuses" in r
    )

    # ========================================================================
    # 2. TICKET CREATION
    # ========================================================================
    print_header("2. TICKET CREATION")

    # Test creating a ticket
    ticket_data = {
        "title": "Test Ticket - Laptop Not Working",
        "description": "My laptop won't turn on. I've tried pressing the power button multiple times but nothing happens. Need urgent help!",
        "user_name": "John Doe",
        "user_email": "john.doe@example.com"
    }

    response = run_test(
        "Create New Ticket",
        "POST",
        "/api/tickets",
        201,
        data=ticket_data,
        validate_fn=lambda r: r.get("success") == True and "ticket_id" in r and "department" in r
    )

    if response:
        ticket_id = response.json().get("ticket_id")
        print_info(f"Created ticket ID: {ticket_id}")

    # Test creating another ticket
    ticket_data_2 = {
        "title": "Need Help with Payroll",
        "description": "I haven't received my salary for this month. Can someone from HR help me with this issue?",
        "user_name": "Jane Smith",
        "user_email": "jane.smith@example.com"
    }

    run_test(
        "Create Second Ticket",
        "POST",
        "/api/tickets",
        201,
        data=ticket_data_2,
        validate_fn=lambda r: r.get("success") == True and r.get("department") is not None
    )

    # Test validation - missing field
    run_test(
        "Create Ticket - Missing Field (Should Fail)",
        "POST",
        "/api/tickets",
        400,
        data={"title": "Test", "description": "Test"},
        validate_fn=lambda r: r.get("success") == False
    )

    # Test validation - title too short
    run_test(
        "Create Ticket - Title Too Short (Should Fail)",
        "POST",
        "/api/tickets",
        400,
        data={
            "title": "Hi",
            "description": "This is a test description",
            "user_name": "Test User",
            "user_email": "test@example.com"
        },
        validate_fn=lambda r: r.get("success") == False
    )

    # ========================================================================
    # 3. TICKET RETRIEVAL
    # ========================================================================
    print_header("3. TICKET RETRIEVAL")

    if ticket_id:
        # Test getting specific ticket
        run_test(
            "Get Specific Ticket",
            "GET",
            f"/api/tickets/{ticket_id}",
            200,
            validate_fn=lambda r: r.get("success") == True and r.get("ticket") is not None
        )

        # Test getting non-existent ticket
        run_test(
            "Get Non-Existent Ticket (Should Fail)",
            "GET",
            "/api/tickets/99999",
            404,
            validate_fn=lambda r: r.get("success") == False
        )
    else:
        print_error("Skipping ticket retrieval tests - no ticket ID available")

    # Test getting all tickets
    run_test(
        "Get All Tickets",
        "GET",
        "/api/tickets",
        200,
        validate_fn=lambda r: r.get("success") == True and "tickets" in r
    )

    # ========================================================================
    # 4. TICKET STATUS UPDATES
    # ========================================================================
    print_header("4. TICKET STATUS UPDATES")

    if ticket_id:
        # Test updating status to in_progress
        run_test(
            "Update Ticket Status to 'in_progress'",
            "PUT",
            f"/api/tickets/{ticket_id}/status",
            200,
            data={"status": "in_progress"},
            validate_fn=lambda r: r.get("success") == True
        )

        # Test updating status to resolved
        run_test(
            "Update Ticket Status to 'resolved'",
            "PUT",
            f"/api/tickets/{ticket_id}/status",
            200,
            data={"status": "resolved"},
            validate_fn=lambda r: r.get("success") == True
        )

        # Test invalid status
        run_test(
            "Update with Invalid Status (Should Fail)",
            "PUT",
            f"/api/tickets/{ticket_id}/status",
            400,
            data={"status": "invalid_status"},
            validate_fn=lambda r: r.get("success") == False
        )

        # Test missing status field
        run_test(
            "Update without Status Field (Should Fail)",
            "PUT",
            f"/api/tickets/{ticket_id}/status",
            400,
            data={},
            validate_fn=lambda r: r.get("success") == False
        )

        # Test updating non-existent ticket
        run_test(
            "Update Non-Existent Ticket (Should Fail)",
            "PUT",
            "/api/tickets/99999/status",
            404,
            data={"status": "resolved"},
            validate_fn=lambda r: r.get("success") == False
        )
    else:
        print_error("Skipping status update tests - no ticket ID available")

    # ========================================================================
    # 5. DEPARTMENT QUERIES
    # ========================================================================
    print_header("5. DEPARTMENT QUERIES")

    # Test getting tickets by department
    departments = ["IT Support", "HR", "Finance", "Facilities", "General"]

    for dept in departments[:2]:  # Test first two departments
        run_test(
            f"Get Tickets for {dept}",
            "GET",
            f"/api/departments/{dept}/tickets",
            200,
            validate_fn=lambda r: r.get("success") == True and "tickets" in r
        )

    # Test with status filter
    run_test(
        "Get IT Support Tickets (Status: resolved)",
        "GET",
        "/api/departments/IT Support/tickets?status=resolved",
        200,
        validate_fn=lambda r: r.get("success") == True
    )

    # Test invalid department
    run_test(
        "Get Tickets for Invalid Department (Should Fail)",
        "GET",
        "/api/departments/InvalidDept/tickets",
        400,
        validate_fn=lambda r: r.get("success") == False
    )

    # ========================================================================
    # 6. DASHBOARD & STATISTICS
    # ========================================================================
    print_header("6. DASHBOARD & STATISTICS")

    # Test dashboard summary
    run_test(
        "Get Dashboard Summary",
        "GET",
        "/api/dashboard/summary",
        200,
        validate_fn=lambda r: r.get("success") == True and "summary" in r
    )

    # Test routing statistics
    run_test(
        "Get Routing Statistics",
        "GET",
        "/api/dashboard/routing",
        200,
        validate_fn=lambda r: r.get("success") == True and "routing_stats" in r
    )

    # ========================================================================
    # 7. ERROR HANDLING
    # ========================================================================
    print_header("7. ERROR HANDLING")

    # Test 404 - non-existent endpoint
    run_test(
        "Test 404 Error",
        "GET",
        "/api/nonexistent",
        404,
        validate_fn=lambda r: r.get("success") == False
    )

    # ========================================================================
    # RESULTS SUMMARY
    # ========================================================================
    print_header("TEST RESULTS SUMMARY")

    print(f"\nTotal Tests: {test_results['total']}")
    print(f"{Colors.GREEN}Passed: {test_results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {test_results['failed']}{Colors.RESET}")

    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")

    if test_results['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)
