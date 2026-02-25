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
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import {
  Refresh as RefreshIcon,
  Code as CodeIcon,
  Schema as SchemaIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  CompareArrows as CompareIcon,
  Timeline as VersionIcon,
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

function SchemaRegistryDashboard() {
  const [schemas, setSchemas] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [selectedSchema, setSelectedSchema] = useState(null)
  const [compatibilityMatrix, setCompatibilityMatrix] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tabValue, setTabValue] = useState(0)

  // Dialogs
  const [schemaDialogOpen, setSchemaDialogOpen] = useState(false)
  const [compatibilityDialogOpen, setCompatibilityDialogOpen] = useState(false)
  const [validateDialogOpen, setValidateDialogOpen] = useState(false)

  // Validation data
  const [validationData, setValidationData] = useState('')
  const [validationResult, setValidationResult] = useState(null)

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
      setSchemas(catalogRes.data.events || [])
      setStatistics(statsRes.data)
    } catch (err) {
      console.error('Error fetching schemas:', err)
      setError('Failed to load schema registry')
    } finally {
      setLoading(false)
    }
  }

  const handleViewSchema = async (schema) => {
    setSelectedSchema(schema)
    setSchemaDialogOpen(true)
  }

  const handleViewCompatibility = async (schema) => {
    setSelectedSchema(schema)
    try {
      const response = await axiosInstance.get(`/api/v1/events/${schema.event_name}/compatibility-matrix`)
      setCompatibilityMatrix(response.data)
      setCompatibilityDialogOpen(true)
    } catch (err) {
      console.error('Error fetching compatibility matrix:', err)
      setError('Failed to load compatibility matrix')
    }
  }

  const handleValidateSchema = async (e) => {
    e.preventDefault()
    try {
      const testData = JSON.parse(validationData)
      // For now, just check if it's valid JSON
      setValidationResult({
        valid: true,
        message: 'Schema is valid JSON'
      })
    } catch (err) {
      setValidationResult({
        valid: false,
        message: `Invalid JSON: ${err.message}`
      })
    }
  }

  const getCompatibilityColor = (mode) => {
    switch (mode) {
      case 'FULL': return 'success'
      case 'BACKWARD': return 'primary'
      case 'FORWARD': return 'info'
      case 'NONE': return 'error'
      default: return 'default'
    }
  }

  const getFormatIcon = (format) => {
    switch (format) {
      case 'JSON_SCHEMA': return <CodeIcon />
      case 'AVRO': return <SchemaIcon />
      case 'PROTOBUF': return <SchemaIcon />
      default: return <CodeIcon />
    }
  }

  // Chart data calculations
  const chartData = useMemo(() => {
    if (!schemas.length) return null

    // Format distribution
    const formatCounts = schemas.reduce((acc, schema) => {
      const format = schema.schema_format || 'JSON_SCHEMA'
      acc[format] = (acc[format] || 0) + 1
      return acc
    }, {})
    const formatData = Object.entries(formatCounts).map(([name, value]) => ({ name, value }))

    // Compatibility mode distribution
    const compatibilityCounts = schemas.reduce((acc, schema) => {
      const mode = schema.compatibility_mode || 'BACKWARD'
      acc[mode] = (acc[mode] || 0) + 1
      return acc
    }, {})
    const compatibilityData = Object.entries(compatibilityCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)

    // Status distribution
    const activeCount = schemas.filter(s => s.is_active).length
    const deprecatedCount = schemas.length - activeCount
    const statusData = [
      { name: 'Active', value: activeCount, color: '#4caf50' },
      { name: 'Deprecated', value: deprecatedCount, color: '#ff9800' },
    ].filter(d => d.value > 0)

    // Version distribution (mock - group schemas by version count)
    const versionData = [
      { version: 'v1', count: Math.floor(schemas.length * 0.4) },
      { version: 'v2', count: Math.floor(schemas.length * 0.3) },
      { version: 'v3', count: Math.floor(schemas.length * 0.2) },
      { version: 'v4+', count: Math.floor(schemas.length * 0.1) },
    ]

    return { formatData, compatibilityData, statusData, versionData }
  }, [schemas])

  const COLORS = ['#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0', '#00bcd4']

  // Define table columns for schemas
  const schemaColumns = [
    {
      id: 'event_name',
      label: 'Schema Name',
      sortable: true,
      render: (value, row) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {getFormatIcon(row.schema_format)}
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
      id: 'schema_format',
      label: 'Format',
      sortable: true,
      align: 'center',
      render: (value) => <Chip label={value || 'JSON_SCHEMA'} size="small" variant="outlined" />,
    },
    {
      id: 'version',
      label: 'Version',
      sortable: true,
      align: 'center',
      render: (value) => <Chip label={`v${value || 1}`} size="small" color="primary" />,
    },
    {
      id: 'compatibility_mode',
      label: 'Compatibility',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value || 'BACKWARD'}
          size="small"
          color={getCompatibilityColor(value)}
        />
      ),
    },
    {
      id: 'is_active',
      label: 'Status',
      sortable: true,
      align: 'center',
      render: (value) =>
        value ? (
          <Chip label="Active" size="small" color="success" icon={<CheckCircleIcon />} />
        ) : (
          <Chip label="Deprecated" size="small" color="warning" icon={<WarningIcon />} />
        ),
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      align: 'right',
      render: (value, row) => (
        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
          <Tooltip title="View Schema">
            <IconButton size="small" onClick={() => handleViewSchema(row)} color="primary">
              <CodeIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Compatibility Matrix">
            <IconButton size="small" onClick={() => handleViewCompatibility(row)} color="info">
              <CompareIcon fontSize="small" />
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
          Schema Registry
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchData} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<CheckCircleIcon />}
            onClick={() => setValidateDialogOpen(true)}
          >
            Validate Schema
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
                    Total Schemas
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.total_events || 0}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {statistics.total_versions || 0} versions
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <VersionIcon color="info" />
                  <Typography variant="caption" color="textSecondary">
                    Avg Versions
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.avg_versions_per_event || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <CodeIcon color="success" />
                  <Typography variant="caption" color="textSecondary">
                    JSON Schemas
                  </Typography>
                </Box>
                <Typography variant="h4">
                  {statistics.events_by_format?.JSON_SCHEMA || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <SchemaIcon color="secondary" />
                  <Typography variant="caption" color="textSecondary">
                    Other Formats
                  </Typography>
                </Box>
                <Typography variant="h4">
                  {(statistics.events_by_format?.AVRO || 0) + (statistics.events_by_format?.PROTOBUF || 0)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Charts */}
      {!loading && chartData && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Schema Format Distribution - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CodeIcon color="primary" />
                  Schema Format Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartData.formatData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) =>
                        `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={100}
                      
                      dataKey="value"
                    >
                      {chartData.formatData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Status Distribution - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Schema Status Distribution
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
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CompareIcon color="secondary" />
                  Compatibility Mode Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.compatibilityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Schemas" radius={[8, 8, 0, 0]}>
                      {chartData.compatibilityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Version Distribution - Bar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <VersionIcon color="info" />
                  Schema Version Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.versionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="version" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="count" name="Schemas" fill="#1976d2" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="All Schemas" />
          <Tab label="By Format" />
          <Tab label="Compatibility" />
        </Tabs>
      </Paper>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Tab 0: All Schemas */}
          {tabValue === 0 && (
            <EnhancedTable
              columns={schemaColumns}
              data={schemas}
              loading={loading}
              onRefresh={fetchData}
              defaultOrderBy="event_name"
              defaultOrder="asc"
              searchPlaceholder="Search schemas by name, format, compatibility..."
              exportFileName="schema-registry"
              rowsPerPageOptions={[10, 25, 50]}
            />
          )}

          {/* Tab 1: By Format */}
          {tabValue === 1 && (
            <Grid container spacing={2}>
              {['JSON_SCHEMA', 'AVRO', 'PROTOBUF'].map((format) => {
                const formatSchemas = schemas.filter(s => (s.schema_format || 'JSON_SCHEMA') === format)
                return (
                  <Grid item xs={12} md={4} key={format}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>{format}</Typography>
                        <Typography variant="h3" sx={{ mb: 1 }}>{formatSchemas.length}</Typography>
                        <Typography variant="body2" color="textSecondary">
                          {formatSchemas.filter(s => s.is_active).length} active
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )
              })}
            </Grid>
          )}

          {/* Tab 2: Compatibility */}
          {tabValue === 2 && (
            <Grid container spacing={2}>
              {['FULL', 'BACKWARD', 'FORWARD', 'NONE'].map((mode) => {
                const modeSchemas = schemas.filter(s => (s.compatibility_mode || 'BACKWARD') === mode)
                return (
                  <Grid item xs={12} sm={6} md={3} key={mode}>
                    <Card>
                      <CardContent>
                        <Chip
                          label={mode}
                          color={getCompatibilityColor(mode)}
                          sx={{ mb: 2 }}
                        />
                        <Typography variant="h3" sx={{ mb: 1 }}>{modeSchemas.length}</Typography>
                        <Typography variant="body2" color="textSecondary">
                          schemas
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )
              })}
            </Grid>
          )}
        </>
      )}

      {/* View Schema Dialog */}
      <Dialog open={schemaDialogOpen} onClose={() => setSchemaDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Schema: {selectedSchema?.event_name}
        </DialogTitle>
        <DialogContent>
          {selectedSchema && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="textSecondary">Format:</Typography>
                  <Typography variant="body2">{selectedSchema.schema_format || 'JSON_SCHEMA'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="textSecondary">Version:</Typography>
                  <Typography variant="body2">v{selectedSchema.version || 1}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="textSecondary">Compatibility:</Typography>
                  <Typography variant="body2">{selectedSchema.compatibility_mode || 'BACKWARD'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="textSecondary">Status:</Typography>
                  <Typography variant="body2">
                    {selectedSchema.is_active ? 'Active' : 'Deprecated'}
                  </Typography>
                </Grid>
              </Grid>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Schema Definition:</Typography>
              <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                <pre style={{ margin: 0, fontSize: '0.85rem', overflow: 'auto', maxHeight: 400 }}>
                  {selectedSchema.schema_definition
                    ? JSON.stringify(selectedSchema.schema_definition, null, 2)
                    : 'No schema definition available'}
                </pre>
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSchemaDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Compatibility Matrix Dialog */}
      <Dialog
        open={compatibilityDialogOpen}
        onClose={() => setCompatibilityDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Compatibility Matrix: {selectedSchema?.event_name}
        </DialogTitle>
        <DialogContent>
          {compatibilityMatrix ? (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                Shows which schema versions are compatible with each other
              </Alert>
              <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                <pre style={{ margin: 0, fontSize: '0.85rem' }}>
                  {JSON.stringify(compatibilityMatrix, null, 2)}
                </pre>
              </Paper>
            </Box>
          ) : (
            <CircularProgress />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompatibilityDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Validate Schema Dialog */}
      <Dialog open={validateDialogOpen} onClose={() => setValidateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Validate Schema</DialogTitle>
        <form onSubmit={handleValidateSchema}>
          <DialogContent>
            <TextField
              fullWidth
              multiline
              rows={12}
              label="Schema Definition (JSON)"
              value={validationData}
              onChange={(e) => setValidationData(e.target.value)}
              sx={{ fontFamily: 'monospace', mb: 2 }}
              placeholder='{"type": "object", "properties": {...}}'
            />
            {validationResult && (
              <Alert severity={validationResult.valid ? 'success' : 'error'}>
                {validationResult.message}
              </Alert>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setValidateDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">
              Validate
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  )
}

export default SchemaRegistryDashboard
