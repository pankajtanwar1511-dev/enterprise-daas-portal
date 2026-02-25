import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { AuthProvider } from './contexts/AuthContext'
import App from './App'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976D2',
      dark: '#0D47A1',
      light: '#BBDEFB',
    },
    secondary: {
      main: '#546E7A',
    },
    success: {
      main: '#4CAF50',
    },
    warning: {
      main: '#FF9800',
    },
    error: {
      main: '#F44336',
    },
    background: {
      default: '#F5F5F5',
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: "'Roboto', 'Helvetica Neue', sans-serif",
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
      color: '#0D47A1',
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      color: '#0D47A1',
    },
    h6: {
      fontSize: '1.1rem',
      fontWeight: 500,
      color: '#546E7A',
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'uppercase',
          borderRadius: 4,
        },
      },
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>
)
