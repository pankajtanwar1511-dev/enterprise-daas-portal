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
} from '@mui/material'
import EnhancedTable from '../common/EnhancedTable'
import { Groups, TrendingUp, Business, Stars } from '@mui/icons-material'

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

function StakeholdersManagement() {
  const [stakeholders, setStakeholders] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    champions: 0,
    supporters: 0,
    executives: 0,
  })

  useEffect(() => {
    fetchStakeholders()
  }, [])

  const fetchStakeholders = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/stakeholders/')
      const data = response.data || []
      setStakeholders(data)

      // Calculate stats
      const champions = data.filter(s => s.engagement_level === 'Champion').length
      const supporters = data.filter(s => s.engagement_level === 'Supporter').length
      const executives = data.filter(s => s.influence_level === 'Executive').length

      setStats({
        total: data.length,
        champions,
        supporters,
        executives,
      })

      setLoading(false)
    } catch (error) {
      console.error('Error fetching stakeholders:', error)
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
      id: 'stakeholder_name',
      label: 'Name',
      sortable: true,
      render: (value) => (
        <Typography variant="body1" fontWeight="600">
          {value}
        </Typography>
      ),
    },
    {
      id: 'role',
      label: 'Role',
      sortable: true,
      render: (value) => (
        <Typography variant="body2">
          {value}
        </Typography>
      ),
    },
    {
      id: 'department',
      label: 'Department',
      sortable: true,
      render: (value) => (
        <Chip label={value} size="small" color="default" />
      ),
    },
    {
      id: 'email',
      label: 'Email',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" color="textSecondary">
          {value}
        </Typography>
      ),
    },
    {
      id: 'engagement_level',
      label: 'Engagement',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={
            value === 'Champion' ? 'success' :
            value === 'Supporter' ? 'primary' :
            value === 'Neutral' ? 'default' :
            'warning'
          }
        />
      ),
    },
    {
      id: 'influence_level',
      label: 'Influence',
      sortable: true,
      align: 'center',
      render: (value) => (
        <Chip
          label={value}
          size="small"
          variant="outlined"
          color={
            value === 'Executive' ? 'error' :
            value === 'High' ? 'warning' :
            value === 'Medium' ? 'primary' :
            'default'
          }
        />
      ),
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Stakeholder Management
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Track business stakeholders, their engagement levels, and data needs across the organization
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Stakeholders"
            value={stats.total}
            subtitle="Across all departments"
            icon={<Groups sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Champions"
            value={stats.champions}
            subtitle="High engagement"
            icon={<Stars sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Supporters"
            value={stats.supporters}
            subtitle="Active supporters"
            icon={<TrendingUp sx={{ fontSize: 40 }} />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Executive Level"
            value={stats.executives}
            subtitle="C-level influence"
            icon={<Business sx={{ fontSize: 40 }} />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Stakeholders Table */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">
              Stakeholder Directory
            </Typography>
          </Box>
          <EnhancedTable
            columns={columns}
            data={stakeholders}
            loading={false}
            onRefresh={fetchStakeholders}
            defaultOrderBy="stakeholder_name"
            defaultOrder="asc"
            searchPlaceholder="Search stakeholders..."
            exportFileName="stakeholders"
            rowsPerPageOptions={[10, 25, 50, 100]}
          />
        </CardContent>
      </Card>

      {/* Engagement Level Summary */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Engagement Level Distribution
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#E8F5E9' }}>
                <Typography variant="h3" color="success.main" fontWeight="bold">
                  {stats.champions}
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  Champions
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Highly engaged and influential
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#E3F2FD' }}>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {stats.supporters}
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  Supporters
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Actively support DaaS initiatives
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#FFF3E0' }}>
                <Typography variant="h3" color="warning.main" fontWeight="bold">
                  {stakeholders.filter(s => s.engagement_level === 'Neutral' || s.engagement_level === 'Observer').length}
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  Neutral/Observer
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Require engagement initiatives
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Influence Level Summary */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Influence Level Distribution
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', border: '2px solid #F44336' }}>
                <Typography variant="h3" color="error.main" fontWeight="bold">
                  {stats.executives}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Executive
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', border: '2px solid #FF9800' }}>
                <Typography variant="h3" color="warning.main" fontWeight="bold">
                  {stakeholders.filter(s => s.influence_level === 'High').length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  High
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', border: '2px solid #2196F3' }}>
                <Typography variant="h3" color="primary" fontWeight="bold">
                  {stakeholders.filter(s => s.influence_level === 'Medium').length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Medium
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', border: '2px solid #9E9E9E' }}>
                <Typography variant="h3" color="text.secondary" fontWeight="bold">
                  {stakeholders.filter(s => s.influence_level === 'Low').length}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Low
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}

export default StakeholdersManagement
