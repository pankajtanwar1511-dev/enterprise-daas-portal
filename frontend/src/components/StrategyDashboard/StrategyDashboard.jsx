import React, { useEffect, useState } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  LinearProgress,
  Paper,
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import {
  TrendingUp,
  AttachMoney,
  Assessment,
  Groups,
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
  LineChart,
  Line,
} from 'recharts'

function MetricCard({ title, value, subtitle, icon, color = 'primary' }) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, color: color === 'success' ? '#4CAF50' : '#1976D2' }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ color: color === 'success' ? '#4CAF50' : '#1976D2' }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

function StrategyDashboard() {
  const [dashboard, setDashboard] = useState(null)
  const [valueMetrics, setValueMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [dashboardRes, valueRes] = await Promise.all([
        axiosInstance.get('/api/v1/strategy/dashboard'),
        axiosInstance.get('/api/v1/strategy/value-delivered')
      ])
      setDashboard(dashboardRes.data)
      setValueMetrics(valueRes.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching strategy data:', error)
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

  // Define columns for value delivered table
  const valueDeliveredColumns = [
    {
      id: 'domain',
      label: 'Domain',
      sortable: true,
      render: (value) => (
        <Typography variant="body1" fontWeight="500">
          {value}
        </Typography>
      ),
    },
    {
      id: 'value_delivered',
      label: 'Value Delivered',
      sortable: true,
      render: (value) => (
        <Typography variant="body1" color="success.main" fontWeight="600">
          {value}
        </Typography>
      ),
    },
    {
      id: 'key_achievement',
      label: 'Key Achievement',
      sortable: false,
      width: '50%',
      render: (value) => (
        <Typography variant="body2" color="textSecondary">
          {value}
        </Typography>
      ),
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        DaaS Strategy Dashboard
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Strategic overview of DaaS initiatives, business goal alignment, and value delivery
      </Typography>

      {/* Key Strategic Metrics */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Business Goals"
            value={dashboard?.business_goals?.active || 0}
            subtitle={`${dashboard?.business_goals?.achievement_rate || 0}% Achievement Rate`}
            icon={<Assessment sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Strategic Initiatives"
            value={dashboard?.strategic_initiatives?.on_track || 0}
            subtitle={`of ${dashboard?.strategic_initiatives?.total || 0} on track`}
            icon={<TrendingUp sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Budget Utilization"
            value={`${dashboard?.budget?.utilization_percentage || 0}%`}
            subtitle={`$${(dashboard?.budget?.remaining / 1000000).toFixed(1)}M remaining`}
            icon={<AttachMoney sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Expected ROI"
            value={`${dashboard?.roi_metrics?.roi_percentage || 0}%`}
            subtitle="Return on Investment"
            icon={<TrendingUp sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Budget Overview */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Budget Overview - FY 2026
          </Typography>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Total Allocated</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${(dashboard?.budget?.total_allocated / 1000000).toFixed(1)}M
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Spent to Date</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${(dashboard?.budget?.total_spent / 1000000).toFixed(1)}M
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2">Remaining</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    ${(dashboard?.budget?.remaining / 1000000).toFixed(1)}M
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={dashboard?.budget?.utilization_percentage || 0}
                  sx={{ height: 8, borderRadius: 4 }}
                />
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  {dashboard?.budget?.utilization_percentage?.toFixed(1)}% Utilized
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Chip
                  label={`${dashboard?.strategic_initiatives?.on_track || 0} Initiatives On Track`}
                  color="success"
                  sx={{ fontSize: '0.9rem', py: 2 }}
                />
                <Chip
                  label={`${dashboard?.strategic_initiatives?.at_risk || 0} Initiatives At Risk`}
                  color="warning"
                  sx={{ fontSize: '0.9rem', py: 2 }}
                />
                <Chip
                  label={`${dashboard?.asset_alignment?.alignment_coverage || 0}% Asset Alignment`}
                  color="info"
                  sx={{ fontSize: '0.9rem', py: 2 }}
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Value Delivered */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Value Delivered Across Domains
          </Typography>
          <EnhancedTable
            columns={valueDeliveredColumns}
            data={valueMetrics?.by_domain || []}
            loading={false}
            onRefresh={fetchData}
            defaultOrderBy="domain"
            defaultOrder="asc"
            searchPlaceholder="Search domains..."
            exportFileName="value_delivered_by_domain"
            rowsPerPageOptions={[10, 25, 50]}
          />
        </CardContent>
      </Card>

      {/* Overall Impact Metrics */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Overall Impact Metrics
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {Object.entries(valueMetrics?.overall_metrics || {}).map(([key, value]) => (
              <Grid item xs={12} sm={6} md={4} key={key}>
                <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#E3F2FD' }}>
                  <Typography variant="h4" color="primary" fontWeight="bold">
                    {value}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ textTransform: 'capitalize' }}>
                    {key.replace(/_/g, ' ')}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Asset-Business Alignment */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Asset-Business Goal Alignment
          </Typography>
          <Typography variant="body2" color="textSecondary" paragraph>
            Demonstrates how data assets directly support strategic business objectives
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <Chip
              label={`${dashboard?.asset_alignment?.total_assets_aligned || 0} Assets Aligned to Goals`}
              color="primary"
              sx={{ fontSize: '0.95rem', py: 2.5, px: 1 }}
            />
            <Chip
              label={`${dashboard?.asset_alignment?.alignment_coverage || 0}% Coverage`}
              color="success"
              sx={{ fontSize: '0.95rem', py: 2.5, px: 1 }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Visualizations */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        {/* Budget Utilization Pie Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Budget Utilization
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Spent', value: dashboard?.budget?.total_spent || 0, color: '#2196F3' },
                      {
                        name: 'Remaining',
                        value: dashboard?.budget?.remaining || 0,
                        color: '#4CAF50',
                      },
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value, percent }) =>
                      `${name}: $${(value / 1000000).toFixed(1)}M (${(percent * 100).toFixed(0)}%)`
                    }
                    outerRadius={80}
                    
                    dataKey="value"
                  >
                    <Cell fill="#2196F3" />
                    <Cell fill="#4CAF50" />
                  </Pie>
                  <Tooltip
                    formatter={(value) => `$${(value / 1000000).toFixed(2)}M`}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Initiative Status Bar Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Strategic Initiatives Status
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={[
                    { status: 'On Track', count: dashboard?.strategic_initiatives?.on_track || 0 },
                    { status: 'At Risk', count: dashboard?.strategic_initiatives?.at_risk || 0 },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="status" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" name="Initiatives">
                    <Cell fill="#4CAF50" />
                    <Cell fill="#FF9800" />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default StrategyDashboard
