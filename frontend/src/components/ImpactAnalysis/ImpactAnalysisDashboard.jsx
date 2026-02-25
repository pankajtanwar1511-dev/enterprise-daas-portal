import React, { useState, useEffect } from 'react'
import axios from 'axios'
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
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Assessment as AnalysisIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  AccountTree as DependencyIcon,
} from '@mui/icons-material'

function ImpactAnalysisDashboard() {
  const [assets, setAssets] = useState([])
  const [selectedAsset, setSelectedAsset] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [visualization, setVisualization] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchAssets()
  }, [])

  const fetchAssets = async () => {
    try {
      const response = await axios.get('/api/v1/assets/?limit=1000')
      setAssets(response.data)
    } catch (err) {
      console.error('Error fetching assets:', err)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedAsset) return

    setLoading(true)
    setError('')
    try {
      // Run impact analysis
      const analysisResponse = await axios.post(`/api/v1/impact/analyze/${selectedAsset}`)
      setAnalysis(analysisResponse.data)

      // Get visualization data
      const vizResponse = await axios.get(`/api/v1/impact/visualization/${selectedAsset}`)
      setVisualization(vizResponse.data)

      // Get history
      const historyResponse = await axios.get(`/api/v1/impact/history/${selectedAsset}`)
      setHistory(historyResponse.data)
    } catch (err) {
      console.error('Error analyzing impact:', err)
      setError(err.response?.data?.detail || 'Failed to analyze impact')
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'error'
      case 'high': return 'warning'
      case 'medium': return 'info'
      case 'low': return 'success'
      default: return 'default'
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Impact Analysis
        </Typography>
      </Box>

      {/* Asset Selection */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={8}>
            <TextField
              select
              fullWidth
              label="Select Asset to Analyze"
              value={selectedAsset}
              onChange={(e) => setSelectedAsset(e.target.value)}
            >
              <MenuItem value="">Choose an asset...</MenuItem>
              {assets.map((asset) => (
                <MenuItem key={asset.asset_id} value={asset.asset_id}>
                  {asset.asset_name} ({asset.environment})
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<AnalysisIcon />}
              onClick={handleAnalyze}
              disabled={!selectedAsset || loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Analyze Impact'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Analysis Results */}
      {analysis && (
        <>
          {/* Summary Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <TrendingUpIcon color="primary" />
                    <Typography variant="caption" color="textSecondary">
                      Impact Score
                    </Typography>
                  </Box>
                  <Typography variant="h4">
                    {analysis.impact_score || 'N/A'}
                  </Typography>
                  <Chip
                    label={analysis.impact_level || 'Unknown'}
                    color={getRiskColor(analysis.impact_level)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <DependencyIcon color="primary" />
                    <Typography variant="caption" color="textSecondary">
                      Dependencies
                    </Typography>
                  </Box>
                  <Typography variant="h4">
                    {analysis.total_dependencies || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <WarningIcon color="warning" />
                    <Typography variant="caption" color="textSecondary">
                      Affected Systems
                    </Typography>
                  </Box>
                  <Typography variant="h4">
                    {analysis.affected_systems || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <ErrorIcon color="error" />
                    <Typography variant="caption" color="textSecondary">
                      Critical Risks
                    </Typography>
                  </Box>
                  <Typography variant="h4">
                    {analysis.critical_dependencies || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Detailed Analysis */}
          <Grid container spacing={3}>
            {/* Upstream Dependencies */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <DependencyIcon color="primary" />
                  Upstream Dependencies
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Assets that this asset depends on
                </Typography>
                {analysis.upstream_dependencies && analysis.upstream_dependencies.length > 0 ? (
                  <List dense>
                    {analysis.upstream_dependencies.map((dep, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemText
                            primary={dep.asset_name || dep.name || `Asset ${dep.asset_id}`}
                            secondary={
                              <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                                <Chip
                                  label={dep.dependency_type || 'Unknown'}
                                  size="small"
                                  variant="outlined"
                                />
                                {dep.criticality && (
                                  <Chip
                                    label={dep.criticality}
                                    color={getRiskColor(dep.criticality)}
                                    size="small"
                                  />
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < analysis.upstream_dependencies.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Alert severity="info">No upstream dependencies found</Alert>
                )}
              </Paper>
            </Grid>

            {/* Downstream Dependents */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <DependencyIcon color="secondary" />
                  Downstream Dependents
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Assets that depend on this asset
                </Typography>
                {analysis.downstream_dependents && analysis.downstream_dependents.length > 0 ? (
                  <List dense>
                    {analysis.downstream_dependents.map((dep, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemText
                            primary={dep.asset_name || dep.name || `Asset ${dep.asset_id}`}
                            secondary={
                              <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                                <Chip
                                  label={dep.dependency_type || 'Unknown'}
                                  size="small"
                                  variant="outlined"
                                />
                                {dep.impact && (
                                  <Chip
                                    label={`Impact: ${dep.impact}`}
                                    color={getRiskColor(dep.impact)}
                                    size="small"
                                  />
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < analysis.downstream_dependents.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Alert severity="info">No downstream dependents found</Alert>
                )}
              </Paper>
            </Grid>

            {/* Risk Assessment */}
            {analysis.risk_assessment && (
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <WarningIcon color="warning" />
                    Risk Assessment
                  </Typography>
                  <Grid container spacing={2}>
                    {analysis.risk_assessment.potential_failures && (
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" sx={{ mb: 1 }}>Potential Failures:</Typography>
                        <List dense>
                          {analysis.risk_assessment.potential_failures.map((failure, index) => (
                            <ListItem key={index}>
                              <ListItemText
                                primary={failure.description || failure}
                                secondary={failure.probability && `Probability: ${failure.probability}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                    )}
                    {analysis.risk_assessment.recommendations && (
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" sx={{ mb: 1 }}>Recommendations:</Typography>
                        <List dense>
                          {analysis.risk_assessment.recommendations.map((rec, index) => (
                            <ListItem key={index}>
                              <ListItemText primary={rec.description || rec} />
                            </ListItem>
                          ))}
                        </List>
                      </Grid>
                    )}
                  </Grid>
                </Paper>
              </Grid>
            )}

            {/* Analysis History */}
            {history && history.length > 0 && (
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Analysis History
                  </Typography>
                  <List dense>
                    {history.slice(0, 5).map((item, index) => (
                      <React.Fragment key={index}>
                        <ListItem>
                          <ListItemText
                            primary={`Impact Score: ${item.impact_score || 'N/A'}`}
                            secondary={
                              <>
                                Level: {item.impact_level || 'Unknown'} |
                                Analyzed: {new Date(item.analyzed_at).toLocaleString()}
                              </>
                            }
                          />
                          <Chip
                            label={item.impact_level || 'Unknown'}
                            color={getRiskColor(item.impact_level)}
                            size="small"
                          />
                        </ListItem>
                        {index < Math.min(history.length, 5) - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </Paper>
              </Grid>
            )}
          </Grid>
        </>
      )}

      {!analysis && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <AnalysisIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            Select an asset and click "Analyze Impact" to see dependency analysis
          </Typography>
        </Paper>
      )}
    </Box>
  )
}

export default ImpactAnalysisDashboard
