# Smart Ticket System - Monolithic Architecture

A comprehensive ticket management system with AI-powered categorization using Anthropic's Claude API. This system automatically categorizes support tickets into appropriate departments using advanced AI.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Architecture Analysis](#architecture-analysis)

## Features

- **Automated Ticket Categorization**: Uses Claude AI to categorize tickets into departments
- **Multiple Departments**: IT Support, HR, Facilities, Finance, and General
- **Status Tracking**: Track tickets through pending, in_progress, and resolved states
- **Department Dashboards**: View and manage tickets by department
- **Confidence Scoring**: AI provides confidence scores for categorizations
- **Fallback Mechanism**: Keyword-based categorization when AI is unavailable
- **RESTful API**: Complete REST API for all operations
- **Official Claude API**: Uses Anthropic's official Claude 3.5 Haiku model (fast and cost-effective)
- **Auto-Initialization**: Database automatically initializes on first run

## Architecture

### Monolithic Design

This application follows a **monolithic architecture** where all components are part of a single application. The code is organized into separate modules for maintainability while maintaining the simplicity of monolithic deployment.

```
┌─────────────────────────────────────────────┐
│         Flask Application (app.py)          │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────────────┐    │
│  │   Ticket     │  │       AI         │    │
│  │  Submission  │──│  Categorization  │    │
│  └──────────────┘  └──────────────────┘    │
│         │                   │               │
│         │                   │               │
│  ┌──────────────┐  ┌──────────────────┐    │
│  │  Department  │  │    Dashboard     │    │
│  │   Routing    │  │    & Reports     │    │
│  └──────────────┘  └──────────────────┘    │
│         │                   │               │
│         └─────────┬─────────┘               │
│                   │                         │
│         ┌─────────────────┐                 │
│         │    Database     │                 │
│         │  (database.py)  │                 │
│         └─────────────────┘                 │
│                   │                         │
└───────────────────┼─────────────────────────┘
                    │
              ┌─────────────┐
              │   SQLite    │
              │  tickets.db │
              └─────────────┘
```

### Benefits of Monolithic Architecture

✅ **Simple Deployment**: Single application to deploy and manage
✅ **Easy Development**: All code in one place, easier to understand
✅ **No Network Latency**: Components communicate via function calls
✅ **Atomic Transactions**: Database operations are straightforward
✅ **Simplified Testing**: Test entire system in one go
✅ **Lower Complexity**: No service discovery, load balancing, or distributed systems concerns

### Trade-offs

⚠️ **Scaling**: Must scale entire application, not individual components
⚠️ **Deployment**: All components deployed together (no independent releases)
⚠️ **Single Point of Failure**: If app goes down, all features are unavailable
⚠️ **Technology Lock-in**: All components must use the same tech stack
⚠️ **Maintenance**: Can become harder to maintain as codebase grows

### Comparison with Microservices

| Aspect | Monolithic | Microservices |
|--------|-----------|---------------|
| **Deployment** | Single deployment unit | Multiple independent services |
| **Scaling** | Scale entire app | Scale individual services |
| **Complexity** | Low | High |
| **Development Speed** | Fast initially | Slower initially, faster long-term |
| **Failure Isolation** | Low | High |
| **Data Consistency** | Easy (local transactions) | Complex (distributed transactions) |
| **Team Organization** | Can share codebase | Teams own services |
| **Technology Flexibility** | Limited | High |

## Project Structure

```
SmartTicketSystem-Monolith/
│
├── app.py                  # Main Flask application with all routes
├── config.py               # Configuration constants
├── database.py             # Database operations and queries
├── ai_categorization.py    # AI categorization logic using g4f
├── routing.py              # Department routing logic
├── init_db.py              # Database initialization script
├── test_tickets.py         # Test script with sample tickets
├── requirements.txt        # Python dependencies
├── tickets.db              # SQLite database (created after init)
└── README.md              # This file
```

### Module Descriptions

**app.py**: Main application file containing:
- Flask routes and endpoints
- Request validation
- Error handling
- API documentation

