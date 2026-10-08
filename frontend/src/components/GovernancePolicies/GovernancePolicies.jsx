import React, { useEffect, useState } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import { Security, Policy, Gavel, VerifiedUser, ExpandMore } from '@mui/icons-material'

function MetricCard({ title, value, subtitle, icon, color = 'primary' }) {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, color: color === 'success' ? '#4CAF50' : '#1976D2' }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ color: color === 'success' ? '#4CAF50' : '#1976D2' }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

function GovernancePolicies() {
  const [policies, setPolicies] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    mandatory: 0,
    enforced: 0,
  })

  useEffect(() => {
    fetchPolicies()
  }, [])

  const fetchPolicies = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/governance/policies')
      const data = response.data || []
      setPolicies(data)

      // Calculate stats
      const active = data.filter(p => p.status === 'Active').length
      const mandatory = data.filter(p => p.enforcement_level === 'Mandatory').length
      const enforced = data.filter(p => p.status === 'Active' && p.enforcement_level === 'Mandatory').length

      setStats({
        total: data.length,
        active,
        mandatory,
        enforced,
      })

      setLoading(false)
    } catch (error) {
      console.error('Error fetching policies:', error)
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

  const columns = [
    {
      id: 'policy_name',
      label: 'Policy Name',
      sortable: true,
      render: (value) => (
        <Typography variant="body1" fontWeight="600">
          {value}
        </Typography>
      ),
    },
    {
      id: 'policy_type',
      label: 'Type',
      sortable: true,
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={
            value === 'Security' ? 'error' :
            value === 'Compliance' ? 'warning' :
            value === 'Data Quality' ? 'info' :
            'default'
          }
        />
      ),
    },
    {
      id: 'enforcement_level',
      label: 'Enforcement',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          size="small"
          variant="outlined"
          color={
            value === 'Mandatory' ? 'error' :
            value === 'Recommended' ? 'warning' :
            'default'
          }
        />
      ),
    },
    {
      id: 'status',
      label: 'Status',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={value === 'Active' ? 'success' : 'default'}
        />
      ),
    },
    {
      id: 'applicability',
      label: 'Applies To',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" color="textSecondary">
          {value || 'All Assets'}
        </Typography>
      ),
    },
    {
      id: 'violation_severity',
      label: 'Severity',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={
            value === 'Critical' ? 'error' :
            value === 'High' ? 'warning' :
            value === 'Medium' ? 'info' :
            'default'
          }
        />
      ),
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Governance Policies
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Manage and enforce governance policies for data assets, compliance, and security standards
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Policies"
            value={stats.total}
            subtitle="Across all domains"
            icon={<Policy sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Policies"
            value={stats.active}
            subtitle="Currently enforced"
            icon={<VerifiedUser sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Mandatory"
            value={stats.mandatory}
            subtitle="Must be complied with"
            icon={<Gavel sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Enforced"
            value={stats.enforced}
            subtitle="Active & mandatory"
            icon={<Security sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Policies Table */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">
              Policy Directory
            </Typography>
          </Box>
          <EnhancedTable
            columns={columns}
            data={policies}
            loading={false}
            onRefresh={fetchPolicies}
            defaultOrderBy="policy_name"
            defaultOrder="asc"
            searchPlaceholder="Search policies..."
            exportFileName="governance_policies"
            rowsPerPageOptions={[10, 25, 50, 100]}
          />
        </CardContent>
      </Card>

      {/* Policy Type Distribution */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Policy Type Distribution
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#FFEBEE' }}>
                <Typography variant="h3" color="error.main" fontWeight="bold">
                  {policies.filter(p => p.policy_type === 'Security').length}
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  Security Policies
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Data protection and access control
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#FFF3E0' }}>
                <Typography variant="h3" color="warning.main" fontWeight="bold">
                  {policies.filter(p => p.policy_type === 'Compliance').length}
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  Compliance Policies
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Regulatory and legal requirements
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#E3F2FD' }}>
                <Typography variant="h3" color="info.main" fontWeight="bold">
                  {policies.filter(p => p.policy_type === 'Data Quality').length}
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  Data Quality Policies
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Data standards and validation
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Policy Details Accordion */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Policy Details
          </Typography>
          <Box sx={{ mt: 2 }}>
            {policies.slice(0, 5).map((policy, index) => (
              <Accordion key={index} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                    <Typography variant="body1" fontWeight="600" sx={{ flex: 1 }}>
                      {policy.policy_name}
                    </Typography>
                    <Chip
                      label={policy.policy_type}
                      size="small"
                      color={
                        policy.policy_type === 'Security' ? 'error' :
                        policy.policy_type === 'Compliance' ? 'warning' :
                        'info'
                      }
                    />
                    <Chip
                      label={policy.enforcement_level}
                      size="small"
                      variant="outlined"
                      color={policy.enforcement_level === 'Mandatory' ? 'error' : 'warning'}
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Typography variant="body2" paragraph>
                        {policy.description || 'No description available'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="caption" color="textSecondary">Status:</Typography>
                      <Typography variant="body2" fontWeight="600">
                        {policy.status}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="caption" color="textSecondary">Violation Severity:</Typography>
                      <Typography variant="body2" fontWeight="600">
                        {policy.violation_severity}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="caption" color="textSecondary">Applicability:</Typography>
                      <Typography variant="body2">
                        {policy.applicability || 'All Assets'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="caption" color="textSecondary">Exemption Allowed:</Typography>
                      <Typography variant="body2">
                        {policy.exemption_allowed ? 'Yes' : 'No'}
                      </Typography>
                    </Grid>
                    {policy.exemption_process && (
                      <Grid item xs={12}>
                        <Typography variant="caption" color="textSecondary">Exemption Process:</Typography>
                        <Typography variant="body2">
                          {policy.exemption_process}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Enforcement Level Summary */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Enforcement Level Summary
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', border: '2px solid #F44336' }}>
                <Typography variant="h3" color="error.main" fontWeight="bold">
                  {stats.mandatory}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Mandatory
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Must be complied with
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', border: '2px solid #FF9800' }}>
                <Typography variant="h3" color="warning.main" fontWeight="bold">
                  {policies.filter(p => p.enforcement_level === 'Recommended').length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Recommended
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Best practice guidelines
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', border: '2px solid #2196F3' }}>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {policies.filter(p => p.enforcement_level === 'Optional').length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Optional
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Discretionary application
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}

export default GovernancePolicies
