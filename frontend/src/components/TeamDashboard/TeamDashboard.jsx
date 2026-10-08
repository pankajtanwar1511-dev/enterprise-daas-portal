import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Divider,
  Stack,
  Paper,
  Alert,
  LinearProgress,
  IconButton,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  Notifications as NotificationsIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  PlayArrow as PlayArrowIcon,
  RateReview as RateReviewIcon,
  Block as BlockIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ArrowForward as ArrowForwardIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../../utils/axiosInstance';


const TeamDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // State for dashboard data
  const [myTasks, setMyTasks] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [recentActivities, setRecentActivities] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState({
    totalTasks: 0,
    overdueTasks: 0,
    completedTasks: 0,
    pendingApprovals: 0,
    unreadNotifications: 0
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch data in parallel
      const [
        tasksResponse,
        approvalsResponse,
        activitiesResponse,
        notificationsResponse,
        notificationCountResponse
      ] = await Promise.all([
        axiosInstance.get(`/api/v1/tasks?limit=10`),
        axiosInstance.get(`/api/v1/change-requests?status=PendingApproval&limit=5`),
        axiosInstance.get(`/api/v1/activity?limit=10`),
        axiosInstance.get(`/api/v1/notifications?limit=5`),
        axiosInstance.get(`/api/v1/notifications/unread-count`)
      ]);

      const tasks = tasksResponse.data;
      setMyTasks(tasks);
      setPendingApprovals(approvalsResponse.data);
      setRecentActivities(activitiesResponse.data);
      setNotifications(notificationsResponse.data);

      // Calculate stats
      const now = new Date();
      const overdueTasks = tasks.filter(task =>
        task.due_date && new Date(task.due_date) < now &&
        task.status !== 'Done' && task.status !== 'Cancelled'
      ).length;

      const completedTasks = tasks.filter(task => task.status === 'Done').length;

      setStats({
        totalTasks: tasks.length,
        overdueTasks: overdueTasks,
        completedTasks: completedTasks,
        pendingApprovals: approvalsResponse.data.length,
        unreadNotifications: notificationCountResponse.data.unread_count
      });

    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch dashboard data');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTaskStatusIcon = (status) => {
    const icons = {
      Todo: <RadioButtonUncheckedIcon fontSize="small" />,
      InProgress: <PlayArrowIcon fontSize="small" />,
      InReview: <RateReviewIcon fontSize="small" />,
      Blocked: <BlockIcon fontSize="small" />,
      Done: <CheckCircleIcon fontSize="small" />
    };
    return icons[status] || <RadioButtonUncheckedIcon fontSize="small" />;
  };

  const getTaskStatusColor = (status) => {
    const colors = {
      Todo: 'default',
      InProgress: 'primary',
      InReview: 'warning',
      Blocked: 'error',
      Done: 'success',
      Cancelled: 'default'
    };
    return colors[status] || 'default';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      Low: 'success',
      Medium: 'info',
      High: 'warning',
      Critical: 'error'
    };
    return colors[priority] || 'default';
  };

  const isOverdue = (dueDate, status) => {
    if (!dueDate || status === 'Done' || status === 'Cancelled') return false;
    return new Date(dueDate) < new Date();
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

  const getActivityIcon = (action) => {
    const icons = {
      created: '➕',
      updated: '✏️',
      deleted: '🗑️',
      approved: '✅',
      rejected: '❌',
      commented: '💬',
      completed: '🎉'
    };
    return icons[action] || '📝';
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>Team Dashboard</Typography>
        <LinearProgress sx={{ mt: 2 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Team Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Your personalized overview of tasks, approvals, and activities
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Total Tasks
                  </Typography>
                  <Typography variant="h4">{stats.totalTasks}</Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <AssignmentIcon />
                </Avatar>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Overdue
                  </Typography>
                  <Typography variant="h4" color="error.main">{stats.overdueTasks}</Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'error.main' }}>
                  <WarningIcon />
                </Avatar>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Completed
                  </Typography>
                  <Typography variant="h4" color="success.main">{stats.completedTasks}</Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <CheckCircleIcon />
                </Avatar>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Pending Approvals
                  </Typography>
                  <Typography variant="h4" color="warning.main">{stats.pendingApprovals}</Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <RateReviewIcon />
                </Avatar>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Unread
                  </Typography>
                  <Typography variant="h4">{stats.unreadNotifications}</Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <Badge badgeContent={stats.unreadNotifications} color="error">
                    <NotificationsIcon />
                  </Badge>
                </Avatar>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* My Tasks */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">My Tasks</Typography>
                <Button
                  size="small"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate('/tasks')}
                >
                  View All
                </Button>
              </Box>

              {myTasks.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No tasks assigned
                  </Typography>
                </Box>
              ) : (
                <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {myTasks.map((task, index) => (
                    <React.Fragment key={task.task_id}>
                      <ListItem
                        sx={{
                          px: 0,
                          backgroundColor: isOverdue(task.due_date, task.status) ? '#fff3e0' : 'transparent',
                          borderRadius: 1,
                          mb: 0.5
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 40 }}>
                          {getTaskStatusIcon(task.status)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                              <Typography variant="body2" fontWeight="medium">
                                {task.title}
                              </Typography>
                              <Chip
                                label={task.priority}
                                size="small"
                                color={getPriorityColor(task.priority)}
                              />
                            </Box>
                          }
                          secondary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                              <Chip
                                label={task.status}
                                size="small"
                                color={getTaskStatusColor(task.status)}
                              />
                              {task.due_date && (
                                <Typography variant="caption" color={isOverdue(task.due_date, task.status) ? 'error' : 'text.secondary'}>
                                  <ScheduleIcon sx={{ fontSize: 14, verticalAlign: 'middle', mr: 0.5 }} />
                                  {new Date(task.due_date).toLocaleDateString()}
                                  {isOverdue(task.due_date, task.status) && ' (Overdue)'}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < myTasks.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Pending Approvals */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Pending Approvals</Typography>
                <Button
                  size="small"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate('/change-requests')}
                >
                  View All
                </Button>
              </Box>

              {pendingApprovals.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No pending approvals
                  </Typography>
                </Box>
              ) : (
                <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {pendingApprovals.map((approval, index) => (
                    <React.Fragment key={approval.change_request_id}>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemIcon sx={{ minWidth: 40 }}>
                          <RateReviewIcon color="warning" />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography variant="body2" fontWeight="medium">
                              {approval.title || `CR-${approval.change_request_id}`}
                            </Typography>
                          }
                          secondary={
                            <Box sx={{ mt: 0.5 }}>
                              <Typography variant="caption" color="text.secondary">
                                {approval.asset?.asset_name || 'Asset'}
                              </Typography>
                              <Typography variant="caption" display="block" color="text.secondary">
                                Submitted {formatRelativeTime(approval.created_at)}
                              </Typography>
                            </Box>
                          }
                        />
                        <Chip label={approval.priority || 'Medium'} size="small" color="warning" />
                      </ListItem>
                      {index < pendingApprovals.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Recent Activity</Typography>
                <Button
                  size="small"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate('/activity')}
                >
                  View All
                </Button>
              </Box>

              {recentActivities.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No recent activity
                  </Typography>
                </Box>
              ) : (
                <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {recentActivities.map((activity, index) => (
                    <React.Fragment key={activity.activity_id}>
                      <ListItem sx={{ px: 0, alignItems: 'flex-start' }}>
                        <ListItemIcon sx={{ minWidth: 40, mt: 0.5 }}>
                          <Typography variant="h6">{getActivityIcon(activity.action)}</Typography>
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography variant="body2">
                              <strong>{activity.user?.full_name || activity.user?.username}</strong> {activity.description}
                            </Typography>
                          }
                          secondary={
                            <Box sx={{ mt: 0.5 }}>
                              <Typography variant="caption" color="text.secondary">
                                {activity.entity_type} • {formatRelativeTime(activity.created_at)}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < recentActivities.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Notifications */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Recent Notifications</Typography>
                <Button
                  size="small"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate('/notifications')}
                >
                  View All
                </Button>
              </Box>

              {notifications.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No notifications
                  </Typography>
                </Box>
              ) : (
                <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                  {notifications.map((notification, index) => (
                    <React.Fragment key={notification.notification_id}>
                      <ListItem
                        sx={{
                          px: 0,
                          backgroundColor: !notification.read ? 'action.hover' : 'transparent',
                          borderRadius: 1,
                          mb: 0.5
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 40 }}>
                          {!notification.read && (
                            <Badge color="primary" variant="dot">
                              <NotificationsIcon color="primary" />
                            </Badge>
                          )}
                          {notification.read && <NotificationsIcon color="disabled" />}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography variant="body2" fontWeight={!notification.read ? 'medium' : 'normal'}>
                              {notification.title}
                            </Typography>
                          }
                          secondary={
                            <Box sx={{ mt: 0.5 }}>
                              <Typography variant="caption" color="text.secondary">
                                {notification.message}
                              </Typography>
                              <Typography variant="caption" display="block" color="text.secondary">
                                {formatRelativeTime(notification.created_at)}
                              </Typography>
                            </Box>
                          }
                        />
                        <Chip
                          label={notification.priority}
                          size="small"
                          color={getPriorityColor(notification.priority)}
                        />
                      </ListItem>
                      {index < notifications.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Upcoming Deadlines Section */}
      <Box sx={{ mt: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <ScheduleIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
              Upcoming Deadlines
            </Typography>

            {myTasks.filter(task => task.due_date && task.status !== 'Done').length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="text.secondary">
                  No upcoming deadlines
                </Typography>
              </Box>
            ) : (
              <Grid container spacing={2} sx={{ mt: 1 }}>
                {myTasks
                  .filter(task => task.due_date && task.status !== 'Done')
                  .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
                  .slice(0, 6)
                  .map(task => (
                    <Grid item xs={12} sm={6} md={4} key={task.task_id}>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 2,
                          borderLeft: isOverdue(task.due_date, task.status) ? '4px solid #d32f2f' : '4px solid #1976d2'
                        }}
                      >
                        <Typography variant="body2" fontWeight="medium" gutterBottom>
                          {task.title}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Chip label={task.status} size="small" color={getTaskStatusColor(task.status)} />
                          <Chip label={task.priority} size="small" color={getPriorityColor(task.priority)} />
                        </Box>
                        <Typography
                          variant="caption"
                          color={isOverdue(task.due_date, task.status) ? 'error' : 'text.secondary'}
                          display="flex"
                          alignItems="center"
                        >
                          <ScheduleIcon sx={{ fontSize: 14, mr: 0.5 }} />
                          Due: {new Date(task.due_date).toLocaleDateString()}
                          {isOverdue(task.due_date, task.status) && ' - OVERDUE'}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
              </Grid>
            )}
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default TeamDashboard;
