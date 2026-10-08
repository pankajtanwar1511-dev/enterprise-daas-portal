import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Grid,
  FormControl,
  InputLabel,
  Select,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Box,
  Typography,
  IconButton,
  Divider,
} from '@mui/material'
import { Add, Delete } from '@mui/icons-material'
import axiosInstance from '../../utils/axiosInstance'

const VENDOR_TYPES = [
  { value: 'Cloud Provider', label: 'Cloud Provider' },
  { value: 'Software Vendor', label: 'Software Vendor' },
  { value: 'Consulting', label: 'Consulting' },
  { value: 'Managed Services', label: 'Managed Services' },
  { value: 'Data Provider', label: 'Data Provider' },
  { value: 'Infrastructure', label: 'Infrastructure' },
]

const STATUS_OPTIONS = [
  { value: 'Active', label: 'Active' },
  { value: 'Inactive', label: 'Inactive' },
  { value: 'Under Review', label: 'Under Review' },
  { value: 'Pending Approval', label: 'Pending Approval' },
]

const PAYMENT_TERMS = [
  { value: 'Net 30', label: 'Net 30' },
  { value: 'Net 60', label: 'Net 60' },
  { value: 'Net 90', label: 'Net 90' },
  { value: 'Monthly', label: 'Monthly' },
  { value: 'Quarterly', label: 'Quarterly' },
  { value: 'Annual', label: 'Annual' },
]

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  )
}

