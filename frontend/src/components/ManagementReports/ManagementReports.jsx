import React, { useEffect, useState } from 'react'
import axios from 'axios'
import {
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Paper,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import {
  TrendingUp,
  CheckCircle,
  Warning,
  Star,
  Assessment,
} from '@mui/icons-material'

function ManagementReports() {
  const [executiveSummary, setExecutiveSummary] = useState(null)
  const [governanceMaturity, setGovernanceMaturity] = useState(null)
  const [boardData, setBoardData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [execRes, govRes, boardRes] = await Promise.all([
        axios.get('/api/v1/reports/executive-summary'),
        axios.get('/api/v1/reports/governance-maturity'),
        axios.get('/api/v1/reports/board-presentation')
      ])
      setExecutiveSummary(execRes.data)
      setGovernanceMaturity(govRes.data)
      setBoardData(boardRes.data)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching reports:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Management Reports
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Executive-level reports for C-suite and board presentation
      </Typography>

      {/* Executive Summary */}
      <Card sx={{ mt: 2, backgroundColor: '#E3F2FD' }}>
        <CardContent>
          <Typography variant="h5" gutterBottom color="primary">
            Executive Summary - {executiveSummary?.report_period}
          </Typography>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#FFFFFF' }}>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {executiveSummary?.executive_summary?.overall_health_score}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Overall Health Score
                </Typography>
                <Chip
                  label={executiveSummary?.executive_summary?.trend}
                  color="success"
                  size="small"
                  sx={{ mt: 1 }}
                />
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#FFFFFF' }}>
                <Typography variant="h3" color="success.main" fontWeight="bold">
                  {executiveSummary?.financial_summary?.roi_generated}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  ROI Generated
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Investment: {executiveSummary?.financial_summary?.total_budget}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#FFFFFF' }}>
                <Typography variant="h3" color="success.main" fontWeight="bold">
                  {executiveSummary?.financial_summary?.projected_savings}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Projected Savings
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Under budget this fiscal year
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Key Achievements */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Key Achievements
          </Typography>
          <List>
            {executiveSummary?.executive_summary?.key_achievements?.map((achievement, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <CheckCircle sx={{ color: '#4CAF50' }} />
                </ListItemIcon>
                <ListItemText primary={achievement} />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Strategic KPIs */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Strategic KPIs
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {Object.entries(executiveSummary?.strategic_kpis || {}).map(([key, kpi]) => (
              <Grid item xs={12} sm={6} md={3} key={key}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    {key.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {kpi.value}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Target: {kpi.target}
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <Chip
                      label={kpi.status}
                      size="small"
                      color={
                        kpi.status === 'Exceeding' ? 'success' :
                        kpi.status === 'On Track' ? 'primary' : 'warning'
                      }
                    />
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Governance Maturity */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Governance Maturity Assessment
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" color="textSecondary">
                Current Maturity Level
              </Typography>
              <Typography variant="h3" color="primary" fontWeight="bold">
                Level {governanceMaturity?.current_maturity_level}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                CMMI: Defined
              </Typography>
            </Box>
            <TrendingUp sx={{ fontSize: 60, color: '#1976D2' }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" color="textSecondary">
                Target Maturity Level
              </Typography>
              <Typography variant="h3" color="success.main" fontWeight="bold">
                Level {governanceMaturity?.target_maturity_level}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                CMMI: Measured
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Maturity Breakdown
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {Object.entries(governanceMaturity?.maturity_breakdown || {}).map(([key, data]) => (
              <Grid item xs={12} sm={6} md={4} key={key}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="body2" fontWeight="500">
                    {key.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                    <Typography variant="h6" fontWeight="bold">
                      {data.score}%
                    </Typography>
                    <Chip
                      label={data.status}
                      size="small"
                      color={data.status === 'Strength' ? 'success' : 'info'}
                    />
                  </Box>
                  <Typography variant="caption" color="textSecondary">
                    Level {data.level}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Board Presentation Summary */}
      <Card sx={{ mt: 3, backgroundColor: '#FFF3E0' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Star sx={{ color: '#FF9800' }} />
            <Typography variant="h5" color="#E65100">
              Board Presentation Summary
            </Typography>
          </Box>

          <Grid container spacing={2}>
            {boardData?.key_messages?.map((message, index) => (
              <Grid item xs={12} key={index}>
                <Paper sx={{ p: 2, backgroundColor: '#FFFFFF' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CheckCircle sx={{ color: '#4CAF50' }} />
                    <Typography variant="body1">{message}</Typography>
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            Strategic Highlights
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {Object.entries(boardData?.strategic_highlights || {}).map(([key, value]) => (
              <Grid item xs={12} sm={6} key={key}>
                <Box sx={{ p: 2, backgroundColor: '#FFFFFF', borderRadius: 1 }}>
                  <Typography variant="body2" color="textSecondary">
                    {key.replace(/_/g, ' ').toUpperCase()}
                  </Typography>
                  <Typography variant="h6" fontWeight="bold" color="primary">
                    {value}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Risks and Mitigation */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Risks & Mitigation
          </Typography>
          {boardData?.risks_and_mitigation?.map((risk, index) => (
            <Paper key={index} sx={{ p: 2, mb: 2, backgroundColor: risk.status === 'Mitigated' ? '#E8F5E9' : '#FFF9C4' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="body1" fontWeight="500">
                  {risk.risk}
                </Typography>
                <Chip
                  label={risk.impact}
                  color={risk.impact === 'High' ? 'error' : 'warning'}
                  size="small"
                />
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                <strong>Mitigation:</strong> {risk.mitigation}
              </Typography>
              <Chip
                label={risk.status}
                color={risk.status === 'Mitigated' ? 'success' : 'info'}
                size="small"
              />
            </Paper>
          ))}
        </CardContent>
      </Card>

      {/* Next Quarter Priorities */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Next Quarter Priorities
          </Typography>
          <List>
            {boardData?.next_quarter_priorities?.map((priority, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <Assessment sx={{ color: '#1976D2' }} />
                </ListItemIcon>
                <ListItemText
                  primary={priority}
                  primaryTypographyProps={{ fontWeight: 500 }}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  )
}

export default ManagementReports
