import React, { useState, useEffect } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  InputAdornment,
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  VpnKey as KeyIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material'

function APIKeyManagementDashboard() {
  const [apiKeys, setApiKeys] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [keyCreatedDialogOpen, setKeyCreatedDialogOpen] = useState(false)
  const [createdKeyData, setCreatedKeyData] = useState(null)
  const [showCreatedKey, setShowCreatedKey] = useState(true)

  const [formData, setFormData] = useState({
    key_name: '',
    expires_in_days: 90,
    scopes: [],
    rate_limit_per_hour: 1000,
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axiosInstance.get('/api/v1/api-keys/')
      setApiKeys(response.data)
    } catch (err) {
      console.error('Error fetching API keys:', err)
      setError('Failed to load API keys')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateKey = async (e) => {
    e.preventDefault()
    try {
      const response = await axiosInstance.post('/api/v1/api-keys/', formData)
      setCreatedKeyData(response.data)
      setKeyCreatedDialogOpen(true)
      setCreateDialogOpen(false)
      fetchData()
      setFormData({
        key_name: '',
        expires_in_days: 90,
        scopes: [],
        rate_limit_per_hour: 1000,
      })
    } catch (err) {
      console.error('Error creating API key:', err)
      setError(err.response?.data?.detail || 'Failed to create API key')
    }
  }

  const handleRevokeKey = async (keyId) => {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) return
    try {
      await axiosInstance.delete(`/api/v1/api-keys/${keyId}`)
      fetchData()
    } catch (err) {
      console.error('Error revoking API key:', err)
      setError('Failed to revoke API key')
    }
  }

  const handleToggleKey = async (keyId, isActive) => {
    try {
      const endpoint = isActive
        ? `/api/v1/api-keys/${keyId}/deactivate`
        : `/api/v1/api-keys/${keyId}/activate`
      await axiosInstance.patch(endpoint)
      fetchData()
    } catch (err) {
      console.error('Error toggling API key:', err)
      setError(err.response?.data?.detail || 'Failed to update API key')
    }
  }

  const handleCopyKey = (text) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  const getStatusChip = (key) => {
    const isExpired = key.expires_at && new Date(key.expires_at) < new Date()
    if (isExpired) {
      return <Chip label="Expired" size="small" color="error" icon={<ErrorIcon />} />
    }
    if (!key.active) {
      return <Chip label="Inactive" size="small" color="warning" icon={<WarningIcon />} />
    }
    return <Chip label="Active" size="small" color="success" icon={<CheckCircleIcon />} />
  }

  const getExpiryText = (expiresAt) => {
    if (!expiresAt) return 'Never expires'
    const expiryDate = new Date(expiresAt)
    const now = new Date()
    if (expiryDate < now) return 'Expired'

    const daysLeft = Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24))
    if (daysLeft === 1) return '1 day left'
    if (daysLeft < 30) return `${daysLeft} days left`
    return expiryDate.toLocaleDateString()
  }

  const activeKeys = apiKeys.filter(k => k.active && (!k.expires_at || new Date(k.expires_at) > new Date())).length
  const expiredKeys = apiKeys.filter(k => k.expires_at && new Date(k.expires_at) < new Date()).length

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          API Key Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchData} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create API Key
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <KeyIcon color="primary" />
                <Typography variant="caption" color="textSecondary">
                  Total Keys
                </Typography>
              </Box>
              <Typography variant="h4">{apiKeys.length}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CheckCircleIcon color="success" />
                <Typography variant="caption" color="textSecondary">
                  Active Keys
                </Typography>
              </Box>
              <Typography variant="h4">{activeKeys}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <ErrorIcon color="error" />
                <Typography variant="caption" color="textSecondary">
                  Expired Keys
                </Typography>
              </Box>
              <Typography variant="h4">{expiredKeys}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <WarningIcon color="warning" />
                <Typography variant="caption" color="textSecondary">
                  Total API Calls
                </Typography>
              </Box>
              <Typography variant="h4">
                {apiKeys.reduce((sum, key) => sum + (key.usage_count || 0), 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper>
          <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
            <Typography variant="h6">Your API Keys</Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Key Name</TableCell>
                  <TableCell>Key Prefix</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Expires</TableCell>
                  <TableCell>Usage</TableCell>
                  <TableCell>Last Used</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {apiKeys.length > 0 ? (
                  apiKeys.map((key) => (
                    <TableRow key={key.key_id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <KeyIcon fontSize="small" color="action" />
                          <Typography variant="body2">{key.key_name}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            {key.key_prefix}...
                          </Typography>
                          <Tooltip title="Copy prefix">
                            <IconButton size="small" onClick={() => handleCopyKey(key.key_prefix)}>
                              <CopyIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                      <TableCell>{getStatusChip(key)}</TableCell>
                      <TableCell>{new Date(key.created_at).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <Typography variant="body2" color={
                          !key.expires_at ? 'textPrimary' :
                          new Date(key.expires_at) < new Date() ? 'error' :
                          Math.ceil((new Date(key.expires_at) - new Date()) / (1000 * 60 * 60 * 24)) < 7 ? 'warning' :
                          'textPrimary'
                        }>
                          {getExpiryText(key.expires_at)}
                        </Typography>
                      </TableCell>
                      <TableCell>{key.usage_count || 0} calls</TableCell>
                      <TableCell>
                        {key.last_used_at ? new Date(key.last_used_at).toLocaleString() : 'Never'}
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
                          <Tooltip title={key.active ? "Deactivate" : "Activate"}>
                            <Switch
                              size="small"
                              checked={key.active}
                              onChange={() => handleToggleKey(key.key_id, key.active)}
                              disabled={key.expires_at && new Date(key.expires_at) < new Date()}
                            />
                          </Tooltip>
                          <Tooltip title="Revoke">
                            <IconButton
                              size="small"
                              onClick={() => handleRevokeKey(key.key_id)}
                              color="error"
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Box sx={{ py: 4 }}>
                        <KeyIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="body2" color="textSecondary">
                          No API keys created yet. Click "Create API Key" to get started.
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {/* Create API Key Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New API Key</DialogTitle>
        <form onSubmit={handleCreateKey}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Key Name"
                  value={formData.key_name}
                  onChange={(e) => setFormData({ ...formData, key_name: e.target.value })}
                  placeholder="Production API Access"
                  helperText="A descriptive name to help you identify this key"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  type="number"
                  label="Expires in Days"
                  value={formData.expires_in_days}
                  onChange={(e) => setFormData({ ...formData, expires_in_days: parseInt(e.target.value) })}
                  inputProps={{ min: 1, max: 365 }}
                  helperText="Set to 0 for no expiration (not recommended)"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  type="number"
                  label="Rate Limit (requests/hour)"
                  value={formData.rate_limit_per_hour}
                  onChange={(e) => setFormData({ ...formData, rate_limit_per_hour: parseInt(e.target.value) })}
                  inputProps={{ min: 100, max: 10000 }}
                />
              </Grid>
              <Grid item xs={12}>
                <Alert severity="info">
                  <Typography variant="body2">
                    <strong>Important:</strong> The API key will only be shown once after creation.
                    Save it immediately in a secure location.
                  </Typography>
                </Alert>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Create Key</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* API Key Created Dialog */}
      <Dialog
        open={keyCreatedDialogOpen}
        onClose={() => setKeyCreatedDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircleIcon color="success" />
            API Key Created Successfully
          </Box>
        </DialogTitle>
        <DialogContent>
          {createdKeyData && (
            <Box>
              <Alert severity="warning" sx={{ mb: 3 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  IMPORTANT: Copy your API key now. You won't be able to see it again!
                </Typography>
              </Alert>

              <Typography variant="subtitle2" sx={{ mb: 1 }}>Key Name:</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>{createdKeyData.key_name}</Typography>

              <Typography variant="subtitle2" sx={{ mb: 1 }}>Your API Key:</Typography>
              <TextField
                fullWidth
                value={createdKeyData.api_key}
                type={showCreatedKey ? "text" : "password"}
                InputProps={{
                  readOnly: true,
                  sx: { fontFamily: 'monospace', fontSize: '0.9rem' },
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowCreatedKey(!showCreatedKey)} edge="end">
                        {showCreatedKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                      <IconButton onClick={() => handleCopyKey(createdKeyData.api_key)} edge="end">
                        <CopyIcon />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 2 }}
              />

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" sx={{ mb: 1 }}>Details:</Typography>
              <Typography variant="body2" color="textSecondary">
                Created: {new Date(createdKeyData.created_at).toLocaleString()}
              </Typography>
              {createdKeyData.expires_at && (
                <Typography variant="body2" color="textSecondary">
                  Expires: {new Date(createdKeyData.expires_at).toLocaleString()}
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            variant="outlined"
            startIcon={<CopyIcon />}
            onClick={() => handleCopyKey(createdKeyData.api_key)}
          >
            Copy Key
          </Button>
          <Button variant="contained" onClick={() => setKeyCreatedDialogOpen(false)}>
            Done
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default APIKeyManagementDashboard
