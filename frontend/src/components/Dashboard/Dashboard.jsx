import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Chip,
  TextField,
  MenuItem,
  Button,
  Paper,
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Error,
  Warning,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

function MetricCard({ title, value, unit, trend, trendValue, status }) {
  const getStatusColor = () => {
    if (status === 'green') return '#4CAF50'
    if (status === 'yellow') return '#FF9800'
    if (status === 'red') return '#F44336'
    return '#1976D2'
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" color="textSecondary" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, color: getStatusColor() }}>
            {value}
          </Typography>
          <Typography variant="h6" color="textSecondary">
            {unit}
          </Typography>
        </Box>
        {trend && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1, gap: 0.5 }}>
            {trend === 'up' ? (
              <TrendingUp sx={{ color: '#4CAF50', fontSize: 18 }} />
            ) : (
              <TrendingDown sx={{ color: '#F44336', fontSize: 18 }} />
            )}
            <Typography variant="body2" sx={{ color: trend === 'up' ? '#4CAF50' : '#F44336' }}>
              {trendValue}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

function Dashboard() {
  const [metrics, setMetrics] = useState(null)
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  // Filter states
  const [filterEnvironment, setFilterEnvironment] = useState('')
  const [filterLifecycle, setFilterLifecycle] = useState('')
  const [filterCompliant, setFilterCompliant] = useState('')

  useEffect(() => {
    fetchData()
  }, [filterEnvironment, filterLifecycle, filterCompliant])

  const fetchData = async () => {
    setLoading(true)
    await Promise.all([fetchMetrics(), fetchAssets()])
    setLoading(false)
  }

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/api/v1/compliance/metrics')
      setMetrics(response.data)
    } catch (error) {
      console.error('Error fetching metrics:', error)
    }
  }

  const fetchAssets = async () => {
    try {
      let url = '/api/v1/assets/?limit=100'
      if (filterEnvironment) url += `&environment=${filterEnvironment}`
      if (filterLifecycle) url += `&lifecycle_stage=${filterLifecycle}`
      if (filterCompliant !== '') url += `&compliant=${filterCompliant}`

      const response = await axios.get(url)
      setAssets(response.data)
    } catch (error) {
      console.error('Error fetching assets:', error)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchData()
    setRefreshing(false)
  }

  const handleClearFilters = () => {
    setFilterEnvironment('')
    setFilterLifecycle('')
    setFilterCompliant('')
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  const getComplianceStatus = () => {
    if (!metrics) return 'yellow'
    if (metrics.compliance_rate >= 95) return 'green'
    if (metrics.compliance_rate >= 85) return 'yellow'
    return 'red'
  }

  // Chart data preparation
  const complianceData = metrics
    ? [
        { name: 'Compliant', value: metrics.compliant_assets, color: '#4CAF50' },
        { name: 'Non-Compliant', value: metrics.non_compliant_assets, color: '#F44336' },
      ]
    : []

  const environmentData = assets.reduce((acc, asset) => {
    const env = asset.environment
    const existing = acc.find((item) => item.environment === env)
    if (existing) {
      existing.count++
      if (asset.naming_compliant) existing.compliant++
    } else {
      acc.push({
        environment: env,
        count: 1,
        compliant: asset.naming_compliant ? 1 : 0,
      })
    }
    return acc
  }, [])

  const COLORS = ['#4CAF50', '#F44336', '#FF9800', '#2196F3']

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">
          Governance Dashboard
        </Typography>
        <Button
          variant="outlined"
          startIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          Refresh Data
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <FilterIcon color="action" />
          <Typography variant="h6">Filters</Typography>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              select
              fullWidth
              label="Environment"
              value={filterEnvironment}
              onChange={(e) => setFilterEnvironment(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Environments</MenuItem>
              <MenuItem value="DEV">DEV</MenuItem>
              <MenuItem value="QA">QA</MenuItem>
              <MenuItem value="UAT">UAT</MenuItem>
              <MenuItem value="PROD">PROD</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              select
              fullWidth
              label="Lifecycle Stage"
              value={filterLifecycle}
              onChange={(e) => setFilterLifecycle(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Stages</MenuItem>
              <MenuItem value="Draft">Draft</MenuItem>
              <MenuItem value="Active">Active</MenuItem>
              <MenuItem value="Deprecated">Deprecated</MenuItem>
              <MenuItem value="Retired">Retired</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              select
              fullWidth
              label="Compliance Status"
              value={filterCompliant}
              onChange={(e) => setFilterCompliant(e.target.value)}
              size="small"
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="true">Compliant</MenuItem>
              <MenuItem value="false">Non-Compliant</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              onClick={handleClearFilters}
              sx={{ height: '40px' }}
            >
              Clear Filters
            </Button>
          </Grid>
        </Grid>
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="textSecondary">
            Showing {assets.length} assets {filterEnvironment || filterLifecycle || filterCompliant ? '(filtered)' : '(all)'}
          </Typography>
        </Box>
      </Paper>

      <Grid container spacing={3} sx={{ mt: 1 }}>
        {/* Total Assets */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Assets"
            value={metrics?.total_assets || 0}
            unit="assets"
          />
        </Grid>

        {/* Compliance Rate */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Compliance Rate"
            value={metrics?.compliance_rate || 0}
            unit="%"
            trend="up"
            trendValue="+2.3%"
            status={getComplianceStatus()}
          />
        </Grid>

        {/* Non-Compliant Assets */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Non-Compliant"
            value={metrics?.non_compliant_assets || 0}
            unit="assets"
            status={metrics?.non_compliant_assets > 0 ? 'red' : 'green'}
          />
        </Grid>

        {/* Missing Documentation */}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Missing Docs"
            value={metrics?.missing_documentation || 0}
            unit="assets"
            status={metrics?.missing_documentation > 0 ? 'yellow' : 'green'}
          />
        </Grid>
      </Grid>

      {/* Status Overview */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Status Overview
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 2 }}>
            <Chip
              icon={<CheckCircle />}
              label={`${metrics?.compliant_assets || 0} Compliant`}
              color="success"
              sx={{ fontSize: '1rem', py: 2.5, px: 1 }}
            />
            <Chip
              icon={<Error />}
              label={`${metrics?.non_compliant_assets || 0} Non-Compliant`}
              color="error"
              sx={{ fontSize: '1rem', py: 2.5, px: 1 }}
            />
            <Chip
              icon={<Warning />}
              label={`${metrics?.missing_documentation || 0} Missing Docs`}
              color="warning"
              sx={{ fontSize: '1rem', py: 2.5, px: 1 }}
            />
            <Chip
              icon={<Warning />}
              label={`${metrics?.pending_changes || 0} Pending Changes`}
              color="info"
              sx={{ fontSize: '1rem', py: 2.5, px: 1 }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Visualizations */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        {/* Compliance Pie Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Compliance Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={complianceData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value, percent }) =>
                      `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                    }
                    outerRadius={80}
                    
                    dataKey="value"
                  >
                    {complianceData.map((entry, index) => (
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

        {/* Assets by Environment Bar Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Assets by Environment
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={environmentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="environment" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="compliant" name="Compliant" fill="#4CAF50" />
                  <Bar
                    dataKey={(data) => data.count - data.compliant}
                    name="Non-Compliant"
                    fill="#F44336"
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Welcome Message */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Welcome to Enterprise DaaS Governance Portal
          </Typography>
          <Typography variant="body1" paragraph>
            This portal provides enterprise-wide governance for data and platform assets, ensuring compliance
            with naming conventions, lifecycle management, and change control processes.
          </Typography>
          <Typography variant="body2" color="textSecondary">
            <strong>Quick Start:</strong>
          </Typography>
          <ul>
            <li>
              <Typography variant="body2">
                Navigate to <strong>Asset Registry</strong> to view and manage assets
              </Typography>
            </li>
            <li>
              <Typography variant="body2">
                Use <strong>Naming Validator</strong> to check compliance before registration
              </Typography>
            </li>
            <li>
              <Typography variant="body2">
                Review <strong>Compliance Dashboard</strong> for governance metrics
              </Typography>
            </li>
          </ul>
        </CardContent>
      </Card>
    </Box>
  )
}

export default Dashboard
