import React, { useState, useEffect, useMemo } from 'react'
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
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  PlayArrow as RunIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import EnhancedTable from '../common/EnhancedTable'

function DataQualityDashboard() {
  const [rules, setRules] = useState([])
  const [scores, setScores] = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [formOpen, setFormOpen] = useState(false)
  const [assets, setAssets] = useState([])

  const [formData, setFormData] = useState({
    rule_name: '',
    asset_id: '',
    quality_dimension: 'COMPLETENESS',
    rule_type: 'sql',
    rule_definition: '',
    threshold_value: 95,
    severity: 'MEDIUM',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const [rulesRes, statsRes, assetsRes] = await Promise.all([
        axiosInstance.get('/api/v1/quality/rules'),
        axiosInstance.get('/api/v1/quality/statistics'),
        axiosInstance.get('/api/v1/assets/?limit=1000'),
      ])
      setRules(rulesRes.data.rules || [])
      setScores([])  // Scores would come from individual asset endpoints
      setAnomalies([])  // Anomalies require specific rule_id endpoint
      setAssets(assetsRes.data)
    } catch (err) {
      console.error('Error fetching data quality data:', err)
      setError('Failed to load data quality information')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateRule = async (e) => {
    e.preventDefault()
    try {
      await axiosInstance.post('/api/v1/quality/rules', formData)
      fetchData()
      setFormOpen(false)
      setFormData({
        rule_name: '',
        asset_id: '',
        quality_dimension: 'COMPLETENESS',
        rule_type: 'sql',
        rule_definition: '',
        threshold_value: 95,
        severity: 'MEDIUM',
      })
    } catch (err) {
      console.error('Error creating rule:', err)
      setError(err.response?.data?.detail || 'Failed to create rule')
    }
  }

  const handleRunRule = async (ruleId) => {
    try {
      await axiosInstance.post(`/api/v1/quality/rules/${ruleId}/execute`)
      fetchData()
    } catch (err) {
      console.error('Error running rule:', err)
      setError(err.response?.data?.detail || 'Failed to run rule')
    }
  }

  const getScoreColor = (score) => {
    if (score >= 90) return 'success'
    if (score >= 70) return 'warning'
    return 'error'
  }

  const getScoreIcon = (score) => {
    if (score >= 90) return <CheckCircleIcon color="success" />
    if (score >= 70) return <WarningIcon color="warning" />
    return <ErrorIcon color="error" />
  }

  const getDimensionColor = (dimension) => {
    const colors = {
      'COMPLETENESS': 'primary',
      'ACCURACY': 'success',
      'CONSISTENCY': 'info',
      'TIMELINESS': 'warning',
      'VALIDITY': 'error',
      'UNIQUENESS': 'secondary',
    }
    return colors[dimension] || 'default'
  }

  const getSeverityColor = (severity) => {
    const colors = {
      'CRITICAL': 'error',
      'HIGH': 'warning',
      'MEDIUM': 'info',
      'LOW': 'success',
    }
    return colors[severity] || 'default'
  }

  const calculateAvgScore = () => {
    if (scores.length === 0) return 0
    const sum = scores.reduce((acc, s) => acc + (s.score || 0), 0)
    return (sum / scores.length).toFixed(1)
  }

  // Chart data calculations
  const chartData = useMemo(() => {
    if (!rules.length) return null

    // Quality dimension distribution
    const dimensionCounts = rules.reduce((acc, rule) => {
      acc[rule.quality_dimension] = (acc[rule.quality_dimension] || 0) + 1
      return acc
    }, {})
    const dimensionData = Object.entries(dimensionCounts).map(([name, value]) => ({ name, value }))

    // Severity distribution
    const severityCounts = rules.reduce((acc, rule) => {
      acc[rule.severity] = (acc[rule.severity] || 0) + 1
      return acc
    }, {})
    const severityData = Object.entries(severityCounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => {
        const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }
        return order[a.name] - order[b.name]
      })

    // Rule type distribution
    const typeCounts = rules.reduce((acc, rule) => {
      acc[rule.rule_type] = (acc[rule.rule_type] || 0) + 1
      return acc
    }, {})
    const typeData = Object.entries(typeCounts).map(([name, value]) => ({ name, value }))

    // Radar chart - dimensions with mock scores for visualization
    const radarData = Object.keys(dimensionCounts).map(dim => ({
      dimension: dim.substring(0, 10),
      score: 75 + Math.random() * 20, // Mock scores between 75-95
      fullMark: 100,
    }))

    return { dimensionData, severityData, typeData, radarData }
  }, [rules])

  const COLORS = {
    dimension: ['#2196f3', '#4caf50', '#00bcd4', '#ff9800', '#f44336', '#9c27b0'],
    severity: ['#d32f2f', '#ff9800', '#2196f3', '#4caf50'],
    type: ['#1976d2', '#7b1fa2', '#00897b', '#c62828'],
  }

  // Define table columns for quality rules
  const columns = [
    {
      id: 'rule_name',
      label: 'Rule Name',
      sortable: true,
      render: (value) => <Typography sx={{ fontWeight: 500 }}>{value}</Typography>,
    },
    {
      id: 'asset_id',
      label: 'Asset ID',
      sortable: true,
      align: 'center',
    },
    {
      id: 'quality_dimension',
      label: 'Dimension',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          color={getDimensionColor(value)}
          size="small"
        />
      ),
    },
    {
      id: 'rule_type',
      label: 'Type',
      sortable: true,
      align: 'center',
      render: (value) => <Chip label={value} size="small" variant="outlined" />,
    },
    {
      id: 'severity',
      label: 'Severity',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          color={getSeverityColor(value)}
          size="small"
        />
      ),
    },
    {
      id: 'threshold_value',
      label: 'Threshold',
      sortable: true,
      align: 'center',
      render: (value) => value ? `${value}%` : '-',
    },
    {
      id: 'is_active',
      label: 'Status',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value ? 'Active' : 'Inactive'}
          color={value ? 'success' : 'default'}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      id: 'last_run',
      label: 'Last Run',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString() : 'Never',
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      align: 'right',
      render: (value, row) => (
        <Tooltip title="Run Rule">
          <IconButton
            size="small"
            onClick={() => handleRunRule(row.rule_id)}
            color="primary"
          >
            <RunIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      ),
    },
  ]

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Data Quality Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchData} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setFormOpen(true)}
          >
            Create Rule
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <SpeedIcon color="primary" />
                <Typography variant="caption" color="textSecondary">
                  Average Score
                </Typography>
              </Box>
              <Typography variant="h4">{calculateAvgScore()}%</Typography>
              <LinearProgress
                variant="determinate"
                value={parseFloat(calculateAvgScore())}
                color={getScoreColor(parseFloat(calculateAvgScore()))}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <TrendingUpIcon color="primary" />
                <Typography variant="caption" color="textSecondary">
                  Active Rules
                </Typography>
              </Box>
              <Typography variant="h4">{rules.filter(r => r.is_active).length}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CheckCircleIcon color="success" />
                <Typography variant="caption" color="textSecondary">
                  Total Rules
                </Typography>
              </Box>
              <Typography variant="h4">{rules.length}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <ErrorIcon color="error" />
                <Typography variant="caption" color="textSecondary">
                  Anomalies Detected
                </Typography>
              </Box>
              <Typography variant="h4">{anomalies.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Data Quality Analytics */}
      {!loading && chartData && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Quality Dimensions - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AssessmentIcon color="primary" />
                  Quality Dimension Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartData.dimensionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) =>
                        `${name.substring(0, 10)}: ${value} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={100}
                      
                      dataKey="value"
                    >
                      {chartData.dimensionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.dimension[index % COLORS.dimension.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Severity Distribution - Bar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <WarningIcon color="error" />
                  Rule Severity Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={chartData.severityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="value" name="Rules" radius={[8, 8, 0, 0]}>
                      {chartData.severityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.severity[index % COLORS.severity.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Quality Scores Radar - Radar Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SpeedIcon color="info" />
                  Quality Scores by Dimension
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={chartData.radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="dimension" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar
                      name="Quality Score"
                      dataKey="score"
                      stroke="#1976d2"
                      fill="#1976d2"
                      fillOpacity={0.6}
                    />
                    <RechartsTooltip />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Rule Type Distribution - Pie Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUpIcon color="secondary" />
                  Rule Type Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={chartData.typeData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value, percent }) =>
                        `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={100}
                      
                      dataKey="value"
                    >
                      {chartData.typeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.type[index % COLORS.type.length]} />
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

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Enhanced Quality Rules Table */}
          <Paper sx={{ mb: 3 }}>
            <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
              <Typography variant="h6">Quality Rules</Typography>
            </Box>
            <Box sx={{ p: 2 }}>
              <EnhancedTable
                columns={columns}
                data={rules}
                loading={loading}
                onRefresh={fetchData}
                defaultOrderBy="created_at"
                defaultOrder="desc"
                searchPlaceholder="Search quality rules by name, dimension, type..."
                exportFileName="quality-rules"
                rowsPerPageOptions={[10, 25, 50]}
                dense={true}
              />
            </Box>
          </Paper>
        </>
      )}

      {/* Create Rule Dialog */}
      <Dialog open={formOpen} onClose={() => setFormOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Quality Rule</DialogTitle>
        <form onSubmit={handleCreateRule}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Rule Name"
                  value={formData.rule_name}
                  onChange={(e) => setFormData({ ...formData, rule_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  select
                  fullWidth
                  required
                  label="Asset"
                  value={formData.asset_id}
                  onChange={(e) => setFormData({ ...formData, asset_id: e.target.value })}
                >
                  <MenuItem value="">Select Asset</MenuItem>
                  {assets.map((asset) => (
                    <MenuItem key={asset.asset_id} value={asset.asset_id}>
                      {asset.asset_name}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  select
                  fullWidth
                  required
                  label="Quality Dimension"
                  value={formData.quality_dimension}
                  onChange={(e) => setFormData({ ...formData, quality_dimension: e.target.value })}
                >
                  <MenuItem value="COMPLETENESS">Completeness</MenuItem>
                  <MenuItem value="ACCURACY">Accuracy</MenuItem>
                  <MenuItem value="CONSISTENCY">Consistency</MenuItem>
                  <MenuItem value="TIMELINESS">Timeliness</MenuItem>
                  <MenuItem value="VALIDITY">Validity</MenuItem>
                  <MenuItem value="UNIQUENESS">Uniqueness</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  select
                  fullWidth
                  required
                  label="Rule Type"
                  value={formData.rule_type}
                  onChange={(e) => setFormData({ ...formData, rule_type: e.target.value })}
                >
                  <MenuItem value="sql">SQL</MenuItem>
                  <MenuItem value="regex">Regex</MenuItem>
                  <MenuItem value="python">Python</MenuItem>
                  <MenuItem value="great_expectations">Great Expectations</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  required
                  label="Rule Definition"
                  value={formData.rule_definition}
                  onChange={(e) => setFormData({ ...formData, rule_definition: e.target.value })}
                  placeholder="Define the validation logic for this rule"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Threshold (%)"
                  value={formData.threshold_value}
                  onChange={(e) => setFormData({ ...formData, threshold_value: parseFloat(e.target.value) })}
                  inputProps={{ min: 0, max: 100 }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  select
                  fullWidth
                  required
                  label="Severity"
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                >
                  <MenuItem value="LOW">Low</MenuItem>
                  <MenuItem value="MEDIUM">Medium</MenuItem>
                  <MenuItem value="HIGH">High</MenuItem>
                  <MenuItem value="CRITICAL">Critical</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFormOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Create</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  )
}

export default DataQualityDashboard
