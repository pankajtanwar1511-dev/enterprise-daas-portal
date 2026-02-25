# Enterprise DaaS Governance Portal - Frontend

Modern React-based frontend for the Enterprise Data-as-a-Service Governance Portal. Built with Material-UI for a professional enterprise experience.

## Technology Stack

- **React 18** - Modern React with hooks
- **Vite** - Next-generation frontend build tool
- **Material-UI (MUI)** - React component library
- **React Router** - Client-side routing
- **Axios** - HTTP client for API requests
- **Recharts** - Charting library for dashboards

## Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000` (or configure via `.env`)

## Getting Started

### Installation

```bash
# Install dependencies
npm install

# Or using yarn
yarn install
```

### Environment Configuration

Create a `.env` file in the frontend directory:

```bash
cp .env.example .env
```

Edit `.env` to configure your API endpoint:

```env
VITE_API_URL=http://localhost:8000
```

**Note**: The `VITE_` prefix is required for Vite to expose variables to the client.

### Development Server

```bash
# Start development server (with hot-reload)
npm run dev

# Or using yarn
yarn dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── Auth/            # Authentication components
│   │   │   ├── Login.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── AssetRegistry/   # Asset management
│   │   │   ├── AssetRegistry.jsx
│   │   │   ├── AssetForm.jsx
│   │   │   └── AssetDialog.jsx
│   │   ├── Dashboard/       # Main dashboard
│   │   ├── ComplianceDashboard/
│   │   ├── StrategyDashboard/
│   │   ├── VendorManagement/
│   │   ├── NamingValidator/
│   │   └── ManagementReports/
│   ├── contexts/            # React Context providers
│   │   └── AuthContext.jsx  # Authentication state
│   ├── utils/               # Utility functions
│   │   └── axiosInstance.js # Configured Axios instance
│   ├── App.jsx              # Main app component
│   └── main.jsx             # Entry point
├── .env.example             # Environment template
├── package.json
└── vite.config.js
```

## Features

### 1. Authentication System

- JWT-based authentication
- Login page with demo credentials
- Protected routes requiring authentication
- Role-based access control (RBAC)
- Automatic token refresh and session management

**Demo Credentials:**
- Username: `admin` | Password: `demo123` (Admin role)
- Username: `jsmith` | Password: `demo123` (Data Steward)
- Other users: `mjohnson`, `rdavis`, `cthomas` (password: `demo123`)

### 2. Asset Registry

- **View Assets**: Browse all data assets with filtering
- **Create Assets**: Register new assets with validation
- **Edit Assets**: Update asset details
- **Delete Assets**: Remove assets with confirmation
- **Real-time Naming Validation**: Instant feedback on naming compliance
- **Filtering**: By environment, lifecycle stage, and compliance status

### 3. DaaS Strategy Dashboard

- Business goals tracking with KPIs
- Strategic initiatives monitoring
- Budget allocation and utilization
- ROI metrics and value delivery
- Asset-business alignment visualization

### 4. Vendor & Budget Management

- Vendor relationship tracking
- SLA performance monitoring
- Budget tracking and forecasting
- Contract renewal alerts
- Cost optimization recommendations

### 5. Compliance Dashboard

- Naming convention compliance tracking
- Policy violations overview
- Data quality metrics
- Regulatory compliance status

### 6. Naming Validator

- Real-time naming convention validation
- Standard format: `{ENV}-{DOMAIN}-{SYSTEM}-{VERSION}`
- Detailed violation explanations
- Format guidelines and examples

### 7. Management Reports

- Executive summary reports
- Domain-specific analytics
- Change management history
- Compliance audit trails

## API Integration

All API calls are made through the configured Axios instance (`src/utils/axiosInstance.js`):

- Automatically adds JWT token to requests
- Handles 401 unauthorized responses (redirects to login)
- Base URL configured via `VITE_API_URL` environment variable

### Using the API Client

```javascript
import axiosInstance from '../utils/axiosInstance'

// GET request
const response = await axiosInstance.get('/api/v1/assets')

// POST request
const response = await axiosInstance.post('/api/v1/assets', {
  asset_name: 'PROD-HR-DW-v1',
  domain_id: 1,
  // ...
})

// PUT request
const response = await axiosInstance.put(`/api/v1/assets/${id}`, updateData)

// DELETE request
await axiosInstance.delete(`/api/v1/assets/${id}`)
```

