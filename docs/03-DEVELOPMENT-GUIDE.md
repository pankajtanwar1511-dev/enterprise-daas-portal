# Enterprise DaaS Governance Portal - Development Guide

**Version:** 3.0
**Last Updated:** February 25, 2026
**Target Audience:** Developers

---

## Table of Contents

1. [Development Setup](#1-development-setup)
2. [Testing Strategy](#2-testing-strategy)
3. [Code Style & Standards](#3-code-style--standards)
4. [Debugging & Troubleshooting](#4-debugging--troubleshooting)

---

## 1. Development Setup

### Quick Start

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
createdb governance_portal
alembic upgrade head && python seed_data.py
uvicorn app.main:app --reload

# Frontend  
cd frontend
npm install && npm run dev
```

### Environment Variables

```bash
# backend/.env
DATABASE_URL=postgresql://postgres:password@localhost/governance_portal
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 2. Testing Strategy

### Test Levels

**Unit Tests (tests/unit/):**
- Fast, fully mocked, no database
- Test individual functions/methods
- Run: `pytest tests/unit/ -v`

**Integration Tests (tests/integration/):**
- Test component interactions
- Use test database
- Run: `pytest tests/integration/ -v`

**E2E Tests (tests/e2e/):**
- Full application flow
- Requires running servers
- Run: `pytest tests/e2e/ -v -m e2e`

### Coverage

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

**Target:** >80% code coverage

---

## 3. Code Style & Standards

### Backend (Python)

**Style Guide:** PEP 8

```bash
# Lint
flake8 app/

# Format
black app/

# Type checking
mypy app/
```

**Best Practices:**
- Use type hints
- Write docstrings
- Keep functions small (<50 lines)
- Use dependency injection
- Log errors with context

### Frontend (JavaScript/React)

**Style Guide:** Airbnb JavaScript Style Guide

```bash
# Lint
npm run lint

# Fix
npm run lint:fix
```

**Best Practices:**
- Functional components with hooks
- Destructure props
- Use Material-UI sx prop for styling
- Keep components focused
- Handle loading/error states

---

## 4. Debugging & Troubleshooting

### Backend Issues

**Issue: Port 8000 already in use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill <PID>

# Or kill by name
pkill -f uvicorn
```

**Issue: ModuleNotFoundError**
```bash
# Ensure virtual environment is activated
source backend/venv/bin/activate  # Check (venv) in prompt

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

**Issue: Database connection error**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection manually
psql -U postgres -d governance_portal

# If database doesn't exist, create it
sudo -u postgres createdb governance_portal

# Check connection string in .env
cat backend/.env | grep DATABASE_URL
```

**Issue: Database migration errors**
```bash
# View current migration version
alembic current

# View migration history
alembic history

# Reset database (DEVELOPMENT ONLY - destroys data!)
dropdb governance_portal
createdb governance_portal
alembic upgrade head
python seed_data.py
```

**Issue: Alembic can't find migrations**
```bash
# Ensure you're in backend/ directory
pwd  # Should show .../enterprise-daas-portal/backend

# Check alembic.ini exists
ls alembic.ini

# Initialize Alembic (if not already done)
alembic init migrations
```

### Frontend Issues

**Issue: Port 5173 already in use**
```bash
# Find and kill process
lsof -i :5173
kill <PID>

# Or kill by name
pkill -f vite
```

**Issue: npm install fails**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

**Issue: Cannot connect to backend**
```bash
# Verify backend is running
curl http://localhost:8000/

# Expected response: {"message":"Enterprise DaaS Governance Portal API"}

# Check CORS settings in backend/app/main.py
# Should include http://localhost:5173 in allowed origins

# Check frontend is making requests to correct URL
# Look for VITE_API_URL in frontend/.env or check axios base URL
```

**Issue: Frontend shows blank page**
```bash
# Check browser console (F12) for errors

# Common causes:
# 1. API endpoint incorrect
# 2. CORS error (check backend logs)
# 3. JavaScript syntax error (check console)
# 4. Missing environment variables

# Try clearing browser cache
# Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
```

### Common Workflow Issues

**Issue: Virtual environment not activated**
```bash
# Symptom: Command not found errors (uvicorn, alembic, etc.)

# Solution: Always activate venv first
cd backend
source venv/bin/activate

# Verify: prompt should show (venv)
```

**Issue: Wrong directory**
```bash
# Symptom: File not found errors

# Check current directory
pwd

# Navigate to correct directory
cd /path/to/enterprise-daas-portal/backend  # or /frontend
```

**Issue: Environment variables not set**
```bash
# Check .env file exists
ls backend/.env

# If missing, create it
cd backend
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost/governance_portal
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF

# Verify .env is loaded
cd backend && source venv/bin/activate
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('SECRET_KEY'))"
```

**Issue: Changes not reflecting in frontend**
```bash
# Frontend has hot reload, but sometimes fails

# Solution 1: Check terminal for errors
# Solution 2: Restart dev server (Ctrl+C, then npm run dev)
# Solution 3: Clear browser cache (Ctrl+Shift+R)
# Solution 4: Check file was actually saved
```

**Issue: Changes not reflecting in backend**
```bash
# Backend auto-reloads with --reload flag

# If not working:
# 1. Check terminal for syntax errors
# 2. Restart: Ctrl+C, then uvicorn app.main:app --reload
# 3. Verify --reload flag is present in command
```

### Performance Issues

**Issue: Slow API responses**
```bash
# Check database query performance
# In psql:
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Enable query logging (backend/app/database.py)
# Set echo=True in create_engine()

# Check for missing indexes
# See Technical Guide Section 3.6 for index strategy
```

**Issue: High memory usage**
```bash
# Check process memory
ps aux | grep uvicorn
ps aux | grep node

# Backend: Check for unclosed database sessions
# Frontend: Check for memory leaks in React components
```

### Debug Tools

**Backend:**
```python
# Python debugger
import pdb; pdb.set_trace()

# Or use ipdb (better)
import ipdb; ipdb.set_trace()

# Logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message", exc_info=True)
```

**API Testing:**
- Interactive docs: http://localhost:8000/api/docs
- curl commands: `curl -X GET http://localhost:8000/api/v1/assets`
- Postman or Insomnia for complex requests

**Frontend:**
- React DevTools browser extension
- Redux DevTools (if using Redux)
- Console.log debugging
- Network tab for API calls (F12 → Network)
- React component profiler

**Database:**
```bash
# View tables
psql -U postgres -d governance_portal -c "\dt"

# Count records
psql -U postgres -d governance_portal -c "SELECT COUNT(*) FROM assets;"

# View recent assets
psql -U postgres -d governance_portal -c "SELECT asset_id, asset_name, created_at FROM assets ORDER BY created_at DESC LIMIT 10;"
```

### Getting Help

If issues persist:

1. **Check logs:**
   - Backend: Console output where uvicorn is running
   - Frontend: Browser console (F12)
   - Database: PostgreSQL logs at `/var/log/postgresql/`

2. **Search documentation:**
   - FastAPI: https://fastapi.tiangolo.com/
   - React: https://react.dev/
   - SQLAlchemy: https://docs.sqlalchemy.org/

3. **Check GitHub Issues:**
   - Search for similar problems
   - Create new issue with error logs and steps to reproduce

---

**Version:** 3.0
**Status:** Published
