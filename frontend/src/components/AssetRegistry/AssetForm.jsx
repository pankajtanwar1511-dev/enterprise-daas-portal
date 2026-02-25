import React, { useState, useEffect } from 'react'
import {
  Box,
  TextField,
  Button,
  Grid,
  MenuItem,
  FormHelperText,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material'
import { CheckCircle, Error as ErrorIcon } from '@mui/icons-material'
import axiosInstance from '../../utils/axiosInstance'

const AssetForm = ({ asset = null, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    asset_name: '',
    domain_id: '',
    environment: '',
    owner_id: '',
    version: '',
    lifecycle_stage: 'Draft',
    documentation_url: '',
    description: '',
    business_justification: '',
  })

  const [domains, setDomains] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [namingValidation, setNamingValidation] = useState(null)
  const [validatingName, setValidatingName] = useState(false)

  const isEditMode = !!asset

  useEffect(() => {
    fetchDomains()
    fetchUsers()

    if (asset) {
      setFormData({
        asset_name: asset.asset_name || '',
        domain_id: asset.domain_id || '',
        environment: asset.environment || '',
        owner_id: asset.owner_id || '',
        version: asset.version || '',
        lifecycle_stage: asset.lifecycle_stage || 'Draft',
        documentation_url: asset.documentation_url || '',
        description: asset.description || '',
        business_justification: asset.business_justification || '',
      })
    }
  }, [asset])

  // Real-time naming validation
  useEffect(() => {
    const timer = setTimeout(() => {
      if (formData.asset_name && formData.asset_name.length >= 3) {
        validateAssetName(formData.asset_name)
      } else {
        setNamingValidation(null)
      }
    }, 500) // Debounce for 500ms

    return () => clearTimeout(timer)
  }, [formData.asset_name])

  const fetchDomains = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/assets/domains')
      setDomains(response.data)
    } catch (err) {
      console.error('Error fetching domains:', err)
    }
  }

  const fetchUsers = async () => {
    try {
      const response = await axiosInstance.get('/api/v1/assets/users')
      setUsers(response.data)
    } catch (err) {
      console.error('Error fetching users:', err)
    }
  }

  const validateAssetName = async (name) => {
    setValidatingName(true)
    try {
      const payload = { asset_name: name }
      // If editing, exclude current asset from duplicate check
      if (isEditMode && asset?.asset_id) {
        payload.exclude_asset_id = asset.asset_id
      }

      const response = await axiosInstance.post('/api/v1/assets/validate-naming', payload)
      setNamingValidation(response.data)
    } catch (err) {
      console.error('Error validating name:', err)
      setNamingValidation(null)
    } finally {
      setValidatingName(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validation
    if (!formData.asset_name || !formData.domain_id || !formData.environment || !formData.owner_id) {
      setError('Please fill in all required fields')
      return
    }

    // Check naming compliance
    if (namingValidation && !namingValidation.is_valid) {
      setError('Asset name does not comply with naming standards. Please fix the issues above.')
      return
    }

    setLoading(true)

    try {
      if (isEditMode) {
        await axiosInstance.put(`/api/v1/assets/${asset.asset_id}`, formData)
      } else {
        await axiosInstance.post('/api/v1/assets', formData)
      }
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${isEditMode ? 'update' : 'create'} asset`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2}>
        {/* Asset Name with Real-time Validation */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            required
            label="Asset Name"
            name="asset_name"
            value={formData.asset_name}
            onChange={handleChange}
            placeholder="e.g., PROD-HR-DW-v1"
            disabled={loading}
            InputProps={{
              endAdornment: validatingName ? (
                <CircularProgress size={20} />
              ) : namingValidation ? (
                namingValidation.is_valid ? (
                  <CheckCircle color="success" />
                ) : (
                  <ErrorIcon color="error" />
                )
              ) : null,
            }}
            helperText={
              namingValidation && (
                <Box component="span">
                  {namingValidation.is_valid ? (
                    <Box component="span" sx={{ color: 'success.main' }}>
                      ✓ Valid naming convention
                    </Box>
                  ) : (
                    <Box>
                      {namingValidation.violations?.map((violation, idx) => (
                        <Box key={idx} component="span" sx={{ color: 'error.main', display: 'block' }}>
                          • {violation}
                        </Box>
                      ))}
                    </Box>
                  )}
                </Box>
              )
            }
          />
          {namingValidation && namingValidation.expected_format && (
            <FormHelperText>
              Expected format: <strong>{namingValidation.expected_format}</strong>
            </FormHelperText>
          )}
        </Grid>

        {/* Domain */}
        <Grid item xs={12} sm={6}>
          <TextField
            select
            fullWidth
            required
            label="Domain"
            name="domain_id"
            value={formData.domain_id}
            onChange={handleChange}
            disabled={loading}
          >
            <MenuItem value="">Select Domain</MenuItem>
            {domains.map((domain) => (
              <MenuItem key={domain.domain_id} value={domain.domain_id}>
                {domain.domain_name} ({domain.domain_code})
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        {/* Environment */}
        <Grid item xs={12} sm={6}>
          <TextField
            select
            fullWidth
            required
            label="Environment"
            name="environment"
            value={formData.environment}
            onChange={handleChange}
            disabled={loading}
          >
            <MenuItem value="">Select Environment</MenuItem>
            <MenuItem value="DEV">Development (DEV)</MenuItem>
            <MenuItem value="QA">Quality Assurance (QA)</MenuItem>
            <MenuItem value="UAT">User Acceptance Testing (UAT)</MenuItem>
            <MenuItem value="PROD">Production (PROD)</MenuItem>
          </TextField>
        </Grid>

        {/* Owner */}
        <Grid item xs={12} sm={6}>
          <TextField
            select
            fullWidth
            required
            label="Asset Owner"
            name="owner_id"
            value={formData.owner_id}
            onChange={handleChange}
            disabled={loading}
          >
            <MenuItem value="">Select Owner</MenuItem>
            {users.map((user) => (
              <MenuItem key={user.user_id} value={user.user_id}>
                {user.first_name} {user.last_name} ({user.username})
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        {/* Version */}
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Version"
            name="version"
            value={formData.version}
            onChange={handleChange}
            placeholder="e.g., v1.0"
            disabled={loading}
          />
        </Grid>

        {/* Lifecycle Stage */}
        <Grid item xs={12} sm={6}>
          <TextField
            select
            fullWidth
            label="Lifecycle Stage"
            name="lifecycle_stage"
            value={formData.lifecycle_stage}
            onChange={handleChange}
            disabled={loading}
          >
            <MenuItem value="Draft">Draft</MenuItem>
            <MenuItem value="Active">Active</MenuItem>
            <MenuItem value="Deprecated">Deprecated</MenuItem>
            <MenuItem value="Retired">Retired</MenuItem>
          </TextField>
        </Grid>

        {/* Documentation URL */}
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Documentation URL"
            name="documentation_url"
            value={formData.documentation_url}
            onChange={handleChange}
            placeholder="https://docs.company.com/..."
            disabled={loading}
          />
        </Grid>

        {/* Description */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Describe the purpose and functionality of this asset"
            disabled={loading}
          />
        </Grid>

        {/* Business Justification */}
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={2}
            label="Business Justification"
            name="business_justification"
            value={formData.business_justification}
            onChange={handleChange}
            placeholder="Explain the business value and rationale"
            disabled={loading}
          />
        </Grid>

        {/* Action Buttons */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={loading}>
              {loading ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  {isEditMode ? 'Updating...' : 'Creating...'}
                </>
              ) : isEditMode ? (
                'Update Asset'
              ) : (
                'Create Asset'
              )}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  )
}

export default AssetForm
