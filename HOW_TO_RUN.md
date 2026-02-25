# How to Run the Enterprise DaaS Governance Portal

**Last Updated:** February 22, 2026
**Status:** ✅ Ready to Run

---

## 🚀 Quick Start (TL;DR)

```bash
# Terminal 1: Start Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

---

## 📋 Prerequisites

### System Requirements
- **Python:** 3.8+ (for backend)
- **Node.js:** 16+ (for frontend)
- **PostgreSQL:** 13+ (production) or SQLite (development)
- **Git:** Latest version

### Check Your Environment
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check Node.js version
node --version     # Should be 16+

# Check npm version
npm --version      # Should be 7+
```

---

## 🏗️ First-Time Setup

### 1. Clone Repository (if not already done)
```bash
git clone <repository-url>
cd enterprise-daas-portal
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///./governance_portal.db
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF

# Run database migrations (if using Alembic)
alembic upgrade head

# Seed database with sample data
python seed_data.py
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file (optional)
cat > .env << EOF
VITE_API_URL=http://localhost:8000
EOF
```

---

## ▶️ Running the Application

### Option 1: Manual Start (Development)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**What you'll see:**
```
Backend (Terminal 1):
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete

Frontend (Terminal 2):
  VITE v5.0.2  ready in 342 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
```

### Option 2: Quick Start Script

Create a startup script:

```bash
# File: start.sh
#!/bin/bash

echo "🚀 Starting Enterprise DaaS Portal..."

# Start backend in background
cd backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
sleep 3

# Start frontend in background
cd ../frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✓ Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to be ready
sleep 5

echo ""
echo "🎉 Application is running!"
echo ""
echo "📍 Access Points:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo ""
echo "📊 Logs:"
echo "   Backend:   tail -f backend.log"
echo "   Frontend:  tail -f frontend.log"
echo ""
echo "🛑 To stop:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
```

Make it executable and run:
```bash
chmod +x start.sh
./start.sh
```

### Option 3: Using Docker (Future)

```bash
# Not yet implemented, coming soon
docker-compose up
```

---

## 🌐 Access the Application

### Frontend (User Interface)
**URL:** http://localhost:5173

**What you'll see:**
- Login page (if authentication is enabled)
- Dashboard with navigation sidebar
- 11 modules:
  1. Dashboard
  2. Asset Registry
  3. Naming Validator
  4. Compliance Dashboard
  5. Strategy Dashboard
  6. Vendor Management
  7. Management Reports
  8. SLA Monitoring
  9. API Keys
  10. Webhooks
  11. Settings

### Backend API
**URL:** http://localhost:8000

**Endpoints:**
- `GET /` - Root endpoint (health check)
- `GET /api/v1/*` - API endpoints
- `GET /api/docs` - Swagger UI (interactive API documentation)
- `GET /api/redoc` - ReDoc (alternative API documentation)

### API Documentation
**URL:** http://localhost:8000/api/docs

**Features:**
- Interactive API testing
- Request/response examples
- Schema definitions
- Authentication testing
- Try out endpoints directly

---

## 🔍 Verify Installation

### 1. Check Backend is Running

```bash
# Test health endpoint
curl http://localhost:8000/

# Expected response:
{"message": "Enterprise DaaS Governance Portal API"}

# Test API endpoint
curl http://localhost:8000/api/v1/domains/

# Should return list of domains
```

### 2. Check Frontend is Running

Open browser:
```
http://localhost:5173
```

You should see the portal interface.

### 3. Check Database

```bash
cd backend
source venv/bin/activate
python

>>> from app.database import engine
>>> from sqlalchemy import inspect
>>> inspector = inspect(engine)
>>> tables = inspector.get_table_names()
>>> print(f"Tables: {len(tables)}")
Tables: 20

>>> exit()
```

---

## 🧪 Run Tests

```bash
cd backend
source venv/bin/activate

# Run all tests with coverage
python run_tests.py

# Run specific test file
pytest tests/unit/test_services.py -v

# Run with detailed output
pytest tests/ -v -s

# View coverage report
xdg-open htmlcov/index.html
```

**Expected output:**
```
=================== 44 passed, 6 failed, 71 errors in 6.65s ===================

Coverage: 50%
```

---

## 🛑 Stopping the Application

### If Running Manually (Ctrl+C)
- Press `Ctrl+C` in each terminal

### If Running in Background
```bash
# Find processes
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Kill by PID
kill <PID>

# Or kill all
pkill -f uvicorn
pkill -f vite
```