function VendorFormDialog({ open, onClose, vendor, onSave }) {
  const [tabValue, setTabValue] = useState(0)
  const [formData, setFormData] = useState({
    vendor_name: '',
    vendor_type: 'Cloud Provider',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    status: 'Active',
    contract_start: '',
    contract_end: '',
    annual_cost: '',
    payment_terms: 'Net 30',
    performance_rating: '',
    notes: '',
  })

  const [slas, setSlas] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (open) {
      if (vendor) {
        // Editing existing vendor
        setFormData({
          vendor_name: vendor.vendor_name || '',
          vendor_type: vendor.vendor_type || 'Cloud Provider',
          contact_name: vendor.contact_name || vendor.contact_person || '',
          contact_email: vendor.contact_email || '',
          contact_phone: vendor.contact_phone || '',
          status: vendor.status || 'Active',
          contract_start: vendor.contract_start || vendor.contract_start_date || '',
          contract_end: vendor.contract_end || vendor.contract_end_date || '',
          annual_cost: vendor.annual_cost || vendor.annual_spend || '',
          payment_terms: vendor.payment_terms || 'Net 30',
          performance_rating: vendor.performance_rating || '',
          notes: vendor.notes || vendor.services_provided || '',
        })
        // Load SLAs if editing
        if (vendor.vendor_id) {
          fetchVendorSLAs(vendor.vendor_id)
        }
      } else {
        // Reset for new vendor
        resetForm()
      }
    }
  }, [open, vendor])

  const resetForm = () => {
    setFormData({
      vendor_name: '',
      vendor_type: 'Cloud Provider',
      contact_name: '',
      contact_email: '',
      contact_phone: '',
      status: 'Active',
      contract_start: '',
      contract_end: '',
      annual_cost: '',
      payment_terms: 'Net 30',
      performance_rating: '',
      notes: '',
    })
    setSlas([])
    setTabValue(0)
    setError(null)
  }

  const fetchVendorSLAs = async (vendorId) => {
    try {
      const response = await axiosInstance.get(`/api/v1/vendors/${vendorId}/slas`)
      setSlas(response.data.slas || [])
    } catch (error) {
      console.error('Error fetching SLAs:', error)
    }
  }

  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    })
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)
      setError(null)

      // Validate required fields
      if (!formData.vendor_name || !formData.vendor_type) {
        setError('Please fill in all required fields (Vendor Name, Type)')
        setLoading(false)
        return
      }

      // Validate email if provided
      if (formData.contact_email && !formData.contact_email.includes('@')) {
        setError('Please enter a valid email address')
        setLoading(false)
        return
      }

      if (vendor) {
        // Update existing vendor
        await axiosInstance.put(`/api/v1/vendors/${vendor.vendor_id}`, formData)
      } else {
        // Create new vendor
        await axiosInstance.post('/api/v1/vendors', formData)
      }

      onSave()
      onClose()
      resetForm()
    } catch (error) {
      console.error('Error saving vendor:', error)
      setError(error.response?.data?.detail || 'Failed to save vendor')
    } finally {
      setLoading(false)
    }
  }

  const handleAddSLA = () => {
    setSlas([
      ...slas,
      {
        sla_metric: '',
        target_value: '',
        current_value: '',
        status: 'Met',
        measurement_period: 'Monthly',
        isNew: true,
      },
    ])
  }

  const handleSLAChange = (index, field, value) => {
    const updatedSLAs = [...slas]
    updatedSLAs[index][field] = value
    setSlas(updatedSLAs)
  }

  const handleRemoveSLA = (index) => {
    const updatedSLAs = slas.filter((_, i) => i !== index)
    setSlas(updatedSLAs)
  }

  const handleSaveSLAs = async () => {
    if (!vendor || !vendor.vendor_id) {
      setError('Please save vendor first before adding SLAs')
      return
    }

    try {
      setLoading(true)
      setError(null)

      // Save only new SLAs
      for (const sla of slas) {
        if (sla.isNew && sla.sla_metric) {
          await axiosInstance.post(`/api/v1/vendors/${vendor.vendor_id}/slas`, {
            sla_name: sla.sla_metric,
            target_value: parseFloat(sla.target_value) || 0,
            current_value: parseFloat(sla.current_value) || 0,
            measurement_period: sla.measurement_period,
            description: sla.sla_metric,
          })
        }
      }

      setError(null)
      alert('SLAs saved successfully!')
      fetchVendorSLAs(vendor.vendor_id)
    } catch (error) {
      console.error('Error saving SLAs:', error)
      setError(error.response?.data?.detail || 'Failed to save SLAs')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {vendor ? 'Edit Vendor' : 'Add New Vendor'}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 2 }}>
          <Tab label="Basic Info" />
          <Tab label="Contract & Financial" />
          <Tab label={`SLAs (${slas.length})`} disabled={!vendor} />
        </Tabs>

        {/* Tab 1: Basic Info */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                required
                label="Vendor Name"
                placeholder="e.g., AWS China, Snowflake, Databricks"
                value={formData.vendor_name}
                onChange={handleChange('vendor_name')}
                helperText="Official vendor/company name"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth required>
                <InputLabel>Vendor Type</InputLabel>
                <Select
                  value={formData.vendor_type}
                  onChange={handleChange('vendor_type')}
                  label="Vendor Type"
                >
                  {VENDOR_TYPES.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Divider sx={{ my: 1 }}>
                <Typography variant="caption" color="textSecondary">
                  Contact Information
                </Typography>
              </Divider>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Contact Person"
                placeholder="John Doe"
                value={formData.contact_name}
                onChange={handleChange('contact_name')}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Contact Email"
                placeholder="john.doe@vendor.com"
                value={formData.contact_email}
                onChange={handleChange('contact_email')}
                type="email"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Contact Phone"
                placeholder="+1 555-1234"
                value={formData.contact_phone}
                onChange={handleChange('contact_phone')}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={handleChange('status')}
                  label="Status"
                >
                  {STATUS_OPTIONS.map((status) => (
                    <MenuItem key={status.value} value={status.value}>
                      {status.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Performance Rating"
                placeholder="1-5"
                value={formData.performance_rating}
                onChange={handleChange('performance_rating')}
                type="number"
                inputProps={{ min: 1, max: 5, step: 0.1 }}
                helperText="Rate from 1 (poor) to 5 (excellent)"
              />
            </Grid>
          </Grid>
        </TabPanel>

        {/* Tab 2: Contract & Financial */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Contract Start Date"
                type="date"
                value={formData.contract_start}
                onChange={handleChange('contract_start')}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Contract End Date"
                type="date"
                value={formData.contract_end}
                onChange={handleChange('contract_end')}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Annual Cost"
                placeholder="e.g., 1500000"
                value={formData.annual_cost}
                onChange={handleChange('annual_cost')}
                type="number"
                inputProps={{ min: 0, step: 1000 }}
                helperText="Total annual contract value in USD"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Payment Terms</InputLabel>
                <Select
                  value={formData.payment_terms}
                  onChange={handleChange('payment_terms')}
                  label="Payment Terms"
                >
                  {PAYMENT_TERMS.map((term) => (
                    <MenuItem key={term.value} value={term.value}>
                      {term.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Services Provided / Notes"
                placeholder="Describe the services this vendor provides..."
                value={formData.notes}
                onChange={handleChange('notes')}
                helperText="Internal notes, services provided, contract details, etc."
              />
            </Grid>
          </Grid>
        </TabPanel>

        {/* Tab 3: SLAs */}
        <TabPanel value={tabValue} index={2}>
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="subtitle1">
              Service Level Agreements
            </Typography>
            <Button
              variant="outlined"
              size="small"
              startIcon={<Add />}
              onClick={handleAddSLA}
            >
              Add SLA
            </Button>
          </Box>

          {slas.length === 0 ? (
            <Alert severity="info">
              No SLAs defined yet. Click "Add SLA" to create one.
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {slas.map((sla, index) => (
                <Grid item xs={12} key={index}>
                  <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          size="small"
                          label="SLA Metric"
                          placeholder="e.g., Uptime"
                          value={sla.sla_metric}
                          onChange={(e) => handleSLAChange(index, 'sla_metric', e.target.value)}
                          disabled={!sla.isNew}
                        />
                      </Grid>
                      <Grid item xs={12} md={2}>
                        <TextField
                          fullWidth
                          size="small"
                          label="Target"
                          placeholder="99.9"
                          value={sla.target_value}
                          onChange={(e) => handleSLAChange(index, 'target_value', e.target.value)}
                          disabled={!sla.isNew}
                        />
                      </Grid>
                      <Grid item xs={12} md={2}>
                        <TextField
                          fullWidth
                          size="small"
                          label="Current"
                          placeholder="99.95"
                          value={sla.current_value}
                          onChange={(e) => handleSLAChange(index, 'current_value', e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12} md={2}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Period</InputLabel>
                          <Select
                            value={sla.measurement_period}
                            onChange={(e) => handleSLAChange(index, 'measurement_period', e.target.value)}
                            label="Period"
                            disabled={!sla.isNew}
                          >
                            <MenuItem value="Daily">Daily</MenuItem>
                            <MenuItem value="Weekly">Weekly</MenuItem>
                            <MenuItem value="Monthly">Monthly</MenuItem>
                            <MenuItem value="Quarterly">Quarterly</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} md={2}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Status</InputLabel>
                          <Select
                            value={sla.status}
                            onChange={(e) => handleSLAChange(index, 'status', e.target.value)}
                            label="Status"
                          >
                            <MenuItem value="Met">Met</MenuItem>
                            <MenuItem value="At Risk">At Risk</MenuItem>
                            <MenuItem value="Breached">Breached</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} md={1}>
                        {sla.isNew && (
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleRemoveSLA(index)}
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        )}
                      </Grid>
                    </Grid>
                  </Box>
                </Grid>
              ))}
            </Grid>
          )}

          {slas.some((sla) => sla.isNew) && (
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                size="small"
                onClick={handleSaveSLAs}
                disabled={loading}
              >
                Save New SLAs
              </Button>
            </Box>
          )}
        </TabPanel>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || tabValue === 2}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {vendor ? 'Update Vendor' : 'Create Vendor'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default VendorFormDialog
