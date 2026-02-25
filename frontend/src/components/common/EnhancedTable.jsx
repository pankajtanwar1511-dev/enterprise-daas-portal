import React, { useState } from 'react'
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
  Chip,
  Typography,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Checkbox,
  Button,
} from '@mui/material'
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  GetApp as ExportIcon,
  ViewColumn as ColumnIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'

/**
 * EnhancedTable - A reusable table component with sorting, filtering, pagination, and export
 *
 * Props:
 * - columns: Array of column definitions { id, label, sortable, filterable, render, align, width }
 * - data: Array of row data objects
 * - loading: Boolean for loading state
 * - onRefresh: Function to refresh data
 * - onRowClick: Function called when a row is clicked
 * - rowsPerPageOptions: Array of page size options (default: [10, 25, 50, 100])
 * - defaultOrderBy: Default column to sort by
 * - defaultOrder: Default sort order ('asc' or 'desc')
 * - searchPlaceholder: Placeholder text for search field
 * - exportFileName: Base name for exported files
 * - stickyHeader: Boolean to make header sticky
 * - dense: Boolean for compact row height
 */
function EnhancedTable({
  columns = [],
  data = [],
  loading = false,
  onRefresh,
  onRowClick,
  rowsPerPageOptions = [10, 25, 50, 100],
  defaultOrderBy = '',
  defaultOrder = 'asc',
  searchPlaceholder = 'Search...',
  exportFileName = 'data',
  stickyHeader = true,
  dense = false,
}) {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(rowsPerPageOptions[0])
  const [orderBy, setOrderBy] = useState(defaultOrderBy)
  const [order, setOrder] = useState(defaultOrder)
  const [searchTerm, setSearchTerm] = useState('')
  const [columnVisibility, setColumnVisibility] = useState(
    columns.reduce((acc, col) => ({ ...acc, [col.id]: true }), {})
  )
  const [columnMenuAnchor, setColumnMenuAnchor] = useState(null)

  // Sorting logic
  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc'
    setOrder(isAsc ? 'desc' : 'asc')
    setOrderBy(property)
  }

  // Search/Filter logic
  const filteredData = data.filter((row) => {
    if (!searchTerm) return true
    return columns.some((column) => {
      const value = row[column.id]
      if (value === null || value === undefined) return false
      return String(value).toLowerCase().includes(searchTerm.toLowerCase())
    })
  })

  // Sorting logic
  const sortedData = [...filteredData].sort((a, b) => {
    if (!orderBy) return 0
    const aVal = a[orderBy]
    const bVal = b[orderBy]

    if (aVal === null || aVal === undefined) return 1
    if (bVal === null || bVal === undefined) return -1

    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return order === 'asc' ? aVal - bVal : bVal - aVal
    }

    const aStr = String(aVal).toLowerCase()
    const bStr = String(bVal).toLowerCase()

    if (aStr < bStr) return order === 'asc' ? -1 : 1
    if (aStr > bStr) return order === 'asc' ? 1 : -1
    return 0
  })

  // Pagination
  const paginatedData = sortedData.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  // Column visibility toggle
  const handleToggleColumn = (columnId) => {
    setColumnVisibility((prev) => ({
      ...prev,
      [columnId]: !prev[columnId],
    }))
  }

  // Export to CSV
  const handleExport = () => {
    const visibleColumns = columns.filter((col) => columnVisibility[col.id])
    const headers = visibleColumns.map((col) => col.label).join(',')
    const rows = sortedData
      .map((row) =>
        visibleColumns
          .map((col) => {
            const value = row[col.id]
            // Handle values with commas or quotes
            if (value === null || value === undefined) return ''
            const str = String(value)
            if (str.includes(',') || str.includes('"') || str.includes('\n')) {
              return `"${str.replace(/"/g, '""')}"`
            }
            return str
          })
          .join(',')
      )
      .join('\n')

    const csv = `${headers}\n${rows}`
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${exportFileName}_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
  }

  const visibleColumns = columns.filter((col) => columnVisibility[col.id])

  return (
    <Box>
      {/* Toolbar */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
          gap: 2,
          flexWrap: 'wrap',
        }}
      >
        <TextField
          size="small"
          placeholder={searchPlaceholder}
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value)
            setPage(0)
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 300 }}
        />

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Toggle Columns">
            <IconButton
              size="small"
              onClick={(e) => setColumnMenuAnchor(e.currentTarget)}
            >
              <ColumnIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Export CSV">
            <IconButton size="small" onClick={handleExport}>
              <ExportIcon />
            </IconButton>
          </Tooltip>

          {onRefresh && (
            <Tooltip title="Refresh">
              <IconButton size="small" onClick={onRefresh}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </Box>

      {/* Column Visibility Menu */}
      <Menu
        anchorEl={columnMenuAnchor}
        open={Boolean(columnMenuAnchor)}
        onClose={() => setColumnMenuAnchor(null)}
      >
        {columns.map((column) => (
          <MenuItem
            key={column.id}
            onClick={() => handleToggleColumn(column.id)}
            dense
          >
            <ListItemIcon>
              <Checkbox
                checked={columnVisibility[column.id]}
                size="small"
                sx={{ p: 0 }}
              />
            </ListItemIcon>
            <ListItemText>{column.label}</ListItemText>
          </MenuItem>
        ))}
      </Menu>

      {/* Results Count */}
      <Box sx={{ mb: 1 }}>
        <Typography variant="body2" color="textSecondary">
          Showing {paginatedData.length} of {sortedData.length} results
          {sortedData.length !== data.length && ` (filtered from ${data.length} total)`}
        </Typography>
      </Box>

      {/* Table */}
      <TableContainer component={Paper} sx={{ boxShadow: 'none', border: '1px solid #e0e0e0' }}>
        <Table stickyHeader={stickyHeader} size={dense ? 'small' : 'medium'}>
          <TableHead>
            <TableRow>
              {visibleColumns.map((column, index) => (
                <TableCell
                  key={column.id}
                  align='left'
                  style={{ width: column.width }}
                  sx={{
                    fontWeight: 600,
                    backgroundColor: '#f5f5f5',
                    borderBottom: '2px solid #e0e0e0',
                    borderRight: index < visibleColumns.length - 1 ? '2px solid #d0d0d0' : 'none',
                    py: 1.5,
                    px: 2,
                  }}
                >
                  {column.sortable !== false ? (
                    <TableSortLabel
                      active={orderBy === column.id}
                      direction={orderBy === column.id ? order : 'asc'}
                      onClick={() => handleRequestSort(column.id)}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={visibleColumns.length} align="center" sx={{ py: 4, border: 'none' }}>
                  <Typography variant="body2" color="textSecondary">
                    Loading...
                  </Typography>
                </TableCell>
              </TableRow>
            ) : paginatedData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={visibleColumns.length} align="center" sx={{ py: 4, border: 'none' }}>
                  <Typography variant="body2" color="textSecondary">
                    {searchTerm ? 'No results found' : 'No data available'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              paginatedData.map((row, index) => (
                <TableRow
                  key={index}
                  hover
                  onClick={() => onRowClick && onRowClick(row)}
                  sx={{
                    cursor: onRowClick ? 'pointer' : 'default',
                    '&:hover': { backgroundColor: '#f9f9f9' },
                    '&:last-child td': { borderBottom: 'none' },
                  }}
                >
                  {visibleColumns.map((column) => (
                    <TableCell
                      key={column.id}
                      align='left'
                      sx={{
                        borderRight: 'none',
                        borderBottom: '1px solid #f0f0f0',
                        py: 1,
                      }}
                    >
                      {column.render
                        ? column.render(row[column.id], row)
                        : row[column.id]}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <TablePagination
        rowsPerPageOptions={rowsPerPageOptions}
        component="div"
        count={sortedData.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Box>
  )
}

export default EnhancedTable
