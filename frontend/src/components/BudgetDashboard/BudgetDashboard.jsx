import React, { useEffect, useState } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  LinearProgress,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import { AttachMoney, TrendingDown, TrendingUp, AccountBalance } from '@mui/icons-material'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
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

function BudgetDashboard() {
  const [summary, setSummary] = useState(null)
  const [allocations, setAllocations] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedYear, setSelectedYear] = useState('all')

  useEffect(() => {
    fetchData()
  }, [selectedYear])

  const fetchData = async () => {
    try {
      const params = selectedYear !== 'all' ? { fiscal_year: selectedYear } : {}

      const [summaryRes, allocationsRes] = await Promise.all([
        axiosInstance.get('/api/v1/budget/summary', { params }),
        axiosInstance.get('/api/v1/budget/allocations', { params }),
      ])

      setSummary(summaryRes.data)
      setAllocations(allocationsRes.data || [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching budget data:', error)
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

  const columns = [
    {
      id: 'fiscal_year',
      label: 'Fiscal Year',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" fontWeight="600">
          FY {value}
        </Typography>
      ),
    },
    {
      id: 'category',
      label: 'Category',
      sortable: true,
      render: (value) => (
        <Typography variant="body2">
          {value}
        </Typography>
      ),
    },
    {
      id: 'domain_id',
      label: 'Domain ID',
      sortable: true,
      align: 'center',
    },
    {
      id: 'allocated_amount',
      label: 'Allocated',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" fontWeight="600">
          ${(value / 1000).toFixed(0)}K
        </Typography>
      ),
    },
    {
      id: 'spent_amount',
      label: 'Spent',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" color="primary">
          ${(value / 1000).toFixed(0)}K
        </Typography>
      ),
    },
    {
      id: 'forecasted_spend',
      label: 'Forecasted',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" color="textSecondary">
          ${(value / 1000).toFixed(0)}K
        </Typography>
      ),
    },
    {
      id: 'variance',
      label: 'Variance',
      sortable: true,
      render: (value) => (
        <Typography
          variant="body2"
          sx={{
            color: value > 0 ? 'success.main' : 'error.main',
            fontWeight: 600,
          }}
        >
          ${Math.abs(value / 1000).toFixed(0)}K {value > 0 ? '↓' : '↑'}
        </Typography>
      ),
    },
    {
      id: 'utilization_pct',
      label: 'Utilization',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1 }}>
          <LinearProgress
            variant="determinate"
            value={value}
            sx={{
              width: 60,
              height: 6,
              borderRadius: 3,
              backgroundColor: '#E0E0E0',
              '& .MuiLinearProgress-bar': {
                backgroundColor: value > 90 ? '#F44336' : value > 70 ? '#FF9800' : '#4CAF50'
              }
            }}
          />
          <Typography variant="caption" fontWeight="600">
            {value.toFixed(0)}%
          </Typography>
        </Box>
      ),
    },
  ]

  const COLORS = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336', '#00BCD4']

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Budget Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Track budget allocations, spending, and financial performance across domains
          </Typography>
        </Box>
        <FormControl sx={{ minWidth: 150 }}>
          <InputLabel>Fiscal Year</InputLabel>
          <Select
            value={selectedYear}
            label="Fiscal Year"
            onChange={(e) => setSelectedYear(e.target.value)}
          >
            <MenuItem value="all">All Years</MenuItem>
            <MenuItem value="2026">FY 2026</MenuItem>
            <MenuItem value="2025">FY 2025</MenuItem>
            <MenuItem value="2024">FY 2024</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Allocated"
            value={`$${(summary?.total_allocated / 1000000 || 0).toFixed(1)}M`}
            subtitle={`${summary?.record_count || 0} allocations`}
            icon={<AccountBalance sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Spent"
            value={`$${(summary?.total_spent / 1000000 || 0).toFixed(1)}M`}
            subtitle={`${summary?.utilization_pct?.toFixed(1) || 0}% utilized`}
            icon={<AttachMoney sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Forecasted Spend"
            value={`$${(summary?.total_forecasted / 1000000 || 0).toFixed(1)}M`}
            subtitle="End of year projection"
            icon={<TrendingUp sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Variance"
            value={`$${(Math.abs(summary?.overall_variance) / 1000000 || 0).toFixed(1)}M`}
            subtitle={summary?.overall_variance > 0 ? 'Under budget' : 'Over budget'}
            icon={<TrendingDown sx={{ fontSize: 40 }} />}
            color={summary?.overall_variance > 0 ? 'success' : 'error'}
          />
        </Grid>
      </Grid>

      {/* Budget Overview */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Budget Overview - {summary?.fiscal_year}
          </Typography>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Total Allocated</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${(summary?.total_allocated / 1000000 || 0).toFixed(2)}M
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Spent to Date</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${(summary?.total_spent / 1000000 || 0).toFixed(2)}M
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2">Remaining</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    ${(summary?.overall_variance / 1000000 || 0).toFixed(2)}M
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={summary?.utilization_pct || 0}
                  sx={{ height: 8, borderRadius: 4 }}
                  color={summary?.utilization_pct > 90 ? 'error' : summary?.utilization_pct > 70 ? 'warning' : 'success'}
                />
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  {summary?.utilization_pct?.toFixed(1) || 0}% Utilized
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, backgroundColor: '#E8F5E9' }}>
                <Typography variant="h5" color="success.main" fontWeight="bold">
                  ${(summary?.overall_variance / 1000000 || 0).toFixed(2)}M
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Remaining Budget
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  {summary?.by_category?.length || 0} categories tracked
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Budget Allocations Table */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Budget Allocations
          </Typography>
          <Box sx={{ mt: 2 }}>
            <EnhancedTable
              columns={columns}
              data={allocations}
              loading={false}
              onRefresh={fetchData}
              defaultOrderBy="fiscal_year"
              defaultOrder="desc"
              searchPlaceholder="Search allocations..."
              exportFileName="budget_allocations"
              rowsPerPageOptions={[10, 25, 50, 100]}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Visualizations */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        {/* Budget by Category Pie Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Budget by Category
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={summary?.by_category?.map((cat) => ({
                      name: cat.category,
                      value: cat.allocated,
                    })) || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value, percent }) =>
                      `${name}: $${(value / 1000000).toFixed(1)}M (${(percent * 100).toFixed(0)}%)`
                    }
                    outerRadius={80}
                    dataKey="value"
                  >
                    {(summary?.by_category || []).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip formatter={(value) => `$${(value / 1000000).toFixed(2)}M`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Budget by Domain Bar Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Budget by Domain
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={summary?.by_domain || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="domain_name" angle={-45} textAnchor="end" height={100} />
                  <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                  <RechartsTooltip formatter={(value) => `$${(value / 1000000).toFixed(2)}M`} />
                  <Legend />
                  <Bar dataKey="allocated" name="Allocated" fill="#2196F3" />
                  <Bar dataKey="spent" name="Spent" fill="#4CAF50" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Category Breakdown */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Budget Breakdown by Category
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {summary?.by_category?.map((cat, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Paper sx={{ p: 2, border: `2px solid ${COLORS[index % COLORS.length]}` }}>
                  <Typography variant="h6" color={COLORS[index % COLORS.length]} fontWeight="bold">
                    {cat.category}
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Allocated:</Typography>
                      <Typography variant="body2" fontWeight="600">
                        ${(cat.allocated / 1000000).toFixed(2)}M
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Spent:</Typography>
                      <Typography variant="body2" fontWeight="600" color="primary">
                        ${(cat.spent / 1000000).toFixed(2)}M
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="body2">Forecasted:</Typography>
                      <Typography variant="body2" fontWeight="600" color="textSecondary">
                        ${(cat.forecasted / 1000000).toFixed(2)}M
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(cat.spent / cat.allocated) * 100}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        backgroundColor: '#E0E0E0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: COLORS[index % COLORS.length]
                        }
                      }}
                    />
                    <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
                      {((cat.spent / cat.allocated) * 100).toFixed(1)}% Utilized
                    </Typography>
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}

export default BudgetDashboard
