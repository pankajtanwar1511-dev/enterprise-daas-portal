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
  Button,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import VendorFormDialog from './VendorFormDialog'
import {
  Business,
  AttachMoney,
  CheckCircle,
  Warning,
  TrendingDown,
  Add,
  Edit,
  Delete,
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
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

function VendorManagement() {
  const [dashboard, setDashboard] = useState(null)
  const [budgetData, setBudgetData] = useState(null)
  const [slaData, setSlaData] = useState(null)
  const [vendors, setVendors] = useState([])
  const [loading, setLoading] = useState(true)

  // Form dialog state
  const [formDialogOpen, setFormDialogOpen] = useState(false)
  const [selectedVendor, setSelectedVendor] = useState(null)

  // Delete confirmation state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [vendorToDelete, setVendorToDelete] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [dashRes, budgetRes, slaRes, vendorsRes] = await Promise.all([
        axiosInstance.get('/api/v1/vendors/dashboard'),
        axiosInstance.get('/api/v1/vendors/budget-tracking'),
        axiosInstance.get('/api/v1/vendors/sla-tracking'),
        axiosInstance.get('/api/v1/vendors/')
      ])
      setDashboard(dashRes.data)
      setBudgetData(budgetRes.data)
      setSlaData(slaRes.data)
      setVendors(vendorsRes.data || [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching vendor data:', error)
      setLoading(false)
    }
  }

  const handleAddVendor = () => {
    setSelectedVendor(null)
    setFormDialogOpen(true)
  }

  const handleEditVendor = (vendor) => {
    setSelectedVendor(vendor)
    setFormDialogOpen(true)
  }

  const handleDeleteClick = (vendor) => {
    setVendorToDelete(vendor)
    setDeleteDialogOpen(true)
  }

  const handleConfirmDelete = async () => {
    try {
      await axiosInstance.delete(`/api/v1/vendors/${vendorToDelete.vendor_id}`)
      setDeleteDialogOpen(false)
      setVendorToDelete(null)
      fetchData() // Refresh data
    } catch (error) {
      console.error('Error deleting vendor:', error)
      alert('Failed to delete vendor')
    }
  }

  const handleFormSave = () => {
    fetchData() // Refresh data after save
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

      {/* Vendor List with CRUD */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">
              Vendor Directory
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddVendor}
            >
              Add New Vendor
            </Button>
          </Box>
          <EnhancedTable
            columns={[
              {
                id: 'vendor_name',
                label: 'Vendor Name',
                sortable: true,
                render: (value) => (
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {value}
                  </Typography>
                ),
              },
              {
                id: 'vendor_type',
                label: 'Type',
                sortable: true,
              },
              {
                id: 'status',
                label: 'Status',
                sortable: true,
                render: (value) => (
                  <Chip
                    label={value}
                    size="small"
                    color={value === 'Active' ? 'success' : 'default'}
                  />
                ),
              },
              {
                id: 'annual_spend',
                label: 'Annual Cost',
                sortable: true,
                render: (value) => value ? `$${(value / 1000000).toFixed(2)}M` : 'N/A',
              },
              {
                id: 'contact_person',
                label: 'Contact',
                sortable: true,
                render: (value, row) => (
                  <Box>
                    <Typography variant="body2">{value || 'N/A'}</Typography>
                    {row.contact_email && (
                      <Typography variant="caption" color="textSecondary">
                        {row.contact_email}
                      </Typography>
                    )}
                  </Box>
                ),
              },
              {
                id: 'performance_rating',
                label: 'Rating',
                sortable: true,
                align: 'center',
                render: (value) => (
                  <Chip
                    label={value ? `${value}/5` : 'N/A'}
                    size="small"
                    color={value >= 4 ? 'success' : value >= 3 ? 'warning' : 'error'}
                  />
                ),
              },
              {
                id: 'actions',
                label: 'Actions',
                sortable: false,
                render: (value, row) => (
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleEditVendor(row)}
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(row)}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                ),
              },
            ]}
            data={vendors}
            loading={false}
            onRefresh={fetchData}
            defaultOrderBy="vendor_name"
            defaultOrder="asc"
            searchPlaceholder="Search vendors..."
            exportFileName="vendors_list"
            rowsPerPageOptions={[10, 25, 50]}
          />
        </CardContent>
      </Card>

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
                  <RechartsTooltip formatter={(value) => `$${(value / 1000000).toFixed(2)}M`} />
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
                  <RechartsTooltip />
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

      {/* Vendor Form Dialog */}
      <VendorFormDialog
        open={formDialogOpen}
        onClose={() => setFormDialogOpen(false)}
        vendor={selectedVendor}
        onSave={handleFormSave}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this vendor?
            <br />
            <br />
            <strong>{vendorToDelete?.vendor_name}</strong>
            <br />
            Type: {vendorToDelete?.vendor_type}
            <br />
            <br />
            This action cannot be undone. All associated SLAs will also be deleted.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Delete Vendor
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default VendorManagement