**config.py**: Centralized configuration:
- Department definitions
- Status options
- AI retry settings
- Flask configuration

**database.py**: Database abstraction layer:
- Connection management
- CRUD operations
- Query helpers
- Transaction handling

**ai_categorization.py**: AI categorization engine:
- Official Anthropic Claude API integration
- Prompt engineering
- Response parsing
- Fallback categorization

**routing.py**: Department routing logic:
- Ticket assignment
- Routing validation
- Statistics gathering

## Prerequisites

### Claude API Key

This application requires a Claude API key from Anthropic.

1. **Get your API key**:
   - Visit [https://console.anthropic.com/](https://console.anthropic.com/)
   - Sign up or log in to your account
   - Navigate to API Keys section
   - Create a new API key

2. **Set up your environment**:

   **Option A: Using .env file (Recommended)**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your API key
   # CLAUDE_API_KEY=your_actual_api_key_here
   ```

   **Option B: Using environment variable**

   On Windows:
   ```bash
   set CLAUDE_API_KEY=your_actual_api_key_here
   ```

   On Mac/Linux:
   ```bash
   export CLAUDE_API_KEY=your_actual_api_key_here
   ```

   **Option C: Using Docker**
   ```bash
   # Create .env file with your API key
   echo "CLAUDE_API_KEY=your_actual_api_key_here" > .env

   # Docker Compose will automatically load it
   ```

**Important**: Never commit your `.env` file or API key to version control!

## Installation

You can run the application either directly with Python or using Docker containers.

### Option 1: Docker (Recommended)

Docker provides an isolated, consistent environment and is the easiest way to get started.

#### Prerequisites

- Docker (20.10 or higher)
- Docker Compose (1.29 or higher)

#### Setup Steps

1. **Clone or download the project**

2. **Build and run with Docker Compose**

```bash
docker-compose up -d
```

This will:
- Build the Docker image
- Initialize the database automatically
- Start the application in the background
- Make it available on `http://localhost:5000`

3. **Check the logs** (optional)

```bash
docker-compose logs -f
```

4. **Stop the application**

```bash
docker-compose down
```

#### Alternative: Using Docker directly

```bash
# Build the image
docker build -t smart-ticket-system .

# Run the container
docker run -d -p 5000:5000 --name ticket-system smart-ticket-system

# View logs
docker logs -f ticket-system

# Stop the container
docker stop ticket-system

# Remove the container
docker rm ticket-system
```

### Option 2: Direct Python Installation

#### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

#### Setup Steps

1. **Clone or download the project**

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Initialize the database**

```bash
python init_db.py
```

You should see:
```
✓ Database initialized successfully!
✓ Created 'tickets' table with proper indexes
✓ Database file: tickets.db
```

4. **Start the application**

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Usage

### Starting the Server

#### With Docker

```bash
docker-compose up -d
```

Check if it's running:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f ticket-system
```

#### With Python

```bash
python app.py
```

You should see:
```
============================================================
Smart Ticket System - Monolithic Architecture
============================================================
Available Departments: IT Support, HR, Facilities, Finance, General
Ticket Statuses: pending, in_progress, resolved

IMPORTANT: Run 'python init_db.py' first if you haven't
           initialized the database yet.

Starting server on 0.0.0.0:5000
============================================================
```

### Creating a Ticket

Use curl, Postman, or the test script:

```bash
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Laptop is running slow",
    "description": "My laptop has been running very slow. Applications take forever to open.",
    "user_name": "John Doe",
    "user_email": "john.doe@company.com"
  }'
```

Response:
```json
{
  "success": true,
  "ticket_id": 1,
  "department": "IT Support",
  "confidence_score": 85,
  "status": "pending",
  "message": "Ticket created and categorized successfully"
}
```

### Running the Test Suite

The test script creates 20 sample tickets covering all departments.

#### With Docker

```bash
# Run tests from your host machine (server must be running)
python test_tickets.py

