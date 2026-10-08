import React, { useState, useEffect } from 'react'
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, MenuItem, Grid, FormControl, InputLabel,
  Select, Alert, CircularProgress,
} from '@mui/material'
import axiosInstance from '../../utils/axiosInstance'

const CHANGE_TYPES = [
  { value: 'Modify', label: 'Modify' },
  { value: 'Deploy', label: 'Deploy' },
  { value: 'Decommission', label: 'Decommission' },
  { value: 'Config', label: 'Configuration Change' },
]

const RISK_LEVELS = [
  { value: 'Low', label: 'Low' },
  { value: 'Medium', label: 'Medium' },
  { value: 'High', label: 'High' },
  { value: 'Critical', label: 'Critical' },
]

function ChangeRequestFormDialog({ open, onClose, changeRequest, onSave }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    asset_id: '',
    change_type: 'Modify',
    risk_level: 'Medium',
    impact_assessment: '',
    rollback_plan: '',
    release_version: '',
  })

  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (open) {
      fetchAssets()
      if (changeRequest) {
        setFormData({
          title: changeRequest.title || '',
          description: changeRequest.description || '',
          asset_id: changeRequest.asset_id || '',
          change_type: changeRequest.change_type || 'Modify',
          risk_level: changeRequest.risk_level || 'Medium',
          impact_assessment: changeRequest.impact_assessment || '',
          rollback_plan: changeRequest.rollback_plan || '',
          release_version: changeRequest.release_version || '',
        })
      } else {
        setFormData({
          title: '',
          description: '',
          asset_id: '',
          change_type: 'Modify',
          risk_level: 'Medium',
          impact_assessment: '',
          rollback_plan: '',
          release_version: '',
        })
      }
    }
  }, [open, changeRequest])

  const fetchAssets = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/assets/')
      setAssets(response.data.assets || [])
    } catch (error) {
      console.error('Error fetching assets:', error)
      setError('Failed to load assets')
    }
  }

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value })
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)
      setError(null)

      if (!formData.title || !formData.description || !formData.asset_id) {
        setError('Please fill in all required fields')
        setLoading(false)
        return
      }

      if (changeRequest) {
        await axiosInstance.put(`/api/v1/change-requests/${changeRequest.change_id}`, formData)
      } else {
        await axiosInstance.post('/api/v1/change-requests', formData)
      }

      onSave()
      onClose()
    } catch (error) {
      console.error('Error saving change request:', error)
      setError(error.response?.data?.detail || 'Failed to save change request')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {changeRequest ? 'Edit Change Request' : 'New Change Request'}
      </DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth required label="Title"
              value={formData.title}
              onChange={handleChange('title')}
              helperText="Brief description of the change"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Asset</InputLabel>
              <Select
                value={formData.asset_id}
                onChange={handleChange('asset_id')}
                label="Asset"
              >
                {assets.map((asset) => (
                  <MenuItem key={asset.asset_id} value={asset.asset_id}>
                    {asset.asset_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth required>
              <InputLabel>Change Type</InputLabel>
              <Select
                value={formData.change_type}
                onChange={handleChange('change_type')}
                label="Change Type"
              >
                {CHANGE_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth required>
              <InputLabel>Risk Level</InputLabel>
              <Select
                value={formData.risk_level}
                onChange={handleChange('risk_level')}
                label="Risk Level"
              >
                {RISK_LEVELS.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    {level.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth required multiline rows={3}
              label="Description"
              value={formData.description}
              onChange={handleChange('description')}
              helperText="Detailed description of what will be changed and why"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth multiline rows={2}
              label="Impact Assessment"
              value={formData.impact_assessment}
              onChange={handleChange('impact_assessment')}
              helperText="What systems/users will be affected?"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth multiline rows={2}
              label="Rollback Plan"
              value={formData.rollback_plan}
              onChange={handleChange('rollback_plan')}
              helperText="How to revert if something goes wrong"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Release Version"
              value={formData.release_version}
              onChange={handleChange('release_version')}
              helperText="Optional: Target release version"
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
          {changeRequest ? 'Update' : 'Submit'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default ChangeRequestFormDialog
