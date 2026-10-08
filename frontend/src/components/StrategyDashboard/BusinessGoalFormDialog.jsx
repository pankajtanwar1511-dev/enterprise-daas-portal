import React, { useState, useEffect } from 'react'
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, MenuItem, Grid, FormControl, InputLabel,
  Select, Alert, CircularProgress,
} from '@mui/material'
import axiosInstance from '../../utils/axiosInstance'

const STATUS_OPTIONS = [
  { value: 'Active', label: 'Active' },
  { value: 'Completed', label: 'Completed' },
  { value: 'Deferred', label: 'Deferred' },
  { value: 'Cancelled', label: 'Cancelled' },
]

const PRIORITY_OPTIONS = [
  { value: 'High', label: 'High' },
  { value: 'Medium', label: 'Medium' },
  { value: 'Low', label: 'Low' },
]

function BusinessGoalFormDialog({ open, onClose, goal, onSave }) {
  const [formData, setFormData] = useState({
    goal_name: '',
    description: '',
    owner_id: 1, // Default to admin user
    target_date: '',
    status: 'Active',
    kpi_metric: '',
    current_value: 0,
    target_value: 0,
    priority: 'Medium',
    success_criteria: '',
    expected_roi: 0,
    investment_amount: 0,
    completion_percentage: 0,
  })

  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (open) {
      fetchUsers()
      if (goal) {
        // Edit mode - populate form with goal data
        setFormData({
          goal_name: goal.goal_name || '',
          description: goal.description || '',
          owner_id: goal.owner_id || 1,
          target_date: goal.target_date || '',
          status: goal.status || 'Active',
          kpi_metric: goal.kpi_metric || '',
          current_value: goal.current_value || 0,
          target_value: goal.target_value || 0,
          priority: goal.priority || 'Medium',
          success_criteria: goal.success_criteria || '',
          expected_roi: goal.expected_roi || 0,
          investment_amount: goal.investment_amount || 0,
          completion_percentage: goal.completion_percentage || 0,
        })
      } else {
        // Create mode - reset form
        setFormData({
          goal_name: '',
          description: '',
          owner_id: 1,
          target_date: '',
          status: 'Active',
          kpi_metric: '',
          current_value: 0,
          target_value: 0,
          priority: 'Medium',
          success_criteria: '',
          expected_roi: 0,
          investment_amount: 0,
          completion_percentage: 0,
        })
      }
    }
  }, [open, goal])

  const fetchUsers = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/users')
      setUsers(response.data.users || [])
    } catch (error) {
      console.error('Error fetching users:', error)
      setError('Failed to load users')
    }
  }

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value })
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)
      setError(null)

      // Validate required fields
      if (!formData.goal_name || !formData.description) {
        setError('Please fill in all required fields')
        setLoading(false)
        return
      }

      if (goal) {
        // Update existing goal
        await axiosInstance.put(`/api/v1/strategy/business-goals/${goal.goal_id}`, formData)
      } else {
        // Create new goal
        await axiosInstance.post('/api/v1/strategy/business-goals/', formData)
      }

      onSave()
      onClose()
    } catch (error) {
      console.error('Error saving business goal:', error)
      setError(error.response?.data?.detail || 'Failed to save business goal')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {goal ? 'Edit Business Goal' : 'New Business Goal'}
      </DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Goal Name */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              label="Goal Name"
              value={formData.goal_name}
              onChange={handleChange('goal_name')}
              helperText="Strategic business goal title"
            />
          </Grid>

          {/* Description */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              multiline
              rows={3}
              label="Description"
              value={formData.description}
              onChange={handleChange('description')}
              helperText="Detailed description of the business goal"
            />
          </Grid>

          {/* Owner */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Goal Owner</InputLabel>
              <Select
                value={formData.owner_id}
                onChange={handleChange('owner_id')}
                label="Goal Owner"
              >
                {users.map((user) => (
                  <MenuItem key={user.user_id} value={user.user_id}>
                    {user.first_name} {user.last_name} ({user.role})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Target Date */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="date"
              label="Target Date"
              value={formData.target_date}
              onChange={handleChange('target_date')}
              InputLabelProps={{ shrink: true }}
              helperText="Expected completion date"
            />
          </Grid>

          {/* Status */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                onChange={handleChange('status')}
                label="Status"
              >
                {STATUS_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Priority */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.priority}
                onChange={handleChange('priority')}
                label="Priority"
              >
                {PRIORITY_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* KPI Metric */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="KPI Metric"
              value={formData.kpi_metric}
              onChange={handleChange('kpi_metric')}
              placeholder="e.g., Reduce data access time by 50%"
              helperText="Key performance indicator to measure"
            />
          </Grid>

          {/* Current Value */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="Current Value"
              value={formData.current_value}
              onChange={handleChange('current_value')}
              inputProps={{ step: 0.01 }}
              helperText="Current KPI value"
            />
          </Grid>

          {/* Target Value */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="Target Value"
              value={formData.target_value}
              onChange={handleChange('target_value')}
              inputProps={{ step: 0.01 }}
              helperText="Target KPI value"
            />
          </Grid>

          {/* Completion Percentage */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="Completion %"
              value={formData.completion_percentage}
              onChange={handleChange('completion_percentage')}
              inputProps={{ min: 0, max: 100 }}
              helperText="0-100%"
            />
          </Grid>

          {/* Success Criteria */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Success Criteria"
              value={formData.success_criteria}
              onChange={handleChange('success_criteria')}
              helperText="Define what success looks like for this goal"
            />
          </Grid>

          {/* Investment Amount */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Investment Amount ($)"
              value={formData.investment_amount}
              onChange={handleChange('investment_amount')}
              inputProps={{ step: 1000 }}
              helperText="Budget allocated for this goal"
            />
          </Grid>

          {/* Expected ROI */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Expected ROI (%)"
              value={formData.expected_roi}
              onChange={handleChange('expected_roi')}
              inputProps={{ step: 0.1 }}
              helperText="Return on investment percentage"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {goal ? 'Update Goal' : 'Create Goal'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default BusinessGoalFormDialog
