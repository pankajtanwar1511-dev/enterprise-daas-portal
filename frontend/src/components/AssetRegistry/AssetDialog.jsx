import React from 'react'
import { Dialog, DialogTitle, DialogContent, IconButton } from '@mui/material'
import { Close as CloseIcon } from '@mui/icons-material'
import AssetForm from './AssetForm'

const AssetDialog = ({ open, onClose, asset = null, onSuccess }) => {
  const isEditMode = !!asset

  const handleSuccess = () => {
    onSuccess()
    onClose()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {isEditMode ? 'Edit Asset' : 'Register New Asset'}
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <AssetForm asset={asset} onSuccess={handleSuccess} onCancel={onClose} />
      </DialogContent>
    </Dialog>
  )
}

export default AssetDialog
