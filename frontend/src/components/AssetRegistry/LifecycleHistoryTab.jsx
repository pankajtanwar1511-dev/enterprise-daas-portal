import React from 'react'
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/lab'
import {
  Box,
  Typography,
  Paper,
  Chip,
  Alert,
} from '@mui/material'
import {
  CheckCircle as ActiveIcon,
  Edit as DraftIcon,
  Warning as DeprecatedIcon,
  Block as RetiredIcon,
} from '@mui/icons-material'

function LifecycleHistoryTab({ history }) {
  // If no history, show empty state
  if (!history || history.length === 0) {
    return (
      <Alert severity="info">
        No lifecycle history available for this asset yet.
      </Alert>
    )
  }

  // Get icon and color for lifecycle stage
  const getStageIcon = (stage) => {
    const stageLower = stage.toLowerCase()
    if (stageLower === 'active') return <ActiveIcon />
    if (stageLower === 'draft') return <DraftIcon />
    if (stageLower === 'deprecated') return <DeprecatedIcon />
    if (stageLower === 'retired') return <RetiredIcon />
    return <DraftIcon />
  }

  const getStageColor = (stage) => {
    const stageLower = stage.toLowerCase()
    if (stageLower === 'active') return 'success'
    if (stageLower === 'draft') return 'info'
    if (stageLower === 'deprecated') return 'warning'
    if (stageLower === 'retired') return 'error'
    return 'default'
  }

  return (
    <Box sx={{ py: 2 }}>
      <Timeline position="right">
        {history.map((entry, index) => (
          <TimelineItem key={entry.history_id}>
            <TimelineOppositeContent
              sx={{ m: 'auto 0', minWidth: '180px' }}
              align="right"
              variant="body2"
              color="text.secondary"
            >
              <Typography variant="caption" display="block">
                {new Date(entry.changed_at).toLocaleDateString()}
              </Typography>
              <Typography variant="caption" display="block">
                {new Date(entry.changed_at).toLocaleTimeString()}
              </Typography>
              <Typography variant="caption" display="block" sx={{ mt: 0.5, fontStyle: 'italic' }}>
                By User ID: {entry.changed_by}
              </Typography>
            </TimelineOppositeContent>

            <TimelineSeparator>
              <TimelineDot color={getStageColor(entry.to_state)}>
                {getStageIcon(entry.to_state)}
              </TimelineDot>
              {index < history.length - 1 && <TimelineConnector />}
            </TimelineSeparator>

            <TimelineContent sx={{ py: '12px', px: 2 }}>
              <Paper elevation={2} sx={{ p: 2, bgcolor: '#FAFAFA' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  {entry.from_state ? (
                    <>
                      <Chip
                        label={entry.from_state}
                        size="small"
                        color={getStageColor(entry.from_state)}
                        variant="outlined"
                      />
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        →
                      </Typography>
                    </>
                  ) : (
                    <Chip
                      label="Created"
                      size="small"
                      color="default"
                      variant="outlined"
                    />
                  )}
                  <Chip
                    label={entry.to_state}
                    size="small"
                    color={getStageColor(entry.to_state)}
                  />
                </Box>

                {entry.change_reason && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    <strong>Reason:</strong> {entry.change_reason}
                  </Typography>
                )}
              </Paper>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Box>
  )
}

export default LifecycleHistoryTab
