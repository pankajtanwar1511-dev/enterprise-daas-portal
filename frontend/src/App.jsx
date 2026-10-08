import React, { useState } from 'react'
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  Container,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Divider,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Inventory2 as AssetsIcon,
  CheckCircle as ValidatorIcon,
  ChangeCircle as ChangesIcon,
  Assessment as ComplianceIcon,
  TrendingUp as StrategyIcon,
  Business as VendorIcon,
  Description as ReportsIcon,
  AccountCircle as AccountIcon,
  Logout as LogoutIcon,
  Slideshow as SlideshowIcon,
  Build as ToolsIcon,
  History as AuditIcon,
  Speed as SpeedIcon,
  Groups as StakeholdersIcon,
  AttachMoney as BudgetIcon,
  Policy as PolicyIcon,
} from '@mui/icons-material'

import { useAuth } from './contexts/AuthContext'
import Login from './components/Auth/Login'
import ProtectedRoute from './components/Auth/ProtectedRoute'
import Dashboard from './components/Dashboard/Dashboard'
import AssetRegistry from './components/AssetRegistry/AssetRegistry'
import NamingValidator from './components/NamingValidator/NamingValidator'
import ComplianceDashboard from './components/ComplianceDashboard/ComplianceDashboard'
import StrategyDashboard from './components/StrategyDashboard/StrategyDashboard'
import VendorManagement from './components/VendorManagement/VendorManagement'
import ManagementReports from './components/ManagementReports/ManagementReports'
import PPTGenerator from './components/PPTGenerator/PPTGenerator'
import AuditLogsDashboard from './components/AuditLogs/AuditLogsDashboard'
import ChangeRequestsDashboard from './components/ChangeRequests/ChangeRequestsDashboard'
import ImpactAnalysisDashboard from './components/ImpactAnalysis/ImpactAnalysisDashboard'
import DataQualityDashboard from './components/DataQuality/DataQualityDashboard'
import DataLineageDashboard from './components/DataLineage/DataLineageDashboard'
import SLAMonitoringDashboard from './components/SLAMonitoring/SLAMonitoringDashboard'
import PolicyEnforcementDashboard from './components/PolicyEnforcement/PolicyEnforcementDashboard'
import APIKeyManagementDashboard from './components/APIKeys/APIKeyManagementDashboard'
import WebhookManagementDashboard from './components/Webhooks/WebhookManagementDashboard'
import EventCatalogDashboard from './components/EventCatalog/EventCatalogDashboard'
import SchemaRegistryDashboard from './components/SchemaRegistry/SchemaRegistryDashboard'
import IntegrationLogsDashboard from './components/IntegrationLogs/IntegrationLogsDashboard'
import BulkImportDashboard from './components/BulkImport/BulkImportDashboard'
import StakeholdersManagement from './components/StakeholdersManagement/StakeholdersManagement'
import BudgetDashboard from './components/BudgetDashboard/BudgetDashboard'
import GovernancePolicies from './components/GovernancePolicies/GovernancePolicies'

const drawerWidth = 240

