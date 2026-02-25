import React, { useState, useEffect, useMemo } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  IconButton,
  Tooltip,
  TextField,
  MenuItem,
} from '@mui/material'
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  CheckCircle as ApproveIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  Assignment as AssignmentIcon,
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
import EnhancedTable from '../common/EnhancedTable'
import ChangeRequestForm from './ChangeRequestForm'
import ChangeRequestDetailDialog from './ChangeRequestDetailDialog'

function ChangeRequestsDashboard() {
  const [requests, setRequests] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Dialogs
  const [formOpen, setFormOpen] = useState(false)
  const [detailOpen, setDetailOpen] = useState(false)
  const [selectedRequest, setSelectedRequest] = useState(null)

  // Filters
  const [filterStatus, setFilterStatus] = useState('')
  const [filterRisk, setFilterRisk] = useState('')

  useEffect(() => {
    fetchRequests()
    fetchStats()
  }, [filterStatus, filterRisk])

  const fetchRequests = async () => {
    setLoading(true)
    setError('')
    try {
      let url = '/api/v1/change-requests/?limit=1000'
      if (filterStatus) url += `&approval_status=${filterStatus}`
      if (filterRisk) url += `&risk_level=${filterRisk}`

      const response = await axiosInstance.get(url)
      setRequests(response.data)
    } catch (err) {
      console.error('Error fetching change requests:', err)
      setError('Failed to load change requests')
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/change-requests/stats/summary')
      setStats(response.data)
    } catch (err) {
      console.error('Error fetching stats:', err)
    }
  }

  const handleRefresh = () => {
    fetchRequests()
    fetchStats()
  }

  const handleViewDetails = (request) => {
    setSelectedRequest(request)
    setDetailOpen(true)
  }

  const handleFormSuccess = () => {
    fetchRequests()
    fetchStats()
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Critical': return 'error'
      case 'High': return 'warning'
      case 'Medium': return 'info'
      case 'Low': return 'success'
      default: return 'default'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'Pending': return 'warning'
      case 'Approved': return 'success'
      case 'Rejected': return 'error'
      default: return 'default'
    }
  }

  const getImplementationColor = (status) => {
    switch (status) {
      case 'Completed': return 'success'
      case 'InProgress': return 'info'
      case 'Submitted': return 'default'
      case 'RolledBack': return 'error'
      default: return 'default'
    }
  }

  // Chart data calculations
  const chartData = useMemo(() => {
    if (!requests.length) return null

    // Approval status distribution
    const statusCounts = requests.reduce((acc, req) => {
      acc[req.approval_status] = (acc[req.approval_status] || 0) + 1
      return acc
    }, {})
    const statusData = Object.entries(statusCounts).map(([name, value]) => ({ name, value }))

    // Risk level distribution
    const riskCounts = requests.reduce((acc, req) => {
      acc[req.risk_level] = (acc[req.risk_level] || 0) + 1
      return acc
    }, {})
    const riskData = Object.entries(riskCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => {
        const order = { Critical: 0, High: 1, Medium: 2, Low: 3 }
        return order[a.name] - order[b.name]
      })

    // Change type distribution
    const typeCounts = requests.reduce((acc, req) => {
      acc[req.change_type] = (acc[req.change_type] || 0) + 1
      return acc
    }, {})
    const typeData = Object.entries(typeCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)

    // Timeline - requests by month
    const timelineMap = requests.reduce((acc, req) => {
      const month = new Date(req.requested_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
      acc[month] = (acc[month] || 0) + 1
      return acc
    }, {})
    const timelineData = Object.entries(timelineMap)
      .map(([month, count]) => ({ month, count }))
      .slice(-6) // Last 6 months

    return { statusData, riskData, typeData, timelineData }
  }, [requests])

  const COLORS = {
    status: ['#ff9800', '#4caf50', '#f44336'],
    risk: ['#d32f2f', '#f57c00', '#1976d2', '#388e3c'],
    type: ['#2196f3', '#9c27b0', '#00bcd4', '#ff5722', '#4caf50'],
  }

  // Define table columns
  const columns = [
    {
      id: 'change_id',
      label: 'ID',
      sortable: true,
      align: 'center',
      width: '80px',
    },
    {
      id: 'title',
      label: 'Title',
      sortable: true,
      render: (value) => (
        <Typography sx={{ fontWeight: 500 }}>
          {value}
        </Typography>
      ),
    },
    {
      id: 'change_type',
      label: 'Change Type',
      sortable: true,
      align: 'center',
      render: (value) => <Chip label={value} size="small" variant="outlined" />,
    },
    {
      id: 'risk_level',
      label: 'Risk Level',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          color={getRiskColor(value)}
          size="small"
        />
      ),
    },
    {
      id: 'approval_status',
      label: 'Approval Status',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          color={getStatusColor(value)}
          size="small"
        />
      ),
    },
    {
      id: 'status',
      label: 'Implementation',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          color={getImplementationColor(value)}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      id: 'requested_at',
      label: 'Requested',
      sortable: true,
      render: (value) => new Date(value).toLocaleDateString(),
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      align: 'right',
      render: (value, row) => (
        <Tooltip title="View Details">
          <IconButton
            size="small"
            onClick={() => handleViewDetails(row)}
            color="info"
          >
            <ViewIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      ),
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Change Requests
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setFormOpen(true)}
          >
            Create Change Request
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TrendingUpIcon color="primary" />
                  <Typography variant="caption" color="textSecondary">
                    Total Requests
                  </Typography>
                </Box>
                <Typography variant="h4">{stats.total_requests}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderLeft: '4px solid #ed6c02' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <WarningIcon color="warning" />
                  <Typography variant="caption" color="textSecondary">
                    Pending Approval
                  </Typography>
                </Box>
                <Typography variant="h4">{stats.pending_approval}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <WarningIcon color="error" />
                  <Typography variant="caption" color="textSecondary">
                    Critical Risk
                  </Typography>
                </Box>
                <Typography variant="h4">{stats.critical_risk}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderLeft: '4px solid #2e7d32' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <ApproveIcon color="success" />
                  <Typography variant="caption" color="textSecondary">
                    Completed
                  </Typography>
                </Box>
                <Typography variant="h4">{stats.completed}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Change Request Analytics */}
      {!loading && chartData && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Approval Status - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ApproveIcon color="primary" />
                  Approval Status Distribution
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
                        <Cell key={`cell-${index}`} fill={COLORS.status[index % COLORS.status.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Risk Level - Bar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <WarningIcon color="error" />
                  Risk Level Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.riskData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Requests" radius={[8, 8, 0, 0]}>
                      {chartData.riskData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.risk[index % COLORS.risk.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Change Type - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AssignmentIcon color="secondary" />
                  Change Type Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartData.typeData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) =>
                        `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={100}
                      
                      dataKey="value"
                    >
                      {chartData.typeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.type[index % COLORS.type.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Timeline - Line Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUpIcon color="info" />
                  Request Trend (Last 6 Months)
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData.timelineData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#1976d2"
                      strokeWidth={3}
                      name="Requests"
                      dot={{ r: 6 }}
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              select
              fullWidth
              label="Approval Status"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Statuses</MenuItem>
              <MenuItem value="Pending">Pending</MenuItem>
              <MenuItem value="Approved">Approved</MenuItem>
              <MenuItem value="Rejected">Rejected</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              select
              fullWidth
              label="Risk Level"
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Risk Levels</MenuItem>
              <MenuItem value="Low">Low</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="High">High</MenuItem>
              <MenuItem value="Critical">Critical</MenuItem>
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {/* Enhanced Requests Table */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <EnhancedTable
          columns={columns}
          data={requests}
          loading={loading}
          onRefresh={handleRefresh}
          defaultOrderBy="requested_at"
          defaultOrder="desc"
          searchPlaceholder="Search change requests by title, type, status..."
          exportFileName="change-requests"
          rowsPerPageOptions={[10, 25, 50, 100]}
        />
      )}

      {/* Create Form Dialog */}
      <ChangeRequestForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={handleFormSuccess}
      />

      {/* Detail Dialog */}
      <ChangeRequestDetailDialog
        open={detailOpen}
        onClose={() => setDetailOpen(false)}
        request={selectedRequest}
        onUpdate={handleFormSuccess}
      />
    </Box>
  )
}

export default ChangeRequestsDashboard