### Using Stop Script
```bash
# File: stop.sh
#!/bin/bash

echo "🛑 Stopping Enterprise DaaS Portal..."

# Stop backend
pkill -f "uvicorn app.main:app"
echo "✓ Backend stopped"

# Stop frontend
pkill -f "vite"
echo "✓ Frontend stopped"

echo "✅ Application stopped"
```

---

## 🔧 Troubleshooting

### Backend Won't Start

**Issue:** Port 8000 already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill <PID>
```

**Issue:** ModuleNotFoundError
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue:** Database error
```bash
# Recreate database
rm governance_portal.db
alembic upgrade head
python seed_data.py
```

### Frontend Won't Start

**Issue:** Port 5173 already in use
```bash
# Find and kill process
lsof -i :5173
kill <PID>
```

**Issue:** npm install fails
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue:** Cannot connect to backend
```bash
# Check backend is running
curl http://localhost:8000/

# Check CORS settings in backend/app/main.py
# Should include http://localhost:5173 in allowed origins
```

### Common Issues

**1. Virtual environment not activated**
```bash
# Symptom: Command not found errors
# Solution: Always activate venv first
source backend/venv/bin/activate
```

**2. Wrong directory**
```bash
# Symptom: File not found errors
# Solution: Check you're in correct directory
pwd  # Should be in backend/ or frontend/
```

**3. Dependencies not installed**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

**4. Environment variables not set**
```bash
# Check .env exists
ls backend/.env

# If not, create it
cd backend
cat > .env << EOF
DATABASE_URL=sqlite:///./governance_portal.db
SECRET_KEY=$(openssl rand -hex 32)
EOF
```

---

## 🔐 Default Credentials

After running `seed_data.py`, use these credentials:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| data_steward | steward123 | Data Steward |
| asset_owner | owner123 | Asset Owner |
| viewer | viewer123 | Viewer |

**⚠️ WARNING:** Change these passwords in production!

---

## 📊 Development Workflow

### Typical Day-to-Day Workflow

**Morning startup:**
```bash
cd enterprise-daas-portal

# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Testing
cd backend
source venv/bin/activate
pytest tests/ --watch  # Run tests on file changes
```

**Making changes:**
1. Edit code in your IDE
2. Backend auto-reloads (--reload flag)
3. Frontend hot-reloads automatically
4. Test in browser at http://localhost:5173
5. Check API docs at http://localhost:8000/api/docs

**Before committing:**
```bash
# Run tests
cd backend && python run_tests.py

# Lint code (if configured)
cd frontend && npm run lint

# Check everything works
curl http://localhost:8000/api/v1/assets/
```

---

## 🚀 Production Deployment

See [Technical Architecture](docs/03-technical-architecture.md) for full deployment guide.

**Quick overview:**
1. Build frontend: `npm run build`
2. Serve frontend: Use Nginx or CloudFront
3. Run backend: Use Gunicorn with Uvicorn workers
4. Database: PostgreSQL on RDS
5. SSL: Use Let's Encrypt or AWS Certificate Manager
6. Monitoring: CloudWatch, DataDog, or similar

---

## 📞 Need Help?

**Documentation:**
- [Quick Implementation Guide](docs/12-quick-implementation-guide.md)
- [Technical Architecture](docs/03-technical-architecture.md)
- [Testing Guide](docs/testing/01-testing-guide.md)
- [CLAUDE.md](CLAUDE.md) - AI assistant instructions

**Common Resources:**
- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- Vite Docs: https://vitejs.dev/
- Material-UI: https://mui.com/

**Logs:**
- Backend logs: Console output or `backend.log`
- Frontend logs: Console output or `frontend.log`
- Browser console: F12 in browser

---

## ✅ Checklist

**Before first run:**
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] .env file created
- [ ] Database seeded

**To start application:**
- [ ] Terminal 1: Backend running on port 8000
- [ ] Terminal 2: Frontend running on port 5173
- [ ] Browser: Open http://localhost:5173
- [ ] Can access API docs at http://localhost:8000/api/docs

**Verify working:**
- [ ] Frontend loads without errors
- [ ] Can view dashboard
- [ ] Can navigate to different modules
- [ ] API calls succeed (check browser DevTools Network tab)
- [ ] Login works (if authentication enabled)

---

**Happy Developing! 🎉**

For detailed scenarios and use cases, see [Application Scenarios](docs/13-application-scenarios.md)
