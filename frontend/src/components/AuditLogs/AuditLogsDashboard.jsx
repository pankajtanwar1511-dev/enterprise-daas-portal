import React, { useState, useEffect, useMemo } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  TextField,
  MenuItem,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  Person as PersonIcon,
  Description as EntityIcon,
  History as ActionIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts'
import EnhancedTable from '../common/EnhancedTable'

function AuditLogsDashboard() {
  const [logs, setLogs] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Filters
  const [filterUserId, setFilterUserId] = useState('')
  const [filterEntityType, setFilterEntityType] = useState('')
  const [filterAction, setFilterAction] = useState('')

  useEffect(() => {
    fetchLogs()
    fetchStats()
  }, [filterUserId, filterEntityType, filterAction])

  const fetchLogs = async () => {
    setLoading(true)
    setError('')
    try {
      let url = '/api/v1/audit-logs/?limit=1000'
      if (filterUserId) url += `&user_id=${filterUserId}`
      if (filterEntityType) url += `&entity_type=${filterEntityType}`
      if (filterAction) url += `&action=${filterAction}`

      const response = await axiosInstance.get(url)
      setLogs(response.data)
    } catch (err) {
      console.error('Error fetching audit logs:', err)
      setError('Failed to load audit logs')
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/audit-logs/stats')
      setStats(response.data)
    } catch (err) {
      console.error('Error fetching audit stats:', err)
    }
  }

  const handleRefresh = () => {
    fetchLogs()
    fetchStats()
  }

  const getActionColor = (action) => {
    const actionUpper = action.toUpperCase()
    if (actionUpper.includes('CREATE')) return 'success'
    if (actionUpper.includes('UPDATE')) return 'info'
    if (actionUpper.includes('DELETE')) return 'error'
    if (actionUpper.includes('LOGIN')) return 'primary'
    return 'default'
  }

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleString()
  }

  const formatValue = (value) => {
    if (!value) return '-'

    // Try to parse as JSON
    try {
      const parsed = JSON.parse(value)
      // If it's an object, format it nicely
      if (typeof parsed === 'object' && parsed !== null) {
        return Object.entries(parsed).map(([key, val]) => (
          <Box key={key} sx={{ fontSize: '0.8rem', lineHeight: 1.4 }}>
            <strong>{key}:</strong> {val}
          </Box>
        ))
      }
      return value
    } catch {
      // Not JSON, return as-is (truncated if too long)
      if (value.length > 100) return value.substring(0, 100) + '...'
      return value
    }
  }

  // Chart data calculations
  const chartData = useMemo(() => {
    if (!logs.length) return null

    // Activity timeline - group by date
    const timelineMap = logs.reduce((acc, log) => {
      const date = new Date(log.timestamp).toLocaleDateString()
      acc[date] = (acc[date] || 0) + 1
      return acc
    }, {})
    const timelineData = Object.entries(timelineMap)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(a.date) - new Date(b.date))
      .slice(-14) // Last 14 days

    // Action type breakdown
    const actionCounts = logs.reduce((acc, log) => {
      acc[log.action] = (acc[log.action] || 0) + 1
      return acc
    }, {})
    const actionData = Object.entries(actionCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)

    // Entity type distribution
    const entityCounts = logs.reduce((acc, log) => {
      acc[log.entity_type] = (acc[log.entity_type] || 0) + 1
      return acc
    }, {})
    const entityData = Object.entries(entityCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)

    // Top users activity
    const userCounts = logs.reduce((acc, log) => {
      acc[log.user_id] = (acc[log.user_id] || 0) + 1
      return acc
    }, {})
    const topUsersData = Object.entries(userCounts)
      .map(([user, count]) => ({ user: `User ${user}`, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10) // Top 10 users

    return { timelineData, actionData, entityData, topUsersData }
  }, [logs])

  const COLORS = ['#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0', '#00bcd4', '#ff5722', '#3f51b5']

  // Define table columns
  const columns = [
    {
      id: 'timestamp',
      label: 'Timestamp',
      sortable: true,
      render: (value) => (
        <Typography sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
          {formatTimestamp(value)}
        </Typography>
      ),
    },
    {
      id: 'user_id',
      label: 'User ID',
      sortable: true,
      align: 'center',
    },
    {
      id: 'action',
      label: 'Action',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          color={getActionColor(value)}
          size="small"
        />
      ),
    },
    {
      id: 'entity_type',
      label: 'Entity Type',
      sortable: true,
      align: 'center',
      render: (value) => <Chip label={value} size="small" variant="outlined" />,
    },
    {
      id: 'entity_id',
      label: 'Entity ID',
      sortable: true,
      align: 'center',
    },
    {
      id: 'old_value',
      label: 'Old Value',
      sortable: false,
      render: (value) => (
        <Box sx={{ fontSize: '0.85rem', maxWidth: '200px', overflow: 'hidden' }}>
          {formatValue(value)}
        </Box>
      ),
    },
    {
      id: 'new_value',
      label: 'New Value',
      sortable: false,
      render: (value) => (
        <Box sx={{ fontSize: '0.85rem', maxWidth: '200px', overflow: 'hidden' }}>
          {formatValue(value)}
        </Box>
      ),
    },
    {
      id: 'ip_address',
      label: 'IP Address',
      sortable: true,
      render: (value) => (
        <Typography sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
          {value || '-'}
        </Typography>
      ),
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Audit Logs Dashboard
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={handleRefresh} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <ActionIcon color="primary" />
                  <Typography variant="caption" color="textSecondary">
                    Total Logs
                  </Typography>
                </Box>
                <Typography variant="h4">{stats.total_logs.toLocaleString()}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <EntityIcon color="primary" />
                  <Typography variant="caption" color="textSecondary">
                    Entity Types
                  </Typography>
                </Box>
                <Typography variant="h4">{stats.by_entity_type.length}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <ActionIcon color="primary" />
                  <Typography variant="caption" color="textSecondary">
                    Action Types
                  </Typography>
                </Box>
                <Typography variant="h4">{stats.by_action.length}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <PersonIcon color="primary" />
                  <Typography variant="caption" color="textSecondary">
                    Active Users
                  </Typography>
                </Box>
                <Typography variant="h4">{stats.top_users.length}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Activity Analytics Charts */}
      {!loading && chartData && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Activity Timeline - Area Chart */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TimelineIcon color="primary" />
                  Activity Timeline (Last 14 Days)
                </Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={chartData.timelineData}>
                    <defs>
                      <linearGradient id="colorActivity" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2196f3" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#2196f3" stopOpacity={0}/>
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
                      fill="url(#colorActivity)"
                      name="Activities"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Action Type Breakdown - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ActionIcon color="primary" />
                  Action Type Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartData.actionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) =>
                        `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={100}
                      
                      dataKey="value"
                    >
                      {chartData.actionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Entity Type Distribution - Bar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <EntityIcon color="secondary" />
                  Entity Type Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.entityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Actions" radius={[8, 8, 0, 0]}>
                      {chartData.entityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Top Users Activity - Horizontal Bar Chart */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PersonIcon color="info" />
                  Top 10 Most Active Users
                </Typography>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={chartData.topUsersData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="user" type="category" width={100} />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="count" name="Activities" fill="#4caf50" radius={[0, 8, 8, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <FilterIcon />
          <Typography variant="h6">Filters</Typography>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="User ID"
              type="number"
              value={filterUserId}
              onChange={(e) => setFilterUserId(e.target.value)}
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              select
              fullWidth
              label="Entity Type"
              value={filterEntityType}
              onChange={(e) => setFilterEntityType(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Entity Types</MenuItem>
              <MenuItem value="Asset">Asset</MenuItem>
              <MenuItem value="User">User</MenuItem>
              <MenuItem value="Domain">Domain</MenuItem>
              <MenuItem value="Vendor">Vendor</MenuItem>
              <MenuItem value="ChangeRequest">Change Request</MenuItem>
              <MenuItem value="Goal">Goal</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              select
              fullWidth
              label="Action"
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Actions</MenuItem>
              <MenuItem value="CREATE">CREATE</MenuItem>
              <MenuItem value="UPDATE">UPDATE</MenuItem>
              <MenuItem value="DELETE">DELETE</MenuItem>
              <MenuItem value="LOGIN">LOGIN</MenuItem>
              <MenuItem value="LOGOUT">LOGOUT</MenuItem>
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {/* Enhanced Logs Table */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <EnhancedTable
          columns={columns}
          data={logs}
          loading={loading}
          onRefresh={handleRefresh}
          defaultOrderBy="timestamp"
          defaultOrder="desc"
          searchPlaceholder="Search audit logs by user, action, entity..."
          exportFileName="audit-logs"
          rowsPerPageOptions={[10, 25, 50, 100]}
          dense={true}
        />
      )}
    </Box>
  )
}

export default AuditLogsDashboard
