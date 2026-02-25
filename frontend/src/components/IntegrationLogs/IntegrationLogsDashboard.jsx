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
  TextField,
  MenuItem,
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Timeline as TimelineIcon,
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
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

function IntegrationLogsDashboard() {
  const [logs, setLogs] = useState([])
  const [webhookLogs, setWebhookLogs] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tabValue, setTabValue] = useState(0)
  const [filterType, setFilterType] = useState('all')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const [auditRes] = await Promise.all([
        axiosInstance.get('/api/v1/audit-logs/?limit=100'),
      ])
      setAuditLogs(auditRes.data)

      // Combine different log sources
      const combined = [
        ...auditRes.data.map(log => ({
          ...log,
          log_type: 'audit',
          timestamp: log.timestamp,
          status: 'success'
        }))
      ]

      setLogs(combined.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)))
    } catch (err) {
      console.error('Error fetching logs:', err)
      setError('Failed to load integration logs')
    } finally {
      setLoading(false)
    }
  }

  const getStatusChip = (status) => {
    switch (status) {
      case 'success':
        return <Chip label="Success" size="small" color="success" icon={<CheckCircleIcon />} />
      case 'error':
        return <Chip label="Error" size="small" color="error" icon={<ErrorIcon />} />
      case 'warning':
        return <Chip label="Warning" size="small" color="warning" icon={<WarningIcon />} />
      default:
        return <Chip label={status} size="small" />
    }
  }

  const getLogTypeColor = (type) => {
    switch (type) {
      case 'audit': return 'primary'
      case 'webhook': return 'secondary'
      case 'api': return 'info'
      case 'pipeline': return 'success'
      default: return 'default'
    }
  }

  const filteredLogs = filterType === 'all'
    ? logs
    : logs.filter(log => log.log_type === filterType)

  const successCount = logs.filter(l => l.status === 'success').length
  const errorCount = logs.filter(l => l.status === 'error').length
  const warningCount = logs.filter(l => l.status === 'warning').length

  // Chart data calculations
  const chartData = useMemo(() => {
    if (!logs.length) return null

    // Status distribution
    const statusData = [
      { name: 'Success', value: successCount, color: '#4caf50' },
      { name: 'Error', value: errorCount, color: '#f44336' },
      { name: 'Warning', value: warningCount, color: '#ff9800' },
    ].filter(d => d.value > 0)

    // Log type distribution
    const typeCounts = logs.reduce((acc, log) => {
      acc[log.log_type] = (acc[log.log_type] || 0) + 1
      return acc
    }, {})
    const typeData = Object.entries(typeCounts).map(([name, value]) => ({ name, value }))

    // Activity timeline (last 7 days)
    const timelineMap = logs.reduce((acc, log) => {
      const date = new Date(log.timestamp).toLocaleDateString()
      acc[date] = (acc[date] || 0) + 1
      return acc
    }, {})
    const timelineData = Object.entries(timelineMap)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(a.date) - new Date(b.date))
      .slice(-7)

    // Action distribution (top 8)
    const actionCounts = logs.reduce((acc, log) => {
      const action = log.action || 'Unknown'
      acc[action] = (acc[action] || 0) + 1
      return acc
    }, {})
    const actionData = Object.entries(actionCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8)

    return { statusData, typeData, timelineData, actionData }
  }, [logs, successCount, errorCount, warningCount])

  const COLORS = ['#4caf50', '#f44336', '#ff9800', '#2196f3', '#9c27b0', '#00bcd4', '#ff5722', '#3f51b5']

  // Helper function to format value changes
  const formatValueChange = (oldValue, newValue) => {
    if (!oldValue && !newValue) return null

    const parseValue = (val) => {
      if (!val) return null
      try {
        const parsed = JSON.parse(val)
        if (typeof parsed === 'object' && parsed !== null) {
          // Extract key fields for display
          const keys = Object.keys(parsed).slice(0, 2) // Show first 2 fields
          return keys.map(k => `${k}: ${parsed[k]}`).join(', ')
        }
        return val
      } catch {
        return val
      }
    }

    const oldFormatted = parseValue(oldValue)
    const newFormatted = parseValue(newValue)

    if (oldFormatted && newFormatted) {
      return (
        <Box>
          <Typography variant="caption" component="div" sx={{ color: 'error.main', mb: 0.5 }}>
            Old: {oldFormatted}
          </Typography>
          <Typography variant="caption" component="div" sx={{ color: 'success.main' }}>
            New: {newFormatted}
          </Typography>
        </Box>
      )
    }

    return oldFormatted || newFormatted
  }

  // Define table columns
  const columns = [
    {
      id: 'timestamp',
      label: 'Timestamp',
      sortable: true,
      render: (value) => new Date(value).toLocaleString(),
    },
    {
      id: 'log_type',
      label: 'Log Type',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={getLogTypeColor(value)}
        />
      ),
    },
    {
      id: 'action',
      label: 'Action',
      sortable: true,
      render: (value) => value || 'N/A',
    },
    {
      id: 'entity',
      label: 'Entity',
      sortable: false,
      render: (value, row) => (
        <Typography variant="body2">
          {row.entity_type} {row.entity_id && `#${row.entity_id}`}
        </Typography>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      sortable: true,
      align: 'center',
      render: (value) => getStatusChip(value),
    },
    {
      id: 'details',
      label: 'Details',
      sortable: false,
      render: (value, row) => {
        if (row.error_message) {
          return (
            <Typography variant="body2" sx={{ fontSize: '0.75rem', color: 'error.main' }}>
              {row.error_message}
            </Typography>
          )
        }

        if (row.old_value || row.new_value) {
          return formatValueChange(row.old_value, row.new_value)
        }

        return <Typography variant="body2" sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>-</Typography>
      },
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Integration Logs
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchData} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button variant="outlined" startIcon={<DownloadIcon />}>
            Export Logs
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
              <Typography variant="caption" color="textSecondary">Total Logs</Typography>
              <Typography variant="h4">{logs.length}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CheckCircleIcon color="success" />
                <Typography variant="caption" color="textSecondary">Success</Typography>
              </Box>
              <Typography variant="h4">{successCount}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #ff9800' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <WarningIcon color="warning" />
                <Typography variant="caption" color="textSecondary">Warnings</Typography>
              </Box>
              <Typography variant="h4">{warningCount}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <ErrorIcon color="error" />
                <Typography variant="caption" color="textSecondary">Errors</Typography>
              </Box>
              <Typography variant="h4">{errorCount}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      {!loading && chartData && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Activity Timeline - Area Chart */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TimelineIcon color="primary" />
                  Log Activity Timeline (Last 7 Days)
                </Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={chartData.timelineData}>
                    <defs>
                      <linearGradient id="colorLogActivity" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2196f3" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#2196f3" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <RechartsTooltip />
                    <Area
                      type="monotone"
                      dataKey="count"
                      stroke="#2196f3"
                      fillOpacity={1}
                      fill="url(#colorLogActivity)"
                      name="Log Count"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Status Distribution - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Status Distribution
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

          {/* Log Type Distribution - Bar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Log Type Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.typeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Count" radius={[8, 8, 0, 0]}>
                      {chartData.typeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Top Actions - Horizontal Bar Chart */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AssessmentIcon color="secondary" />
                  Top Actions by Frequency
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.actionData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11 }} />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Count" fill="#9c27b0" radius={[0, 8, 8, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              select
              fullWidth
              size="small"
              label="Log Type"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <MenuItem value="all">All Types</MenuItem>
              <MenuItem value="audit">Audit Logs</MenuItem>
              <MenuItem value="webhook">Webhook Deliveries</MenuItem>
              <MenuItem value="api">API Calls</MenuItem>
              <MenuItem value="pipeline">Pipeline Runs</MenuItem>
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      <EnhancedTable
        columns={columns}
        data={filteredLogs}
        loading={loading}
        onRefresh={fetchData}
        defaultOrderBy="timestamp"
        defaultOrder="desc"
        searchPlaceholder="Search integration logs by type, action, entity..."
        exportFileName="integration-logs"
        rowsPerPageOptions={[10, 25, 50, 100]}
        dense={true}
      />
    </Box>
  )
}

export default IntegrationLogsDashboard
