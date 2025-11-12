"""
Test Script for Smart Ticket System

This script demonstrates the ticket system functionality by creating
various sample tickets that should be categorized into different departments.

Usage:
    1. Start the Flask application: python app.py
    2. In a new terminal, run: python test_tickets.py

The script will:
- Create sample tickets covering all departments
- Display categorization results
- Show the effectiveness of AI categorization
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
BASE_URL = 'http://localhost:5000'
API_URL = f'{BASE_URL}/api'

# Test Tickets - Each should be categorized into a different department
SAMPLE_TICKETS = [
    # IT Support Tickets
    {
        'title': 'Cannot access email account',
        'description': 'I am unable to login to my email account. Keep getting "invalid password" error even though I am sure my password is correct. Need help resetting it.',
        'user_name': 'John Doe',
        'user_email': 'john.doe@company.com',
        'expected_department': 'IT Support'
    },
    {
        'title': 'Laptop running very slow',
        'description': 'My laptop has been running extremely slow for the past week. Applications take forever to open and the system freezes frequently. I think I might need more RAM or the hard drive might be full.',
        'user_name': 'Sarah Smith',
        'user_email': 'sarah.smith@company.com',
        'expected_department': 'IT Support'
    },
    {
        'title': 'Need software installation',
        'description': 'I need Adobe Photoshop installed on my workstation for the new marketing project. Can someone from IT help me with the installation and licensing?',
        'user_name': 'Mike Johnson',
        'user_email': 'mike.johnson@company.com',
        'expected_department': 'IT Support'
    },
    {
        'title': 'WiFi connection issues',
        'description': 'The WiFi in the office keeps disconnecting every few minutes. This is affecting my productivity as I cannot stay connected to video calls or download files.',
        'user_name': 'Emily Davis',
        'user_email': 'emily.davis@company.com',
        'expected_department': 'IT Support'
    },

    # HR Tickets
    {
        'title': 'Question about health benefits',
        'description': 'I would like to know more about the dental coverage in our health benefits package. Specifically, does it cover orthodontic treatments? Also, how do I add a dependent to my plan?',
        'user_name': 'Robert Wilson',
        'user_email': 'robert.wilson@company.com',
        'expected_department': 'HR'
    },
    {
        'title': 'Payroll discrepancy',
        'description': 'My last paycheck seems to be missing overtime hours from last month. I worked 10 hours of overtime but they are not reflected in my pay stub. Can you please review this?',
        'user_name': 'Lisa Anderson',
        'user_email': 'lisa.anderson@company.com',
        'expected_department': 'HR'
    },
    {
        'title': 'Sick leave request',
        'description': 'I need to take sick leave for next Monday and Tuesday as I have a medical procedure scheduled. How do I formally request this leave and what documentation do you need?',
        'user_name': 'David Martinez',
        'user_email': 'david.martinez@company.com',
        'expected_department': 'HR'
    },
    {
        'title': 'Performance review question',
        'description': 'My annual performance review is coming up next week. I wanted to know what format it will take and if there is any preparation I should do beforehand.',
        'user_name': 'Jennifer Taylor',
        'user_email': 'jennifer.taylor@company.com',
        'expected_department': 'HR'
    },

    # Facilities Tickets
    {
        'title': 'Office temperature too cold',
        'description': 'The air conditioning in our section of the office is set way too cold. Multiple people have complained about it. Can someone adjust the thermostat or check the HVAC system?',
        'user_name': 'Christopher Brown',
        'user_email': 'christopher.brown@company.com',
        'expected_department': 'Facilities'
    },
    {
        'title': 'Broken office chair',
        'description': 'My office chair is broken - the hydraulic lift no longer works and one of the armrests is loose. I need a replacement as soon as possible for ergonomic reasons.',
        'user_name': 'Amanda White',
        'user_email': 'amanda.white@company.com',
        'expected_department': 'Facilities'
    },
    {
        'title': 'Meeting room cleaning needed',
        'description': 'Conference Room B has not been cleaned in several days. There are coffee stains on the table and the trash bins are overflowing. We have an important client meeting scheduled there tomorrow.',
        'user_name': 'James Garcia',
        'user_email': 'james.garcia@company.com',
        'expected_department': 'Facilities'
    },
    {
        'title': 'Parking spot request',
        'description': 'I recently transferred to this office location and need to be assigned a parking spot. Is there an available spot in the employee parking lot?',
        'user_name': 'Maria Rodriguez',
        'user_email': 'maria.rodriguez@company.com',
        'expected_department': 'Facilities'
    },

    # Finance Tickets
    {
        'title': 'Expense reimbursement inquiry',
        'description': 'I submitted an expense report three weeks ago for client dinner expenses totaling $235. I have not yet received reimbursement. Can you check the status of this?',
        'user_name': 'Daniel Lee',
        'user_email': 'daniel.lee@company.com',
        'expected_department': 'Finance'
    },
    {
        'title': 'Invoice payment question',
        'description': 'We received an invoice from our vendor that seems to have incorrect amounts. Before processing payment, I need someone from finance to review it and confirm the discrepancy.',
        'user_name': 'Michelle Chen',
        'user_email': 'michelle.chen@company.com',
        'expected_department': 'Finance'
    },
    {
        'title': 'Budget allocation question',
        'description': 'I need clarification on my department budget for Q4. How much is allocated for marketing expenses and what is the approval process for expenditures over $5000?',
        'user_name': 'Kevin Patel',
        'user_email': 'kevin.patel@company.com',
        'expected_department': 'Finance'
    },
    {
        'title': 'Purchase order approval',
        'description': 'I need to purchase new equipment for our team totaling $12,000. What is the process for getting purchase order approval and how long does it typically take?',
        'user_name': 'Rachel Kim',
        'user_email': 'rachel.kim@company.com',
        'expected_department': 'Finance'
    },

    # General Tickets
    {
        'title': 'General inquiry about office hours',
        'description': 'I was wondering if the office building will be open during the upcoming holiday weekend. I need to pick up some materials I left in my office.',
        'user_name': 'Steven Thompson',
        'user_email': 'steven.thompson@company.com',
        'expected_department': 'General'
    },
    {
        'title': 'Suggestion for employee lounge',
        'description': 'I have a suggestion to improve the employee lounge. It would be great if we could have a coffee machine and some comfortable seating. This would make breaks more relaxing.',
        'user_name': 'Nicole Jackson',
        'user_email': 'nicole.jackson@company.com',
        'expected_department': 'General'
    }
]


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70)


def print_subheader(text):
    """Print a formatted subheader"""
    print("\n" + "-" * 70)
    print(text)
    print("-" * 70)


def check_server():
    """Check if the server is running"""
    try:
        response = requests.get(f'{API_URL}/health', timeout=5)
        if response.status_code == 200:
            return True
        return False
    except requests.exceptions.RequestException:
        return False


def create_ticket(ticket_data):
    """Create a ticket via API"""
    try:
        response = requests.post(
            f'{API_URL}/tickets',
            json={
                'title': ticket_data['title'],
                'description': ticket_data['description'],
                'user_name': ticket_data['user_name'],
                'user_email': ticket_data['user_email']
            },
            timeout=30
        )

        if response.status_code == 201:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def get_dashboard_summary():
    """Get dashboard summary"""
    try:
        response = requests.get(f'{API_URL}/dashboard/summary', timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None


def run_tests():
    """Run the ticket creation tests"""
    print_header("SMART TICKET SYSTEM - TEST SCRIPT")

    # Check if server is running
    print("\nChecking if server is running...", end=' ')
    if not check_server():
        print("❌ FAILED")
        print("\nERROR: Server is not running!")
        print("Please start the server first: python app.py")
        return
    print("✓ Server is running")

    # Create tickets
    print_subheader("Creating Sample Tickets")

    results = []
    correct_categorizations = 0
    total_tickets = len(SAMPLE_TICKETS)

    for i, ticket_data in enumerate(SAMPLE_TICKETS, 1):
        print(f"\n[{i}/{total_tickets}] Creating: {ticket_data['title']}")
        print(f"    Expected: {ticket_data['expected_department']}")

        result = create_ticket(ticket_data)

        if result and result.get('success'):
            department = result.get('department')
            confidence = result.get('confidence_score')
            ticket_id = result.get('ticket_id')

            print(f"    Result:   {department} (confidence: {confidence}%)")
            print(f"    Ticket ID: {ticket_id}")

            # Check if categorization matches expectation
            is_correct = (department == ticket_data['expected_department'])
            if is_correct:
                correct_categorizations += 1
                print("    Status:   ✓ Correct")
            else:
                print("    Status:   ✗ Incorrect")

            results.append({
                'ticket_id': ticket_id,
                'title': ticket_data['title'],
                'expected': ticket_data['expected_department'],
                'actual': department,
                'confidence': confidence,
                'correct': is_correct
            })
        else:
            print("    Status:   ❌ Failed to create")
            results.append({
                'title': ticket_data['title'],
                'expected': ticket_data['expected_department'],
                'actual': 'ERROR',
                'confidence': 0,
                'correct': False
            })

        # Small delay to avoid overwhelming the AI service
        time.sleep(1)

    # Display summary
    print_subheader("TEST RESULTS SUMMARY")

    accuracy = (correct_categorizations / total_tickets * 100) if total_tickets > 0 else 0
    print(f"\nTotal Tickets Created: {total_tickets}")
    print(f"Correct Categorizations: {correct_categorizations}")
    print(f"Incorrect Categorizations: {total_tickets - correct_categorizations}")
    print(f"Accuracy: {accuracy:.1f}%")

    # Display categorization breakdown
    print("\n\nCategorization Breakdown:")
    print(f"{'Expected':<15} {'Actual':<15} {'Confidence':<12} {'Status':<10}")
    print("-" * 55)

    for result in results:
        status = "✓ Correct" if result['correct'] else "✗ Wrong"
        print(f"{result['expected']:<15} {result['actual']:<15} {result['confidence']:<12} {status:<10}")

    # Get dashboard summary
    print_subheader("DASHBOARD SUMMARY")
    summary = get_dashboard_summary()

    if summary and summary.get('success'):
        stats = summary['summary']
        print(f"\nTotal Tickets: {stats['total_tickets']}")
        print(f"Average Confidence: {stats['average_confidence']}%")

        print("\nTickets by Department:")
        for dept, count in stats['by_department'].items():
            print(f"  {dept}: {count}")

        print("\nTickets by Status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")

    print_header("TEST COMPLETE")
    print(f"\nYou can view all tickets at: {BASE_URL}/api/tickets")
    print(f"Dashboard summary: {BASE_URL}/api/dashboard/summary")
    print("\nPress Ctrl+C to exit")


if __name__ == '__main__':
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError running tests: {e}")
