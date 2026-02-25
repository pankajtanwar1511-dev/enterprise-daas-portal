import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext(null)

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Check if user is logged in on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (err) {
        console.error('Failed to parse stored user:', err)
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      }
    }

    setLoading(false)
  }, [])

  const login = async (username, password) => {
    try {
      setError(null)
      setLoading(true)

      // OAuth2 password flow requires FormData
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await axios.post(`${API_URL}/api/v1/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      const { access_token, user: userData } = response.data

      // Store token and user data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))

      setUser(userData)
      setLoading(false)

      return { success: true }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Login failed. Please check your credentials.'
      setError(errorMessage)
      setLoading(false)
      return { success: false, error: errorMessage }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
    setError(null)
  }

  const register = async (userData) => {
    try {
      setError(null)
      setLoading(true)

      const response = await axios.post(`${API_URL}/api/v1/auth/register`, userData)

      const { user: newUser } = response.data

      setLoading(false)
      return { success: true, user: newUser }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Registration failed. Please try again.'
      setError(errorMessage)
      setLoading(false)
      return { success: false, error: errorMessage }
    }
  }

  const getToken = () => {
    return localStorage.getItem('access_token')
  }

  const isAuthenticated = () => {
    return !!user && !!localStorage.getItem('access_token')
  }

  const hasRole = (requiredRole) => {
    if (!user) return false
    return user.role === requiredRole
  }

  const hasAnyRole = (roles) => {
    if (!user) return false
    return roles.includes(user.role)
  }

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    register,
    getToken,
    isAuthenticated,
    hasRole,
    hasAnyRole,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
