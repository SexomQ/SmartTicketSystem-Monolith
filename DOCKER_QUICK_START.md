# Docker Quick Start Guide

This guide will help you get the Smart Ticket System running in Docker in under 2 minutes.

## Prerequisites

- Docker installed ([Download Docker](https://www.docker.com/products/docker-desktop))
- Docker Compose installed (included with Docker Desktop)

## Quick Start (3 Commands)

### 1. Navigate to the project directory

```bash
cd SmartTicketSystem-Monolith
```

### 2. Build and start the application

```bash
docker-compose up -d
```

This command will:
- Build the Docker image with all dependencies
- Initialize the SQLite database automatically
- Start the application in detached mode (background)
- Expose the application on port 5000

### 3. Verify it's running

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Smart Ticket System",
  "architecture": "monolithic",
  "version": "1.0.0"
}
```

## That's It!

Your application is now running at: **http://localhost:5000**

## Common Commands

### View logs
```bash
docker-compose logs -f
```

### Stop the application
```bash
docker-compose down
```

### Restart the application
```bash
docker-compose restart
```

### Run tests
```bash
# From your host machine
python test_tickets.py

# OR inside the container
docker-compose exec ticket-system python test_tickets.py
```

### Access the container shell
```bash
docker-compose exec ticket-system /bin/bash
```

## Testing the Application

### Create a test ticket

```bash
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test ticket",
    "description": "My computer won't turn on",
    "user_name": "Test User",
    "user_email": "test@example.com"
  }'
```

### Get dashboard summary

```bash
curl http://localhost:5000/api/dashboard/summary
```

### List all departments

```bash
curl http://localhost:5000/api/departments
```

## Troubleshooting

### Container won't start

Check the logs:
```bash
docker-compose logs ticket-system
```

### Port 5000 is already in use

Edit `docker-compose.yml` and change the port:
```yaml
ports:
  - "5001:5000"  # Use port 5001 instead
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### Code changes not reflected

Rebuild the image:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints
- Run the test suite: `python test_tickets.py`
- Check the architecture analysis in the README

## Cleaning Up

To completely remove the application and its data:

```bash
# Stop and remove containers, networks
docker-compose down

# Remove the Docker image
docker rmi smartticketsystem-monolith-ticket-system

# Remove volumes (WARNING: This deletes the database)
docker-compose down -v
```

## Environment Variables

You can customize the application by setting environment variables in `docker-compose.yml`:

```yaml
environment:
  - FLASK_ENV=production
  - FLASK_DEBUG=False
  - DATABASE_NAME=tickets.db
```

## Production Considerations

For production deployment, consider:

1. **Use proper secrets management** for sensitive data
2. **Configure a reverse proxy** (Nginx, Traefik)
3. **Set up SSL/TLS** certificates
4. **Use PostgreSQL** instead of SQLite for better concurrency
5. **Add monitoring** (Prometheus, Grafana)
6. **Configure log aggregation** (ELK stack, Loki)
7. **Set resource limits** in docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
```

## Need Help?

- Check the [full README](README.md) for detailed documentation
- Review the [API Documentation](README.md#api-documentation)
- Check the [Troubleshooting section](README.md#troubleshooting)
