import React, { useState, useEffect } from 'react'
import axios from '../../utils/axiosInstance'
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
  Tab,
  Tabs,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  PlayArrow as TestIcon,
  Webhook as WebhookIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Visibility as VisibilityIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material'

const EVENT_TYPES = [
  { value: 'asset.created', label: 'Asset Created' },
  { value: 'asset.updated', label: 'Asset Updated' },
  { value: 'asset.deleted', label: 'Asset Deleted' },
  { value: 'compliance.violation', label: 'Compliance Violation' },
  { value: 'change.approved', label: 'Change Approved' },
  { value: 'change.rejected', label: 'Change Rejected' },
  { value: 'sla.breached', label: 'SLA Breached' },
  { value: 'budget.threshold', label: 'Budget Threshold' },
  { value: 'user.created', label: 'User Created' },
]

function WebhookManagementDashboard() {
  const [webhooks, setWebhooks] = useState([])
  const [selectedWebhook, setSelectedWebhook] = useState(null)
  const [deliveries, setDeliveries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tabValue, setTabValue] = useState(0)

  // Dialogs
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [deliveriesDialogOpen, setDeliveriesDialogOpen] = useState(false)
  const [secretDialogOpen, setSecretDialogOpen] = useState(false)
  const [webhookSecret, setWebhookSecret] = useState('')

  // Form data
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    events: [],
    retry_count: 3,
    timeout_seconds: 30,
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axios.get('/api/v1/webhooks/')
      setWebhooks(response.data)
    } catch (err) {
      console.error('Error fetching webhooks:', err)
      setError('Failed to load webhooks')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateWebhook = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/v1/webhooks/', formData)
      fetchData()
      setCreateDialogOpen(false)
      setFormData({
        name: '',
        url: '',
        events: [],
        retry_count: 3,
        timeout_seconds: 30,
      })
    } catch (err) {
      console.error('Error creating webhook:', err)
      setError(err.response?.data?.detail || 'Failed to create webhook')
    }
  }

  const handleUpdateWebhook = async (e) => {
    e.preventDefault()
    try {
      await axios.put(`/api/v1/webhooks/${selectedWebhook.webhook_id}`, formData)
      fetchData()
      setEditDialogOpen(false)
    } catch (err) {
      console.error('Error updating webhook:', err)
      setError(err.response?.data?.detail || 'Failed to update webhook')
    }
  }

  const handleDeleteWebhook = async (webhookId) => {
    if (!confirm('Are you sure you want to delete this webhook?')) return
    try {
      await axios.delete(`/api/v1/webhooks/${webhookId}`)
      fetchData()
    } catch (err) {
      console.error('Error deleting webhook:', err)
      setError('Failed to delete webhook')
    }
  }

  const handleToggleWebhook = async (webhook) => {
    try {
      await axios.put(`/api/v1/webhooks/${webhook.webhook_id}`, {
        active: !webhook.active
      })
      fetchData()
    } catch (err) {
      console.error('Error toggling webhook:', err)
      setError('Failed to update webhook')
    }
  }

  const handleTestWebhook = async (webhook) => {
    try {
      const result = await axios.post(`/api/v1/webhooks/${webhook.webhook_id}/test`, {
        event: webhook.events[0] || 'asset.created',
        test_payload: null
      })
      alert(`Webhook test successful!\nStatus: ${result.data.status_code}\nDuration: ${result.data.duration_ms}ms`)
    } catch (err) {
      console.error('Error testing webhook:', err)
      alert(`Webhook test failed: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleViewDeliveries = async (webhook) => {
    setSelectedWebhook(webhook)
    try {
      const response = await axios.get(`/api/v1/webhooks/${webhook.webhook_id}/deliveries`)
      setDeliveries(response.data)
      setDeliveriesDialogOpen(true)
    } catch (err) {
      console.error('Error fetching deliveries:', err)
      setError('Failed to load delivery logs')
    }
  }

  const handleViewSecret = async (webhook) => {
    try {
      const response = await axios.get(`/api/v1/webhooks/${webhook.webhook_id}/secret`)
      setWebhookSecret(response.data.secret)
      setSecretDialogOpen(true)
    } catch (err) {
      console.error('Error fetching secret:', err)
      setError(err.response?.data?.detail || 'Failed to get webhook secret')
    }
  }

  const handleEditClick = (webhook) => {
    setSelectedWebhook(webhook)
    setFormData({
      name: webhook.name,
      url: webhook.url,
      events: webhook.events,
      retry_count: webhook.retry_count,
      timeout_seconds: webhook.timeout_seconds,
    })
    setEditDialogOpen(true)
  }

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  const activeWebhooks = webhooks.filter(w => w.active).length
  const totalDeliveries = webhooks.reduce((sum, w) => sum + (w.delivery_count || 0), 0)
  const failedDeliveries = webhooks.reduce((sum, w) => sum + (w.failed_delivery_count || 0), 0)

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Webhook Management
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
            Create Webhook
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
                <WebhookIcon color="primary" />
                <Typography variant="caption" color="textSecondary">
                  Total Webhooks
                </Typography>
              </Box>
              <Typography variant="h4">{webhooks.length}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CheckCircleIcon color="success" />
                <Typography variant="caption" color="textSecondary">
                  Active Webhooks
                </Typography>
              </Box>
              <Typography variant="h4">{activeWebhooks}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CheckCircleIcon color="info" />
                <Typography variant="caption" color="textSecondary">
                  Total Deliveries
                </Typography>
              </Box>
              <Typography variant="h4">{totalDeliveries}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <ErrorIcon color="error" />
                <Typography variant="caption" color="textSecondary">
                  Failed Deliveries
                </Typography>
              </Box>
              <Typography variant="h4">{failedDeliveries}</Typography>
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
            <Typography variant="h6">Configured Webhooks</Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>URL</TableCell>
                  <TableCell>Events</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Last Triggered</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {webhooks.length > 0 ? (
                  webhooks.map((webhook) => (
                    <TableRow key={webhook.webhook_id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <WebhookIcon fontSize="small" color="action" />
                          <Typography variant="body2">{webhook.name}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                          {webhook.url.length > 40 ? webhook.url.substring(0, 40) + '...' : webhook.url}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {webhook.events.slice(0, 2).map((event, idx) => (
                            <Chip key={idx} label={event} size="small" variant="outlined" />
                          ))}
                          {webhook.events.length > 2 && (
                            <Chip label={`+${webhook.events.length - 2}`} size="small" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        {webhook.active ? (
                          <Chip label="Active" size="small" color="success" icon={<CheckCircleIcon />} />
                        ) : (
                          <Chip label="Inactive" size="small" color="warning" icon={<WarningIcon />} />
                        )}
                      </TableCell>
                      <TableCell>
                        {webhook.last_triggered ? new Date(webhook.last_triggered).toLocaleString() : 'Never'}
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
                          <Tooltip title="Test Webhook">
                            <IconButton size="small" onClick={() => handleTestWebhook(webhook)} color="primary">
                              <TestIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="View Deliveries">
                            <IconButton size="small" onClick={() => handleViewDeliveries(webhook)} color="info">
                              <VisibilityIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton size="small" onClick={() => handleEditClick(webhook)}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={webhook.active ? "Deactivate" : "Activate"}>
                            <Switch
                              size="small"
                              checked={webhook.active}
                              onChange={() => handleToggleWebhook(webhook)}
                            />
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton
                              size="small"
                              onClick={() => handleDeleteWebhook(webhook.webhook_id)}
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
                    <TableCell colSpan={6} align="center">
                      <Box sx={{ py: 4 }}>
                        <WebhookIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="body2" color="textSecondary">
                          No webhooks configured. Click "Create Webhook" to get started.
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

      {/* Create/Edit Webhook Dialog */}
      <Dialog
        open={createDialogOpen || editDialogOpen}
        onClose={() => {
          setCreateDialogOpen(false)
          setEditDialogOpen(false)
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{editDialogOpen ? 'Edit Webhook' : 'Create Webhook'}</DialogTitle>
        <form onSubmit={editDialogOpen ? handleUpdateWebhook : handleCreateWebhook}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Webhook Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Production Asset Notifications"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Webhook URL"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  placeholder="https://your-service.com/webhook"
                  helperText="The endpoint URL to receive webhook events"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  select
                  fullWidth
                  required
                  label="Events"
                  value={formData.events}
                  onChange={(e) => setFormData({ ...formData, events: e.target.value })}
                  SelectProps={{ multiple: true }}
                  helperText="Select events to subscribe to"
                >
                  {EVENT_TYPES.map((event) => (
                    <MenuItem key={event.value} value={event.value}>
                      {event.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Retry Count"
                  value={formData.retry_count}
                  onChange={(e) => setFormData({ ...formData, retry_count: parseInt(e.target.value) })}
                  inputProps={{ min: 0, max: 10 }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Timeout (seconds)"
                  value={formData.timeout_seconds}
                  onChange={(e) => setFormData({ ...formData, timeout_seconds: parseInt(e.target.value) })}
                  inputProps={{ min: 5, max: 120 }}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => {
                setCreateDialogOpen(false)
                setEditDialogOpen(false)
              }}
            >
              Cancel
            </Button>
            <Button type="submit" variant="contained">
              {editDialogOpen ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Deliveries Dialog */}
      <Dialog
        open={deliveriesDialogOpen}
        onClose={() => setDeliveriesDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Delivery Logs: {selectedWebhook?.name}
        </DialogTitle>
        <DialogContent>
          {deliveries.length > 0 ? (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Event</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Response</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>Delivered At</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {deliveries.map((delivery) => (
                    <TableRow key={delivery.delivery_id}>
                      <TableCell>
                        <Chip label={delivery.event} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        {delivery.success ? (
                          <Chip
                            label={`${delivery.status_code || 'Success'}`}
                            size="small"
                            color="success"
                            icon={<CheckCircleIcon />}
                          />
                        ) : (
                          <Chip
                            label={delivery.error_message || 'Failed'}
                            size="small"
                            color="error"
                            icon={<ErrorIcon />}
                          />
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontSize: '0.75rem', fontFamily: 'monospace' }}>
                          {delivery.response_body
                            ? delivery.response_body.substring(0, 30) + '...'
                            : delivery.error_message || '-'}
                        </Typography>
                      </TableCell>
                      <TableCell>{delivery.duration_ms}ms</TableCell>
                      <TableCell>{new Date(delivery.delivered_at).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Alert severity="info">No delivery logs available for this webhook</Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeliveriesDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Secret Dialog */}
      <Dialog open={secretDialogOpen} onClose={() => setSecretDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Webhook Secret</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Use this secret to verify webhook signatures in your endpoint
          </Alert>
          <TextField
            fullWidth
            value={webhookSecret}
            InputProps={{
              readOnly: true,
              sx: { fontFamily: 'monospace' },
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSecretDialogOpen(false)}>Close</Button>
          <Button
            variant="contained"
            startIcon={<CopyIcon />}
            onClick={() => handleCopy(webhookSecret)}
          >
            Copy Secret
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default WebhookManagementDashboard
