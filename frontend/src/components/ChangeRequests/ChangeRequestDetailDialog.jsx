import React, { useState, useEffect } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  Typography,
  Chip,
  Box,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
} from '@mui/material'
import {
  Close as CloseIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  PlayArrow as CompleteIcon,
} from '@mui/icons-material'

function ChangeRequestDetailDialog({ open, onClose, request, onUpdate }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [details, setDetails] = useState(null)
  const [approvalComments, setApprovalComments] = useState('')
  const [showApprovalForm, setShowApprovalForm] = useState(false)
  const [approvalAction, setApprovalAction] = useState(null) // 'approve' or 'reject'

  useEffect(() => {
    if (open && request) {
      fetchDetails()
    }
  }, [open, request])

  const fetchDetails = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await axiosInstance.get(`/api/v1/change-requests/${request.change_id}`)
      setDetails(response.data)
    } catch (err) {
      console.error('Error fetching change request details:', err)
      setError('Failed to load change request details')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async () => {
    setLoading(true)
    setError('')
    try {
      await axiosInstance.put(`/api/v1/change-requests/${request.change_id}/approve`, null, {
        params: { approval_comments: approvalComments }
      })
      onUpdate()
      handleClose()
    } catch (err) {
      console.error('Error approving change request:', err)
      setError(err.response?.data?.detail || 'Failed to approve change request')
    } finally {
      setLoading(false)
    }
  }

  const handleReject = async () => {
    if (!approvalComments.trim()) {
      setError('Rejection comments are required')
      return
    }

    setLoading(true)
    setError('')
    try {
      await axiosInstance.put(`/api/v1/change-requests/${request.change_id}/reject`, null, {
        params: { approval_comments: approvalComments }
      })
      onUpdate()
      handleClose()
    } catch (err) {
      console.error('Error rejecting change request:', err)
      setError(err.response?.data?.detail || 'Failed to reject change request')
    } finally {
      setLoading(false)
    }
  }

  const handleComplete = async () => {
    setLoading(true)
    setError('')
    try {
      await axiosInstance.put(`/api/v1/change-requests/${request.change_id}/complete`)
      onUpdate()
      handleClose()
    } catch (err) {
      console.error('Error completing change request:', err)
      setError(err.response?.data?.detail || 'Failed to complete change request')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setApprovalComments('')
    setShowApprovalForm(false)
    setApprovalAction(null)
    setError('')
    setDetails(null)
    onClose()
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Critical': return 'error'
      case 'High': return 'warning'
      case 'Medium': return 'info'
      case 'Low': return 'success'
      default: return 'default'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'Pending': return 'warning'
      case 'Approved': return 'success'
      case 'Rejected': return 'error'
      default: return 'default'
    }
  }

  if (!details && !loading) return null

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ bgcolor: '#0D47A1', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        Change Request Details
        <IconButton onClick={handleClose} sx={{ color: 'white' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        {loading && !details ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
        ) : details && (
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="h6">{details.title}</Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Change ID</Typography>
                <Typography variant="body1">{details.change_id}</Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Asset</Typography>
                <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                  {details.asset_name || `Asset ID: ${details.asset_id}`}
                </Typography>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Change Type</Typography>
                <Box sx={{ mt: 0.5 }}>
                  <Chip label={details.change_type} size="small" variant="outlined" />
                </Box>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Risk Level</Typography>
                <Box sx={{ mt: 0.5 }}>
                  <Chip label={details.risk_level} color={getRiskColor(details.risk_level)} size="small" />
                </Box>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Approval Status</Typography>
                <Box sx={{ mt: 0.5 }}>
                  <Chip label={details.approval_status} color={getStatusColor(details.approval_status)} size="small" />
                </Box>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Implementation Status</Typography>
                <Box sx={{ mt: 0.5 }}>
                  <Chip label={details.status} size="small" variant="outlined" />
                </Box>
              </Grid>

              <Grid item xs={12}>
                <Divider sx={{ my: 1 }} />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="caption" color="textSecondary">Description</Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
                  {details.description}
                </Typography>
              </Grid>

              {details.impact_assessment && (
                <Grid item xs={12}>
                  <Typography variant="caption" color="textSecondary">Impact Assessment</Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
                    {details.impact_assessment}
                  </Typography>
                </Grid>
              )}

              {details.rollback_plan && (
                <Grid item xs={12}>
                  <Typography variant="caption" color="textSecondary">Rollback Plan</Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
                    {details.rollback_plan}
                  </Typography>
                </Grid>
              )}

              <Grid item xs={12}>
                <Divider sx={{ my: 1 }} />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Typography variant="caption" color="textSecondary">Requested By</Typography>
                <Typography variant="body2">{details.requester_name || `User ID: ${details.requested_by}`}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {new Date(details.requested_at).toLocaleString()}
                </Typography>
              </Grid>

              {details.approver_name && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="caption" color="textSecondary">
                    {details.approval_status === 'Approved' ? 'Approved By' : 'Rejected By'}
                  </Typography>
                  <Typography variant="body2">{details.approver_name}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    {new Date(details.approved_at).toLocaleString()}
                  </Typography>
                </Grid>
              )}

              {details.approval_comments && (
                <Grid item xs={12}>
                  <Typography variant="caption" color="textSecondary">Approval Comments</Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
                    {details.approval_comments}
                  </Typography>
                </Grid>
              )}

              {details.implementation_date && (
                <Grid item xs={12}>
                  <Typography variant="caption" color="textSecondary">Implemented On</Typography>
                  <Typography variant="body2">
                    {new Date(details.implementation_date).toLocaleString()}
                  </Typography>
                </Grid>
              )}

              {showApprovalForm && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label={approvalAction === 'reject' ? 'Rejection Comments (Required)' : 'Approval Comments (Optional)'}
                    value={approvalComments}
                    onChange={(e) => setApprovalComments(e.target.value)}
                    placeholder="Enter your comments..."
                  />
                </Grid>
              )}
            </Grid>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
        <Box>
          {details && details.approval_status === 'Pending' && !showApprovalForm && (
            <>
              <Button
                startIcon={<RejectIcon />}
                color="error"
                onClick={() => {
                  setShowApprovalForm(true)
                  setApprovalAction('reject')
                }}
              >
                Reject
              </Button>
              <Button
                startIcon={<ApproveIcon />}
                color="success"
                onClick={() => {
                  setShowApprovalForm(true)
                  setApprovalAction('approve')
                }}
                sx={{ ml: 1 }}
              >
                Approve
              </Button>
            </>
          )}

          {details && details.approval_status === 'Approved' && details.status === 'InProgress' && (
            <Button
              startIcon={<CompleteIcon />}
              color="success"
              variant="contained"
              onClick={handleComplete}
              disabled={loading}
            >
              Mark as Completed
            </Button>
          )}
        </Box>

        <Box>
          {showApprovalForm && (
            <>
              <Button onClick={() => {
                setShowApprovalForm(false)
                setApprovalAction(null)
                setApprovalComments('')
              }}>
                Cancel Action
              </Button>
              <Button
                variant="contained"
                color={approvalAction === 'approve' ? 'success' : 'error'}
                onClick={approvalAction === 'approve' ? handleApprove : handleReject}
                disabled={loading}
                sx={{ ml: 1 }}
              >
                {loading ? <CircularProgress size={24} /> : `Confirm ${approvalAction === 'approve' ? 'Approval' : 'Rejection'}`}
              </Button>
            </>
          )}
          {!showApprovalForm && (
            <Button onClick={handleClose}>Close</Button>
          )}
        </Box>
      </DialogActions>
    </Dialog>
  )
}

export default ChangeRequestDetailDialog