# OR run tests inside the container
docker-compose exec ticket-system python test_tickets.py
```

#### With Python

```bash
python test_tickets.py
```

This will:
- Create tickets for each department
- Display categorization results
- Show accuracy statistics
- Display dashboard summary

## API Documentation

### Base URL

```
http://localhost:5000/api
```

### Endpoints

#### 1. Create Ticket

**POST** `/tickets`

Create a new support ticket. The system will automatically categorize it.

**Request Body:**
```json
{
  "title": "Ticket title",
  "description": "Detailed description of the issue",
  "user_name": "User Name",
  "user_email": "user@example.com"
}
```

**Response (201):**
```json
{
  "success": true,
  "ticket_id": 123,
  "department": "IT Support",
  "confidence_score": 85,
  "status": "pending",
  "message": "Ticket created and categorized successfully"
}
```

#### 2. Get Ticket

**GET** `/tickets/<id>`

Retrieve details of a specific ticket.

**Response (200):**
```json
{
  "success": true,
  "ticket": {
    "id": 123,
    "title": "Cannot access email",
    "description": "I cannot login to my email account",
    "user_name": "John Doe",
    "user_email": "john.doe@company.com",
    "department": "IT Support",
    "confidence_score": 85,
    "status": "pending",
    "created_at": "2025-01-15 10:30:00",
    "updated_at": "2025-01-15 10:30:00"
  }
}
```

#### 3. Get All Tickets

**GET** `/tickets`

Retrieve all tickets in the system.

**Response (200):**
```json
{
  "success": true,
  "count": 50,
  "tickets": [...]
}
```

#### 4. Update Ticket Status

**PUT** `/tickets/<id>/status`

Update the status of a ticket.

**Request Body:**
```json
{
  "status": "in_progress"
}
```

Valid statuses: `pending`, `in_progress`, `resolved`

**Response (200):**
```json
{
  "success": true,
  "message": "Ticket status updated to in_progress"
}
```

#### 5. Get Department Tickets

**GET** `/departments/<department>/tickets?status=<status>`

Get all tickets for a specific department, optionally filtered by status.

**Parameters:**
- `department`: IT Support, HR, Facilities, Finance, or General
- `status` (optional): pending, in_progress, or resolved

**Response (200):**
```json
{
  "success": true,
  "department": "IT Support",
  "status_filter": null,
  "ticket_count": 15,
  "tickets": [...]
}
```

#### 6. Dashboard Summary

**GET** `/dashboard/summary`

Get summary statistics for all tickets.

**Response (200):**
```json
{
  "success": true,
  "summary": {
    "total_tickets": 100,
    "by_department": {
      "IT Support": 35,
      "HR": 20,
      "Facilities": 15,
      "Finance": 18,
      "General": 12
    },
    "by_status": {
      "pending": 45,
      "in_progress": 30,
      "resolved": 25
    },
    "average_confidence": 78.5
  }
}
```

#### 7. Routing Statistics

**GET** `/dashboard/routing`

Get detailed routing statistics.

**Response (200):**
```json
{
  "success": true,
  "routing_stats": {
    "department_distribution": {...},
    "average_confidence": 78.5,
    "total_routed": 100,
    "department_percentages": {
      "IT Support": 35.0,
      "HR": 20.0,
      ...
    }
  }
}
```

#### 8. System Endpoints

**GET** `/health` - Health check
**GET** `/departments` - List all departments
**GET** `/statuses` - List all ticket statuses
**GET** `/` - API information

## Testing

### Manual Testing

1. **Start the server:**
```bash
python app.py
```

2. **In a new terminal, run the test script:**
```bash
python test_tickets.py
```

### Expected Results

The test script creates 20 tickets across all departments. You should see:

- Accuracy around 80-95% (depending on AI availability)
- Correct categorization for most tickets
- Confidence scores typically between 60-95%
- Complete dashboard summary

### Testing Individual Endpoints

Use curl or Postman to test specific endpoints:

```bash
# Health check
curl http://localhost:5000/api/health

# Get all departments
curl http://localhost:5000/api/departments

