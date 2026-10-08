import React, { useState } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Card,
  CardContent,
} from '@mui/material'
import { Error, CheckCircle, Lightbulb, Info } from '@mui/icons-material'

function NamingValidator() {
  const [assetName, setAssetName] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleValidate = async () => {
    if (!assetName.trim()) return

    setLoading(true)
    try {
      const response = await axiosInstance.post('/api/v1/compliance/validate/naming', {
        asset_name: assetName,
      })
      setResult(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Validation error:', error)
      setLoading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Naming Convention Validator
      </Typography>

      <Typography variant="body1" color="textSecondary" paragraph>
        Validate asset names against the enterprise naming convention standard before registration.
      </Typography>

      {/* Naming Standard Card */}
      <Card sx={{ mb: 3, backgroundColor: '#E3F2FD' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Info color="primary" />
            <Typography variant="h6" color="primary">
              Naming Convention Standard
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ fontFamily: 'monospace', fontSize: '1.1rem', fontWeight: 500 }}>
            {'{ENV}'}-{'{DOMAIN}'}-{'{SYSTEM}'}-{'{VERSION}'}
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            <strong>Example:</strong> PROD-HR-DW-v1
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body2" color="textSecondary">
            <strong>ENV:</strong> DEV, QA, UAT, PROD<br />
            <strong>DOMAIN:</strong> HR, FIN, OPS, SALES, IT, DATA<br />
            <strong>SYSTEM:</strong> 2-10 alphanumeric characters<br />
            <strong>VERSION:</strong> v{'{major}'} or v{'{major}'}.{'{minor}'} (e.g., v1, v2.1)
          </Typography>
        </CardContent>
      </Card>

      {/* Validation Form */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Enter Asset Name to Validate
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
          <TextField
            fullWidth
            label="Asset Name"
            value={assetName}
            onChange={(e) => setAssetName(e.target.value)}
            placeholder="PROD-HR-DW-v1"
            sx={{ fontFamily: 'monospace' }}
            onKeyPress={(e) => {
              if (e.key === 'Enter') handleValidate()
            }}
          />
          <Button
            variant="contained"
            onClick={handleValidate}
            disabled={!assetName.trim() || loading}
            sx={{ minWidth: 120, height: 56 }}
          >
            {loading ? 'Validating...' : 'Validate'}
          </Button>
        </Box>
      </Paper>

      {/* Validation Results */}
      {result && (
        <Box sx={{ mt: 3 }}>
          {result.valid ? (
            <Alert severity="success" icon={<CheckCircle />} sx={{ mb: 2 }}>
              <AlertTitle sx={{ fontSize: '1.1rem', fontWeight: 600 }}>
                Compliant
              </AlertTitle>
              Asset name <strong>{assetName}</strong> complies with naming convention standard.
              You can proceed with registration.
            </Alert>
          ) : (
            <>
              <Alert severity="error" icon={<Error />} sx={{ mb: 2 }}>
                <AlertTitle sx={{ fontSize: '1.1rem', fontWeight: 600 }}>
                  Non-Compliant
                </AlertTitle>
                Asset name <strong>{assetName}</strong> does not comply with naming convention.
                Please fix the violations below.
              </Alert>

              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6" color="error" gutterBottom>
                  Violations
                </Typography>
                <List>
                  {result.violations.map((violation, index) => (
                    <ListItem key={index} sx={{ alignItems: 'flex-start' }}>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <Error color="error" />
                      </ListItemIcon>
                      <ListItemText primary={violation} />
                    </ListItem>
                  ))}
                </List>
              </Paper>

              {result.suggestions && result.suggestions.length > 0 && (
                <Paper sx={{ p: 2, backgroundColor: '#FFF9C4' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Lightbulb color="warning" />
                    <Typography variant="h6" color="warning.dark">
                      Suggestions
                    </Typography>
                  </Box>
                  <List>
                    {result.suggestions.map((suggestion, index) => (
                      <ListItem key={index} sx={{ alignItems: 'flex-start' }}>
                        <ListItemIcon sx={{ minWidth: 40 }}>
                          <Lightbulb color="warning" />
                        </ListItemIcon>
                        <ListItemText primary={suggestion} />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              )}
            </>
          )}
        </Box>
      )}

      {/* Examples */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Examples
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CheckCircle color="success" />
              <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                PROD-HR-DW-v1
              </Typography>
              <Typography variant="body2" color="textSecondary">
                (HR Data Warehouse Production)
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CheckCircle color="success" />
              <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                QA-FIN-ETL-v2.3
              </Typography>
              <Typography variant="body2" color="textSecondary">
                (Finance ETL QA environment)
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Error color="error" />
              <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                production-hr-dw
              </Typography>
              <Typography variant="body2" color="textSecondary">
                (Missing version, wrong format)
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}

export default NamingValidator
