import React, { useState, useEffect } from 'react';
import {
  Badge,
  IconButton,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
  Button,
  Chip,
  Stack,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Tooltip
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Circle as CircleIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  DoneAll as DoneAllIcon
} from '@mui/icons-material';
import axiosInstance from '../../utils/axiosInstance';


const NotificationCenter = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const open = Boolean(anchorEl);

  useEffect(() => {
    fetchUnreadCount();
    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchUnreadCount = async () => {
    try {
      const response = await axiosInstance.get(`/api/v1/notifications/unread-count`);
      setUnreadCount(response.data.unread_count);
    } catch (err) {
      console.error('Error fetching unread count:', err);
    }
  };

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get(`/api/v1/notifications?limit=20`);
      setNotifications(response.data);
    } catch (err) {
      console.error('Error fetching notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
    fetchNotifications();
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const markAsRead = async (notificationId) => {
    try {
      await axiosInstance.post(
        `/api/v1/notifications/${notificationId}/read`,
        {}
      );
      // Update local state
      setNotifications(notifications.map(n =>
        n.notification_id === notificationId ? { ...n, read: true } : n
      ));
      fetchUnreadCount();
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      await axiosInstance.post(
        `/api/v1/notifications/read-all`,
        {}
      );
      // Update local state
      setNotifications(notifications.map(n => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Error marking all as read:', err);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      await axiosInstance.delete(`/api/v1/notifications/${notificationId}`);
      // Update local state
      setNotifications(notifications.filter(n => n.notification_id !== notificationId));
      fetchUnreadCount();
    } catch (err) {
      console.error('Error deleting notification:', err);
    }
  };

  const handleNotificationClick = (notification) => {
    // Mark as read
    if (!notification.read) {
      markAsRead(notification.notification_id);
    }

    // Navigate to link if available
    if (notification.link) {
      window.location.href = notification.link;
    }

    handleClose();
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

  const getTypeIcon = (type) => {
    // Return icon based on notification type
    return type;
  };

  const formatTimestamp = (timestamp) => {
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
    <>
      <Tooltip title="Notifications">
        <IconButton
          onClick={handleClick}
          size="large"
          aria-controls={open ? 'notification-menu' : undefined}
          aria-haspopup="true"
          aria-expanded={open ? 'true' : undefined}
        >
          <Badge badgeContent={unreadCount} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>
      </Tooltip>

      <Menu
        id="notification-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 400,
            maxHeight: 500
          }
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Notifications</Typography>
            {unreadCount > 0 && (
              <Button
                size="small"
                startIcon={<DoneAllIcon />}
                onClick={markAllAsRead}
              >
                Mark all read
              </Button>
            )}
          </Box>
          {unreadCount > 0 && (
            <Typography variant="caption" color="text.secondary">
              {unreadCount} unread notification{unreadCount > 1 ? 's' : ''}
            </Typography>
          )}
        </Box>

        <Divider />

        {/* Notifications List */}
        {loading ? (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Loading notifications...
            </Typography>
          </Box>
        ) : notifications.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <NotificationsIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              No notifications
            </Typography>
          </Box>
        ) : (
          <List sx={{ p: 0, maxHeight: 400, overflow: 'auto' }}>
            {notifications.map((notification) => (
              <React.Fragment key={notification.notification_id}>
                <ListItem
                  disablePadding
                  sx={{
                    backgroundColor: notification.read ? 'inherit' : 'action.hover'
                  }}
                >
                  <ListItemButton onClick={() => handleNotificationClick(notification)}>
                    <Box sx={{ width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 0.5 }}>
                        {!notification.read && (
                          <CircleIcon
                            sx={{
                              fontSize: 8,
                              color: 'primary.main',
                              mr: 1,
                              mt: 1
                            }}
                          />
                        )}
                        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                            <Typography variant="subtitle2" noWrap>
                              {notification.title}
                            </Typography>
                            <Chip
                              label={notification.priority}
                              size="small"
                              color={getPriorityColor(notification.priority)}
                              sx={{ ml: 1 }}
                            />
                          </Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                            {notification.message}
                          </Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="caption" color="text.secondary">
                              {formatTimestamp(notification.created_at)}
                            </Typography>
                            <Stack direction="row" spacing={1}>
                              {!notification.read && (
                                <Tooltip title="Mark as read">
                                  <IconButton
                                    size="small"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      markAsRead(notification.notification_id);
                                    }}
                                  >
                                    <CheckCircleIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              )}
                              <Tooltip title="Delete">
                                <IconButton
                                  size="small"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    deleteNotification(notification.notification_id);
                                  }}
                                >
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Stack>
                          </Box>
                        </Box>
                      </Box>
                    </Box>
                  </ListItemButton>
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        )}

        {/* Footer */}
        {notifications.length > 0 && (
          <>
            <Divider />
            <Box sx={{ p: 1, textAlign: 'center' }}>
              <Button size="small" fullWidth onClick={() => {
                handleClose();
                window.location.href = '/notifications';
              }}>
                View All Notifications
              </Button>
            </Box>
          </>
        )}
      </Menu>
    </>
  );
};

export default NotificationCenter;
