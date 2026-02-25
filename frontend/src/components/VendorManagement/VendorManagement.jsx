import React, { useEffect, useState } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Paper,
  Chip,
  LinearProgress,
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import {
  Business,
  AttachMoney,
  CheckCircle,
  Warning,
  TrendingDown,
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

function VendorManagement() {
  const [dashboard, setDashboard] = useState(null)
  const [budgetData, setBudgetData] = useState(null)
  const [slaData, setSlaData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [dashRes, budgetRes, slaRes] = await Promise.all([
        axiosInstance.get('/api/v1/vendors/dashboard'),
        axiosInstance.get('/api/v1/vendors/budget-tracking'),
        axiosInstance.get('/api/v1/vendors/sla-tracking')
      ])
      setDashboard(dashRes.data)
      setBudgetData(budgetRes.data)
      setSlaData(slaRes.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching vendor data:', error)
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

  // Budget by Category table columns
  const budgetColumns = [
    {
      id: 'category',
      label: 'Category',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {value}
        </Typography>
      ),
    },
    {
      id: 'allocated',
      label: 'Allocated',
      sortable: true,
      render: (value) => `$${(value / 1000000).toFixed(2)}M`,
    },
    {
      id: 'spent',
      label: 'Spent',
      sortable: true,
      render: (value) => `$${(value / 1000000).toFixed(2)}M`,
    },
    {
      id: 'forecast',
      label: 'Forecast',
      sortable: true,
      render: (value) => `$${(value / 1000000).toFixed(2)}M`,
    },
    {
      id: 'variance',
      label: 'Variance',
      sortable: true,
      render: (value) => (
        <Typography
          variant="body2"
          sx={{
            color: value < 0 ? 'success.main' : 'error.main',
            fontWeight: 600,
          }}
        >
          ${Math.abs(value / 1000).toFixed(0)}K {value < 0 ? 'Under' : 'Over'}
        </Typography>
      ),
    },
  ]

  // Vendor SLA Performance table columns
  const slaColumns = [
    {
      id: 'vendor_name',
      label: 'Vendor',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {value}
        </Typography>
      ),
    },
    {
      id: 'metric',
      label: 'Metric',
      sortable: true,
    },
    {
      id: 'target',
      label: 'Target',
      sortable: true,
    },
    {
      id: 'current',
      label: 'Current',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          {value}
        </Typography>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          color={
            value === 'Met' ? 'success' : value === 'At Risk' ? 'warning' : 'error'
          }
          size="small"
        />
      ),
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Vendor & Budget Management
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Manage vendor relationships, SLAs, and budget allocation for DaaS initiatives
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" color="textSecondary">Total Vendors</Typography>
                  <Typography variant="h3" fontWeight="bold">{dashboard?.vendor_summary?.active_vendors || 0}</Typography>
                </Box>
                <Business sx={{ fontSize: 40, color: '#1976D2' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" color="textSecondary">Annual Cost</Typography>
                  <Typography variant="h3" fontWeight="bold">
                    ${(dashboard?.cost_management?.total_annual_cost / 1000000).toFixed(1)}M
                  </Typography>
                </Box>
                <AttachMoney sx={{ fontSize: 40, color: '#4CAF50' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" color="textSecondary">SLA Compliance</Typography>
                  <Typography variant="h3" fontWeight="bold">{slaData?.sla_summary?.compliance_rate || '0%'}</Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, color: '#4CAF50' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" color="textSecondary">Cost Savings</Typography>
                  <Typography variant="h3" fontWeight="bold" color="success.main">
                    {dashboard?.cost_management?.cost_trend || '0%'}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">YoY Reduction</Typography>
                </Box>
                <TrendingDown sx={{ fontSize: 40, color: '#4CAF50' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Budget Tracking */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Budget Tracking - FY 2026
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Box>
                <Typography variant="subtitle2" gutterBottom>Overall Budget Status</Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Total Allocated</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${(budgetData?.budget_overview?.total_allocated / 1000000).toFixed(1)}M
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Spent to Date</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    ${(budgetData?.budget_overview?.total_spent / 1000000).toFixed(1)}M
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2">Variance</Typography>
                  <Typography variant="body2" fontWeight="bold" color="success.main">
                    ${Math.abs(budgetData?.budget_overview?.variance / 1000000).toFixed(1)}M Under Budget
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={budgetData?.budget_overview?.utilization_rate || 0}
                  sx={{ height: 8, borderRadius: 4 }}
                  color="success"
                />
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  {budgetData?.budget_overview?.utilization_rate?.toFixed(1)}% Utilized
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>Cost Optimization Opportunities</Typography>
              <Paper sx={{ p: 2, backgroundColor: '#E8F5E9' }}>
                <Typography variant="h5" color="success.main" fontWeight="bold">
                  ${(budgetData?.cost_optimization?.potential_savings / 1000).toFixed(0)}K
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Potential Annual Savings Identified
                </Typography>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  {budgetData?.cost_optimization?.opportunities_identified} Opportunities
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Budget by Category */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Budget by Category
          </Typography>
          <Box sx={{ mt: 2 }}>
            <EnhancedTable
              columns={budgetColumns}
              data={budgetData?.by_category || []}
              loading={loading}
              onRefresh={fetchData}
              defaultOrderBy="category"
              defaultOrder="asc"
              searchPlaceholder="Search budget categories..."
              exportFileName="budget-by-category"
              rowsPerPageOptions={[5, 10, 25]}
              dense={true}
            />
          </Box>
        </CardContent>
      </Card>

      {/* SLA Performance */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Vendor SLA Performance
          </Typography>
          <Box sx={{ mt: 2 }}>
            <EnhancedTable
              columns={slaColumns}
              data={slaData?.critical_slas || []}
              loading={loading}
              onRefresh={fetchData}
              defaultOrderBy="vendor_name"
              defaultOrder="asc"
              searchPlaceholder="Search vendor SLAs..."
              exportFileName="vendor-sla-performance"
              rowsPerPageOptions={[5, 10, 25]}
              dense={true}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Cost Optimization Recommendations */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Cost Optimization Recommendations
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            {budgetData?.cost_optimization?.recommendations?.map((rec, index) => (
              <Paper key={index} sx={{ p: 2, backgroundColor: '#FFF9C4', display: 'flex', alignItems: 'center', gap: 2 }}>
                <AttachMoney sx={{ color: '#F57F17' }} />
                <Typography variant="body1">{rec}</Typography>
              </Paper>
            ))}
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
                Budget Distribution by Category
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={budgetData?.by_category?.map((cat) => ({
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
                    {(budgetData?.by_category || []).map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={['#2196F3', '#4CAF50', '#FF9800', '#9C27B0'][index % 4]}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `$${(value / 1000000).toFixed(2)}M`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* SLA Performance Bar Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                SLA Compliance Status
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={[
                    { status: 'Met', count: slaData?.sla_summary?.met || 0 },
                    { status: 'At Risk', count: slaData?.sla_summary?.at_risk || 0 },
                    { status: 'Breached', count: slaData?.sla_summary?.breached || 0 },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="status" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" name="SLAs">
                    <Cell fill="#4CAF50" />
                    <Cell fill="#FF9800" />
                    <Cell fill="#F44336" />
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

export default VendorManagement
