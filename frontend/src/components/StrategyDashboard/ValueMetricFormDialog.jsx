import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Grid,
  FormControl,
  InputLabel,
  Select,
  Alert,
  CircularProgress,
} from '@mui/material'
import axiosInstance from '../../utils/axiosInstance'

const METRIC_TYPES = [
  { value: 'cost_savings', label: 'Cost Savings' },
  { value: 'time_reduction', label: 'Time Reduction' },
  { value: 'revenue_increase', label: 'Revenue Increase' },
  { value: 'efficiency_gain', label: 'Efficiency Gain' },
  { value: 'quality_improvement', label: 'Quality Improvement' },
]

const MEASUREMENT_PERIODS = [
  { value: 'One-time', label: 'One-time' },
  { value: 'Monthly', label: 'Monthly' },
  { value: 'Quarterly', label: 'Quarterly' },
  { value: 'Annual', label: 'Annual' },
]

const DATA_SOURCES = [
  { value: 'manual', label: 'Manual Entry' },
  { value: 'calculated', label: 'Calculated' },
  { value: 'integrated', label: 'Integrated System' },
  { value: 'system_generated', label: 'System Generated' },
]

const STATUS_OPTIONS = [
  { value: 'Draft', label: 'Draft' },
  { value: 'Approved', label: 'Approved' },
  { value: 'Published', label: 'Published' },
  { value: 'Archived', label: 'Archived' },
]

function ValueMetricFormDialog({ open, onClose, metric, onSave }) {
  const [formData, setFormData] = useState({
    domain_id: '',
    initiative_id: '',
    business_goal_id: '',
    metric_type: '',
    value_delivered: '',
    key_achievement: '',
    measurement_date: new Date().toISOString().split('T')[0],
    measurement_period: 'Quarterly',
    data_source: 'manual',
    status: 'Draft',
    is_active: true,
    display_order: 0,
    created_by: 1, // TODO: Get from authenticated user
    notes: '',
  })

  const [domains, setDomains] = useState([])
  const [initiatives, setInitiatives] = useState([])
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (open) {
      fetchDropdownData()
      if (metric) {
        // Editing existing metric
        setFormData({
          domain_id: metric.domain_id || '',
          initiative_id: metric.initiative_id || '',
          business_goal_id: metric.business_goal_id || '',
          metric_type: metric.metric_type || '',
          value_delivered: metric.value_delivered || '',
          key_achievement: metric.key_achievement || '',
          measurement_date: metric.measurement_date || new Date().toISOString().split('T')[0],
          measurement_period: metric.measurement_period || 'Quarterly',
          data_source: metric.data_source || 'manual',
          status: metric.status || 'Draft',
          is_active: metric.is_active !== undefined ? metric.is_active : true,
          display_order: metric.display_order || 0,
          created_by: metric.created_by || 1,
          notes: metric.notes || '',
        })
      } else {
        // Reset for new metric
        setFormData({
          domain_id: '',
          initiative_id: '',
          business_goal_id: '',
          metric_type: '',
          value_delivered: '',
          key_achievement: '',
          measurement_date: new Date().toISOString().split('T')[0],
          measurement_period: 'Quarterly',
          data_source: 'manual',
          status: 'Draft',
          is_active: true,
          display_order: 0,
          created_by: 1,
          notes: '',
        })
      }
    }
  }, [open, metric])

  const fetchDropdownData = async () => {
    try {
      const [domainsRes, initiativesRes, goalsRes] = await Promise.all([
        axiosInstance.get('/api/v1/assets/domains'),
        axiosInstance.get('/api/v1/strategy/initiatives'),
        axiosInstance.get('/api/v1/strategy/goals'),
      ])
      setDomains(domainsRes.data || [])
      setInitiatives(initiativesRes.data || [])
      setGoals(goalsRes.data || [])
    } catch (error) {
      console.error('Error fetching dropdown data:', error)
      setError('Failed to load form options')
    }
  }

  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    })
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)
      setError(null)

      // Validate required fields
      if (!formData.domain_id || !formData.value_delivered || !formData.key_achievement) {
        setError('Please fill in all required fields')
        setLoading(false)
        return
      }

      if (metric) {
        // Update existing metric
        await axiosInstance.put(`/api/v1/strategy/value-metrics/${metric.metric_id}`, formData)
      } else {
        // Create new metric
        await axiosInstance.post('/api/v1/strategy/value-metrics', formData)
      }

      onSave()
      onClose()
    } catch (error) {
      console.error('Error saving metric:', error)
      setError(error.response?.data?.detail || 'Failed to save metric')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {metric ? 'Edit Value Delivered Metric' : 'Add New Value Delivered Metric'}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Domain</InputLabel>
              <Select
                value={formData.domain_id}
                onChange={handleChange('domain_id')}
                label="Domain"
              >
                {domains.map((domain) => (
                  <MenuItem key={domain.domain_id} value={domain.domain_id}>
                    {domain.domain_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Metric Type</InputLabel>
              <Select
                value={formData.metric_type}
                onChange={handleChange('metric_type')}
                label="Metric Type"
              >
                {METRIC_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              label="Value Delivered"
              placeholder="e.g., $850K cost savings, 60% faster decisions"
              value={formData.value_delivered}
              onChange={handleChange('value_delivered')}
              helperText="Short description of the value (shown in summary)"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              required
              multiline
              rows={3}
              label="Key Achievement"
              placeholder="Detailed description of what was accomplished..."
              value={formData.key_achievement}
              onChange={handleChange('key_achievement')}
              helperText="Detailed explanation of the achievement"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="date"
              label="Measurement Date"
              value={formData.measurement_date}
              onChange={handleChange('measurement_date')}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Measurement Period</InputLabel>
              <Select
                value={formData.measurement_period}
                onChange={handleChange('measurement_period')}
                label="Measurement Period"
              >
                {MEASUREMENT_PERIODS.map((period) => (
                  <MenuItem key={period.value} value={period.value}>
                    {period.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Data Source</InputLabel>
              <Select
                value={formData.data_source}
                onChange={handleChange('data_source')}
                label="Data Source"
              >
                {DATA_SOURCES.map((source) => (
                  <MenuItem key={source.value} value={source.value}>
                    {source.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                onChange={handleChange('status')}
                label="Status"
              >
                {STATUS_OPTIONS.map((status) => (
                  <MenuItem key={status.value} value={status.value}>
                    {status.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Initiative (Optional)</InputLabel>
              <Select
                value={formData.initiative_id}
                onChange={handleChange('initiative_id')}
                label="Initiative (Optional)"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {initiatives.map((initiative) => (
                  <MenuItem key={initiative.initiative_id} value={initiative.initiative_id}>
                    {initiative.initiative_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Business Goal (Optional)</InputLabel>
              <Select
                value={formData.business_goal_id}
                onChange={handleChange('business_goal_id')}
                label="Business Goal (Optional)"
              >
                <MenuItem value="">
                  <em>None</em>
                </MenuItem>
                {goals.map((goal) => (
                  <MenuItem key={goal.goal_id} value={goal.goal_id}>
                    {goal.goal_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Notes (Optional)"
              placeholder="Internal notes, calculation methodology, etc..."
              value={formData.notes}
              onChange={handleChange('notes')}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {metric ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default ValueMetricFormDialog
