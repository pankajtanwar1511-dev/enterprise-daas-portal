import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Divider,
  Tab,
  Tabs,
  Avatar,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  TrendingUp as StrategyIcon,
  Business as VendorIcon,
  Assessment as ReportsIcon,
  Inventory2 as AssetsIcon,
  CheckCircle as ValidatorIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  AutoGraph as AnalyticsIcon,
  Build as ToolsIcon,
  Rocket as RocketIcon,
  EmojiEvents as TrophyIcon,
  School as LearnIcon,
  Support as SupportIcon,
  ArrowForward as ArrowIcon,
  Star as StarIcon,
  Timeline as LineageIcon,
  VerifiedUser as ComplianceIcon,
  Code as CodeIcon,
  CloudQueue as CloudIcon,
} from '@mui/icons-material'

const WelcomePage = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(0)

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue)
  }

  // Role-based feature cards
  const roleFeatures = {
    executives: [
      {
        title: 'Dashboard',
        description: 'Real-time KPIs and health metrics for your entire data estate',
        icon: <DashboardIcon sx={{ fontSize: 40, color: '#1976D2' }} />,
        path: '/',
        stat: '127+ Assets',
      },
      {
        title: 'DaaS Strategy',
        description: 'Track business goals, ROI, and initiative progress',
        icon: <StrategyIcon sx={{ fontSize: 40, color: '#2E7D32' }} />,
        path: '/strategy',
        stat: '$2.3M ROI',
      },
      {
        title: 'Vendor & Budget',
        description: 'Manage vendor contracts and track spend',
        icon: <VendorIcon sx={{ fontSize: 40, color: '#ED6C02' }} />,
        path: '/vendors',
        stat: '$80K Saved',
      },
      {
        title: 'Management Reports',
        description: 'Auto-generate board presentations in seconds',
        icon: <ReportsIcon sx={{ fontSize: 40, color: '#9C27B0' }} />,
        path: '/reports',
        stat: '15hr → 10min',
      },
    ],
    stewards: [
      {
        title: 'Compliance Dashboard',
        description: 'Monitor 95%+ compliance across all assets',
        icon: <ComplianceIcon sx={{ fontSize: 40, color: '#1976D2' }} />,
        path: '/compliance',
        stat: '94% Compliant',
      },
      {
        title: 'Data Quality',
        description: 'Prevent bad decisions with automated quality checks',
        icon: <VerifiedUser sx={{ fontSize: 40, color: '#2E7D32' }} />,
        path: '/data-quality',
        stat: '98% Quality',
      },
      {
        title: 'Data Lineage',
        description: 'Trace data from source to consumption in seconds',
        icon: <LineageIcon sx={{ fontSize: 40, color: '#ED6C02' }} />,
        path: '/data-lineage',
        stat: '8hr → 20min',
      },
      {
        title: 'Audit Logs',
        description: 'Tamper-proof audit trail for compliance',
        icon: <SecurityIcon sx={{ fontSize: 40, color: '#D32F2F' }} />,
        path: '/audit-logs',
        stat: '100% Tracked',
      },
    ],
    developers: [
      {
        title: 'Naming Validator',
        description: 'Enforce standards before deployment',
        icon: <ValidatorIcon sx={{ fontSize: 40, color: '#1976D2' }} />,
        path: '/validator',
        stat: '5min → 30sec',
      },
      {
        title: 'Impact Analysis',
        description: 'Know what breaks before making changes',
        icon: <AnalyticsIcon sx={{ fontSize: 40, color: '#2E7D32' }} />,
        path: '/impact-analysis',
        stat: '70% ↓ Incidents',
      },
      {
        title: 'CI/CD Policies',
        description: 'Automated quality gates in your pipeline',
        icon: <CodeIcon sx={{ fontSize: 40, color: '#ED6C02' }} />,
        path: '/policy-enforcement',
        stat: 'Auto-Enforce',
      },
      {
        title: 'Integration Logs',
        description: 'Debug integrations in minutes, not hours',
        icon: <ToolsIcon sx={{ fontSize: 40, color: '#9C27B0' }} />,
        path: '/integration-logs',
        stat: '80% Faster',
      },
    ],
    devops: [
      {
        title: 'SLA Monitoring',
        description: 'Track vendor performance and claim SLA credits',
        icon: <SpeedIcon sx={{ fontSize: 40, color: '#1976D2' }} />,
        path: '/sla-monitoring',
        stat: '99.9% Uptime',
      },
      {
        title: 'Webhooks',
        description: 'Real-time alerts to Slack, Teams, JIRA, PagerDuty',
        icon: <CloudIcon sx={{ fontSize: 40, color: '#2E7D32' }} />,
        path: '/webhooks',
        stat: '247 Events',
      },
      {
        title: 'API Keys',
        description: 'Centralized key management with auto-rotation',
        icon: <SecurityIcon sx={{ fontSize: 40, color: '#ED6C02' }} />,
        path: '/api-keys',
        stat: '90-day Rotate',
      },
      {
        title: 'Schema Registry',
        description: 'Prevent breaking changes across services',
        icon: <ToolsIcon sx={{ fontSize: 40, color: '#9C27B0' }} />,
        path: '/schema-registry',
        stat: 'Zero Breaks',
      },
    ],
  }

  const stats = [
    { label: 'Total Assets', value: '127', icon: <AssetsIcon />, color: '#1976D2' },
    { label: 'Compliance Rate', value: '94%', icon: <ComplianceIcon />, color: '#2E7D32' },
    { label: 'ROI Achieved', value: '$2.3M', icon: <TrophyIcon />, color: '#ED6C02' },
    { label: 'Time Saved', value: '90%', icon: <SpeedIcon />, color: '#9C27B0' },
  ]

  const successStories = [
    {
      team: 'Finance Team',
      challenge: 'Missing revenue data in quarterly reports',
      solution: 'Data Quality + Integration Logs',
      result: '15 minutes to fix (vs. 8 hours)',
      icon: '💰',
    },
    {
      team: 'Sales Operations',
      challenge: '200 legacy assets in Excel needed migration',
      solution: 'Bulk Import',
      result: '18 hours → 30 minutes',
      icon: '📊',
    },
    {
      team: 'Engineering Team',
      challenge: 'Production API change broke mobile app',
      solution: 'Schema Registry + Impact Analysis',
      result: 'Zero breaking changes since',
      icon: '🚀',
    },
  ]

  const quickStartSteps = [
    { step: 1, title: 'See the Big Picture', action: 'Go to Dashboard', path: '/' },
    { step: 2, title: 'Explore Your Assets', action: 'Browse Asset Registry', path: '/assets' },
    { step: 3, title: 'Check Compliance', action: 'View Compliance Dashboard', path: '/compliance' },
    { step: 4, title: 'Learn the Tools', action: 'Try Naming Validator', path: '/validator' },
  ]

  return (
    <Box sx={{ backgroundColor: '#F5F5F5', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="xl">
        {/* Hero Section */}
        <Paper
          elevation={0}
          sx={{
            background: 'linear-gradient(135deg, #0D47A1 0%, #1976D2 50%, #42A5F5 100%)',
            color: 'white',
            p: 6,
            borderRadius: 4,
            mb: 4,
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <Box sx={{ position: 'relative', zIndex: 1 }}>
            <Chip
              label="Version 2.0"
              sx={{
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 600,
                mb: 2,
              }}
            />
            <Typography variant="h3" fontWeight={700} gutterBottom>
              Welcome to Enterprise DaaS Governance Portal
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.95, maxWidth: '800px', mb: 3 }}>
              Your Command Center for Data Governance, Strategy, and Operations
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9, maxWidth: '700px', mb: 4 }}>
              Transform data governance from a compliance checkbox to a strategic business enabler.
              Manage 127+ assets, track $2.3M ROI, and maintain 94% compliance—all in one unified platform.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="large"
                endIcon={<RocketIcon />}
                onClick={() => navigate('/')}
                sx={{
                  backgroundColor: 'white',
                  color: '#0D47A1',
                  fontWeight: 600,
                  '&:hover': { backgroundColor: '#E3F2FD' },
                }}
              >
                Get Started
              </Button>
              <Button
                variant="outlined"
                size="large"
                endIcon={<LearnIcon />}
                sx={{
                  borderColor: 'white',
                  color: 'white',
                  fontWeight: 600,
                  '&:hover': {
                    borderColor: 'white',
                    backgroundColor: 'rgba(255,255,255,0.1)',
                  },
                }}
              >
                View Documentation
              </Button>
            </Box>
          </Box>
          {/* Decorative circles */}
          <Box
            sx={{
              position: 'absolute',
              top: -100,
              right: -100,
              width: 400,
              height: 400,
              borderRadius: '50%',
              backgroundColor: 'rgba(255,255,255,0.1)',
            }}
          />
          <Box
            sx={{
              position: 'absolute',
              bottom: -150,
              left: -150,
              width: 500,
              height: 500,
              borderRadius: '50%',
              backgroundColor: 'rgba(255,255,255,0.05)',
            }}
          />
        </Paper>

        {/* Stats Section */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                elevation={2}
                sx={{
                  height: '100%',
                  borderTop: `4px solid ${stat.color}`,
                  transition: 'transform 0.2s',
                  '&:hover': { transform: 'translateY(-4px)' },
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ backgroundColor: stat.color, mr: 2 }}>{stat.icon}</Avatar>
                    <Box>
                      <Typography variant="h4" fontWeight={700} color={stat.color}>
                        {stat.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {stat.label}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Features by Role */}
        <Paper elevation={2} sx={{ mb: 4, borderRadius: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 3, pt: 2 }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab
                label="For Executives"
                icon={<TrophyIcon />}
                iconPosition="start"
                sx={{ textTransform: 'none', fontWeight: 600 }}
              />
              <Tab
                label="For Data Stewards"
                icon={<ComplianceIcon />}
                iconPosition="start"
                sx={{ textTransform: 'none', fontWeight: 600 }}
              />
              <Tab
                label="For Developers"
                icon={<CodeIcon />}
                iconPosition="start"
                sx={{ textTransform: 'none', fontWeight: 600 }}
              />
              <Tab
                label="For DevOps"
                icon={<CloudIcon />}
                iconPosition="start"
                sx={{ textTransform: 'none', fontWeight: 600 }}
              />
            </Tabs>
          </Box>
          <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
              {roleFeatures[
                ['executives', 'stewards', 'developers', 'devops'][activeTab]
              ].map((feature, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card
                    elevation={1}
                    sx={{
                      height: '100%',
                      transition: 'all 0.2s',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: 4,
                      },
                    }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                        <Box sx={{ mr: 2 }}>{feature.icon}</Box>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="h6" fontWeight={600} gutterBottom>
                            {feature.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            {feature.description}
                          </Typography>
                          <Chip
                            label={feature.stat}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        </Box>
                      </Box>
                    </CardContent>
                    <CardActions>
                      <Button
                        size="small"
                        endIcon={<ArrowIcon />}
                        onClick={() => navigate(feature.path)}
                      >
                        Explore
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Paper>

        <Grid container spacing={4}>
          {/* Quick Start Guide */}
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 3, height: '100%', borderRadius: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <RocketIcon sx={{ fontSize: 32, color: '#1976D2', mr: 1 }} />
                <Typography variant="h5" fontWeight={600}>
                  Quick Start (5 minutes)
                </Typography>
              </Box>
              <List>
                {quickStartSteps.map((item, index) => (
                  <React.Fragment key={index}>
                    <ListItem
                      sx={{
                        backgroundColor: '#F5F5F5',
                        borderRadius: 2,
                        mb: 2,
                        '&:hover': { backgroundColor: '#E3F2FD' },
                      }}
                    >
                      <ListItemIcon>
                        <Avatar sx={{ backgroundColor: '#1976D2', width: 32, height: 32 }}>
                          {item.step}
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={item.title}
                        secondary={item.action}
                        primaryTypographyProps={{ fontWeight: 600 }}
                      />
                      <IconButton onClick={() => navigate(item.path)} color="primary">
                        <ArrowIcon />
                      </IconButton>
                    </ListItem>
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Success Stories */}
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 3, height: '100%', borderRadius: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <TrophyIcon sx={{ fontSize: 32, color: '#ED6C02', mr: 1 }} />
                <Typography variant="h5" fontWeight={600}>
                  Success Stories
                </Typography>
              </Box>
              {successStories.map((story, index) => (
                <Card
                  key={index}
                  elevation={0}
                  sx={{
                    backgroundColor: '#F5F5F5',
                    mb: 2,
                    borderLeft: '4px solid #ED6C02',
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Typography variant="h4" sx={{ mr: 1 }}>
                        {story.icon}
                      </Typography>
                      <Typography variant="subtitle1" fontWeight={600}>
                        {story.team}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      <strong>Challenge:</strong> {story.challenge}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      <strong>Solution:</strong> {story.solution}
                    </Typography>
                    <Chip
                      label={story.result}
                      size="small"
                      color="success"
                      icon={<StarIcon />}
                    />
                  </CardContent>
                </Card>
              ))}
            </Paper>
          </Grid>
        </Grid>

        {/* Help Section */}
        <Paper elevation={2} sx={{ mt: 4, p: 4, borderRadius: 3, textAlign: 'center' }}>
          <SupportIcon sx={{ fontSize: 48, color: '#1976D2', mb: 2 }} />
          <Typography variant="h5" fontWeight={600} gutterBottom>
            Need Help?
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            We're here to help you succeed. Access documentation, join training, or contact support.
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Button variant="outlined" startIcon={<LearnIcon />}>
              View Documentation
            </Button>
            <Button variant="outlined" startIcon={<School />}>
              Training Schedule
            </Button>
            <Button variant="contained" startIcon={<SupportIcon />}>
              Contact Support
            </Button>
          </Box>
        </Paper>
      </Container>
    </Box>
  )
}

export default WelcomePage