const menuSections = [
  {
    title: 'Main',
    items: [
      { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
      { text: 'DaaS Strategy', icon: <StrategyIcon />, path: '/strategy' },
      { text: 'Stakeholders', icon: <StakeholdersIcon />, path: '/stakeholders' },
      { text: 'Budget Dashboard', icon: <BudgetIcon />, path: '/budget' },
      { text: 'Governance Policies', icon: <PolicyIcon />, path: '/governance' },
      { text: 'Vendor & Budget', icon: <VendorIcon />, path: '/vendors' },
      { text: 'Management Reports', icon: <ReportsIcon />, path: '/reports' },
      { text: 'Asset Registry', icon: <AssetsIcon />, path: '/assets' },
      { text: 'Change Requests', icon: <ChangesIcon />, path: '/change-requests' },
      { text: 'Compliance Dashboard', icon: <ComplianceIcon />, path: '/compliance' },
      { text: 'Audit Logs', icon: <AuditIcon />, path: '/audit-logs' },
    ]
  },
  {
    title: 'Tools',
    items: [
      { text: 'Naming Validator', icon: <ValidatorIcon />, path: '/validator' },
      { text: 'Impact Analysis', icon: <ComplianceIcon />, path: '/impact-analysis' },
      { text: 'Data Quality', icon: <ValidatorIcon />, path: '/data-quality' },
      { text: 'Data Lineage', icon: <StrategyIcon />, path: '/data-lineage' },
      { text: 'SLA Monitoring', icon: <SpeedIcon />, path: '/sla-monitoring' },
      { text: 'CI/CD Policies', icon: <ToolsIcon />, path: '/policy-enforcement' },
      { text: 'API Keys', icon: <AccountIcon />, path: '/api-keys' },
      { text: 'Webhooks', icon: <ChangesIcon />, path: '/webhooks' },
      { text: 'Event Catalog', icon: <ReportsIcon />, path: '/event-catalog' },
      { text: 'Schema Registry', icon: <ValidatorIcon />, path: '/schema-registry' },
      { text: 'Integration Logs', icon: <AuditIcon />, path: '/integration-logs' },
      { text: 'Bulk Import', icon: <AssetsIcon />, path: '/bulk-import' },
      { text: 'PPT Generator', icon: <SlideshowIcon />, path: '/ppt-generator' },
    ]
  }
]

function App() {
  const location = useLocation()
  const { user, logout, isAuthenticated, loading } = useAuth()
  const [anchorEl, setAnchorEl] = useState(null)

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleLogout = () => {
    logout()
    handleMenuClose()
  }

  // Show loading screen while checking authentication
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          backgroundColor: '#F5F5F5',
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom>
            Loading...
          </Typography>
        </Box>
      </Box>
    )
  }

  // If on login page, render only login component
  if (location.pathname === '/login') {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
      </Routes>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Top AppBar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: '#0D47A1',
        }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600, flexGrow: 1, color: '#FFFFFF' }}>
            Enterprise DaaS Governance Portal
          </Typography>

          {/* User Profile Menu */}
          {user && (
            <>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
                  {user.first_name} {user.last_name}
                  <Typography component="span" variant="caption" sx={{ display: 'block', opacity: 0.8 }}>
                    {user.role}
                  </Typography>
                </Typography>
                <IconButton
                  onClick={handleMenuOpen}
                  size="small"
                  sx={{ ml: 1 }}
                  aria-controls="user-menu"
                  aria-haspopup="true"
                >
                  <Avatar sx={{ width: 36, height: 36, bgcolor: '#1976D2' }}>
                    {user.first_name?.charAt(0)}
                    {user.last_name?.charAt(0)}
                  </Avatar>
                </IconButton>
              </Box>

              <Menu
                id="user-menu"
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                <MenuItem disabled>
                  <Box>
                    <Typography variant="subtitle2">
                      {user.first_name} {user.last_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {user.email}
                    </Typography>
                    <Typography variant="caption" display="block" color="text.secondary">
                      Role: {user.role}
                    </Typography>
                  </Box>
                </MenuItem>
                <Divider />
                <MenuItem onClick={handleLogout}>
                  <ListItemIcon>
                    <LogoutIcon fontSize="small" />
                  </ListItemIcon>
                  Logout
                </MenuItem>
              </Menu>
            </>
          )}
        </Toolbar>
      </AppBar>

      {/* Side Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: 'border-box',
            backgroundColor: '#FAFAFA',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', mt: 2 }}>
          {menuSections.map((section, sectionIndex) => (
            <Box key={section.title}>
              {sectionIndex > 0 && <Divider sx={{ my: 1 }} />}
              <Typography
                variant="overline"
                sx={{
                  px: 2,
                  py: 1,
                  display: 'block',
                  color: '#757575',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  letterSpacing: '0.5px',
                }}
              >
                {section.title}
              </Typography>
              <List sx={{ pt: 0 }}>
                {section.items.map((item) => (
                  <ListItem key={item.text} disablePadding>
                    <ListItemButton
                      component={Link}
                      to={item.path}
                      selected={location.pathname === item.path}
                      sx={{
                        '&.Mui-selected': {
                          backgroundColor: '#E3F2FD',
                          borderLeft: '4px solid #1976D2',
                        },
                        '&:hover': {
                          backgroundColor: '#E0E0E0',
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: location.pathname === item.path ? '#1976D2' : '#546E7A' }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText primary={item.text} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          ))}
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, p: 3, backgroundColor: '#F5F5F5', minHeight: '100vh' }}>
        <Toolbar />
        <Container maxWidth="xl" sx={{ mt: 2 }}>
          <Routes>
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/strategy"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward', 'AssetOwner']}>
                  <StrategyDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/vendors"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <VendorManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward', 'AssetOwner']}>
                  <ManagementReports />
                </ProtectedRoute>
              }
            />
            <Route
              path="/ppt-generator"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward', 'AssetOwner']}>
                  <PPTGenerator />
                </ProtectedRoute>
              }
            />
            <Route
              path="/assets"
              element={
                <ProtectedRoute>
                  <AssetRegistry />
                </ProtectedRoute>
              }
            />
            <Route
              path="/validator"
              element={
                <ProtectedRoute>
                  <NamingValidator />
                </ProtectedRoute>
              }
            />
            <Route
              path="/compliance"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <ComplianceDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/audit-logs"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <AuditLogsDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/change-requests"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward', 'AssetOwner']}>
                  <ChangeRequestsDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/impact-analysis"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward', 'AssetOwner']}>
                  <ImpactAnalysisDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/data-quality"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <DataQualityDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/data-lineage"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward', 'AssetOwner']}>
                  <DataLineageDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/sla-monitoring"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <SLAMonitoringDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/policy-enforcement"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <PolicyEnforcementDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/api-keys"
              element={
                <ProtectedRoute>
                  <APIKeyManagementDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/webhooks"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <WebhookManagementDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/event-catalog"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward', 'AssetOwner']}>
                  <EventCatalogDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/schema-registry"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward', 'AssetOwner']}>
                  <SchemaRegistryDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/integration-logs"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <IntegrationLogsDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/bulk-import"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <BulkImportDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/stakeholders"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward', 'AssetOwner']}>
                  <StakeholdersManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/budget"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <BudgetDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/governance"
              element={
                <ProtectedRoute requireAnyRole={['Admin', 'DataSteward']}>
                  <GovernancePolicies />
                </ProtectedRoute>
              }
            />
          </Routes>
        </Container>
      </Box>
    </Box>
  )
}

export default App
