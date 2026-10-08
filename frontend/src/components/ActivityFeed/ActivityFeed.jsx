import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Stack,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import axiosInstance from '../../utils/axiosInstance';

const ActivityFeed = ({ entityType = null, entityId = null, limit = 20 }) => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    entity_type: entityType || '',
    action: '',
    days: 7
  });

  useEffect(() => {
    fetchActivities();
  }, [filters, entityType, entityId]);

  const fetchActivities = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = `/api/v1/activity?limit=${limit}`;

      if (entityType && entityId) {
        url = `/api/v1/activity/entity/${entityType}/${entityId}?limit=${limit}`;
      } else {
        const params = new URLSearchParams();
        if (filters.entity_type) params.append('entity_type', filters.entity_type);
        if (filters.action) params.append('action', filters.action);
        if (filters.days) params.append('days', filters.days);

        url += `&${params.toString()}`;
      }

      const response = await axiosInstance.get(url);
      setActivities(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch activities');
      console.error('Error fetching activities:', err);
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action) => {
    const colors = {
      created: 'success',
      updated: 'info',
      deleted: 'error',
      approved: 'success',
      rejected: 'error',
      commented: 'primary',
      assigned: 'warning',
      completed: 'success',
      status_changed: 'info'
    };
    return colors[action] || 'default';
  };

  const getEntityIcon = (entityType) => {
    const icons = {
      asset: '📦',
      change_request: '🔄',
      initiative: '🎯',
      business_goal: '🎪',
      task: '✅',
      vendor: '🏢',
      sla: '📋'
    };
    return icons[entityType] || '📄';
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatRelativeTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  return (
    <Box>
      {/* Filters (only show if not entity-specific) */}
      {!entityType && !entityId && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Entity Type</InputLabel>
                  <Select
                    value={filters.entity_type}
                    label="Entity Type"
                    onChange={(e) => setFilters({ ...filters, entity_type: e.target.value })}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="asset">Assets</MenuItem>
                    <MenuItem value="change_request">Change Requests</MenuItem>
                    <MenuItem value="initiative">Initiatives</MenuItem>
                    <MenuItem value="task">Tasks</MenuItem>
                    <MenuItem value="vendor">Vendors</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Action</InputLabel>
                  <Select
                    value={filters.action}
                    label="Action"
                    onChange={(e) => setFilters({ ...filters, action: e.target.value })}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="created">Created</MenuItem>
                    <MenuItem value="updated">Updated</MenuItem>
                    <MenuItem value="deleted">Deleted</MenuItem>
                    <MenuItem value="approved">Approved</MenuItem>
                    <MenuItem value="rejected">Rejected</MenuItem>
                    <MenuItem value="commented">Commented</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Time Range</InputLabel>
                  <Select
                    value={filters.days}
                    label="Time Range"
                    onChange={(e) => setFilters({ ...filters, days: e.target.value })}
                  >
                    <MenuItem value={1}>Last 24 hours</MenuItem>
                    <MenuItem value={7}>Last 7 days</MenuItem>
                    <MenuItem value={30}>Last 30 days</MenuItem>
                    <MenuItem value={90}>Last 90 days</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Activity Timeline */}
      {loading ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Loading activities...
          </Typography>
        </Box>
      ) : error ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="error">
            {error}
          </Typography>
        </Box>
      ) : activities.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            No activities found
          </Typography>
        </Box>
      ) : (
        <Timeline position="right">
          {activities.map((activity, index) => (
            <TimelineItem key={activity.activity_id}>
              <TimelineOppositeContent color="text.secondary" sx={{ maxWidth: '120px' }}>
                <Typography variant="caption">
                  {formatRelativeTime(activity.created_at)}
                </Typography>
                <Typography variant="caption" display="block">
                  {new Date(activity.created_at).toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </Typography>
              </TimelineOppositeContent>

              <TimelineSeparator>
                <TimelineDot color={getActionColor(activity.action)} />
                {index < activities.length - 1 && <TimelineConnector />}
              </TimelineSeparator>

              <TimelineContent>
                <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
                  <Stack direction="row" spacing={2} alignItems="flex-start">
                    <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem' }}>
                      {activity.user?.full_name?.charAt(0) || activity.user?.username?.charAt(0) || '?'}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Typography variant="subtitle2">
                          {activity.user?.full_name || activity.user?.username || 'Unknown User'}
                        </Typography>
                        <Chip
                          label={activity.action}
                          size="small"
                          color={getActionColor(activity.action)}
                        />
                      </Box>
                      <Typography variant="body2" color="text.primary" sx={{ mb: 0.5 }}>
                        {activity.description}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          {getEntityIcon(activity.entity_type)} {activity.entity_type}
                        </Typography>
                        {activity.entity_name && (
                          <>
                            <Typography variant="caption" color="text.secondary">•</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {activity.entity_name}
                            </Typography>
                          </>
                        )}
                      </Box>
                    </Box>
                  </Stack>
                </Paper>
              </TimelineContent>
            </TimelineItem>
          ))}
        </Timeline>
      )}
    </Box>
  );
};

export default ActivityFeed;
