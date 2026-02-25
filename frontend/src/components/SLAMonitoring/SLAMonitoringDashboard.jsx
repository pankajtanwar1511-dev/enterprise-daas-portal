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
  LinearProgress,
  TextField,
  MenuItem,
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Speed as SpeedIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
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
  ReferenceLine,
} from 'recharts'

function SLAMonitoringDashboard() {
  const [metrics, setMetrics] = useState([])
  const [summary, setSummary] = useState(null)
  const [breaches, setBreaches] = useState([])
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedMetric, setSelectedMetric] = useState('availability')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const [metricsRes, summaryRes, breachesRes, assetsRes] = await Promise.all([
        axiosInstance.get('/api/v1/sla/metrics'),
        axiosInstance.get('/api/v1/sla/statistics'),
        axiosInstance.get('/api/v1/sla/violations'),
        axiosInstance.get('/api/v1/assets?limit=1000'),
      ])
      setMetrics(metricsRes.data.metrics || [])
      setSummary(summaryRes.data)
      setBreaches(breachesRes.data.violations || [])
      setAssets(assetsRes.data)
    } catch (err) {
      console.error('Error fetching SLA data:', err)
      setError('Failed to load SLA monitoring data')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (value, threshold) => {
    if (value >= threshold) return 'success'
    if (value >= threshold * 0.9) return 'warning'
    return 'error'
  }

  const getStatusIcon = (value, threshold) => {
    if (value >= threshold) return <CheckCircleIcon color="success" />
    if (value >= threshold * 0.9) return <WarningIcon color="warning" />
    return <ErrorIcon color="error" />
  }

  const calculateCompliance = () => {
    if (!summary) return 0
    const total = summary.total_slas || 1
    const breached = summary.breached_slas || 0
    return (((total - breached) / total) * 100).toFixed(1)
  }

  // Chart data calculations
  const chartData = useMemo(() => {
    if (!metrics.length && !breaches.length) return null

    // SLA Status Distribution
    const total = summary?.total_slas || 0
    const breached = summary?.breached_slas || 0
    const meeting = total - breached
    const statusData = [
      { name: 'Meeting SLAs', value: meeting, color: '#4caf50' },
      { name: 'Breached SLAs', value: breached, color: '#f44336' },
    ].filter(d => d.value > 0)

    // Metric Type Distribution
    const metricTypeCounts = metrics.reduce((acc, metric) => {
      acc[metric.metric_type] = (acc[metric.metric_type] || 0) + 1
      return acc
    }, {})
    const metricTypeData = Object.entries(metricTypeCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)

    // Breach Severity Distribution
    const severityCounts = breaches.reduce((acc, breach) => {
      const severity = breach.severity || 'Medium'
      acc[severity] = (acc[severity] || 0) + 1
      return acc
    }, {})

    // Severity color palette - 3 distinct colors
    const SEVERITY_COLORS = ['#d32f2f', '#ed6c02', '#0288d1', '#9c27b0', '#00bcd4']

    const severityData = Object.entries(severityCounts)
      .map(([name, value], index) => ({
        name,
        value,
        color: SEVERITY_COLORS[index % SEVERITY_COLORS.length]
      }))
      .sort((a, b) => b.value - a.value)

    // Breaches by Metric Type
    const breachTypeCounts = breaches.reduce((acc, breach) => {
      acc[breach.metric_type] = (acc[breach.metric_type] || 0) + 1
      return acc
    }, {})
    const breachTypeData = Object.entries(breachTypeCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)

    // Metrics Trend (last 20 data points)
    const trendData = metrics.slice(0, 20).reverse().map((m, i) => ({
      name: `T-${20 - i}`,
      value: m.metric_value || 0,
      target: m.sla_target || 100,
    }))

    // Breaches Timeline (last 10 breaches)
    const breachTimelineData = breaches
      .slice(0, 10)
      .reverse()
      .map((b, i) => ({
        name: new Date(b.breached_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        count: 1,
        severity: b.severity,
      }))
      // Group by date
      .reduce((acc, item) => {
        const existing = acc.find(a => a.name === item.name)
        if (existing) {
          existing.count++
        } else {
          acc.push(item)
        }
        return acc
      }, [])

    return { statusData, metricTypeData, severityData, breachTypeData, trendData, breachTimelineData }
  }, [metrics, breaches, summary])

  const COLORS = ['#4caf50', '#f44336', '#ff9800', '#2196f3', '#9c27b0', '#00bcd4', '#ff5722', '#3f51b5']

  // Define table columns for SLA Metrics
  const metricsColumns = [
    {
      id: 'asset_id',
      label: 'Asset',
      sortable: true,
    },
    {
      id: 'metric_type',
      label: 'Metric Type',
      sortable: true,
      render: (value) => <Chip label={value} size="small" />,
    },
    {
      id: 'metric_value',
      label: 'Current Value',
      sortable: true,
      align: 'center',
      render: (value, row) => (
        <Typography variant="body2">
          {value?.toFixed(2) || 0}
          {row.metric_type === 'availability' || row.metric_type === 'uptime' ? '%' : 'ms'}
        </Typography>
      ),
    },
    {
      id: 'sla_target',
      label: 'Target',
      sortable: true,
      align: 'center',
      render: (value, row) => (
        <Typography variant="body2">
          {value?.toFixed(2) || 0}
          {row.metric_type === 'availability' || row.metric_type === 'uptime' ? '%' : 'ms'}
        </Typography>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      sortable: false,
      align: 'center',
      render: (value, row) => getStatusIcon(row.metric_value || 0, row.sla_target || 100),
    },
    {
      id: 'recorded_at',
      label: 'Last Updated',
      sortable: true,
      render: (value) => (
        <Typography sx={{ fontSize: '0.75rem' }}>
          {new Date(value).toLocaleString()}
        </Typography>
      ),
    },
  ]

  // Define table columns for SLA Breaches
  const breachesColumns = [
    {
      id: 'asset_id',
      label: 'Asset',
      sortable: true,
    },
    {
      id: 'metric_type',
      label: 'Metric Type',
      sortable: true,
      render: (value) => <Chip label={value} size="small" />,
    },
    {
      id: 'actual_value',
      label: 'Actual Value',
      sortable: true,
      align: 'center',
      render: (value) => value?.toFixed(2) || 0,
    },
    {
      id: 'sla_target',
      label: 'SLA Target',
      sortable: true,
      align: 'center',
      render: (value) => value?.toFixed(2) || 0,
    },
    {
      id: 'severity',
      label: 'Severity',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value || 'Medium'}
          color={
            value === 'High' ? 'error' :
            value === 'Medium' ? 'warning' : 'info'
          }
          size="small"
        />
      ),
    },
    {
      id: 'breached_at',
      label: 'Breached At',
      sortable: true,
      render: (value) => (
        <Typography sx={{ fontSize: '0.75rem' }}>
          {new Date(value).toLocaleString()}
        </Typography>
      ),
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Real-Time SLA Monitoring
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchData} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      {summary && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <SpeedIcon color="primary" />
                  <Typography variant="caption" color="textSecondary">
                    SLA Compliance
                  </Typography>
                </Box>
                <Typography variant="h4">{calculateCompliance()}%</Typography>
                <LinearProgress
                  variant="determinate"
                  value={parseFloat(calculateCompliance())}
                  color={getStatusColor(parseFloat(calculateCompliance()), 95)}
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TrendingUpIcon color="primary" />
                  <Typography variant="caption" color="textSecondary">
                    Active SLAs
                  </Typography>
                </Box>
                <Typography variant="h4">{summary.total_slas || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <CheckCircleIcon color="success" />
                  <Typography variant="caption" color="textSecondary">
                    Meeting SLAs
                  </Typography>
                </Box>
                <Typography variant="h4">
                  {(summary.total_slas || 0) - (summary.breached_slas || 0)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <ErrorIcon color="error" />
                  <Typography variant="caption" color="textSecondary">
                    SLA Breaches
                  </Typography>
                </Box>
                <Typography variant="h4">{summary.breached_slas || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Charts Section */}
      {!loading && chartData && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* SLA Status Overview - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SpeedIcon color="primary" />
                  SLA Status Overview
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
                        <Cell key={`status-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Metric Type Distribution - Bar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AssessmentIcon color="secondary" />
                  Metric Type Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.metricTypeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Metrics Count" radius={[8, 8, 0, 0]}>
                      {chartData.metricTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Breach Severity Distribution - Pie Chart */}
          {chartData.severityData.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ErrorIcon color="error" />
                    Breach Severity Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={chartData.severityData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value, percent }) =>
                          `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                        }
                        outerRadius={100}
                        dataKey="value"
                      >
                        {chartData.severityData.map((entry, index) => (
                          <Cell key={`severity-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Breaches by Metric Type - Bar Chart */}
          {chartData.breachTypeData.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <WarningIcon color="warning" />
                    Breaches by Metric Type
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData.breachTypeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Bar dataKey="value" name="Breach Count" radius={[8, 8, 0, 0]}>
                        {chartData.breachTypeData.map((entry, index) => (
                          <Cell key={`breach-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* SLA Metrics Trend - Area Chart with Target Line */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TimelineIcon color="primary" />
                  SLA Metrics Trend Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={chartData.trendData}>
                    <defs>
                      <linearGradient id="colorMetricValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1976d2" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#1976d2" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#1976d2"
                      fillOpacity={1}
                      fill="url(#colorMetricValue)"
                      name="Actual Value"
                    />
                    <ReferenceLine
                      y={95}
                      stroke="#FF9800"
                      strokeDasharray="5 5"
                      label={{ value: 'Target 95%', position: 'right', fill: '#FF9800' }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Breach Timeline - Bar Chart */}
          {chartData.breachTimelineData.length > 0 && (
            <Grid item xs={12}>
              <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TimelineIcon color="error" />
                    SLA Breach Timeline
                  </Typography>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={chartData.breachTimelineData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Bar dataKey="count" name="Breach Count" fill="#d32f2f" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {/* Metrics Table */}
          <Grid item xs={12} md={8}>
            <Paper>
              <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
                <Typography variant="h6">SLA Metrics</Typography>
              </Box>
              <Box sx={{ p: 2 }}>
                <EnhancedTable
                  columns={metricsColumns}
                  data={metrics}
                  loading={loading}
                  onRefresh={fetchData}
                  defaultOrderBy="recorded_at"
                  defaultOrder="desc"
                  searchPlaceholder="Search SLA metrics by asset, type..."
                  exportFileName="sla-metrics"
                  rowsPerPageOptions={[10, 25, 50]}
                  dense={true}
                />
              </Box>
            </Paper>
          </Grid>

          {/* Quick Stats */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, mb: 2 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Metric Types</Typography>
              <TextField
                select
                fullWidth
                size="small"
                label="Select Metric"
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value)}
              >
                <MenuItem value="availability">Availability</MenuItem>
                <MenuItem value="latency">Latency</MenuItem>
                <MenuItem value="throughput">Throughput</MenuItem>
                <MenuItem value="uptime">Uptime</MenuItem>
                <MenuItem value="error_rate">Error Rate</MenuItem>
              </TextField>
            </Paper>

            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>Health Summary</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="caption" color="textSecondary">Excellent</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={70}
                      color="success"
                      sx={{ flexGrow: 1 }}
                    />
                    <Typography variant="body2">70%</Typography>
                  </Box>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary">At Risk</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={20}
                      color="warning"
                      sx={{ flexGrow: 1 }}
                    />
                    <Typography variant="body2">20%</Typography>
                  </Box>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary">Breached</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={10}
                      color="error"
                      sx={{ flexGrow: 1 }}
                    />
                    <Typography variant="body2">10%</Typography>
                  </Box>
                </Box>
              </Box>
            </Paper>
          </Grid>

          {/* SLA Breaches */}
          {breaches.length > 0 && (
            <Grid item xs={12}>
              <Paper>
                <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
                  <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ErrorIcon color="error" />
                    SLA Breaches
                  </Typography>
                </Box>
                <Box sx={{ p: 2 }}>
                  <EnhancedTable
                    columns={breachesColumns}
                    data={breaches}
                    loading={loading}
                    onRefresh={fetchData}
                    defaultOrderBy="breached_at"
                    defaultOrder="desc"
                    searchPlaceholder="Search SLA breaches by asset, metric..."
                    exportFileName="sla-breaches"
                    rowsPerPageOptions={[10, 25, 50]}
                    dense={true}
                  />
                </Box>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}
    </Box>
  )
}

export default SLAMonitoringDashboard
