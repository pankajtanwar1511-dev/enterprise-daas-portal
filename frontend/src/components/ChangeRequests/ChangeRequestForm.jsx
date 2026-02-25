import React, { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Grid,
  CircularProgress,
  Alert,
  IconButton,
} from '@mui/material'
import { Close as CloseIcon } from '@mui/icons-material'

function ChangeRequestForm({ open, onClose, onSuccess }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [assets, setAssets] = useState([])

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    asset_id: '',
    change_type: 'Modify',
    risk_level: 'Medium',
    impact_assessment: '',
    rollback_plan: '',
  })

  useEffect(() => {
    if (open) {
      fetchAssets()
    }
  }, [open])

  const fetchAssets = async () => {
    try {
      const response = await axios.get('/api/v1/assets/?limit=1000')
      setAssets(response.data)
    } catch (err) {
      console.error('Error fetching assets:', err)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await axios.post('/api/v1/change-requests/', formData)
      onSuccess()
      handleClose()
    } catch (err) {
      console.error('Error creating change request:', err)
      setError(err.response?.data?.detail || 'Failed to create change request')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setFormData({
      title: '',
      description: '',
      asset_id: '',
      change_type: 'Modify',
      risk_level: 'Medium',
      impact_assessment: '',
      rollback_plan: '',
    })
    setError('')
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ bgcolor: '#0D47A1', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        Create Change Request
        <IconButton onClick={handleClose} sx={{ color: 'white' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Brief description of the change"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                multiline
                rows={3}
                label="Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Detailed description of the change request"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Asset"
                name="asset_id"
                value={formData.asset_id}
                onChange={handleChange}
              >
                <MenuItem value="">Select Asset</MenuItem>
                {assets.map((asset) => (
                  <MenuItem key={asset.asset_id} value={asset.asset_id}>
                    {asset.asset_name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                required
                label="Change Type"
                name="change_type"
                value={formData.change_type}
                onChange={handleChange}
              >
                <MenuItem value="Modify">Modify</MenuItem>
                <MenuItem value="Deploy">Deploy</MenuItem>
                <MenuItem value="Decommission">Decommission</MenuItem>
                <MenuItem value="Config">Configuration</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                required
                label="Risk Level"
                name="risk_level"
                value={formData.risk_level}
                onChange={handleChange}
              >
                <MenuItem value="Low">Low</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Critical">Critical</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Impact Assessment"
                name="impact_assessment"
                value={formData.impact_assessment}
                onChange={handleChange}
                placeholder="Describe the potential impact of this change"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Rollback Plan"
                name="rollback_plan"
                value={formData.rollback_plan}
                onChange={handleChange}
                placeholder="Describe the rollback procedure if the change fails"
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Create Request'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export default ChangeRequestForm
