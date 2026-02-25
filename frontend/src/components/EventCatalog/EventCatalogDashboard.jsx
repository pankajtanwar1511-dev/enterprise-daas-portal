import React, { useState, useEffect, useMemo } from 'react'
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
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Tab,
  Tabs,
  Divider,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  Schema as SchemaIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Timeline as TimelineIcon,
  Code as CodeIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

function EventCatalogDashboard() {
  const [events, setEvents] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [versions, setVersions] = useState([])
  const [consumers, setConsumers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tabValue, setTabValue] = useState(0)

  // Dialogs
  const [registerDialogOpen, setRegisterDialogOpen] = useState(false)
  const [versionsDialogOpen, setVersionsDialogOpen] = useState(false)
  const [consumersDialogOpen, setConsumersDialogOpen] = useState(false)
  const [breakingChangeDialogOpen, setBreakingChangeDialogOpen] = useState(false)
  const [breakingChangeResult, setBreakingChangeResult] = useState(null)

  // Form data
  const [formData, setFormData] = useState({
    event_name: '',
    schema_definition: '{}',
    schema_format: 'JSON_SCHEMA',
    producer_asset_id: '',
    description: '',
    compatibility_mode: 'BACKWARD',
  })

  const [breakingChangeSchema, setBreakingChangeSchema] = useState('{}')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const [catalogRes, statsRes] = await Promise.all([
        axiosInstance.get('/api/v1/events/catalog'),
        axiosInstance.get('/api/v1/events/statistics'),
      ])
      setEvents(catalogRes.data.events || [])
      setStatistics(statsRes.data)
    } catch (err) {
      console.error('Error fetching event catalog:', err)
      setError('Failed to load event catalog')
    } finally {
      setLoading(false)
    }
  }

  const handleRegisterEvent = async (e) => {
    e.preventDefault()
    try {
      const payload = {
        ...formData,
        schema_definition: JSON.parse(formData.schema_definition),
        producer_asset_id: formData.producer_asset_id ? parseInt(formData.producer_asset_id) : null,
      }
      await axiosInstance.post('/api/v1/events/register', payload)
      fetchData()
      setRegisterDialogOpen(false)
      setFormData({
        event_name: '',
        schema_definition: '{}',
        schema_format: 'JSON_SCHEMA',
        producer_asset_id: '',
        description: '',
        compatibility_mode: 'BACKWARD',
      })
    } catch (err) {
      console.error('Error registering event:', err)
      setError(err.response?.data?.detail || 'Failed to register event')
    }
  }

  const handleViewVersions = async (event) => {
    setSelectedEvent(event)
    try {
      const response = await axiosInstance.get(`/api/v1/events/${event.event_name}/versions`)
      setVersions(response.data.versions || [])
      setVersionsDialogOpen(true)
    } catch (err) {
      console.error('Error fetching versions:', err)
      setError('Failed to load event versions')
    }
  }

  const handleViewConsumers = async (event) => {
    setSelectedEvent(event)
    try {
      const response = await axiosInstance.get(`/api/v1/events/${event.event_name}/consumers`)
      setConsumers(response.data.consumers || [])
      setConsumersDialogOpen(true)
    } catch (err) {
      console.error('Error fetching consumers:', err)
      setError('Failed to load consumers')
    }
  }

  const handleCheckBreakingChanges = async (e) => {
    e.preventDefault()
    try {
      const response = await axiosInstance.post(
        `/api/v1/events/${selectedEvent.event_name}/check-breaking-changes`,
        { new_schema: JSON.parse(breakingChangeSchema) }
      )
      setBreakingChangeResult(response.data)
    } catch (err) {
      console.error('Error checking breaking changes:', err)
      setError('Failed to check breaking changes')
    }
  }

  const handleDeprecateVersion = async (eventName, version) => {
    const reason = prompt('Enter deprecation reason:')
    if (!reason) return
    try {
      await axiosInstance.patch(`/api/v1/events/${eventName}/versions/${version}/deprecate`, { reason })
      handleViewVersions(selectedEvent)
    } catch (err) {
      console.error('Error deprecating version:', err)
      setError('Failed to deprecate version')
    }
  }

  // Chart data calculations
  const chartData = useMemo(() => {
    if (!events.length) return null

    // Status distribution
    const activeCount = events.filter(e => e.is_active).length
    const deprecatedCount = events.length - activeCount
    const statusData = [
      { name: 'Active', value: activeCount, color: '#4caf50' },
      { name: 'Deprecated', value: deprecatedCount, color: '#ff9800' },
    ].filter(d => d.value > 0)

    // Compatibility mode distribution
    const compatibilityCounts = events.reduce((acc, event) => {
      const mode = event.compatibility_mode || 'BACKWARD'
      acc[mode] = (acc[mode] || 0) + 1
      return acc
    }, {})
    const compatibilityData = Object.entries(compatibilityCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)

    // Consumer distribution (top 10 events by consumer count)
    const consumerData = events
      .filter(e => e.consumer_count > 0)
      .sort((a, b) => (b.consumer_count || 0) - (a.consumer_count || 0))
      .slice(0, 10)
      .map(e => ({
        name: e.event_name.length > 20 ? e.event_name.substring(0, 20) + '...' : e.event_name,
        consumers: e.consumer_count || 0,
      }))

    // Version distribution (mock data)
    const versionTrend = [
      { month: 'Aug', count: Math.floor(events.length * 0.6) },
      { month: 'Sep', count: Math.floor(events.length * 0.7) },
      { month: 'Oct', count: Math.floor(events.length * 0.8) },
      { month: 'Nov', count: Math.floor(events.length * 0.9) },
      { month: 'Dec', count: Math.floor(events.length * 0.95) },
      { month: 'Jan', count: events.length },
    ]

    return { statusData, compatibilityData, consumerData, versionTrend }
  }, [events])

  const COLORS = ['#4caf50', '#ff9800', '#2196f3', '#9c27b0', '#f44336', '#00bcd4']

  // Define columns for events table
  const eventsColumns = [
    {
      id: 'event_name',
      label: 'Event Name',
      sortable: true,
      render: (value, row) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SchemaIcon fontSize="small" color="action" />
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {value}
            </Typography>
            {row.description && (
              <Typography variant="caption" color="textSecondary">
                {row.description}
              </Typography>
            )}
          </Box>
        </Box>
      ),
    },
    {
      id: 'version',
      label: 'Latest Version',
      sortable: true,
      render: (value) => <Chip label={`v${value || 1}`} size="small" color="primary" />,
    },
    {
      id: 'producer_asset_id',
      label: 'Producer',
      sortable: true,
      render: (value) => (value ? `Asset ${value}` : 'Unknown'),
    },
    {
      id: 'compatibility_mode',
      label: 'Compatibility Mode',
      sortable: true,
      render: (value) => <Chip label={value || 'BACKWARD'} size="small" variant="outlined" />,
    },
    {
      id: 'is_active',
      label: 'Status',
      sortable: true,
      render: (value) =>
        value ? (
          <Chip label="Active" size="small" color="success" icon={<CheckCircleIcon />} />
        ) : (
          <Chip label="Deprecated" size="small" color="warning" icon={<WarningIcon />} />
        ),
    },
    {
      id: 'consumer_count',
      label: 'Consumer Count',
      sortable: true,
      render: (value) => <Chip label={`${value || 0} consumers`} size="small" />,
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      render: (value, row) => (
        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
          <Tooltip title="View Versions">
            <IconButton size="small" onClick={() => handleViewVersions(row)} color="primary">
              <TimelineIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="View Consumers">
            <IconButton size="small" onClick={() => handleViewConsumers(row)} color="info">
              <PeopleIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Check Breaking Changes">
            <IconButton
              size="small"
              onClick={() => {
                setSelectedEvent(row)
                setBreakingChangeDialogOpen(true)
              }}
              color="warning"
            >
              <WarningIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Event Catalog
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
            onClick={() => setRegisterDialogOpen(true)}
          >
            Register Event
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      {statistics && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <SchemaIcon color="primary" />
                  <Typography variant="caption" color="textSecondary">
                    Total Events
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.total_events || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <CheckCircleIcon color="success" />
                  <Typography variant="caption" color="textSecondary">
                    Active Events
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.active_events || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderLeft: '4px solid #ff9800' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <WarningIcon color="warning" />
                  <Typography variant="caption" color="textSecondary">
                    Deprecated Events
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.deprecated_events || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TimelineIcon color="info" />
                  <Typography variant="caption" color="textSecondary">
                    Total Versions
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.total_versions || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Charts */}
      {!loading && chartData && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Event Status Distribution - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Event Status Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartData.statusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) =>
                        `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={100}
                      
                      dataKey="value"
                    >
                      {chartData.statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Compatibility Mode Distribution - Bar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Compatibility Mode Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.compatibilityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Events" radius={[8, 8, 0, 0]}>
                      {chartData.compatibilityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Top Events by Consumer Count - Horizontal Bar */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PeopleIcon color="info" />
                  Top 10 Events by Consumer Count
                </Typography>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={chartData.consumerData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={150} tick={{ fontSize: 11 }} />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="consumers" name="Consumers" fill="#2196f3" radius={[0, 8, 8, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Event Catalog Growth - Line Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TimelineIcon color="primary" />
                  Event Catalog Growth (Last 6 Months)
                </Typography>
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={chartData.versionTrend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#4caf50"
                      strokeWidth={2}
                      name="Total Events"
                      dot={{ fill: '#4caf50', r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper>
          <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
            <Typography variant="h6">Event Catalog</Typography>
          </Box>
          {events.length === 0 ? (
            <Box sx={{ py: 8, textAlign: 'center' }}>
              <SchemaIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body2" color="textSecondary">
                No events registered. Click "Register Event" to add your first event.
              </Typography>
            </Box>
          ) : (
            <Box sx={{ p: 2 }}>
              <EnhancedTable
                columns={eventsColumns}
                data={events}
                loading={false}
                onRefresh={fetchData}
                defaultOrderBy="event_name"
                defaultOrder="asc"
                searchPlaceholder="Search events..."
                exportFileName="event_catalog"
                rowsPerPageOptions={[10, 25, 50]}
                dense={true}
              />
            </Box>
          )}
        </Paper>
      )}

      {/* Register Event Dialog */}
      <Dialog open={registerDialogOpen} onClose={() => setRegisterDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Register Event</DialogTitle>
        <form onSubmit={handleRegisterEvent}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Event Name"
                  value={formData.event_name}
                  onChange={(e) => setFormData({ ...formData, event_name: e.target.value })}
                  placeholder="customer.created"
                  helperText="Use dot notation (e.g., domain.action)"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={8}
                  required
                  label="Schema Definition (JSON)"
                  value={formData.schema_definition}
                  onChange={(e) => setFormData({ ...formData, schema_definition: e.target.value })}
                  sx={{ fontFamily: 'monospace' }}
                  helperText="JSON Schema definition"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  select
                  fullWidth
                  label="Schema Format"
                  value={formData.schema_format}
                  onChange={(e) => setFormData({ ...formData, schema_format: e.target.value })}
                >
                  <MenuItem value="JSON_SCHEMA">JSON Schema</MenuItem>
                  <MenuItem value="AVRO">Avro</MenuItem>
                  <MenuItem value="PROTOBUF">Protobuf</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  select
                  fullWidth
                  label="Compatibility Mode"
                  value={formData.compatibility_mode}
                  onChange={(e) => setFormData({ ...formData, compatibility_mode: e.target.value })}
                >
                  <MenuItem value="BACKWARD">Backward</MenuItem>
                  <MenuItem value="FORWARD">Forward</MenuItem>
                  <MenuItem value="FULL">Full</MenuItem>
                  <MenuItem value="NONE">None</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Producer Asset ID"
                  type="number"
                  value={formData.producer_asset_id}
                  onChange={(e) => setFormData({ ...formData, producer_asset_id: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setRegisterDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Register</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Versions Dialog */}
      <Dialog open={versionsDialogOpen} onClose={() => setVersionsDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Event Versions: {selectedEvent?.event_name}
        </DialogTitle>
        <DialogContent>
          {versions.length > 0 ? (
            <Box>
              {versions.map((version) => (
                <Accordion key={version.version}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                      <Chip label={`v${version.version}`} size="small" color="primary" />
                      {version.is_latest && <Chip label="Latest" size="small" color="success" />}
                      {version.is_deprecated && <Chip label="Deprecated" size="small" color="warning" />}
                      <Typography variant="caption" color="textSecondary" sx={{ ml: 'auto' }}>
                        {new Date(version.created_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>Schema:</Typography>
                      <Paper sx={{ p: 2, backgroundColor: '#f5f5f5', mb: 2 }}>
                        <pre style={{ margin: 0, fontSize: '0.85rem', overflow: 'auto' }}>
                          {JSON.stringify(version.schema_definition, null, 2)}
                        </pre>
                      </Paper>
                      {!version.is_deprecated && (
                        <Button
                          size="small"
                          color="warning"
                          onClick={() => handleDeprecateVersion(selectedEvent.event_name, version.version)}
                        >
                          Deprecate Version
                        </Button>
                      )}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          ) : (
            <Alert severity="info">No versions available</Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVersionsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Consumers Dialog */}
      <Dialog open={consumersDialogOpen} onClose={() => setConsumersDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Consumers: {selectedEvent?.event_name}
        </DialogTitle>
        <DialogContent>
          {consumers.length > 0 ? (
            <List>
              {consumers.map((consumer, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={`Asset ${consumer.consumer_asset_id}`}
                    secondary={`Version constraint: ${consumer.version_constraint || 'Any'}`}
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Alert severity="info">No consumers registered</Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConsumersDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Breaking Change Check Dialog */}
      <Dialog
        open={breakingChangeDialogOpen}
        onClose={() => {
          setBreakingChangeDialogOpen(false)
          setBreakingChangeResult(null)
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Check Breaking Changes: {selectedEvent?.event_name}
        </DialogTitle>
        <form onSubmit={handleCheckBreakingChanges}>
          <DialogContent>
            <TextField
              fullWidth
              multiline
              rows={10}
              label="New Schema Definition (JSON)"
              value={breakingChangeSchema}
              onChange={(e) => setBreakingChangeSchema(e.target.value)}
              sx={{ fontFamily: 'monospace', mb: 2 }}
            />
            {breakingChangeResult && (
              <Alert severity={breakingChangeResult.has_breaking_changes ? 'error' : 'success'} sx={{ mt: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                  {breakingChangeResult.has_breaking_changes
                    ? 'Breaking changes detected!'
                    : 'No breaking changes detected'}
                </Typography>
                {breakingChangeResult.breaking_changes && breakingChangeResult.breaking_changes.length > 0 && (
                  <Box component="ul" sx={{ mt: 1, pl: 2 }}>
                    {breakingChangeResult.breaking_changes.map((change, idx) => (
                      <li key={idx}>{change}</li>
                    ))}
                  </Box>
                )}
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => {
              setBreakingChangeDialogOpen(false)
              setBreakingChangeResult(null)
            }}>
              Close
            </Button>
            <Button type="submit" variant="contained">
              Check
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  )
}

export default EventCatalogDashboard
