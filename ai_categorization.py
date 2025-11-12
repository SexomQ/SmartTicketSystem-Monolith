"""
AI Categorization Module for Smart Ticket System

Uses Anthropic's Claude API to categorize tickets into departments.
This module handles:
- AI model interaction via official Anthropic SDK
- Response parsing
- Retry logic for robustness
- Fallback strategies when AI is unavailable

The module is designed to be resilient and always return a result,
even if the AI service is unavailable.
"""

import logging
import time
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError
from config import (
    DEPARTMENTS,
    AI_MAX_RETRIES,
    AI_RETRY_DELAY,
    AI_DEFAULT_CONFIDENCE,
    AI_FALLBACK_CONFIDENCE,
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_MAX_TOKENS
)

logger = logging.getLogger(__name__)


def categorize_ticket(title, description):
    """
    Categorize a ticket into a department using AI.

    This function uses the g4f library to access AI models without API keys.
    It implements retry logic and has fallback behavior for robustness.

    Args:
        title: Ticket title
        description: Ticket description

    Returns:
        tuple: (department_name, confidence_score)
               Always returns a valid department, defaults to 'General' on failure
    """
    # Build the prompt for the AI
    prompt = _build_categorization_prompt(title, description)

    # Try to get AI categorization with retries
    for attempt in range(AI_MAX_RETRIES):
        try:
            logger.info(f"AI categorization attempt {attempt + 1}/{AI_MAX_RETRIES}")

            # Call AI service
            response_text = _call_ai_service(prompt)

            # Parse the response
            department, confidence = _parse_ai_response(response_text)

            # Validate and return if successful
            if department and department in DEPARTMENTS:
                if confidence is None:
                    confidence = AI_DEFAULT_CONFIDENCE
                logger.info(f"Categorized as: {department} (confidence: {confidence}%)")
                return department, confidence
            else:
                logger.warning(f"Invalid department in response: {department}")

        except Exception as e:
            logger.error(f"AI categorization error (attempt {attempt + 1}): {e}")

            # Wait before retrying (except on last attempt)
            if attempt < AI_MAX_RETRIES - 1:
                time.sleep(AI_RETRY_DELAY)

    # All attempts failed - use fallback strategy
    logger.warning("All AI categorization attempts failed, using fallback")
    return _fallback_categorization(title, description)


def _build_categorization_prompt(title, description):
    """
    Build the prompt for AI categorization.

    Args:
        title: Ticket title
        description: Ticket description

    Returns:
        str: Formatted prompt for the AI
    """
    prompt = f"""Categorize this support ticket into exactly one of these departments: IT Support, HR, Facilities, Finance, or General.

Ticket Title: {title}
Ticket Description: {description}

Respond in this exact format:
Department: [department name]
Confidence: [number from 0-100]

Rules:
- IT Support: Technical issues, software, hardware, network, passwords, computers, internet, email, applications
- HR: Employee relations, benefits, payroll, hiring, leave, training, performance reviews, workplace issues
- Facilities: Building maintenance, office space, equipment, cleaning, parking, security, temperature
- Finance: Budgets, expenses, invoicing, purchasing, reimbursements, accounting, financial reports
- General: Everything else that doesn't fit above categories"""

    return prompt


def _call_ai_service(prompt):
    """
    Make a call to the Claude API using the official Anthropic SDK.

    Args:
        prompt: The prompt to send to the AI

    Returns:
        str: AI response text

    Raises:
        Exception: If the AI service call fails
    """
    if not CLAUDE_API_KEY:
        raise ValueError("CLAUDE_API_KEY environment variable is not set")

    try:
        # Create Anthropic client with explicit configuration
        # Note: Some versions don't support proxies parameter, so we just use api_key
        client = Anthropic(
            api_key=CLAUDE_API_KEY,
            timeout=30.0  # 30 second timeout for API calls
        )

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = response.content[0].text.strip()
        logger.info(f"AI Response: {response_text}")

        return response_text

    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        raise
    except APIConnectionError as e:
        logger.error(f"API connection error: {e}")
        raise
    except APIError as e:
        logger.error(f"API error: {e}")
        raise
    except TypeError as e:
        # Handle initialization errors (like proxy parameter issues)
        logger.error(f"Client initialization error: {e}")
        raise


def _parse_ai_response(response_text):
    """
    Parse the AI response to extract department and confidence.

    Args:
        response_text: Raw text response from AI

    Returns:
        tuple: (department, confidence) or (None, None) if parsing fails
    """
    department = None
    confidence = None

    for line in response_text.split('\n'):
        line = line.strip()

        if line.startswith('Department:'):
            dept = line.replace('Department:', '').strip()
            # Match department case-insensitively
            for valid_dept in DEPARTMENTS:
                if valid_dept.lower() == dept.lower():
                    department = valid_dept
                    break

        elif line.startswith('Confidence:'):
            try:
                confidence = int(line.replace('Confidence:', '').strip())
                # Clamp confidence to valid range
                confidence = max(0, min(100, confidence))
            except ValueError:
                logger.warning(f"Could not parse confidence value: {line}")
                confidence = None

    return department, confidence


def _fallback_categorization(title, description):
    """
    Fallback categorization using simple keyword matching.

    This is used when AI service is unavailable. It's not as accurate
    as AI but ensures the system continues to function.

    Args:
        title: Ticket title
        description: Ticket description

    Returns:
        tuple: (department_name, confidence_score)
    """
    text = (title + " " + description).lower()

    # Keyword-based matching
    it_keywords = ['computer', 'laptop', 'software', 'hardware', 'network', 'internet',
                   'email', 'password', 'login', 'system', 'application', 'printer',
                   'wifi', 'server', 'database', 'access', 'account']

    hr_keywords = ['payroll', 'salary', 'benefits', 'leave', 'vacation', 'sick',
                   'employee', 'hiring', 'training', 'performance', 'hr', 'human resources']

    facilities_keywords = ['building', 'office', 'room', 'maintenance', 'cleaning',
                          'parking', 'security', 'temperature', 'hvac', 'desk',
                          'chair', 'facility', 'repair']

    finance_keywords = ['budget', 'expense', 'invoice', 'payment', 'reimbursement',
                       'purchase', 'accounting', 'financial', 'cost', 'money']

    # Count keyword matches
    scores = {
        'IT Support': sum(1 for keyword in it_keywords if keyword in text),
        'HR': sum(1 for keyword in hr_keywords if keyword in text),
        'Facilities': sum(1 for keyword in facilities_keywords if keyword in text),
        'Finance': sum(1 for keyword in finance_keywords if keyword in text),
        'General': 0
    }

    # Find department with most matches
    department = max(scores, key=scores.get)

    # If no keywords matched, use General
    if scores[department] == 0:
        department = 'General'
        confidence = AI_FALLBACK_CONFIDENCE
    else:
        # Calculate confidence based on match count
        confidence = min(50 + (scores[department] * 10), 75)

    logger.info(f"Fallback categorization: {department} (confidence: {confidence}%)")
    return department, confidence


def recategorize_ticket(title, description):
    """
    Recategorize an existing ticket.

    This can be used if the initial categorization was incorrect
    or if the ticket details have changed.

    Args:
        title: Ticket title
        description: Ticket description

    Returns:
        tuple: (department_name, confidence_score)
    """
    logger.info("Recategorizing ticket")
    return categorize_ticket(title, description)
