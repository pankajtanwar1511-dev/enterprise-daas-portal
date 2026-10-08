import React, { useState, useEffect } from 'react'
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, MenuItem, Grid, FormControl, InputLabel,
  Select, Alert, CircularProgress,
} from '@mui/material'
import axiosInstance from '../../utils/axiosInstance'

const STATUS_OPTIONS = [
  { value: 'Planning', label: 'Planning' },
  { value: 'In Progress', label: 'In Progress' },
  { value: 'Completed', label: 'Completed' },
  { value: 'On Hold', label: 'On Hold' },
  { value: 'At Risk', label: 'At Risk' },
]

function StrategicInitiativeFormDialog({ open, onClose, initiative, onSave }) {
  const [formData, setFormData] = useState({
    initiative_name: '',
    description: '',
    business_goal_id: '',
    initiative_lead_id: 1, // Default to admin user
    budget_allocated: 0,
    budget_spent: 0,
    start_date: '',
    target_date: '',
    status: 'Planning',
    expected_roi: 0,
    stakeholder_count: 0,
    completion_percentage: 0,
  })

  const [users, setUsers] = useState([])
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (open) {
      fetchDropdownData()
      if (initiative) {
        // Edit mode - populate form with initiative data
        setFormData({
          initiative_name: initiative.initiative_name || '',
          description: initiative.description || '',
          business_goal_id: initiative.business_goal_id || '',
          initiative_lead_id: initiative.initiative_lead_id || 1,
          budget_allocated: initiative.budget_allocated || 0,
          budget_spent: initiative.budget_spent || 0,
          start_date: initiative.start_date || '',
          target_date: initiative.target_date || '',
          status: initiative.status || 'Planning',
          expected_roi: initiative.expected_roi || 0,
          stakeholder_count: initiative.stakeholder_count || 0,
          completion_percentage: initiative.completion_percentage || 0,
        })
      } else {
        // Create mode - reset form
        setFormData({
          initiative_name: '',
          description: '',
          business_goal_id: '',
          initiative_lead_id: 1,
          budget_allocated: 0,
          budget_spent: 0,
          start_date: '',
          target_date: '',
          status: 'Planning',
          expected_roi: 0,
          stakeholder_count: 0,
          completion_percentage: 0,
        })
      }
    }
  }, [open, initiative])

  const fetchDropdownData = async () => {
    try {
      const [usersRes, goalsRes] = await Promise.all([
        axiosInstance.get('/api/v1/users'),
        axiosInstance.get('/api/v1/strategy/business-goals')
      ])
      setUsers(usersRes.data.users || [])
      setGoals(goalsRes.data.goals || [])
    } catch (error) {
      console.error('Error fetching dropdown data:', error)
      setError('Failed to load form options')
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
      if (!formData.initiative_name || !formData.description) {
        setError('Please fill in all required fields')
        setLoading(false)
        return
      }

      if (initiative) {
        // Update existing initiative
        await axiosInstance.put(`/api/v1/strategy/strategic-initiatives/${initiative.initiative_id}`, formData)
      } else {
        // Create new initiative
        await axiosInstance.post('/api/v1/strategy/strategic-initiatives/', formData)
      }

      onSave()
      onClose()
    } catch (error) {
      console.error('Error saving strategic initiative:', error)
      setError(error.response?.data?.detail || 'Failed to save strategic initiative')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {initiative ? 'Edit Strategic Initiative' : 'New Strategic Initiative'}
      </DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Initiative Name */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              label="Initiative Name"
              value={formData.initiative_name}
              onChange={handleChange('initiative_name')}
              helperText="Strategic DaaS project or program name"
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
              helperText="Detailed description of the initiative"
            />
          </Grid>

          {/* Business Goal */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Business Goal</InputLabel>
              <Select
                value={formData.business_goal_id}
                onChange={handleChange('business_goal_id')}
                label="Business Goal"
              >
                <MenuItem value="">None</MenuItem>
                {goals.map((goal) => (
                  <MenuItem key={goal.goal_id} value={goal.goal_id}>
                    {goal.goal_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Initiative Lead */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Initiative Lead</InputLabel>
              <Select
                value={formData.initiative_lead_id}
                onChange={handleChange('initiative_lead_id')}
                label="Initiative Lead"
              >
                {users.map((user) => (
                  <MenuItem key={user.user_id} value={user.user_id}>
                    {user.first_name} {user.last_name} ({user.role})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Start Date */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="date"
              label="Start Date"
              value={formData.start_date}
              onChange={handleChange('start_date')}
              InputLabelProps={{ shrink: true }}
            />
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

          {/* Completion Percentage */}
          <Grid item xs={12} md={6}>
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

          {/* Budget Allocated */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Budget Allocated ($)"
              value={formData.budget_allocated}
              onChange={handleChange('budget_allocated')}
              inputProps={{ step: 1000 }}
            />
          </Grid>

          {/* Budget Spent */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Budget Spent ($)"
              value={formData.budget_spent}
              onChange={handleChange('budget_spent')}
              inputProps={{ step: 1000 }}
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
            />
          </Grid>

          {/* Stakeholder Count */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Stakeholder Count"
              value={formData.stakeholder_count}
              onChange={handleChange('stakeholder_count')}
              inputProps={{ min: 0 }}
              helperText="Number of stakeholders involved"
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
          {initiative ? 'Update Initiative' : 'Create Initiative'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default StrategicInitiativeFormDialog
