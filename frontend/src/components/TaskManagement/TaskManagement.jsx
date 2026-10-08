import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Stack,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  FilterList as FilterIcon,
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  PlayArrow as PlayArrowIcon,
  RateReview as RateReviewIcon,
  Block as BlockIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import axiosInstance from '../../utils/axiosInstance';


const TaskManagement = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    assigned_to: '',
    overdue: false
  });

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assigned_to: null,
    initiative_id: null,
    priority: 'Medium',
    status: 'Todo',
    due_date: '',
    start_date: '',
    estimated_hours: null,
    tags: []
  });

  useEffect(() => {
    fetchTasks();
  }, [filters]);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.assigned_to) params.append('assigned_to', filters.assigned_to);
      if (filters.overdue) params.append('overdue', 'true');

      const response = await axiosInstance.get(`/api/v1/tasks?${params.toString()}`);
      setTasks(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (task = null) => {
    if (task) {
      setEditingTask(task);
      setFormData({
        title: task.title,
        description: task.description || '',
        assigned_to: task.assigned_to,
        initiative_id: task.initiative_id,
        priority: task.priority,
        status: task.status,
        due_date: task.due_date || '',
        start_date: task.start_date || '',
        estimated_hours: task.estimated_hours,
        tags: task.tags || []
      });
    } else {
      setEditingTask(null);
      setFormData({
        title: '',
        description: '',
        assigned_to: null,
        initiative_id: null,
        priority: 'Medium',
        status: 'Todo',
        due_date: '',
        start_date: '',
        estimated_hours: null,
        tags: []
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingTask(null);
    setFormData({
      title: '',
      description: '',
      assigned_to: null,
      initiative_id: null,
      priority: 'Medium',
      status: 'Todo',
      due_date: '',
      start_date: '',
      estimated_hours: null,
      tags: []
    });
  };

  const handleSubmit = async () => {
    try {
      const payload = {
        ...formData,
        due_date: formData.due_date || null,
        start_date: formData.start_date || null,
        estimated_hours: formData.estimated_hours ? parseInt(formData.estimated_hours) : null
      };

      if (editingTask) {
        // Update existing task
        await axiosInstance.put(
          `/api/v1/tasks/${editingTask.task_id}`,
          payload
        );
      } else {
        // Create new task
        await axiosInstance.post(
          `/api/v1/tasks`,
          payload
        );
      }

      handleCloseDialog();
      fetchTasks();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save task');
      console.error('Error saving task:', err);
    }
  };

  const handleDelete = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await axiosInstance.delete(`/api/v1/tasks/${taskId}`);
      fetchTasks();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete task');
      console.error('Error deleting task:', err);
    }
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

  const getStatusIcon = (status) => {
    const icons = {
      Todo: <RadioButtonUncheckedIcon fontSize="small" />,
      InProgress: <PlayArrowIcon fontSize="small" />,
      InReview: <RateReviewIcon fontSize="small" />,
      Blocked: <BlockIcon fontSize="small" />,
      Done: <CheckCircleIcon fontSize="small" />,
      Cancelled: <CancelIcon fontSize="small" />
    };
    return icons[status] || <RadioButtonUncheckedIcon fontSize="small" />;
  };

  const getStatusColor = (status) => {
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

  const isOverdue = (dueDate, status) => {
    if (!dueDate || status === 'Done' || status === 'Cancelled') return false;
    return new Date(dueDate) < new Date();
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Task Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Create Task
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  label="Status"
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="Todo">Todo</MenuItem>
                  <MenuItem value="InProgress">In Progress</MenuItem>
                  <MenuItem value="InReview">In Review</MenuItem>
                  <MenuItem value="Blocked">Blocked</MenuItem>
                  <MenuItem value="Done">Done</MenuItem>
                  <MenuItem value="Cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Priority</InputLabel>
                <Select
                  value={filters.priority}
                  label="Priority"
                  onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="Low">Low</MenuItem>
                  <MenuItem value="Medium">Medium</MenuItem>
                  <MenuItem value="High">High</MenuItem>
                  <MenuItem value="Critical">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button
                variant={filters.overdue ? 'contained' : 'outlined'}
                color="error"
                fullWidth
                onClick={() => setFilters({ ...filters, overdue: !filters.overdue })}
              >
                {filters.overdue ? 'Showing Overdue' : 'Show Overdue'}
              </Button>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => setFilters({ status: '', priority: '', assigned_to: '', overdue: false })}
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tasks Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Status</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Assignee</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Tags</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Loading tasks...
                </TableCell>
              </TableRow>
            ) : tasks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No tasks found
                </TableCell>
              </TableRow>
            ) : (
              tasks.map((task) => (
                <TableRow
                  key={task.task_id}
                  sx={{
                    backgroundColor: isOverdue(task.due_date, task.status) ? '#fff3e0' : 'inherit'
                  }}
                >
                  <TableCell>
                    <Chip
                      icon={getStatusIcon(task.status)}
                      label={task.status}
                      color={getStatusColor(task.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {task.title}
                    </Typography>
                    {task.description && (
                      <Typography variant="caption" color="text.secondary">
                        {task.description.substring(0, 50)}
                        {task.description.length > 50 ? '...' : ''}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={task.priority}
                      color={getPriorityColor(task.priority)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {task.assignee ? task.assignee.full_name || task.assignee.username : 'Unassigned'}
                  </TableCell>
                  <TableCell>
                    {task.due_date ? (
                      <Box>
                        <Typography variant="body2">
                          {new Date(task.due_date).toLocaleDateString()}
                        </Typography>
                        {isOverdue(task.due_date, task.status) && (
                          <Typography variant="caption" color="error">
                            Overdue
                          </Typography>
                        )}
                      </Box>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap">
                      {task.tags && task.tags.length > 0 ? (
                        task.tags.slice(0, 2).map((tag, index) => (
                          <Chip key={index} label={tag} size="small" variant="outlined" />
                        ))
                      ) : (
                        '-'
                      )}
                      {task.tags && task.tags.length > 2 && (
                        <Chip label={`+${task.tags.length - 2}`} size="small" variant="outlined" />
                      )}
                    </Stack>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => handleOpenDialog(task)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton size="small" onClick={() => handleDelete(task.task_id)} color="error">
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingTask ? 'Edit Task' : 'Create New Task'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  multiline
                  rows={3}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={formData.priority}
                    label="Priority"
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  >
                    <MenuItem value="Low">Low</MenuItem>
                    <MenuItem value="Medium">Medium</MenuItem>
                    <MenuItem value="High">High</MenuItem>
                    <MenuItem value="Critical">Critical</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    label="Status"
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  >
                    <MenuItem value="Todo">Todo</MenuItem>
                    <MenuItem value="InProgress">In Progress</MenuItem>
                    <MenuItem value="InReview">In Review</MenuItem>
                    <MenuItem value="Blocked">Blocked</MenuItem>
                    <MenuItem value="Done">Done</MenuItem>
                    <MenuItem value="Cancelled">Cancelled</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Start Date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Due Date"
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Estimated Hours"
                  type="number"
                  value={formData.estimated_hours || ''}
                  onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={!formData.title}>
            {editingTask ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaskManagement;