## Authentication Flow

1. User enters credentials on Login page
2. Frontend sends credentials to `/api/v1/auth/login`
3. Backend validates and returns JWT token + user info
4. Token stored in `localStorage`
5. `axiosInstance` automatically includes token in subsequent requests
6. Protected routes check authentication status
7. On token expiry (401 response), user redirected to login

## Role-Based Access Control

Routes can be protected with specific roles:

```javascript
<ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
  <VendorManagement />
</ProtectedRoute>
```

Available roles:
- **Admin** - Full access to all features
- **DataSteward** - Governance and approval authority
- **AssetOwner** - Manage owned assets
- **Viewer** - Read-only access

## Form Validation

### Asset Form Validation

- **Required fields**: Asset name, domain, environment, owner
- **Real-time naming validation**: Debounced API calls (500ms)
- **Format compliance**: Visual feedback (✓ or ✗)
- **Error messages**: Specific violation details

### Naming Convention

Valid asset names must follow:
```
{ENV}-{DOMAIN}-{SYSTEM}-{VERSION}
```

Examples:
- ✅ `PROD-HR-DW-v1`
- ✅ `QA-FIN-ETL-v2.1`
- ❌ `production-finance-system`

## Styling and Theming

The application uses Material-UI with a custom theme (`main.jsx`):

**Color Palette:**
- Primary: `#1976D2` (Blue)
- Dark Primary: `#0D47A1`
- Success: `#4CAF50`
- Warning: `#FF9800`
- Error: `#F44336`

**Typography:**
- Font Family: Roboto, Helvetica Neue
- Headings: Color `#0D47A1` (Dark Blue)

## Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR - changes appear immediately without full page reload.

### Debugging

- Open browser DevTools console for errors
- Check Network tab for API requests
- Use React DevTools extension for component inspection

### Common Issues

**401 Unauthorized Errors:**
- Token expired - log out and log back in
- Backend not running - start backend server
- CORS issues - ensure backend has correct CORS configuration

**API Connection Errors:**
- Check `VITE_API_URL` in `.env`
- Verify backend is running on correct port
- Check browser console for CORS errors

**Build Errors:**
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`

## Testing

### Manual Testing Checklist

- [ ] Login with demo credentials
- [ ] View dashboard (should show real data)
- [ ] Navigate to Asset Registry
- [ ] Create new asset (test naming validation)
- [ ] Edit existing asset
- [ ] Delete asset
- [ ] Test filters on Asset Registry
- [ ] View Strategy Dashboard
- [ ] View Vendor Management
- [ ] Test logout functionality
- [ ] Verify protected routes redirect to login

### Testing Protected Routes

1. Access the app without logging in
2. Should redirect to `/login`
3. After login, should redirect to dashboard
4. Try accessing role-restricted pages with different user roles

## Production Deployment

### Build Optimization

```bash
# Create optimized production build
npm run build
```

Output will be in `dist/` directory.

### Environment Variables for Production

Create production `.env.production`:

```env
VITE_API_URL=https://api.yourdomain.com
```

### Serving Production Build

**Option 1: Static file server**
```bash
npm install -g serve
serve -s dist -p 3000
```

**Option 2: Nginx**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
    }
}
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Create feature branch from `main`
2. Make changes following existing code style
3. Test thoroughly
4. Submit pull request with description

## License

Proprietary - Internal Enterprise Use Only

---

## Quick Reference

### Start Development
```bash
npm install
cp .env.example .env
npm run dev
```

### API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | User login |
| `/api/v1/auth/me` | GET | Get current user |
| `/api/v1/assets` | GET | List assets |
| `/api/v1/assets` | POST | Create asset |
| `/api/v1/assets/{id}` | PUT | Update asset |
| `/api/v1/assets/{id}` | DELETE | Delete asset |
| `/api/v1/assets/validate-naming` | POST | Validate asset name |
| `/api/v1/strategy/dashboard` | GET | Strategy metrics |
| `/api/v1/vendors/dashboard` | GET | Vendor metrics |

For complete API documentation, visit: `http://localhost:8000/api/docs`

---

**Last Updated:** February 22, 2026
