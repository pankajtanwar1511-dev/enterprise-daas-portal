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
import ValueMetricFormDialog from './ValueMetricFormDialog'
import BusinessGoalFormDialog from './BusinessGoalFormDialog'
import StrategicInitiativeFormDialog from './StrategicInitiativeFormDialog'
import {
  TrendingUp,
  AttachMoney,
  Assessment,
  Groups,
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
  const [businessGoals, setBusinessGoals] = useState([])
  const [strategicInitiatives, setStrategicInitiatives] = useState([])
  const [loading, setLoading] = useState(true)

  // Value Metrics form dialog state
  const [formDialogOpen, setFormDialogOpen] = useState(false)
  const [selectedMetric, setSelectedMetric] = useState(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [metricToDelete, setMetricToDelete] = useState(null)

  // Business Goals form dialog state
  const [goalFormDialogOpen, setGoalFormDialogOpen] = useState(false)
  const [selectedGoal, setSelectedGoal] = useState(null)
  const [goalDeleteDialogOpen, setGoalDeleteDialogOpen] = useState(false)
  const [goalToDelete, setGoalToDelete] = useState(null)

  // Strategic Initiatives form dialog state
  const [initiativeFormDialogOpen, setInitiativeFormDialogOpen] = useState(false)
  const [selectedInitiative, setSelectedInitiative] = useState(null)
  const [initiativeDeleteDialogOpen, setInitiativeDeleteDialogOpen] = useState(false)
  const [initiativeToDelete, setInitiativeToDelete] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [dashboardRes, valueRes, goalsRes, initiativesRes] = await Promise.all([
        axiosInstance.get('/api/v1/strategy/dashboard'),
        axiosInstance.get('/api/v1/strategy/value-delivered'),
        axiosInstance.get('/api/v1/strategy/business-goals'),
        axiosInstance.get('/api/v1/strategy/strategic-initiatives')
      ])
      setDashboard(dashboardRes.data)
      setValueMetrics(valueRes.data)
      setBusinessGoals(goalsRes.data.goals || [])
      setStrategicInitiatives(initiativesRes.data.initiatives || [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching strategy data:', error)
      setLoading(false)
    }
  }

  const handleAddMetric = () => {
    setSelectedMetric(null)
    setFormDialogOpen(true)
  }

  const handleEditMetric = (metric) => {
    setSelectedMetric(metric)
    setFormDialogOpen(true)
  }

  const handleDeleteClick = (metric) => {
    setMetricToDelete(metric)
    setDeleteDialogOpen(true)
  }

  const handleConfirmDelete = async () => {
    try {
      await axiosInstance.delete(`/api/v1/strategy/value-metrics/${metricToDelete.metric_id}`)
      setDeleteDialogOpen(false)
      setMetricToDelete(null)
      fetchData() // Refresh data
    } catch (error) {
      console.error('Error deleting metric:', error)
      alert('Failed to delete metric')
    }
  }

  const handleFormSave = () => {
    fetchData() // Refresh data after save
  }

  // Business Goals handlers
  const handleAddGoal = () => {
    setSelectedGoal(null)
    setGoalFormDialogOpen(true)
  }

  const handleEditGoal = (goal) => {
    setSelectedGoal(goal)
    setGoalFormDialogOpen(true)
  }

  const handleDeleteGoalClick = (goal) => {
    setGoalToDelete(goal)
    setGoalDeleteDialogOpen(true)
  }

  const handleConfirmDeleteGoal = async () => {
    try {
      await axiosInstance.delete(`/api/v1/strategy/business-goals/${goalToDelete.goal_id}`)
      setGoalDeleteDialogOpen(false)
      setGoalToDelete(null)
      fetchData() // Refresh data
    } catch (error) {
      console.error('Error deleting business goal:', error)
      alert('Failed to delete business goal')
    }
  }

  const handleGoalFormSave = () => {
    fetchData() // Refresh data after save
  }

  // Strategic Initiatives handlers
  const handleAddInitiative = () => {
    setSelectedInitiative(null)
    setInitiativeFormDialogOpen(true)
  }

  const handleEditInitiative = (initiative) => {
    setSelectedInitiative(initiative)
    setInitiativeFormDialogOpen(true)
  }

  const handleDeleteInitiativeClick = (initiative) => {
    setInitiativeToDelete(initiative)
    setInitiativeDeleteDialogOpen(true)
  }

  const handleConfirmDeleteInitiative = async () => {
    try {
      await axiosInstance.delete(`/api/v1/strategy/strategic-initiatives/${initiativeToDelete.initiative_id}`)
      setInitiativeDeleteDialogOpen(false)
      setInitiativeToDelete(null)
      fetchData() // Refresh data
    } catch (error) {
      console.error('Error deleting strategic initiative:', error)
      alert('Failed to delete strategic initiative')
    }
  }

  const handleInitiativeFormSave = () => {
    fetchData() // Refresh data after save
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  // Define columns for strategic initiatives table
  const strategicInitiativesColumns = [
    {
      id: 'initiative_name',
      label: 'Initiative Name',
      sortable: true,
      render: (value) => (
        <Typography variant="body1" fontWeight="500">
          {value}
        </Typography>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      sortable: true,
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={
            value === 'Completed' ? 'success' :
            value === 'In Progress' ? 'primary' :
            value === 'At Risk' ? 'error' :
            value === 'On Hold' ? 'warning' :
            'default'
          }
        />
      ),
    },
    {
      id: 'completion_percentage',
      label: 'Progress',
      sortable: true,
      render: (value) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LinearProgress
            variant="determinate"
            value={value || 0}
            sx={{ width: 100, height: 8, borderRadius: 4 }}
          />
          <Typography variant="body2">{value || 0}%</Typography>
        </Box>
      ),
    },
    {
      id: 'budget_allocated',
      label: 'Budget',
      sortable: true,
      render: (value, row) => (
        <Box>
          <Typography variant="body2" fontWeight="500">
            ${((value || 0) / 1000).toFixed(0)}K
          </Typography>
          <Typography variant="caption" color="textSecondary">
            Spent: ${((row.budget_spent || 0) / 1000).toFixed(0)}K
          </Typography>
        </Box>
      ),
    },
    {
      id: 'target_date',
      label: 'Target Date',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString() : 'N/A',
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      render: (value, row) => (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Edit">
            <IconButton size="small" color="primary" onClick={() => handleEditInitiative(row)}>
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" color="error" onClick={() => handleDeleteInitiativeClick(row)}>
              <Delete fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ]

  // Define columns for business goals table
  const businessGoalsColumns = [
    {
      id: 'goal_name',
      label: 'Goal Name',
      sortable: true,
      render: (value) => (
        <Typography variant="body1" fontWeight="500">
          {value}
        </Typography>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      sortable: true,
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={value === 'Active' ? 'success' : value === 'Completed' ? 'primary' : 'default'}
        />
      ),
    },
    {
      id: 'priority',
      label: 'Priority',
      sortable: true,
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={value === 'High' ? 'error' : value === 'Medium' ? 'warning' : 'default'}
        />
      ),
    },
    {
      id: 'completion_percentage',
      label: 'Progress',
      sortable: true,
      render: (value) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LinearProgress
            variant="determinate"
            value={value || 0}
            sx={{ width: 100, height: 8, borderRadius: 4 }}
          />
          <Typography variant="body2">{value || 0}%</Typography>
        </Box>
      ),
    },
    {
      id: 'target_date',
      label: 'Target Date',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString() : 'N/A',
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      render: (value, row) => (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Edit">
            <IconButton size="small" color="primary" onClick={() => handleEditGoal(row)}>
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" color="error" onClick={() => handleDeleteGoalClick(row)}>
              <Delete fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ]

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
      width: '40%',
      render: (value) => (
        <Typography variant="body2" color="textSecondary">
          {value}
        </Typography>
      ),
    },
    {
      id: 'status',
      label: 'Status',
      sortable: true,
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={value === 'Published' ? 'success' : value === 'Approved' ? 'primary' : 'default'}
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
            <IconButton size="small" color="primary" onClick={() => handleEditMetric(row)}>
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" color="error" onClick={() => handleDeleteClick(row)}>
              <Delete fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
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
            value={`${dashboard?.strategic_initiatives?.on_track || 0} of ${dashboard?.strategic_initiatives?.total || 0}`}
            subtitle="on track"
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
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">
              Value Delivered Across Domains
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddMetric}
            >
              Add New Metric
            </Button>
          </Box>
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

      {/* Business Goals */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">
              Strategic Business Goals
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddGoal}
            >
              Add New Goal
            </Button>
          </Box>
          <EnhancedTable
            columns={businessGoalsColumns}
            data={businessGoals}
            loading={false}
            onRefresh={fetchData}
            defaultOrderBy="goal_name"
            defaultOrder="asc"
            searchPlaceholder="Search goals..."
            exportFileName="business_goals"
            rowsPerPageOptions={[10, 25, 50]}
          />
        </CardContent>
      </Card>

      {/* Business Goal Form Dialog */}
      <BusinessGoalFormDialog
        open={goalFormDialogOpen}
        onClose={() => {
          setGoalFormDialogOpen(false)
          setSelectedGoal(null)
        }}
        goal={selectedGoal}
        onSave={handleGoalFormSave}
      />

      {/* Business Goal Delete Confirmation Dialog */}
      <Dialog open={goalDeleteDialogOpen} onClose={() => setGoalDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this business goal?
            <br />
            <br />
            <strong>{goalToDelete?.goal_name}</strong>
            <br />
            {goalToDelete?.description}
            <br /><br />
            This action cannot be undone. All associated strategic initiatives will be unlinked.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGoalDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmDeleteGoal} color="error" variant="contained">
            Delete Goal
          </Button>
        </DialogActions>
      </Dialog>

      {/* Strategic Initiatives */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">
              Strategic Initiatives
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddInitiative}
            >
              Add New Initiative
            </Button>
          </Box>
          <EnhancedTable
            columns={strategicInitiativesColumns}
            data={strategicInitiatives}
            loading={false}
            onRefresh={fetchData}
            defaultOrderBy="initiative_name"
            defaultOrder="asc"
            searchPlaceholder="Search initiatives..."
            exportFileName="strategic_initiatives"
            rowsPerPageOptions={[10, 25, 50]}
          />
        </CardContent>
      </Card>

      {/* Strategic Initiative Form Dialog */}
      <StrategicInitiativeFormDialog
        open={initiativeFormDialogOpen}
        onClose={() => {
          setInitiativeFormDialogOpen(false)
          setSelectedInitiative(null)
        }}
        initiative={selectedInitiative}
        onSave={handleInitiativeFormSave}
      />

      {/* Strategic Initiative Delete Confirmation Dialog */}
      <Dialog open={initiativeDeleteDialogOpen} onClose={() => setInitiativeDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this strategic initiative?
            <br />
            <br />
            <strong>{initiativeToDelete?.initiative_name}</strong>
            <br />
            {initiativeToDelete?.description}
            <br /><br />
            This action cannot be undone. All associated deliverables will also be deleted.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInitiativeDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmDeleteInitiative} color="error" variant="contained">
            Delete Initiative
          </Button>
        </DialogActions>
      </Dialog>

      {/* Value Metric Form Dialog */}
      <ValueMetricFormDialog
        open={formDialogOpen}
        onClose={() => setFormDialogOpen(false)}
        metric={selectedMetric}
        onSave={handleFormSave}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this value delivered metric?
            <br />
            <br />
            <strong>{metricToDelete?.value_delivered}</strong>
            <br />
            {metricToDelete?.key_achievement}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

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
                  <RechartsTooltip
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
                  <RechartsTooltip />
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
