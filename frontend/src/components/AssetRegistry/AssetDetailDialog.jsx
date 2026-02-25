import React, { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Box,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Typography,
  Grid,
  Chip,
  Divider,
} from '@mui/material'
import {
  Close as CloseIcon,
  Info as InfoIcon,
  History as HistoryIcon,
  Assignment as AuditIcon,
} from '@mui/icons-material'
import LifecycleHistoryTab from './LifecycleHistoryTab'

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

function AssetDetailDialog({ open, onClose, asset }) {
  const [tabValue, setTabValue] = useState(0)
  const [lifecycleHistory, setLifecycleHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (open && asset) {
      fetchLifecycleHistory()
    }
  }, [open, asset])

  const fetchLifecycleHistory = async () => {
    if (!asset) return

    setLoading(true)
    setError('')
    try {
      const response = await axios.get(`/api/v1/assets/${asset.asset_id}/lifecycle-history`)
      setLifecycleHistory(response.data)
    } catch (err) {
      console.error('Error fetching lifecycle history:', err)
      setError('Failed to load lifecycle history')
    } finally {
      setLoading(false)
    }
  }

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue)
  }

  const handleClose = () => {
    setTabValue(0) // Reset to first tab
    onClose()
  }

  if (!asset) return null

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ bgcolor: '#0D47A1', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', display: 'block' }}>
            Asset Details
          </Typography>
          <Typography variant="h5" component="div" sx={{ fontWeight: 600, fontFamily: 'monospace', letterSpacing: '0.5px' }}>
            {asset.asset_name}
          </Typography>
        </Box>
        <IconButton
          onClick={handleClose}
          sx={{ color: 'white' }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab icon={<InfoIcon />} label="Overview" iconPosition="start" />
          <Tab icon={<HistoryIcon />} label="Lifecycle History" iconPosition="start" />
          <Tab icon={<AuditIcon />} label="Audit Log" iconPosition="start" disabled />
        </Tabs>
      </Box>

      <DialogContent>
        {/* Overview Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="textSecondary">Asset Name</Typography>
              <Typography variant="body1" sx={{ fontFamily: 'monospace', mb: 2 }}>{asset.asset_name}</Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="textSecondary">Environment</Typography>
              <Box sx={{ mb: 2 }}>
                <Chip label={asset.environment} color="primary" size="small" />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="textSecondary">Lifecycle Stage</Typography>
              <Box sx={{ mb: 2 }}>
                <Chip label={asset.lifecycle_stage} color="success" size="small" />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="textSecondary">Version</Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>{asset.version}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="caption" color="textSecondary">Description</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {asset.description || 'No description provided'}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="caption" color="textSecondary">Business Justification</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {asset.business_justification || 'No business justification provided'}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="textSecondary">Created At</Typography>
              <Typography variant="body2">
                {new Date(asset.created_at).toLocaleString()}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="caption" color="textSecondary">Last Updated</Typography>
              <Typography variant="body2">
                {new Date(asset.updated_at).toLocaleString()}
              </Typography>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Lifecycle History Tab */}
        <TabPanel value={tabValue} index={1}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : (
            <LifecycleHistoryTab history={lifecycleHistory} />
          )}
        </TabPanel>

        {/* Audit Log Tab (Placeholder) */}
        <TabPanel value={tabValue} index={2}>
          <Alert severity="info">
            Audit log feature coming soon...
          </Alert>
        </TabPanel>
      </DialogContent>
    </Dialog>
  )
}

export default AssetDetailDialog
