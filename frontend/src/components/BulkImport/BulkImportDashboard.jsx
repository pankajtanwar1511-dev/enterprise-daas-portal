import React, { useState, useMemo } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Stepper,
  Step,
  StepLabel,
  Alert,
  Chip,
  LinearProgress,
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import {
  CloudUpload as UploadIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const steps = ['Upload File', 'Validate Data', 'Review', 'Import']

function BulkImportDashboard() {
  const [activeStep, setActiveStep] = useState(0)
  const [file, setFile] = useState(null)
  const [validationResults, setValidationResults] = useState(null)
  const [importStatus, setImportStatus] = useState(null)
  const [error, setError] = useState('')

  // Mock import history data
  const [importHistory] = useState([
    { date: 'Jan 15', total: 120, success: 115, failed: 5 },
    { date: 'Jan 18', total: 200, success: 195, failed: 5 },
    { date: 'Jan 20', total: 180, success: 175, failed: 5 },
    { date: 'Jan 22', total: 150, success: 145, failed: 5 },
    { date: 'Jan 25', total: 220, success: 210, failed: 10 },
  ])

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0]
    if (uploadedFile) {
      setFile(uploadedFile)
      setActiveStep(1)
      // Simulate validation
      setTimeout(() => {
        setValidationResults({
          total: 150,
          valid: 145,
          invalid: 5,
          errors: [
            { row: 12, field: 'asset_name', error: 'Invalid naming format' },
            { row: 45, field: 'domain_id', error: 'Domain does not exist' },
            { row: 78, field: 'owner_id', error: 'Owner not found' },
            { row: 102, field: 'environment', error: 'Invalid environment value' },
            { row: 133, field: 'asset_name', error: 'Duplicate asset name' },
          ]
        })
        setActiveStep(2)
      }, 2000)
    }
  }

  const handleImport = () => {
    setActiveStep(3)
    setImportStatus({ progress: 0 })

    // Simulate import progress
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      setImportStatus({ progress })
      if (progress >= 100) {
        clearInterval(interval)
        setImportStatus({ progress: 100, completed: true, imported: 145, failed: 5 })
      }
    }, 500)
  }

  const handleReset = () => {
    setActiveStep(0)
    setFile(null)
    setValidationResults(null)
    setImportStatus(null)
    setError('')
  }

  // Chart data calculations
  const chartData = useMemo(() => {
    // Current validation breakdown (if available)
    const validationBreakdown = validationResults ? [
      { name: 'Valid', value: validationResults.valid, color: '#4caf50' },
      { name: 'Invalid', value: validationResults.invalid, color: '#f44336' },
    ] : []

    // Error type distribution
    const errorTypeCounts = validationResults?.errors.reduce((acc, error) => {
      acc[error.field] = (acc[error.field] || 0) + 1
      return acc
    }, {}) || {}
    const errorTypeData = Object.entries(errorTypeCounts)
      .map(([field, count]) => ({ field, count }))
      .sort((a, b) => b.count - a.count)

    // Import history summary
    const totalImports = importHistory.reduce((sum, h) => sum + h.total, 0)
    const totalSuccess = importHistory.reduce((sum, h) => sum + h.success, 0)
    const totalFailed = importHistory.reduce((sum, h) => sum + h.failed, 0)

    const historySummary = [
      { name: 'Successful', value: totalSuccess, color: '#4caf50' },
      { name: 'Failed', value: totalFailed, color: '#f44336' },
    ]

    return { validationBreakdown, errorTypeData, historySummary, importHistory }
  }, [validationResults, importHistory])

  const COLORS = ['#4caf50', '#f44336', '#ff9800', '#2196f3', '#9c27b0']

  // Define columns for validation errors table
  const errorColumns = [
    {
      id: 'row',
      label: 'Row',
      sortable: true,
    },
    {
      id: 'field',
      label: 'Field',
      sortable: true,
      render: (value) => <Chip label={value} size="small" />,
    },
    {
      id: 'error',
      label: 'Error',
      sortable: false,
      width: '50%',
    },
  ]

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Bulk Import Assets
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Import History Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Import History Summary - Pie Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AssessmentIcon color="primary" />
                Historical Import Summary
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={chartData.historySummary}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value, percent }) =>
                      `${name}: ${value} (${(percent * 100).toFixed(1)}%)`
                    }
                    outerRadius={80}
                    
                    dataKey="value"
                  >
                    {chartData.historySummary.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Import Trend - Line Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TimelineIcon color="secondary" />
                Import Activity Trend
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={chartData.importHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="success"
                    stroke="#4caf50"
                    strokeWidth={2}
                    name="Successful"
                    dot={{ fill: '#4caf50', r: 4 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="failed"
                    stroke="#f44336"
                    strokeWidth={2}
                    name="Failed"
                    dot={{ fill: '#f44336', r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Current Validation Breakdown (only show if validating or reviewing) */}
        {validationResults && chartData.validationBreakdown.length > 0 && (
          <>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Current Validation Results
                  </Typography>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={chartData.validationBreakdown}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value, percent }) =>
                          `${name}: ${value} (${(percent * 100).toFixed(1)}%)`
                        }
                        outerRadius={80}
                        
                        dataKey="value"
                      >
                        {chartData.validationBreakdown.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Error Type Distribution */}
            {chartData.errorTypeData.length > 0 && (
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Error Distribution by Field
                    </Typography>
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={chartData.errorTypeData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="field" tick={{ fontSize: 11 }} />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="count" name="Errors" radius={[8, 8, 0, 0]}>
                          {chartData.errorTypeData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </>
        )}
      </Grid>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Step 0: Upload */}
      {activeStep === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" sx={{ mb: 2 }}>
            Upload CSV or Excel File
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
            Supported formats: .csv, .xlsx, .xls
          </Typography>
          <Button
            variant="contained"
            component="label"
            startIcon={<UploadIcon />}
          >
            Select File
            <input
              type="file"
              hidden
              accept=".csv,.xlsx,.xls"
              onChange={handleFileUpload}
            />
          </Button>
        </Paper>
      )}

      {/* Step 1: Validating */}
      {activeStep === 1 && !validationResults && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" sx={{ mb: 3 }}>
            Validating {file?.name}...
          </Typography>
          <LinearProgress />
        </Paper>
      )}

      {/* Step 2: Review */}
      {activeStep === 2 && validationResults && (
        <Box>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="caption">Total Records</Typography>
                  <Typography variant="h4">{validationResults.total}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="caption">Valid Records</Typography>
                  <Typography variant="h4" color="success.main">{validationResults.valid}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card sx={{ borderLeft: '4px solid #d32f2f' }}>
                <CardContent>
                  <Typography variant="caption">Invalid Records</Typography>
                  <Typography variant="h4" color="error.main">{validationResults.invalid}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {validationResults.errors.length > 0 && (
            <Paper sx={{ mb: 3 }}>
              <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
                <Typography variant="h6">Validation Errors</Typography>
              </Box>
              <Box sx={{ p: 2 }}>
                <EnhancedTable
                  columns={errorColumns}
                  data={validationResults.errors}
                  loading={false}
                  defaultOrderBy="row"
                  defaultOrder="asc"
                  searchPlaceholder="Search errors..."
                  exportFileName="validation_errors"
                  rowsPerPageOptions={[5, 10, 25]}
                  dense={true}
                />
              </Box>
            </Paper>
          )}

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button variant="outlined" onClick={handleReset}>
              Cancel
            </Button>
            <Button variant="contained" onClick={handleImport}>
              Import {validationResults.valid} Valid Records
            </Button>
          </Box>
        </Box>
      )}

      {/* Step 3: Importing */}
      {activeStep === 3 && importStatus && (
        <Paper sx={{ p: 4 }}>
          {!importStatus.completed ? (
            <Box>
              <Typography variant="h6" sx={{ mb: 3 }}>
                Importing assets... {importStatus.progress}%
              </Typography>
              <LinearProgress variant="determinate" value={importStatus.progress} />
            </Box>
          ) : (
            <Box textAlign="center">
              <CheckIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              <Typography variant="h5" sx={{ mb: 2 }}>
                Import Completed!
              </Typography>
              <Grid container spacing={2} justifyContent="center" sx={{ mb: 3 }}>
                <Grid item>
                  <Chip
                    icon={<CheckIcon />}
                    label={`${importStatus.imported} Imported`}
                    color="success"
                  />
                </Grid>
                {importStatus.failed > 0 && (
                  <Grid item>
                    <Chip
                      icon={<ErrorIcon />}
                      label={`${importStatus.failed} Failed`}
                      color="error"
                    />
                  </Grid>
                )}
              </Grid>
              <Button variant="contained" onClick={handleReset} startIcon={<RefreshIcon />}>
                Import Another File
              </Button>
            </Box>
          )}
        </Paper>
      )}
    </Box>
  )
}

export default BulkImportDashboard
