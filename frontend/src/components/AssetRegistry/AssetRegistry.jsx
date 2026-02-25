import React, { useEffect, useState, useMemo } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Chip,
  CircularProgress,
  TextField,
  MenuItem,
  Grid,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar,
  Tooltip,
  Paper,
  Card,
  CardContent,
} from '@mui/material'
import {
  CheckCircle,
  Error,
  Add,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Storage as StorageIcon,
  TrendingUp as TrendingUpIcon,
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'
import EnhancedTable from '../common/EnhancedTable'
import AssetDialog from './AssetDialog'
import AssetDetailDialog from './AssetDetailDialog'

function AssetRegistry() {
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [filterEnv, setFilterEnv] = useState('')
  const [filterLifecycle, setFilterLifecycle] = useState('')
  const [filterCompliant, setFilterCompliant] = useState('')

  // Dialog states
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [assetToDelete, setAssetToDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [assetForDetail, setAssetForDetail] = useState(null)

  // Snackbar state
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' })

  useEffect(() => {
    fetchAssets()
  }, [filterEnv, filterLifecycle, filterCompliant])

  const fetchAssets = async () => {
    setLoading(true)
    try {
      let url = `/api/v1/assets/?limit=1000`
      if (filterEnv) url += `&environment=${filterEnv}`
      if (filterLifecycle) url += `&lifecycle_stage=${filterLifecycle}`
      if (filterCompliant !== '') url += `&compliant=${filterCompliant}`

      const response = await axiosInstance.get(url)
      setAssets(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching assets:', error)
      showSnackbar('Error fetching assets', 'error')
      setLoading(false)
    }
  }

  const handleCreateAsset = () => {
    setSelectedAsset(null)
    setDialogOpen(true)
  }

  const handleEditAsset = (asset) => {
    setSelectedAsset(asset)
    setDialogOpen(true)
  }

  const handleDeleteAsset = (asset) => {
    setAssetToDelete(asset)
    setDeleteDialogOpen(true)
  }

  const handleViewDetails = (asset) => {
    setAssetForDetail(asset)
    setDetailDialogOpen(true)
  }

  const confirmDelete = async () => {
    if (!assetToDelete) return

    setDeleting(true)
    try {
      await axiosInstance.delete(`/api/v1/assets/${assetToDelete.asset_id}`)
      showSnackbar('Asset deleted successfully', 'success')
      setDeleteDialogOpen(false)
      setAssetToDelete(null)
      fetchAssets() // Refresh the list
    } catch (error) {
      console.error('Error deleting asset:', error)
      showSnackbar(error.response?.data?.detail || 'Error deleting asset', 'error')
    } finally {
      setDeleting(false)
    }
  }

  const handleDialogSuccess = () => {
    showSnackbar(
      selectedAsset ? 'Asset updated successfully' : 'Asset created successfully',
      'success'
    )
    fetchAssets() // Refresh the list
  }

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity })
  }

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false })
  }

  const getLifecycleColor = (stage) => {
    switch (stage) {
      case 'Active':
        return 'success'
      case 'Draft':
        return 'warning'
      case 'Deprecated':
        return 'error'
      case 'Retired':
        return 'default'
      default:
        return 'default'
    }
  }

  const getEnvironmentColor = (env) => {
    switch (env) {
      case 'PROD':
        return 'error'
      case 'QA':
        return 'warning'
      case 'DEV':
        return 'info'
      case 'UAT':
        return 'secondary'
      default:
        return 'default'
    }
  }

  // Chart data calculations
  const chartData = useMemo(() => {
    if (!assets.length) return null

    // Environment distribution
    const envCounts = assets.reduce((acc, asset) => {
      acc[asset.environment] = (acc[asset.environment] || 0) + 1
      return acc
    }, {})
    const envData = Object.entries(envCounts).map(([name, value]) => ({ name, value }))

    // Lifecycle distribution
    const lifecycleCounts = assets.reduce((acc, asset) => {
      acc[asset.lifecycle_stage] = (acc[asset.lifecycle_stage] || 0) + 1
      return acc
    }, {})
    const lifecycleData = Object.entries(lifecycleCounts).map(([name, value]) => ({ name, value }))

    // Compliance status
    const compliantCount = assets.filter(a => a.naming_compliant).length
    const nonCompliantCount = assets.length - compliantCount
    const complianceData = [
      { name: 'Compliant', value: compliantCount },
      { name: 'Non-Compliant', value: nonCompliantCount },
    ]

    // Domain distribution (extract from asset_name)
    const domainCounts = assets.reduce((acc, asset) => {
      const parts = asset.asset_name?.split('-')
      const domain = parts && parts.length > 1 ? parts[1] : 'Unknown'
      acc[domain] = (acc[domain] || 0) + 1
      return acc
    }, {})
    const domainData = Object.entries(domainCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6) // Top 6 domains

    return { envData, lifecycleData, complianceData, domainData }
  }, [assets])

  const COLORS = {
    env: ['#f44336', '#ff9800', '#2196f3', '#9c27b0'],
    lifecycle: ['#4caf50', '#ff9800', '#f44336', '#757575'],
    compliance: ['#4caf50', '#f44336'],
    domain: ['#1976d2', '#388e3c', '#f57c00', '#7b1fa2', '#c2185b', '#0288d1'],
  }

  // Define table columns
  const columns = [
    {
      id: 'asset_name',
      label: 'Asset Name',
      sortable: true,
      render: (value) => (
        <Typography sx={{ fontFamily: 'monospace', fontSize: '0.95rem' }}>
          {value}
        </Typography>
      ),
    },
    {
      id: 'environment',
      label: 'Environment',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          color={getEnvironmentColor(value)}
          size="small"
        />
      ),
    },
    {
      id: 'lifecycle_stage',
      label: 'Lifecycle',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          color={getLifecycleColor(value)}
          size="small"
        />
      ),
    },
    {
      id: 'version',
      label: 'Version',
      sortable: true,
      align: 'center',
    },
    {
      id: 'naming_compliant',
      label: 'Compliance',
      sortable: true,
      align: 'center',
      render: (value) =>
        value ? (
          <Chip
            icon={<CheckCircle />}
            label="Compliant"
            color="success"
            size="small"
            variant="outlined"
          />
        ) : (
          <Chip
            icon={<Error />}
            label="Non-Compliant"
            color="error"
            size="small"
            variant="outlined"
          />
        ),
    },
    {
      id: 'created_at',
      label: 'Created',
      sortable: true,
      render: (value) => new Date(value).toLocaleDateString(),
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      align: 'right',
      render: (value, row) => (
        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
          <Tooltip title="View Details">
            <IconButton
              size="small"
              onClick={() => handleViewDetails(row)}
              color="info"
            >
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Edit Asset">
            <IconButton
              size="small"
              onClick={() => handleEditAsset(row)}
              color="primary"
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete Asset">
            <IconButton
              size="small"
              onClick={() => handleDeleteAsset(row)}
              color="error"
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Asset Registry
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreateAsset}
          sx={{ textTransform: 'none' }}
        >
          Register New Asset
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <TextField
              select
              fullWidth
              label="Environment"
              value={filterEnv}
              onChange={(e) => setFilterEnv(e.target.value)}
              size="small"
            >
              <MenuItem value="">All Environments</MenuItem>
              <MenuItem value="DEV">DEV</MenuItem>
              <MenuItem value="QA">QA</MenuItem>
              <MenuItem value="UAT">UAT</MenuItem>
              <MenuItem value="PROD">PROD</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={4}>
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
          <Grid item xs={12} sm={4}>
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
        </Grid>
      </Paper>

      {/* Asset Analytics Charts */}
      {!loading && chartData && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Summary Stats */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <StorageIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Total Assets
                    </Typography>
                    <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                      {assets.length}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <CheckCircle sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Compliance Rate
                    </Typography>
                    <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                      {((chartData.complianceData[0]?.value / assets.length) * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TrendingUpIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Active Assets
                    </Typography>
                    <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                      {assets.filter(a => a.lifecycle_stage === 'Active').length}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <StorageIcon sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.9 }}>
                      Environments
                    </Typography>
                    <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                      {chartData.envData.length}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Environment Distribution - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <StorageIcon color="primary" />
                  Assets by Environment
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartData.envData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) =>
                        `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={100}
                      
                      dataKey="value"
                    >
                      {chartData.envData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.env[index % COLORS.env.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Lifecycle Distribution - Bar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUpIcon color="primary" />
                  Lifecycle Stage Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.lifecycleData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Assets" radius={[8, 8, 0, 0]}>
                      {chartData.lifecycleData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.lifecycle[index % COLORS.lifecycle.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Domain Distribution - Bar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <StorageIcon color="secondary" />
                  Top Domains by Asset Count
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.domainData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={80} />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Assets" radius={[0, 8, 8, 0]}>
                      {chartData.domainData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.domain[index % COLORS.domain.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Compliance Status - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle color="success" />
                  Naming Convention Compliance
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartData.complianceData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) =>
                        `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={100}
                      
                      dataKey="value"
                    >
                      {chartData.complianceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.compliance[index]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Enhanced Assets Table */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <EnhancedTable
          columns={columns}
          data={assets}
          loading={loading}
          onRefresh={fetchAssets}
          defaultOrderBy="created_at"
          defaultOrder="desc"
          searchPlaceholder="Search assets by name, environment, version..."
          exportFileName="assets"
          rowsPerPageOptions={[10, 25, 50, 100]}
        />
      )}

      {/* Create/Edit Dialog */}
      <AssetDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        asset={selectedAsset}
        onSuccess={handleDialogSuccess}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the asset:{' '}
            <strong>{assetToDelete?.asset_name}</strong>?
          </Typography>
          <Typography color="error" sx={{ mt: 2 }}>
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={deleting}>
            Cancel
          </Button>
          <Button onClick={confirmDelete} color="error" variant="contained" disabled={deleting}>
            {deleting ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Asset Detail Dialog */}
      <AssetDetailDialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        asset={assetForDetail}
      />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default AssetRegistry