# Get dashboard summary
curl http://localhost:5000/api/dashboard/summary
```

## Architecture Analysis

### Why Monolithic?

This project uses a monolithic architecture for several reasons:

1. **Project Scope**: The system has well-defined boundaries and limited features
2. **Team Size**: Typically developed/maintained by a small team
3. **Deployment Simplicity**: Single deployment unit is easier to manage
4. **Performance**: No network overhead between components
5. **Development Speed**: Faster to develop initially

### When to Consider Microservices

Consider migrating to microservices when:

- **Scale**: Different components need independent scaling (e.g., AI service needs more resources)
- **Team Size**: Multiple teams working on different features
- **Technology**: Need different tech stacks for different components
- **Deployment**: Need to deploy features independently
- **Resilience**: Need to isolate failures in specific components

### Migration Path

The modular structure makes migration easier:

```
Current Monolith          →    Future Microservices
─────────────────              ────────────────────
app.py                    →    API Gateway
database.py               →    Database Service
ai_categorization.py      →    AI Service (Python)
routing.py                →    Routing Service
```

### Performance Considerations

**Monolithic Advantages:**
- No network latency between modules
- Single database connection pool
- Simplified caching
- Easy to profile and optimize

**Monolithic Challenges:**
- AI calls can block other operations (solution: async processing)
- Database can become bottleneck (solution: connection pooling, indexes)
- Memory usage grows with features (solution: resource limits, monitoring)

### Database Design

**Current: SQLite**
- Perfect for development and small deployments
- Single file, no setup required
- Good performance for <100k records

**Future: PostgreSQL/MySQL**
- Better for production
- Concurrent access
- Advanced features (JSON, full-text search)

### Error Handling

The system implements multiple layers of error handling:

1. **AI Service Retry**: 3 attempts with backoff
2. **Fallback Categorization**: Keyword-based when AI fails
3. **Database Transactions**: Automatic rollback on errors
4. **API Validation**: Input validation at endpoint level
5. **Logging**: Comprehensive logging for debugging

## Troubleshooting

### Server won't start

**Problem**: `Address already in use`
**Solution**: Another process is using port 5000
```bash
# Change port in config.py or kill the process
lsof -ti:5000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :5000    # Windows
```

### Database errors

**Problem**: `no such table: tickets`
**Solution**: Initialize the database
```bash
python init_db.py
```

### AI categorization fails

**Problem**: All tickets categorized as "General" with low confidence
**Solution**:
- Check if CLAUDE_API_KEY is set correctly
- Verify your API key is valid at https://console.anthropic.com/
- Check if you have API credits/quota available
- Check internet connection
- The fallback system is working (using keywords)

**Problem**: `ValueError: CLAUDE_API_KEY environment variable is not set`
**Solution**: Set your Claude API key
```bash
# Create .env file
echo "CLAUDE_API_KEY=your_actual_api_key_here" > .env

# Or set environment variable
export CLAUDE_API_KEY=your_actual_api_key_here  # Mac/Linux
set CLAUDE_API_KEY=your_actual_api_key_here     # Windows
```

### Import errors

**Problem**: `ModuleNotFoundError`
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Docker Issues

**Problem**: `Cannot connect to the Docker daemon`
**Solution**: Make sure Docker is running
```bash
# Check Docker status
docker --version
docker info
```

**Problem**: Port 5000 already in use with Docker
**Solution**: Change the port mapping in docker-compose.yml
```yaml
ports:
  - "5001:5000"  # Use port 5001 instead
```

**Problem**: Container keeps restarting
**Solution**: Check the logs
```bash
docker-compose logs ticket-system
```

**Problem**: Database not persisting after container restart
**Solution**: Make sure the volume is properly configured in docker-compose.yml

**Problem**: Changes to code not reflected in container
**Solution**: Rebuild the image
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

**Note**: This system uses Anthropic's official Claude API for AI-powered ticket categorization. You need a valid API key to use the AI features. The fallback keyword-based categorization ensures the system continues working even when AI services are unavailable or API key is not configured.