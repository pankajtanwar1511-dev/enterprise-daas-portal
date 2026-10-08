import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Avatar,
  Stack,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Divider,
  Alert
} from '@mui/material';
import {
  Send as SendIcon,
  MoreVert as MoreVertIcon,
  Reply as ReplyIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import axiosInstance from '../../utils/axiosInstance';


const CommentSection = ({ entityType, entityId }) => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState(null);
  const [editingComment, setEditingComment] = useState(null);
  const [editText, setEditText] = useState('');

  useEffect(() => {
    if (entityType && entityId) {
      fetchComments();
    }
  }, [entityType, entityId]);

  const fetchComments = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axiosInstance.get(
        `/api/v1/comments?entity_type=${entityType}&entity_id=${entityId}&include_replies=true`
      );
      setComments(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch comments');
      console.error('Error fetching comments:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async () => {
    if (!newComment.trim()) return;

    try {
      const payload = {
        entity_type: entityType,
        entity_id: parseInt(entityId),
        comment_text: newComment,
        parent_comment_id: replyingTo?.comment_id || null
      };

      await axiosInstance.post(`/api/v1/comments`, payload);

      setNewComment('');
      setReplyingTo(null);
      fetchComments();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to post comment');
      console.error('Error posting comment:', err);
    }
  };

  const handleEditComment = async (commentId) => {
    if (!editText.trim()) return;

    try {
      await axiosInstance.put(
        `/api/v1/comments/${commentId}`,
        { comment_text: editText }
      );

      setEditingComment(null);
      setEditText('');
      fetchComments();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update comment');
      console.error('Error updating comment:', err);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) {
      return;
    }

    try {
      await axiosInstance.delete(`/api/v1/comments/${commentId}`);
      fetchComments();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete comment');
      console.error('Error deleting comment:', err);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 7) return date.toLocaleDateString();
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  const CommentItem = ({ comment, isReply = false }) => {
    const [anchorEl, setAnchorEl] = useState(null);
    const currentUserId = 1; // TODO: Get from auth context

    const handleMenuClick = (event) => {
      setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
      setAnchorEl(null);
    };

    const startEditing = () => {
      setEditingComment(comment.comment_id);
      setEditText(comment.comment_text);
      handleMenuClose();
    };

    const startReplying = () => {
      setReplyingTo(comment);
      handleMenuClose();
    };

    return (
      <Box sx={{ ml: isReply ? 6 : 0, mb: 2 }}>
        <Paper variant="outlined" sx={{ p: 2 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Avatar sx={{ width: 32, height: 32 }}>
                {comment.user?.full_name?.charAt(0) || comment.user?.username?.charAt(0) || '?'}
              </Avatar>
              <Box>
                <Typography variant="subtitle2">
                  {comment.user?.full_name || comment.user?.username || 'Unknown User'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatTimestamp(comment.created_at)}
                  {comment.edited && ' (edited)'}
                </Typography>
              </Box>
            </Stack>
            <IconButton size="small" onClick={handleMenuClick}>
              <MoreVertIcon fontSize="small" />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
            >
              {!isReply && (
                <MenuItem onClick={startReplying}>
                  <ReplyIcon fontSize="small" sx={{ mr: 1 }} />
                  Reply
                </MenuItem>
              )}
              {comment.user_id === currentUserId && (
                <>
                  <MenuItem onClick={startEditing}>
                    <EditIcon fontSize="small" sx={{ mr: 1 }} />
                    Edit
                  </MenuItem>
                  <MenuItem onClick={() => {
                    handleDeleteComment(comment.comment_id);
                    handleMenuClose();
                  }}>
                    <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
                    Delete
                  </MenuItem>
                </>
              )}
            </Menu>
          </Box>

          {/* Content */}
          {editingComment === comment.comment_id ? (
            <Box sx={{ mt: 1 }}>
              <TextField
                fullWidth
                multiline
                rows={2}
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                sx={{ mb: 1 }}
              />
              <Stack direction="row" spacing={1} justifyContent="flex-end">
                <Button size="small" onClick={() => {
                  setEditingComment(null);
                  setEditText('');
                }}>
                  Cancel
                </Button>
                <Button size="small" variant="contained" onClick={() => handleEditComment(comment.comment_id)}>
                  Save
                </Button>
              </Stack>
            </Box>
          ) : (
            <>
              {comment.deleted ? (
                <Typography variant="body2" color="text.secondary" fontStyle="italic">
                  [This comment has been deleted]
                </Typography>
              ) : (
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {comment.comment_text}
                </Typography>
              )}
            </>
          )}
        </Paper>

        {/* Replies */}
        {comment.replies && comment.replies.length > 0 && (
          <Box sx={{ mt: 2 }}>
            {comment.replies.map((reply) => (
              <CommentItem key={reply.comment_id} comment={reply} isReply={true} />
            ))}
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Comments ({comments.length})
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* New Comment Input */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        {replyingTo && (
          <Box sx={{ mb: 2 }}>
            <Chip
              label={`Replying to ${replyingTo.user?.full_name || replyingTo.user?.username}`}
              onDelete={() => setReplyingTo(null)}
              size="small"
            />
          </Box>
        )}
        <TextField
          fullWidth
          multiline
          rows={3}
          placeholder={replyingTo ? 'Write a reply...' : 'Write a comment...'}
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          sx={{ mb: 2 }}
        />
        <Stack direction="row" spacing={1} justifyContent="flex-end">
          {replyingTo && (
            <Button size="small" onClick={() => setReplyingTo(null)}>
              Cancel Reply
            </Button>
          )}
          <Button
            variant="contained"
            endIcon={<SendIcon />}
            onClick={handleSubmitComment}
            disabled={!newComment.trim()}
          >
            {replyingTo ? 'Reply' : 'Comment'}
          </Button>
        </Stack>
      </Paper>

      {/* Comments List */}
      {loading ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Loading comments...
          </Typography>
        </Box>
      ) : comments.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            No comments yet. Be the first to comment!
          </Typography>
        </Box>
      ) : (
        <Box>
          {comments.map((comment) => (
            <CommentItem key={comment.comment_id} comment={comment} />
          ))}
        </Box>
      )}
    </Box>
  );
};

export default CommentSection;
