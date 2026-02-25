import React, { useEffect, useState, useMemo } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Chip,
  LinearProgress,
} from '@mui/material'
import { Error, Warning, CheckCircle, TrendingUp } from '@mui/icons-material'
import EnhancedTable from '../common/EnhancedTable'
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
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'

function ComplianceDashboard() {
  const [metrics, setMetrics] = useState(null)
  const [violations, setViolations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [metricsRes, violationsRes] = await Promise.all([
        axiosInstance.get('/api/v1/compliance/metrics'),
        axiosInstance.get('/api/v1/compliance/violations'),
      ])
      setMetrics(metricsRes.data)
      setViolations(violationsRes.data.violations)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching compliance data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  const complianceRate = metrics?.compliance_rate || 0
  const getComplianceColor = () => {
    if (complianceRate >= 95) return 'success'
    if (complianceRate >= 85) return 'warning'
    return 'error'
  }

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'error'
      case 'medium':
        return 'warning'
      case 'low':
        return 'info'
      default:
        return 'default'
    }
  }

  // Chart data preparation
  const complianceStatusData = metrics
    ? [
        { name: 'Compliant', value: metrics.compliant_assets, color: '#4CAF50' },
        { name: 'Non-Compliant', value: metrics.non_compliant_assets, color: '#F44336' },
        { name: 'Missing Docs', value: metrics.missing_documentation, color: '#FF9800' },
      ]
    : []

  const violationsBySeverity = violations.reduce((acc, violation) => {
    const severity = violation.severity
    const existing = acc.find((item) => item.severity === severity)
    if (existing) {
      existing.count++
    } else {
      acc.push({ severity, count: 1 })
    }
    return acc
  }, [])

  const violationsByType = violations.reduce((acc, violation) => {
    const type = violation.violation_type
    const existing = acc.find((item) => item.type === type)
    if (existing) {
      existing.count++
    } else {
      acc.push({ type, count: 1 })
    }
    return acc
  }, [])

  const SEVERITY_COLORS = {
    High: '#F44336',
    Medium: '#FF9800',
    Low: '#2196F3',
  }

  // Chart data for compliance trends
  const chartData = useMemo(() => {
    if (!metrics) return null

    // Mock historical compliance trend data (last 6 months)
    const trendData = [
      { month: 'Aug', rate: 82, compliant: 78, total: 95 },
      { month: 'Sep', rate: 85, compliant: 85, total: 100 },
      { month: 'Oct', rate: 88, compliant: 92, total: 105 },
      { month: 'Nov', rate: 91, compliant: 100, total: 110 },
      { month: 'Dec', rate: 89, compliant: 98, total: 110 },
      { month: 'Jan', rate: complianceRate, compliant: metrics.compliant_assets, total: metrics.total_assets },
    ]

    // Violations trend over time
    const violationsTrendData = [
      { month: 'Aug', violations: 15 },
      { month: 'Sep', violations: 12 },
      { month: 'Oct', violations: 10 },
      { month: 'Nov', violations: 8 },
      { month: 'Dec', violations: 11 },
      { month: 'Jan', violations: violations.length },
    ]

    return { trendData, violationsTrendData }
  }, [metrics, violations, complianceRate])

  // Define columns for violations table
  const violationsColumns = [
    {
      id: 'asset_id',
      label: 'Asset ID',
      sortable: true,
    },
    {
      id: 'violation_type',
      label: 'Violation Type',
      sortable: true,
    },
    {
      id: 'severity',
      label: 'Severity',
      sortable: true,
      render: (value) => (
        <Chip
          label={value}
          color={getSeverityColor(value)}
          size="small"
        />
      ),
    },
    {
      id: 'description',
      label: 'Description',
      sortable: false,
      width: '40%',
    },
    {
      id: 'detected_at',
      label: 'Detected',
      sortable: true,
      render: (value) => new Date(value).toLocaleDateString(),
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Compliance Dashboard
      </Typography>

      {/* Overview Metrics */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Compliance Rate */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Overall Compliance Rate
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, my: 2 }}>
                <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                  <CircularProgress
                    variant="determinate"
                    value={complianceRate}
                    size={100}
                    thickness={6}
                    color={getComplianceColor()}
                  />
                  <Box
                    sx={{
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      position: 'absolute',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="h5" component="div" color="text.secondary">
                      {Math.round(complianceRate)}%
                    </Typography>
                  </Box>
                </Box>
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    {metrics?.compliant_assets} of {metrics?.total_assets} assets compliant
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Target: ≥95%
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ mt: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={complianceRate}
                  color={getComplianceColor()}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Status Breakdown */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Status Breakdown
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CheckCircle color="success" />
                    <Typography>Compliant Assets</Typography>
                  </Box>
                  <Chip label={metrics?.compliant_assets || 0} color="success" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Error color="error" />
                    <Typography>Non-Compliant Assets</Typography>
                  </Box>
                  <Chip label={metrics?.non_compliant_assets || 0} color="error" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Warning color="warning" />
                    <Typography>Missing Documentation</Typography>
                  </Box>
                  <Chip label={metrics?.missing_documentation || 0} color="warning" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Warning color="info" />
                    <Typography>Pending Changes</Typography>
                  </Box>
                  <Chip label={metrics?.pending_changes || 0} color="info" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Visualizations */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        {/* Compliance Trend - Area Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp color="primary" />
                Compliance Rate Trend (Last 6 Months)
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={chartData?.trendData || []}>
                  <defs>
                    <linearGradient id="colorCompliance" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#4CAF50" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#4CAF50" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <ReferenceLine
                    y={95}
                    stroke="#FF9800"
                    strokeDasharray="5 5"
                    label={{ value: 'Target 95%', position: 'right', fill: '#FF9800' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="rate"
                    stroke="#4CAF50"
                    fillOpacity={1}
                    fill="url(#colorCompliance)"
                    name="Compliance Rate (%)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Compliance Status Pie Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Compliance Status Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={complianceStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value, percent }) =>
                      `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                    }
                    outerRadius={80}
                    
                    dataKey="value"
                  >
                    {complianceStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Violations by Severity Bar Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Violations by Severity
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={violationsBySeverity}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="severity" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" name="Violations" fill="#F44336">
                    {violationsBySeverity.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={SEVERITY_COLORS[entry.severity] || '#999'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Violations Trend - Line Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Violations Trend Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData?.violationsTrendData || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="violations"
                    stroke="#F44336"
                    strokeWidth={2}
                    name="Active Violations"
                    dot={{ fill: '#F44336', r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Violations by Type - Pie Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Violations by Type
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={violationsByType}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ type, count, percent }) =>
                      `${type}: ${count} (${(percent * 100).toFixed(0)}%)`
                    }
                    outerRadius={80}
                    
                    dataKey="count"
                  >
                    {violationsByType.map((entry, index) => {
                      const COLORS = ['#F44336', '#FF9800', '#2196F3', '#9C27B0', '#4CAF50']
                      return <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    })}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Violations Table */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Active Compliance Violations
          </Typography>
          {violations.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <CheckCircle color="success" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h6" color="success.main">
                No Active Violations
              </Typography>
              <Typography variant="body2" color="textSecondary">
                All assets are compliant with governance policies.
              </Typography>
            </Box>
          ) : (
            <EnhancedTable
              columns={violationsColumns}
              data={violations}
              loading={false}
              onRefresh={fetchData}
              defaultOrderBy="detected_at"
              defaultOrder="desc"
              searchPlaceholder="Search violations..."
              exportFileName="compliance_violations"
              rowsPerPageOptions={[10, 25, 50]}
            />
          )}
        </CardContent>
      </Card>

      {/* Governance Policies Summary */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Governance Policies Enforced
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
                <Typography variant="h6" sx={{ mt: 1 }}>
                  Naming Convention
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Automated validation
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
                <Typography variant="h6" sx={{ mt: 1 }}>
                  Ownership Assignment
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  100% coverage required
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
                <Typography variant="h6" sx={{ mt: 1 }}>
                  Documentation
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Required for Active assets
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
                <Typography variant="h6" sx={{ mt: 1 }}>
                  Lifecycle Management
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Enforced transitions
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}

export default ComplianceDashboard
