# Docker Deployment Guide
## Enterprise DaaS Governance Portal

This guide explains how to run the entire application stack using Docker.

---

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### One-Command Startup

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL** database (port 5432)
- **Backend** API (port 8000)
- **Frontend** UI (port 80)
- **Redis** cache (port 6379)

### Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📋 Detailed Instructions

### 1. Build Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### 2. Start Services

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached)
docker-compose up -d

# Start specific services
docker-compose up -d postgres backend
```

### 3. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### 4. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ DELETES DATA)
docker-compose down -v
```

---

## 🗄️ Database Management

### Run Migrations

```bash
# Migrations run automatically on startup
# To run manually:
docker-compose exec backend alembic upgrade head
```

### Seed Data

```bash
docker-compose exec backend python seed_data.py
```

### Access Database

```bash
# Using docker-compose
docker-compose exec postgres psql -U daas_admin -d governance_portal

# From host (if port exposed)
psql -h localhost -U daas_admin -d governance_portal
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U daas_admin governance_portal > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U daas_admin governance_portal < backup.sql
```

---

## 🔧 Development Mode

### Hot Reload (Backend)

The backend is configured with `--reload` flag and volume mounting for hot reload:

```yaml
volumes:
  - ./backend:/app
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Edit code → Changes reflect automatically ✅

### Frontend Development

For frontend development with hot reload, use local npm:

```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173
```

Configure frontend to call backend at `http://localhost:8000`

---

## 🌍 Environment Variables

### Using .env file

Create `.env` file in project root:

```bash
# .env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://daas_admin:password@postgres:5432/governance_portal
ALLOWED_ORIGINS=http://localhost,http://localhost:3000
```

Docker Compose automatically loads `.env` file.

### Override for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    environment:
      DATABASE_URL: postgresql://user:pass@prod-db:5432/governance_portal
      DEBUG: "False"
      LOG_LEVEL: INFO
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📊 Monitoring & Health Checks

### Check Service Health

```bash
# All services status
docker-compose ps

# Health check details
docker inspect daas-backend | grep Health -A 10
```

### Resource Usage

```bash
# Real-time stats
docker stats daas-backend daas-frontend daas-postgres

# Disk usage
docker system df
```

---

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready → Wait longer, increase sleep in command
# 2. Migration failed → Check migration files
# 3. Port already in use → Change port in docker-compose.yml
```

### Database Connection Error

```bash
# Test database connectivity
docker-compose exec backend python -c "from app.database import engine; engine.connect()"

# Check postgres is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### Frontend Shows 404

```bash
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Check nginx logs
docker-compose logs frontend
```

### Clear Everything and Start Fresh

```bash
# ⚠️ THIS DELETES ALL DATA
docker-compose down -v
docker system prune -a
docker-compose up -d
```

---

## 📦 Production Deployment

### 1. Build Production Images

```bash
# Set production environment
export ENVIRONMENT=production

# Build with production tags
docker-compose build

# Tag images
docker tag daas-backend:latest your-registry/daas-backend:v2.0
docker tag daas-frontend:latest your-registry/daas-frontend:v2.0
```

### 2. Push to Registry

```bash
docker push your-registry/daas-backend:v2.0
docker push your-registry/daas-frontend:v2.0
```

### 3. Deploy to Server

```bash
# On production server
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. SSL/TLS with Nginx

Add reverse proxy with Let's Encrypt:

```bash
# Use nginx-proxy + letsencrypt-companion
# See: https://github.com/nginx-proxy/nginx-proxy
```

---

## 🔒 Security Best Practices

1. **Change default passwords** in production
2. **Use secrets management** (Docker Secrets, AWS Secrets Manager)
3. **Run as non-root user** (already configured in Dockerfiles)
4. **Enable SSL/TLS** for production
5. **Limit exposed ports** (only 80/443 in production)
6. **Use private Docker registry** for images
7. **Scan images for vulnerabilities**:
   ```bash
   docker scan daas-backend:latest
   ```

---

## 🧪 Testing with Docker

```bash
# Run backend tests
docker-compose exec backend pytest tests/ -v

# Run tests with coverage
docker-compose exec backend pytest tests/ --cov=app --cov-report=html
```

---

## 📝 Useful Commands

```bash
# Execute command in running container
docker-compose exec backend bash

# Copy files from container
docker cp daas-backend:/app/logs/app.log ./local-logs/

# View container details
docker inspect daas-backend

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Last Updated:** February 2026
**Version:** 2.0.0
