import React from 'react'
import { Navigate } from 'react-router-dom'
import { Box, CircularProgress } from '@mui/material'
import { useAuth } from '../../contexts/AuthContext'

const ProtectedRoute = ({ children, requireRole = null, requireAnyRole = null }) => {
  const { user, loading, isAuthenticated, hasRole, hasAnyRole } = useAuth()

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  // Check role-based access if required
  if (requireRole && !hasRole(requireRole)) {
    return (
      <Box sx={{ p: 3 }}>
        <h2>Access Denied</h2>
        <p>You do not have permission to access this page.</p>
        <p>Required role: {requireRole}</p>
        <p>Your role: {user?.role}</p>
      </Box>
    )
  }

  // Check if user has any of the required roles
  if (requireAnyRole && !hasAnyRole(requireAnyRole)) {
    return (
      <Box sx={{ p: 3 }}>
        <h2>Access Denied</h2>
        <p>You do not have permission to access this page.</p>
        <p>Required roles: {requireAnyRole.join(', ')}</p>
        <p>Your role: {user?.role}</p>
      </Box>
    )
  }

  // Render protected content
  return children
}

export default ProtectedRoute
