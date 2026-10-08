import React, { useState, useEffect } from 'react'
import axios from '../../utils/axiosInstance'
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Switch,
  FormControlLabel,
  Tab,
  Tabs,
  Divider,
} from '@mui/material'
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  PlayArrow as TestIcon,
  Code as CodeIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Policy as PolicyIcon,
  GitHub as GitHubIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'

function PolicyEnforcementDashboard() {
  const [policies, setPolicies] = useState([])
  const [validations, setValidations] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tabValue, setTabValue] = useState(0)

  // Dialogs
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [testDialogOpen, setTestDialogOpen] = useState(false)
  const [integrationDialogOpen, setIntegrationDialogOpen] = useState(false)
  const [selectedIntegration, setSelectedIntegration] = useState('github')
  const [integrationConfig, setIntegrationConfig] = useState(null)

  // Form data
  const [formData, setFormData] = useState({
    policy_name: '',
    policy_type: 'NAMING_CONVENTION',
    description: '',
    is_blocking: true,
    enforcement_level: 'strict',
    applies_to_domains: [],
    applies_to_environments: [],
    policy_definition: {}
  })

  // Test validation data
  const [testData, setTestData] = useState({
    asset_name: '',
    environment: 'PROD',
    domain: 'DATA',
    description: '',
    owner_id: '',
    data_classification: 'Internal',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const [policiesRes, validationsRes, statsRes] = await Promise.all([
        axios.get('/api/v1/policies/list'),
        axios.get('/api/v1/policies/validations'),
        axios.get('/api/v1/policies/statistics'),
      ])

      // Parse JSON strings for applies_to_domains and applies_to_environments
      const parsedPolicies = (policiesRes.data.policies || []).map(policy => ({
        ...policy,
        applies_to_domains: typeof policy.applies_to_domains === 'string'
          ? JSON.parse(policy.applies_to_domains)
          : policy.applies_to_domains || [],
        applies_to_environments: typeof policy.applies_to_environments === 'string'
          ? JSON.parse(policy.applies_to_environments)
          : policy.applies_to_environments || []
      }))

      setPolicies(parsedPolicies)
      setValidations(validationsRes.data.validations || [])
      setStatistics(statsRes.data)
    } catch (err) {
      console.error('Error fetching policy data:', err)
      setError('Failed to load policy enforcement data')
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePolicy = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/api/v1/policies/create', formData)
      fetchData()
      setCreateDialogOpen(false)
      setFormData({
        policy_name: '',
        policy_type: 'NAMING_CONVENTION',
        description: '',
        is_blocking: true,
        enforcement_level: 'strict',
        applies_to_domains: [],
        applies_to_environments: [],
        policy_definition: {}
      })
    } catch (err) {
      console.error('Error creating policy:', err)
      setError(err.response?.data?.detail || 'Failed to create policy')
    }
  }

  const handleTestValidation = async (e) => {
    e.preventDefault()
    try {
      const result = await axios.post('/api/v1/policies/validate', testData)
      alert(`Validation Result:\n${result.data.passed ? 'PASSED' : 'FAILED'}\n\nViolations: ${result.data.violations?.length || 0}`)
      fetchData()
      setTestDialogOpen(false)
    } catch (err) {
      console.error('Error testing validation:', err)
      setError(err.response?.data?.detail || 'Validation test failed')
    }
  }

  const handleTogglePolicy = async (policyId, currentState) => {
    try {
      await axios.patch(`/api/v1/policies/policies/${policyId}`, null, {
        params: { is_active: !currentState }
      })
      fetchData()
    } catch (err) {
      console.error('Error toggling policy:', err)
      setError('Failed to update policy')
    }
  }

  const handleDeletePolicy = async (policyId) => {
    if (!confirm('Are you sure you want to delete this policy?')) return
    try {
      await axios.delete(`/api/v1/policies/policies/${policyId}`)
      fetchData()
    } catch (err) {
      console.error('Error deleting policy:', err)
      setError('Failed to delete policy')
    }
  }

  const handleGetIntegrationConfig = async (platform) => {
    try {
      const endpoint = platform === 'github'
        ? '/api/v1/policies/integrations/github-actions'
        : '/api/v1/policies/integrations/gitlab-ci'
      const response = await axios.get(endpoint)
      setIntegrationConfig(response.data)
      setSelectedIntegration(platform)
      setIntegrationDialogOpen(true)
    } catch (err) {
      console.error('Error getting integration config:', err)
      setError('Failed to generate integration configuration')
    }
  }

  const getPolicyTypeColor = (type) => {
    switch (type) {
      case 'NAMING_CONVENTION': return 'primary'
      case 'DOCUMENTATION': return 'secondary'
      case 'DATA_CLASSIFICATION': return 'warning'
      case 'OWNER_ASSIGNMENT': return 'info'
      default: return 'default'
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          CI/CD Policy Enforcement
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchData} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<TestIcon />}
            onClick={() => setTestDialogOpen(true)}
          >
            Test Validation
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Policy
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      {statistics && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <PolicyIcon color="primary" />
                  <Typography variant="caption" color="textSecondary">
                    Active Policies
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.active_policies || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <CheckCircleIcon color="success" />
                  <Typography variant="caption" color="textSecondary">
                    Passing Validations
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.passing_validations || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderLeft: '4px solid #ff9800' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <WarningIcon color="warning" />
                  <Typography variant="caption" color="textSecondary">
                    Blocking Policies
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.blocking_policies || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <ErrorIcon color="error" />
                  <Typography variant="caption" color="textSecondary">
                    Failed Validations
                  </Typography>
                </Box>
                <Typography variant="h4">{statistics.failed_validations || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Governance Policies" />
          <Tab label="Validation History" />
          <Tab label="CI/CD Integration" />
        </Tabs>
      </Paper>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Tab 0: Policies */}
          {tabValue === 0 && (
            <Paper>
              <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
                <Typography variant="h6">Governance Policies</Typography>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Policy Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Enforcement</TableCell>
                      <TableCell>Blocking</TableCell>
                      <TableCell>Enabled</TableCell>
                      <TableCell>Applies To</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {policies.length > 0 ? (
                      policies.map((policy) => (
                        <TableRow key={policy.policy_id}>
                          <TableCell>{policy.policy_name}</TableCell>
                          <TableCell>
                            <Chip
                              label={policy.policy_type}
                              size="small"
                              color={getPolicyTypeColor(policy.policy_type)}
                            />
                          </TableCell>
                          <TableCell>
                            <Chip label={policy.enforcement_level} size="small" variant="outlined" />
                          </TableCell>
                          <TableCell>
                            {policy.is_blocking ? (
                              <Chip label="Blocking" size="small" color="warning" />
                            ) : (
                              <Chip label="Warning" size="small" color="info" />
                            )}
                          </TableCell>
                          <TableCell>
                            <Switch
                              checked={policy.is_active}
                              onChange={() => handleTogglePolicy(policy.policy_id, policy.is_active)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {policy.applies_to_domains?.length > 0 && (
                              <Typography variant="caption" display="block">
                                Domains: {policy.applies_to_domains.join(', ')}
                              </Typography>
                            )}
                            {policy.applies_to_environments?.length > 0 && (
                              <Typography variant="caption" display="block">
                                Envs: {policy.applies_to_environments.join(', ')}
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell align="right">
                            <Tooltip title="Delete">
                              <IconButton
                                size="small"
                                onClick={() => handleDeletePolicy(policy.policy_id)}
                                color="error"
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={7} align="center">
                          <Typography variant="body2" color="textSecondary">
                            No policies defined
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          )}

          {/* Tab 1: Validation History */}
          {tabValue === 1 && (
            <Paper>
              <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
                <Typography variant="h6">Recent Validations</Typography>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Asset Name</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Violations</TableCell>
                      <TableCell>Validated At</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {validations.length > 0 ? (
                      validations.map((validation) => (
                        <TableRow key={validation.validation_id}>
                          <TableCell>{validation.asset_name}</TableCell>
                          <TableCell>
                            {validation.passed ? (
                              <Chip label="Passed" size="small" color="success" icon={<CheckCircleIcon />} />
                            ) : (
                              <Chip label="Failed" size="small" color="error" icon={<ErrorIcon />} />
                            )}
                          </TableCell>
                          <TableCell>
                            {validation.violation_count > 0 ? (
                              <Chip label={`${validation.violation_count} violations`} size="small" color="error" />
                            ) : (
                              <Chip label="No violations" size="small" color="success" />
                            )}
                          </TableCell>
                          <TableCell>{new Date(validation.validated_at).toLocaleString()}</TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={4} align="center">
                          <Typography variant="body2" color="textSecondary">
                            No validation history
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          )}

          {/* Tab 2: CI/CD Integration */}
          {tabValue === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <GitHubIcon sx={{ fontSize: 40 }} />
                      <Box>
                        <Typography variant="h6">GitHub Actions</Typography>
                        <Typography variant="body2" color="textSecondary">
                          Automated policy checks in GitHub workflows
                        </Typography>
                      </Box>
                    </Box>
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={<CodeIcon />}
                      onClick={() => handleGetIntegrationConfig('github')}
                    >
                      Generate GitHub Actions Config
                    </Button>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <PolicyIcon sx={{ fontSize: 40, color: '#FC6D26' }} />
                      <Box>
                        <Typography variant="h6">GitLab CI</Typography>
                        <Typography variant="body2" color="textSecondary">
                          Automated policy checks in GitLab pipelines
                        </Typography>
                      </Box>
                    </Box>
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={<CodeIcon />}
                      onClick={() => handleGetIntegrationConfig('gitlab')}
                    >
                      Generate GitLab CI Config
                    </Button>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Integration Guide</Typography>
                  <Typography variant="body2" paragraph>
                    Integrate governance policy validation into your CI/CD pipeline to automatically check assets before deployment:
                  </Typography>
                  <Typography variant="body2" component="div">
                    <strong>Benefits:</strong>
                    <ul>
                      <li>Automatic validation on every commit/PR</li>
                      <li>Block deployments that violate governance policies</li>
                      <li>Early detection of naming convention issues</li>
                      <li>Enforce documentation and ownership requirements</li>
                      <li>Maintain audit trail of all validations</li>
                    </ul>
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          )}
        </>
      )}

      {/* Create Policy Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Governance Policy</DialogTitle>
        <form onSubmit={handleCreatePolicy}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Policy Name"
                  value={formData.policy_name}
                  onChange={(e) => setFormData({ ...formData, policy_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  select
                  fullWidth
                  required
                  label="Policy Type"
                  value={formData.policy_type}
                  onChange={(e) => setFormData({ ...formData, policy_type: e.target.value })}
                >
                  <MenuItem value="NAMING_CONVENTION">Naming Convention</MenuItem>
                  <MenuItem value="DOCUMENTATION">Documentation</MenuItem>
                  <MenuItem value="DATA_CLASSIFICATION">Data Classification</MenuItem>
                  <MenuItem value="OWNER_ASSIGNMENT">Owner Assignment</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_blocking}
                      onChange={(e) => setFormData({ ...formData, is_blocking: e.target.checked })}
                    />
                  }
                  label="Blocking"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  select
                  fullWidth
                  label="Enforcement Level"
                  value={formData.enforcement_level}
                  onChange={(e) => setFormData({ ...formData, enforcement_level: e.target.value })}
                >
                  <MenuItem value="strict">Strict</MenuItem>
                  <MenuItem value="moderate">Moderate</MenuItem>
                  <MenuItem value="lenient">Lenient</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Create</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Test Validation Dialog */}
      <Dialog open={testDialogOpen} onClose={() => setTestDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Test Policy Validation</DialogTitle>
        <form onSubmit={handleTestValidation}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  required
                  label="Asset Name"
                  value={testData.asset_name}
                  onChange={(e) => setTestData({ ...testData, asset_name: e.target.value })}
                  placeholder="PROD-DATA-PLATFORM-v1"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  select
                  fullWidth
                  label="Environment"
                  value={testData.environment}
                  onChange={(e) => setTestData({ ...testData, environment: e.target.value })}
                >
                  <MenuItem value="DEV">DEV</MenuItem>
                  <MenuItem value="QA">QA</MenuItem>
                  <MenuItem value="UAT">UAT</MenuItem>
                  <MenuItem value="PROD">PROD</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  select
                  fullWidth
                  label="Domain"
                  value={testData.domain}
                  onChange={(e) => setTestData({ ...testData, domain: e.target.value })}
                >
                  <MenuItem value="HR">HR</MenuItem>
                  <MenuItem value="FIN">FIN</MenuItem>
                  <MenuItem value="OPS">OPS</MenuItem>
                  <MenuItem value="SALES">SALES</MenuItem>
                  <MenuItem value="IT">IT</MenuItem>
                  <MenuItem value="DATA">DATA</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Description"
                  value={testData.description}
                  onChange={(e) => setTestData({ ...testData, description: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setTestDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained" startIcon={<TestIcon />}>
              Run Validation
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Integration Config Dialog */}
      <Dialog
        open={integrationDialogOpen}
        onClose={() => setIntegrationDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedIntegration === 'github' ? 'GitHub Actions' : 'GitLab CI'} Configuration
        </DialogTitle>
        <DialogContent>
          {integrationConfig && (
            <>
              <Typography variant="body2" paragraph>
                <strong>Instructions:</strong>
              </Typography>
              <Box component="ol" sx={{ pl: 2 }}>
                {integrationConfig.instructions.map((instruction, index) => (
                  <Typography key={index} component="li" variant="body2" sx={{ mb: 0.5 }}>
                    {instruction}
                  </Typography>
                ))}
              </Box>
              <Divider sx={{ my: 2 }} />
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Configuration YAML:</strong>
              </Typography>
              <Paper
                sx={{
                  p: 2,
                  backgroundColor: '#f5f5f5',
                  fontFamily: 'monospace',
                  fontSize: '0.85rem',
                  overflow: 'auto',
                  maxHeight: 400,
                }}
              >
                <pre>{integrationConfig.config}</pre>
              </Paper>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIntegrationDialogOpen(false)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              navigator.clipboard.writeText(integrationConfig.config)
              alert('Configuration copied to clipboard!')
            }}
          >
            Copy to Clipboard
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default PolicyEnforcementDashboard
