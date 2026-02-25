import React, { useState, useEffect } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Button,
  TextField,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material'
import {
  AccountTree as LineageIcon,
  Refresh as RefreshIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material'

function DataLineageDashboard() {
  const [assets, setAssets] = useState([])
  const [selectedAsset, setSelectedAsset] = useState('')
  const [lineageData, setLineageData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchAssets()
  }, [])

  const fetchAssets = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/assets/?limit=1000')
      setAssets(response.data)
    } catch (err) {
      console.error('Error fetching assets:', err)
    }
  }

  const handleTraceLineage = async () => {
    if (!selectedAsset) return

    setLoading(true)
    setError('')
    try {
      const response = await axiosInstance.get(`/api/v1/lineage/trace/${selectedAsset}`)
      setLineageData(response.data)
    } catch (err) {
      console.error('Error tracing lineage:', err)
      setError(err.response?.data?.detail || 'Failed to trace lineage')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Data Lineage Tracker
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={8}>
            <TextField
              select
              fullWidth
              label="Select Asset to Trace Lineage"
              value={selectedAsset}
              onChange={(e) => setSelectedAsset(e.target.value)}
            >
              <MenuItem value="">Choose an asset...</MenuItem>
              {assets.map((asset) => (
                <MenuItem key={asset.asset_id} value={asset.asset_id}>
                  {asset.asset_name}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<LineageIcon />}
              onClick={handleTraceLineage}
              disabled={!selectedAsset || loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Trace Lineage'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {lineageData && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <LineageIcon color="primary" />
                Upstream Sources
              </Typography>
              {lineageData.upstream && lineageData.upstream.length > 0 ? (
                <List>
                  {lineageData.upstream.map((source, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemText
                          primary={source.asset_name || source.source_name || `Source ${index + 1}`}
                          secondary={source.description || source.lineage_type}
                        />
                      </ListItem>
                      {index < lineageData.upstream.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Alert severity="info">No upstream sources found</Alert>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <TimelineIcon color="secondary" />
                Downstream Consumers
              </Typography>
              {lineageData.downstream && lineageData.downstream.length > 0 ? (
                <List>
                  {lineageData.downstream.map((consumer, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemText
                          primary={consumer.asset_name || consumer.target_name || `Consumer ${index + 1}`}
                          secondary={consumer.description || consumer.lineage_type}
                        />
                      </ListItem>
                      {index < lineageData.downstream.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Alert severity="info">No downstream consumers found</Alert>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Lineage Summary</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Total Sources</Typography>
                    <Typography variant="h4">{lineageData.upstream?.length || 0}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Total Consumers</Typography>
                    <Typography variant="h4">{lineageData.downstream?.length || 0}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Lineage Depth</Typography>
                    <Typography variant="h4">{lineageData.depth || 1}</Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" color="textSecondary">Total Nodes</Typography>
                    <Typography variant="h4">
                      {(lineageData.upstream?.length || 0) + (lineageData.downstream?.length || 0) + 1}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {!lineageData && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <LineageIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            Select an asset and click "Trace Lineage" to visualize data flow
          </Typography>
        </Paper>
      )}
    </Box>
  )
}

export default DataLineageDashboard
