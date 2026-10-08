import React, { useState, useEffect } from 'react'
import axiosInstance from '../../utils/axiosInstance'
import pptxgen from 'pptxgenjs'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Button,
  TextField,
  Paper,
  Divider,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material'
import {
  PictureAsPdf,
  Download,
  Check,
  Slideshow,
} from '@mui/icons-material'

function PPTGenerator() {
  const [generating, setGenerating] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  // Presentation settings
  const [presentationTitle, setPresentationTitle] = useState('Enterprise DaaS Governance Report')
  const [companyName, setCompanyName] = useState('Your Company Name')
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0])

  // Section selection
  const [sections, setSections] = useState({
    coverSlide: true,
    executiveSummary: true,
    dashboardMetrics: true,
    complianceOverview: true,
    complianceCharts: true,
    violationsTable: true,
    strategyMetrics: true,
    strategyCharts: true,
    vendorMetrics: true,
    vendorCharts: true,
    assetInventory: true,
    recommendations: true,
  })

  // Data state
  const [data, setData] = useState({
    metrics: null,
    violations: [],
    assets: [],
    strategy: null,
    vendors: null,
  })

  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    try {
      const [metricsRes, violationsRes, assetsRes, strategyRes, vendorRes] = await Promise.all([
        axiosInstance.get('/api/v1/compliance/metrics'),
        axiosInstance.get('/api/v1/compliance/violations'),
        axiosInstance.get('/api/v1/assets/?limit=100'),
        axiosInstance.get('/api/v1/strategy/dashboard'),
        axiosInstance.get('/api/v1/vendors/dashboard'),
      ])

      setData({
        metrics: metricsRes.data,
        violations: violationsRes.data.violations || [],
        assets: assetsRes.data,
        strategy: strategyRes.data,
        vendors: vendorRes.data,
      })
    } catch (err) {
      console.error('Error fetching data:', err)
      setError('Failed to fetch data for presentation')
    }
  }

  const handleSectionToggle = (section) => {
    setSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const handleSelectAll = () => {
    const allSelected = Object.values(sections).every((v) => v)
    const newState = {}
    Object.keys(sections).forEach((key) => {
      newState[key] = !allSelected
    })
    setSections(newState)
  }

  const generatePPT = async () => {
    setGenerating(true)
    setSuccess(false)
    setError('')

    try {
      const pptx = new pptxgen()

      // Set presentation properties
      pptx.author = companyName
      pptx.company = companyName
      pptx.title = presentationTitle
      pptx.subject = 'DaaS Governance Report'

      // Define professional color scheme
      const colors = {
        primary: '1565C0',      // Deep blue
        primaryLight: '42A5F5', // Light blue
        success: '43A047',      // Professional green
        error: 'E53935',        // Professional red
        warning: 'FB8C00',      // Professional orange
        dark: '37474F',         // Professional dark gray
        light: 'FAFAFA',        // Very light gray
        white: 'FFFFFF',
        accent: 'E3F2FD',       // Light blue accent
        headerBg: '0D47A1',     // Dark blue for headers
      }

      // Helper function to add consistent slide header
      const addSlideHeader = (slide, title) => {
        slide.background = { color: colors.white }
        slide.addShape(pptx.ShapeType.rect, {
          x: 0,
          y: 0,
          w: 10,
          h: 0.7,
          fill: { color: colors.headerBg },
        })
        slide.addText(title, {
          x: 0.5,
          y: 0.1,
          w: 9,
          h: 0.5,
          fontSize: 22,
          bold: true,
          color: colors.white,
        })
      }

      // Helper to calculate optimal table configuration based on data volume
      const getTableConfig = (rowCount) => {
        // Slide dimensions: 10" wide x 7.5" tall
        const slideHeight = 7.5
        const headerHeight = 0.7
        const footerSpace = 0.5  // Increased for safety
        const topMargin = 0.2
        const availableHeight = slideHeight - headerHeight - footerSpace - topMargin

        // Calculate optimal row height based on number of rows
        // More rows = smaller row height to fit more content
        let rowHeight = 0.40  // Default for small tables (<10 rows)
        let fontSize = 11

        if (rowCount > 30) {
          rowHeight = 0.22
          fontSize = 7
        } else if (rowCount > 25) {
          rowHeight = 0.25
          fontSize = 8
        } else if (rowCount > 20) {
          rowHeight = 0.28
          fontSize = 9
        } else if (rowCount > 15) {
          rowHeight = 0.30
          fontSize = 9
        } else if (rowCount > 10) {
          rowHeight = 0.35
          fontSize = 10
        }

        // Calculate how many rows can fit on one slide
        const maxRows = Math.floor(availableHeight / rowHeight)

        return {
          rowHeight,
          maxRows,
          tableStartY: headerHeight + topMargin,
          fontSize,
          availableHeight,
          maxY: slideHeight - footerSpace,  // Maximum safe Y position
        }
      }

      // Helper to ensure content fits within slide
      const getSafeContentHeight = (startY) => {
        const slideHeight = 7.5
        const footerSpace = 0.5
        const maxY = slideHeight - footerSpace
        return maxY - startY
      }

      // Helper to safely truncate text
      const truncateText = (text, maxLength) => {
        if (!text) return ''
        const str = String(text)
        if (str.length <= maxLength) return str

        // Try to truncate at word boundary if possible
        const truncated = str.substring(0, maxLength - 3)
        const lastSpace = truncated.lastIndexOf(' ')

        if (lastSpace > maxLength * 0.7) {
          // If we found a space in the last 30%, use it
          return truncated.substring(0, lastSpace) + '...'
        }

        // Otherwise just hard truncate
        return truncated + '...'
      }

      // Helper to create colored table header
      const createTableHeader = (headers, color) => {
        return headers.map(header => ({
          text: header,
          options: {
            bold: true,
            fontSize: 10,
            fill: { color: color },
            color: colors.white,
          },
        }))
      }

      // 1. Cover Slide (Enhanced design)
      if (sections.coverSlide) {
        const slide1 = pptx.addSlide()
        slide1.background = { color: colors.headerBg }

        // Add decorative shape
        slide1.addShape(pptx.ShapeType.rect, {
          x: 0,
          y: 0,
          w: 10,
          h: 2.5,
          fill: { color: colors.primary, transparency: 30 },
        })

        slide1.addText(presentationTitle, {
          x: 0.5,
          y: 2.2,
          w: 9,
          h: 1.2,
          fontSize: 40,
          bold: true,
          color: colors.white,
          align: 'center',
        })

        // Decorative line
        slide1.addShape(pptx.ShapeType.rect, {
          x: 2.5,
          y: 3.6,
          w: 5,
          h: 0.02,
          fill: { color: colors.accent },
        })

        slide1.addText(companyName, {
          x: 0.5,
          y: 4.0,
          w: 9,
          h: 0.5,
          fontSize: 22,
          color: colors.accent,
          align: 'center',
        })

        slide1.addText(reportDate, {
          x: 0.5,
          y: 4.7,
          w: 9,
          h: 0.4,
          fontSize: 16,
          color: colors.accent,
          align: 'center',
        })

        // Footer
        slide1.addText('Enterprise DaaS Governance Portal', {
          x: 0.5,
          y: 6.8,
          w: 9,
          h: 0.3,
          fontSize: 10,
          color: colors.accent,
          align: 'center',
          italic: true,
        })
      }

      // 2. Executive Summary (Dynamic sizing)
      if (sections.executiveSummary && data.metrics) {
        const slide2 = pptx.addSlide()
        addSlideHeader(slide2, 'Executive Summary')

        const summaryData = [
          createTableHeader(['Metric', 'Value', 'Status'], colors.primary),
          [
            'Total Assets',
            String(data.metrics.total_assets),
            'Active',
          ],
          [
            'Compliance Rate',
            `${data.metrics.compliance_rate.toFixed(1)}%`,
            data.metrics.compliance_rate >= 95 ? 'Excellent' : data.metrics.compliance_rate >= 85 ? 'Good' : 'Action Needed',
          ],
          [
            'Compliant Assets',
            String(data.metrics.compliant_assets),
            'On Track',
          ],
          [
            'Non-Compliant',
            String(data.metrics.non_compliant_assets),
            data.metrics.non_compliant_assets === 0 ? 'None' : 'Fix Needed',
          ],
          [
            'Missing Docs',
            String(data.metrics.missing_documentation),
            data.metrics.missing_documentation === 0 ? 'Complete' : 'In Progress',
          ],
        ]

        const summaryConfig = getTableConfig(summaryData.length)

        slide2.addTable(summaryData, {
          x: 0.5,
          y: summaryConfig.tableStartY,
          w: 9.0,
          colW: [3.0, 3.0, 3.0],
          fontSize: summaryConfig.fontSize,
          border: { pt: 0.5, color: 'E0E0E0' },
          fill: { color: colors.accent },
          color: colors.dark,
          rowH: summaryConfig.rowHeight,
          valign: 'middle',
          align: 'center',
        })

        // Key Insights box - positioned below table with SAFE height
        const tableEndY = summaryConfig.tableStartY + (summaryData.length * summaryConfig.rowHeight)
        const insightsY = tableEndY + 0.3

        // Calculate safe box height: max position 6.2", so maxBoxHeight = 6.2 - insightsY
        const maxSafeBoxEnd = 6.2
        const maxInsightsHeight = maxSafeBoxEnd - insightsY
        const insightsBoxHeight = Math.min(1.8, Math.max(1.2, maxInsightsHeight))  // Between 1.2" and 1.8"

        slide2.addShape(pptx.ShapeType.rect, {
          x: 0.5,
          y: insightsY,
          w: 9.0,
          h: insightsBoxHeight,
          fill: { color: colors.accent },
          line: { color: colors.primary, width: 1 },
        })

        slide2.addText('Key Insights', {
          x: 0.7,
          y: insightsY + 0.12,
          w: 8.6,
          h: 0.25,
          fontSize: 13,
          bold: true,
          color: colors.primary,
        })

        const insights = [
          `• ${data.metrics.compliance_rate.toFixed(1)}% compliance rate ${data.metrics.compliance_rate >= 95 ? 'exceeds' : 'approaching'} target`,
          `• ${data.metrics.compliant_assets} of ${data.metrics.total_assets} assets meet naming standards`,
          `• ${data.metrics.non_compliant_assets} asset${data.metrics.non_compliant_assets !== 1 ? 's' : ''} require${data.metrics.non_compliant_assets === 1 ? 's' : ''} immediate remediation`,
        ]

        slide2.addText(insights.join('\n'), {
          x: 0.7,
          y: insightsY + 0.45,
          w: 8.6,
          h: insightsBoxHeight - 0.55,
          fontSize: 10,
          color: colors.dark,
          lineSpacing: 14,
          valign: 'top',
        })
      }

      // 3. Dashboard Metrics (Enhanced visual design)
      if (sections.dashboardMetrics && data.metrics) {
        const slide3 = pptx.addSlide()
        addSlideHeader(slide3, 'Governance Dashboard Metrics')

        // Add metric boxes with shadow effect
        const metrics = [
          {
            title: 'Total Assets',
            value: data.metrics.total_assets,
            color: colors.primary,
            x: 0.6,
            y: 1.2,
          },
          {
            title: 'Compliance Rate',
            value: `${data.metrics.compliance_rate.toFixed(1)}%`,
            color: data.metrics.compliance_rate >= 95 ? colors.success : data.metrics.compliance_rate >= 85 ? colors.warning : colors.error,
            x: 2.9,
            y: 1.2,
          },
          {
            title: 'Compliant',
            value: data.metrics.compliant_assets,
            color: colors.success,
            x: 5.2,
            y: 1.2,
          },
          {
            title: 'Non-Compliant',
            value: data.metrics.non_compliant_assets,
            color: colors.error,
            x: 7.5,
            y: 1.2,
          },
        ]

        metrics.forEach((metric) => {
          slide3.addShape(pptx.ShapeType.rect, {
            x: metric.x,
            y: metric.y,
            w: 2.2,
            h: 1.4,
            fill: { color: metric.color },
            line: { color: colors.dark, width: 0.5, transparency: 70 },
          })

          slide3.addText(metric.title, {
            x: metric.x,
            y: metric.y + 0.15,
            w: 2.2,
            h: 0.35,
            fontSize: 12,
            color: colors.white,
            align: 'center',
            bold: true,
          })

          slide3.addText(String(metric.value), {
            x: metric.x,
            y: metric.y + 0.6,
            w: 2.2,
            h: 0.6,
            fontSize: 32,
            color: colors.white,
            align: 'center',
            bold: true,
          })
        })

        // Add breakdown by environment with dynamic sizing
        const envBreakdown = data.assets.reduce((acc, asset) => {
          acc[asset.environment] = (acc[asset.environment] || 0) + 1
          return acc
        }, {})

        const envData = [
          createTableHeader(['Environment', 'Count', '%'], colors.primary),
          ...Object.entries(envBreakdown).map(([env, count]) => [
            env,
            String(count),
            `${((count / data.assets.length) * 100).toFixed(0)}%`,
          ]),
        ]

        const envConfig = getTableConfig(envData.length)

        slide3.addText('Assets by Environment', {
          x: 0.5,
          y: 2.9,
          w: 4.5,
          h: 0.3,
          fontSize: 14,
          bold: true,
          color: colors.primary,
        })

        slide3.addTable(envData, {
          x: 0.5,
          y: 3.3,
          w: 4.5,
          colW: [2.0, 1.25, 1.25],
          fontSize: envConfig.fontSize,
          border: { pt: 0.5, color: 'E0E0E0' },
          fill: { color: colors.white },
          color: colors.dark,
          align: 'center',
          valign: 'middle',
          rowH: envConfig.rowHeight,
        })
      }

      // 4. Compliance Overview (Visual metrics)
      if (sections.complianceOverview && data.metrics) {
        const slideComp = pptx.addSlide()
        addSlideHeader(slideComp, 'Compliance Overview')

        // Visual metric boxes
        const compMetrics = [
          {
            title: 'Total Assets',
            value: data.metrics.total_assets,
            color: colors.primary,
            x: 0.5,
            y: 1.2,
          },
          {
            title: 'Compliance Rate',
            value: `${data.metrics.compliance_rate}%`,
            color: data.metrics.compliance_rate >= 95 ? colors.success : colors.warning,
            x: 5.3,
            y: 1.2,
          },
          {
            title: 'Compliant',
            value: data.metrics.compliant_assets,
            color: colors.success,
            x: 0.5,
            y: 3.2,
          },
          {
            title: 'Non-Compliant',
            value: data.metrics.non_compliant_assets,
            color: colors.error,
            x: 5.3,
            y: 3.2,
          },
        ]

        compMetrics.forEach((metric) => {
          slideComp.addShape(pptx.ShapeType.rect, {
            x: metric.x,
            y: metric.y,
            w: 4.5,
            h: 1.6,
            fill: { color: metric.color },
          })

          slideComp.addText(metric.title, {
            x: metric.x,
            y: metric.y + 0.2,
            w: 4.5,
            h: 0.4,
            fontSize: 16,
            color: 'FFFFFF',
            align: 'center',
            bold: true,
          })

          slideComp.addText(String(metric.value), {
            x: metric.x,
            y: metric.y + 0.7,
            w: 4.5,
            h: 0.7,
            fontSize: 48,
            color: 'FFFFFF',
            align: 'center',
            bold: true,
          })
        })

        // Compliance target status
        const targetText =
          data.metrics.compliance_rate >= 95
            ? '✓ Target Achieved: Compliance rate exceeds 95% target'
            : `⚠ Action Required: ${(95 - data.metrics.compliance_rate).toFixed(1)}% improvement needed to reach 95% target`

        slideComp.addText(targetText, {
          x: 0.5,
          y: 5.2,
          w: 9,
          h: 0.6,
          fontSize: 15,
          color: data.metrics.compliance_rate >= 95 ? colors.success : colors.warning,
          align: 'center',
          bold: true,
        })
      }

      // 4b. Compliance Charts & Distribution (Fixed for legend height)
      if (sections.complianceCharts && data.metrics) {
        const slide4 = pptx.addSlide()
        addSlideHeader(slide4, 'Compliance Distribution Analysis')

        // Pie chart data
        const chartData = [
          {
            name: 'Compliant',
            labels: ['Compliant'],
            values: [data.metrics.compliant_assets],
          },
          {
            name: 'Non-Compliant',
            labels: ['Non-Compliant'],
            values: [data.metrics.non_compliant_assets],
          },
        ]

        // Add pie chart - reduced height to prevent overflow
        slide4.addChart(pptx.ChartType.pie, chartData, {
          x: 0.5,
          y: 1.0,
          w: 5.0,
          h: 3.8,  // Reduced: 1.0 + 3.8 = 4.8"
          showLegend: true,
          legendPos: 'r',  // Right legend instead of bottom
          dataLabelColor: 'FFFFFF',
          dataLabelFontSize: 13,
          showValue: true,
          showPercent: true,
          showTitle: false,
        })

        // Add summary text in a box - sized to fit content
        const summaryBoxHeight = 3.5  // Fits the text content properly
        slide4.addShape(pptx.ShapeType.rect, {
          x: 5.7,
          y: 1.0,
          w: 3.8,
          h: summaryBoxHeight,  // Box end: 1.0 + 3.5 = 4.5" (safe!)
          fill: { color: colors.accent },
          line: { color: colors.primary, width: 1 },
        })

        slide4.addText('Compliance Summary', {
          x: 5.9,
          y: 1.15,
          w: 3.4,
          h: 0.3,
          fontSize: 14,
          bold: true,
          color: colors.primary,
        })

        const complianceText = [
          `Total Assets: ${data.metrics.total_assets}`,
          '',
          `Compliant: ${data.metrics.compliant_assets}`,
          `(${data.metrics.compliance_rate.toFixed(1)}%)`,
          '',
          `Non-Compliant: ${data.metrics.non_compliant_assets}`,
          '',
          `Missing Docs: ${data.metrics.missing_documentation}`,
          '',
          data.metrics.compliance_rate >= 95
            ? '✓ Target Achieved'
            : `⚠ ${(95 - data.metrics.compliance_rate).toFixed(1)}% needed`,
        ]

        slide4.addText(complianceText.join('\n'), {
          x: 5.9,
          y: 1.55,
          w: 3.4,
          h: 2.8,  // Adjusted to fit within 3.5" box
          fontSize: 10,
          color: colors.dark,
          valign: 'top',
          lineSpacing: 13,
        })
      }

      // 5. Violations Table (Dynamic sizing based on data)
      if (sections.violationsTable && data.violations.length > 0) {
        // Calculate optimal configuration
        const tableConfig = getTableConfig(data.violations.length)
        const violationsPerSlide = tableConfig.maxRows - 1 // -1 for header row
        const totalViolationSlides = Math.ceil(data.violations.length / violationsPerSlide)

        for (let slideIndex = 0; slideIndex < totalViolationSlides; slideIndex++) {
          const slide5 = pptx.addSlide()
          const slideTitle = totalViolationSlides > 1
            ? `Compliance Violations (Page ${slideIndex + 1}/${totalViolationSlides})`
            : 'Active Compliance Violations'

          addSlideHeader(slide5, slideTitle)

          const startIdx = slideIndex * violationsPerSlide
          const endIdx = Math.min(startIdx + violationsPerSlide, data.violations.length)
          const slideViolations = data.violations.slice(startIdx, endIdx)

          const violationData = [
            createTableHeader(['Asset', 'Type', 'Severity', 'Description'], colors.error),
            ...slideViolations.map((v) => [
              String(v.asset_id),
              truncateText(v.violation_type, 18),
              v.severity,
              truncateText(v.description, 80),
            ]),
          ]

          const actualRows = slideViolations.length + 1
          const config = getTableConfig(actualRows)

          slide5.addTable(violationData, {
            x: 0.5,
            y: config.tableStartY,
            w: 9.0,
            colW: [0.8, 1.6, 1.0, 5.6],
            fontSize: config.fontSize,
            border: { pt: 0.5, color: 'E0E0E0' },
            fill: { color: colors.white },
            color: colors.dark,
            align: 'left',
            valign: 'middle',
            rowH: config.rowHeight,
          })

          if (totalViolationSlides > 1) {
            slide5.addText(
              `Showing ${startIdx + 1}-${endIdx} of ${data.violations.length} violations`,
              {
                x: 0.5,
                y: 6.8,
                w: 9.0,
                h: 0.25,
                fontSize: 8,
                color: '999999',
                italic: true,
                align: 'right',
              }
            )
          }
        }
      }

      // 6. Strategy Metrics (Dynamic sizing)
      if (sections.strategyMetrics && data.strategy) {
        const slide6 = pptx.addSlide()
        addSlideHeader(slide6, 'DaaS Strategy Overview')

        const strategyData = [
          createTableHeader(['Category', 'Metric', 'Value'], colors.primary),
          [
            'Business Goals',
            'Active Goals',
            String(data.strategy.business_goals.active),
          ],
          [
            'Business Goals',
            'Achievement Rate',
            `${data.strategy.business_goals.achievement_rate}%`,
          ],
          [
            'Initiatives',
            'Total',
            String(data.strategy.strategic_initiatives.total),
          ],
          [
            'Initiatives',
            'On Track',
            String(data.strategy.strategic_initiatives.on_track),
          ],
          [
            'Initiatives',
            'At Risk',
            String(data.strategy.strategic_initiatives.at_risk),
          ],
          [
            'Budget',
            'Total Allocated',
            `$${(data.strategy.budget.total_allocated / 1000000).toFixed(1)}M`,
          ],
          [
            'Budget',
            'Utilization',
            `${data.strategy.budget.utilization_percentage.toFixed(1)}%`,
          ],
          [
            'ROI',
            'Expected ROI',
            `${data.strategy.roi_metrics.roi_percentage}%`,
          ],
        ]

        const config = getTableConfig(strategyData.length)

        slide6.addTable(strategyData, {
          x: 0.5,
          y: config.tableStartY,
          w: 9.0,
          colW: [2.5, 3.3, 3.2],
          fontSize: config.fontSize,
          border: { pt: 0.5, color: 'E0E0E0' },
          fill: { color: colors.white },
          color: colors.dark,
          align: 'left',
          valign: 'middle',
          rowH: config.rowHeight,
        })
      }

      // 6b. Strategy Charts (Budget & Initiatives visualization) - No titles to save space
      if (sections.strategyCharts && data.strategy) {
        const slideStrategy = pptx.addSlide()
        addSlideHeader(slideStrategy, 'Strategic Initiatives & Budget')

        // Add chart titles as text to control positioning
        slideStrategy.addText('Budget Utilization', {
          x: 0.5,
          y: 0.85,
          w: 4.5,
          h: 0.3,
          fontSize: 14,
          bold: true,
          color: colors.primary,
          align: 'center',
        })

        slideStrategy.addText('Initiative Status', {
          x: 5.2,
          y: 0.85,
          w: 4.3,
          h: 0.3,
          fontSize: 14,
          bold: true,
          color: colors.primary,
          align: 'center',
        })

        // Budget Pie Chart - no title, right legend
        const budgetChartData = [
          {
            name: 'Spent',
            labels: ['Spent'],
            values: [data.strategy.budget.total_spent],
          },
          {
            name: 'Remaining',
            labels: ['Remaining'],
            values: [data.strategy.budget.remaining],
          },
        ]

        slideStrategy.addChart(pptx.ChartType.pie, budgetChartData, {
          x: 0.5,
          y: 1.2,
          w: 4.5,
          h: 2.5,
          showLegend: true,
          legendPos: 'r',
          dataLabelColor: 'FFFFFF',
          dataLabelFontSize: 11,
          showValue: false,
          showPercent: true,
          showTitle: false,
        })

        // Initiatives Bar Chart - no title
        const initiativesChartData = [
          {
            name: 'Initiatives',
            labels: ['On Track', 'At Risk'],
            values: [
              data.strategy.strategic_initiatives.on_track,
              data.strategy.strategic_initiatives.at_risk,
            ],
          },
        ]

        slideStrategy.addChart(pptx.ChartType.bar, initiativesChartData, {
          x: 5.2,
          y: 1.2,
          w: 4.3,
          h: 2.5,
          showLegend: false,
          barDir: 'col',
          dataLabelColor: '000000',
          dataLabelFontSize: 11,
          showValue: true,
          showTitle: false,
          valAxisMaxVal: Math.max(
            data.strategy.strategic_initiatives.on_track,
            data.strategy.strategic_initiatives.at_risk
          ) + 2,
        })

        // Key metrics summary in a box - positioned closer to charts
        const metricsBoxY = 4.1  // Charts h=2.5 end at ~3.9", start box at 4.1"
        const metricsBoxHeight = 1.0  // Box end: 4.1 + 1.0 = 5.1" (safe!)

        slideStrategy.addShape(pptx.ShapeType.rect, {
          x: 0.5,
          y: metricsBoxY,
          w: 9.0,
          h: metricsBoxHeight,
          fill: { color: colors.accent },
          line: { color: colors.primary, width: 1 },
        })

        slideStrategy.addText('Key Strategic Metrics', {
          x: 0.7,
          y: metricsBoxY + 0.1,
          w: 8.6,
          h: 0.25,
          fontSize: 12,
          bold: true,
          color: colors.primary,
        })

        const metricsText = [
          `Budget Allocated: $${(data.strategy.budget.total_allocated / 1000000).toFixed(1)}M  |  ` +
          `Budget Utilized: ${data.strategy.budget.utilization_percentage.toFixed(1)}%`,
          `Total Initiatives: ${data.strategy.strategic_initiatives.total}  |  ` +
          `Expected ROI: ${data.strategy.roi_metrics.roi_percentage}%`,
        ]

        slideStrategy.addText(metricsText.join('\n'), {
          x: 0.7,
          y: metricsBoxY + 0.38,
          w: 8.6,
          h: 0.55,
          fontSize: 10,
          color: colors.dark,
          valign: 'middle',
          lineSpacing: 14,
        })
      }

      // 6c. Vendor Metrics & Charts - Fixed overflow
      if (sections.vendorMetrics && data.vendors) {
        const slideVendor = pptx.addSlide()
        addSlideHeader(slideVendor, 'Vendor & Budget Management')

        // Vendor metrics in visual boxes (adjusted to fit within slide)
        const vendorMetrics = [
          {
            title: 'Total Vendors',
            value: data.vendors.vendor_summary.active_vendors,
            x: 0.5,
            y: 1.0,
            color: colors.primary,
          },
          {
            title: 'Annual Cost',
            value: `$${(data.vendors.cost_management.total_annual_cost / 1000000).toFixed(1)}M`,
            x: 2.9,
            y: 1.0,
            color: colors.warning,
          },
          {
            title: 'Cost Trend',
            value: data.vendors.cost_management.cost_trend,
            x: 5.3,
            y: 1.0,
            color: colors.success,
          },
          {
            title: 'SLA Compliance',
            value: data.vendors.sla_performance.overall_compliance,
            x: 7.7,
            y: 1.0,
            color: colors.success,
          },
        ]

        vendorMetrics.forEach((metric) => {
          slideVendor.addShape(pptx.ShapeType.rect, {
            x: metric.x,
            y: metric.y,
            w: 2.2,
            h: 1.2,
            fill: { color: metric.color },
          })

          slideVendor.addText(metric.title, {
            x: metric.x,
            y: metric.y + 0.15,
            w: 2.2,
            h: 0.3,
            fontSize: 10,
            color: 'FFFFFF',
            align: 'center',
            bold: true,
          })

          slideVendor.addText(String(metric.value), {
            x: metric.x,
            y: metric.y + 0.55,
            w: 2.2,
            h: 0.5,
            fontSize: 22,
            color: 'FFFFFF',
            align: 'center',
            bold: true,
          })
        })

        // Cost optimization info - safe position
        slideVendor.addText('Cost Optimization:', {
          x: 0.5,
          y: 2.4,
          w: 9,
          h: 0.3,
          fontSize: 15,
          bold: true,
          color: colors.dark,
        })

        const costText = [
          `Potential Savings: ${data.vendors.cost_management.cost_optimization_opportunities}`,
          `Monthly Average: $${(data.vendors.cost_management.monthly_average / 1000).toFixed(0)}K`,
          `Cost Trend: ${data.vendors.cost_management.cost_trend} YoY`,
        ]

        slideVendor.addText(costText.join('\n'), {
          x: 0.5,
          y: 2.8,
          w: 9,
          h: 0.9,
          fontSize: 12,
          color: colors.dark,
          lineSpacing: 16,
        })

        // SLA Performance Metrics in visual boxes
        slideVendor.addText('SLA Performance Summary:', {
          x: 0.5,
          y: 4.0,
          w: 9,
          h: 0.3,
          fontSize: 15,
          bold: true,
          color: colors.dark,
        })

        const slaMetricBoxes = [
          {
            title: 'At Risk',
            value: `${data.vendors.sla_performance.at_risk_count} SLAs`,
            x: 1.5,
            y: 4.5,
            color: colors.warning,
          },
          {
            title: 'Breached',
            value: `${data.vendors.sla_performance.breached_count} SLAs`,
            x: 4.2,
            y: 4.5,
            color: colors.error,
          },
          {
            title: 'Overall Compliance',
            value: data.vendors.sla_performance.overall_compliance,
            x: 6.9,
            y: 4.5,
            color: colors.success,
          },
        ]

        slaMetricBoxes.forEach((metric) => {
          slideVendor.addShape(pptx.ShapeType.rect, {
            x: metric.x,
            y: metric.y,
            w: 2.4,
            h: 1.0,
            fill: { color: metric.color },
          })

          slideVendor.addText(metric.title, {
            x: metric.x,
            y: metric.y + 0.12,
            w: 2.4,
            h: 0.25,
            fontSize: 10,
            color: 'FFFFFF',
            align: 'center',
            bold: true,
          })

          slideVendor.addText(String(metric.value), {
            x: metric.x,
            y: metric.y + 0.45,
            w: 2.4,
            h: 0.4,
            fontSize: 16,
            color: 'FFFFFF',
            align: 'center',
            bold: true,
          })
        })
      }

      // 6d. Vendor Charts - Reduced chart height to prevent overflow
      if (sections.vendorCharts && data.vendors) {
        const slideVendorChart = pptx.addSlide()
        addSlideHeader(slideVendorChart, 'Vendor SLA Compliance Analysis')

        // Add chart title as text
        slideVendorChart.addText('SLA Compliance Status', {
          x: 0.5,
          y: 0.85,
          w: 9.0,
          h: 0.3,
          fontSize: 16,
          bold: true,
          color: colors.primary,
          align: 'center',
        })

        // SLA Status Bar Chart - reduced height to prevent overflow
        const slaStatusData = [
          {
            name: 'SLAs',
            labels: ['Met', 'At Risk', 'Breached'],
            values: [
              Object.values(data.vendors.sla_performance.by_status)[0] || 0,
              data.vendors.sla_performance.at_risk_count,
              data.vendors.sla_performance.breached_count,
            ],
          },
        ]

        // Chart reduced significantly: h=3.5 to leave room for text box
        // Chart end: 1.2 + 3.5 = 4.7" (with padding ~5.2")
        slideVendorChart.addChart(pptx.ChartType.bar, slaStatusData, {
          x: 0.5,
          y: 1.2,
          w: 9.0,
          h: 3.5,
          barDir: 'col',
          showLegend: false,
          dataLabelColor: '000000',
          dataLabelFontSize: 12,
          showValue: true,
          showTitle: false,
        })

        // Summary text in safe box below chart - positioned safely
        slideVendorChart.addShape(pptx.ShapeType.rect, {
          x: 0.5,
          y: 5.0,
          w: 9.0,
          h: 0.55,
          fill: { color: colors.accent },
          line: { color: colors.primary, width: 1 },
        })

        slideVendorChart.addText(
          `Total SLAs tracked across ${data.vendors.vendor_summary.active_vendors} active vendors`,
          {
            x: 0.7,
            y: 5.15,
            w: 8.6,
            h: 0.3,
            fontSize: 11,
            color: colors.dark,
            italic: true,
            align: 'center',
            valign: 'middle',
          }
        )
      }

      // 7. Asset Inventory (Dynamic sizing based on data)
      if (sections.assetInventory && data.assets.length > 0) {
        // Calculate optimal configuration
        const tableConfig = getTableConfig(data.assets.length)
        const assetsPerSlide = tableConfig.maxRows - 1 // -1 for header row
        const totalAssetSlides = Math.ceil(data.assets.length / assetsPerSlide)

        for (let slideIndex = 0; slideIndex < totalAssetSlides; slideIndex++) {
          const slide7 = pptx.addSlide()
          const slideTitle = totalAssetSlides > 1
            ? `Asset Inventory (Page ${slideIndex + 1}/${totalAssetSlides})`
            : 'Asset Inventory'

          addSlideHeader(slide7, slideTitle)

          const startIdx = slideIndex * assetsPerSlide
          const endIdx = Math.min(startIdx + assetsPerSlide, data.assets.length)
          const slideAssets = data.assets.slice(startIdx, endIdx)

          const assetData = [
            createTableHeader(['Asset Name', 'Env', 'Lifecycle', 'Compliant'], colors.primary),
            ...slideAssets.map((a) => [
              truncateText(a.asset_name, 35),
              a.environment,
              truncateText(a.lifecycle_stage, 12),
              a.naming_compliant ? 'Yes' : 'No',
            ]),
          ]

          const actualRows = slideAssets.length + 1
          const config = getTableConfig(actualRows)

          slide7.addTable(assetData, {
            x: 0.5,
            y: config.tableStartY,
            w: 9.0,
            colW: [3.8, 1.4, 2.1, 1.7],
            fontSize: config.fontSize,
            border: { pt: 0.5, color: 'E0E0E0' },
            fill: { color: colors.white },
            color: colors.dark,
            align: 'left',
            valign: 'middle',
            rowH: config.rowHeight,
          })

          if (totalAssetSlides > 1) {
            slide7.addText(
              `Showing ${startIdx + 1}-${endIdx} of ${data.assets.length} total assets`,
              {
                x: 0.5,
                y: 6.8,
                w: 9.0,
                h: 0.25,
                fontSize: 8,
                color: '999999',
                italic: true,
                align: 'right',
              }
            )
          }
        }
      }

      // 8. Recommendations - Safe layout with conservative height
      if (sections.recommendations) {
        const slide8 = pptx.addSlide()
        addSlideHeader(slide8, 'Recommendations & Next Steps')

        const recommendations = []

        if (data.metrics && data.metrics.non_compliant_assets > 0) {
          recommendations.push(
            `• Address ${data.metrics.non_compliant_assets} non-compliant asset${data.metrics.non_compliant_assets > 1 ? 's' : ''} to improve governance`
          )
        }

        if (data.metrics && data.metrics.compliance_rate < 95) {
          recommendations.push(
            `• Implement naming convention training to reach 95% target`
          )
        }

        if (data.metrics && data.metrics.missing_documentation > 0) {
          recommendations.push(
            `• Complete documentation for ${data.metrics.missing_documentation} asset${data.metrics.missing_documentation > 1 ? 's' : ''}`
          )
        }

        recommendations.push('• Schedule quarterly governance reviews with stakeholders')
        recommendations.push('• Automate compliance checks in CI/CD pipelines')
        recommendations.push('• Establish asset lifecycle management process')
        recommendations.push('• Implement role-based access controls for sensitive data')
        recommendations.push('• Enable real-time monitoring and alerting')

        // Background box for recommendations - sized to fit content
        const boxY = 1.0
        const boxHeight = 3.8  // Box end: 1.0 + 3.8 = 4.8" (fits content, very safe!)

        slide8.addShape(pptx.ShapeType.rect, {
          x: 0.5,
          y: boxY,
          w: 9.0,
          h: boxHeight,
          fill: { color: colors.accent },
          line: { color: colors.primary, width: 1 },
        })

        slide8.addText('Key Recommendations:', {
          x: 0.7,
          y: boxY + 0.15,
          w: 8.6,
          h: 0.3,
          fontSize: 14,
          bold: true,
          color: colors.primary,
        })

        slide8.addText(recommendations.join('\n'), {
          x: 0.7,
          y: boxY + 0.5,
          w: 8.6,
          h: 3.1,
          fontSize: 10,
          color: colors.dark,
          bullet: false,
          lineSpacing: 13,
          valign: 'top',
        })
      }

      // Generate and download
      const fileName = `DaaS_Governance_Report_${reportDate}.pptx`
      await pptx.writeFile({ fileName })

      setSuccess(true)
      setGenerating(false)
    } catch (err) {
      console.error('Error generating PPT:', err)
      setError('Failed to generate presentation: ' + err.message)
      setGenerating(false)
    }
  }

  const selectedCount = Object.values(sections).filter((v) => v).length
  const totalSections = Object.keys(sections).length

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        PowerPoint Generator
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Create a professional presentation from your governance data. Select the sections you want to include.
      </Typography>

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(false)}>
          <strong>Success!</strong> Your presentation has been downloaded. Check your Downloads folder.
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Settings */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Presentation Settings
              </Typography>

              <TextField
                fullWidth
                label="Title"
                value={presentationTitle}
                onChange={(e) => setPresentationTitle(e.target.value)}
                margin="normal"
              />

              <TextField
                fullWidth
                label="Company Name"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                margin="normal"
              />

              <TextField
                fullWidth
                label="Report Date"
                type="date"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
                margin="normal"
                InputLabelProps={{ shrink: true }}
              />

              <Divider sx={{ my: 2 }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="body2">
                  {selectedCount} of {totalSections} sections selected
                </Typography>
                <Button size="small" onClick={handleSelectAll}>
                  {selectedCount === totalSections ? 'Deselect All' : 'Select All'}
                </Button>
              </Box>

              <Button
                fullWidth
                variant="contained"
                size="large"
                startIcon={generating ? <CircularProgress size={20} color="inherit" /> : <Slideshow />}
                onClick={generatePPT}
                disabled={generating || selectedCount === 0}
                sx={{ mt: 2 }}
              >
                {generating ? 'Generating...' : 'Generate Presentation'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Section Selection */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Select Slides to Include
              </Typography>

              <Paper sx={{ p: 2, bgcolor: '#F5F5F5', mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Introduction
                </Typography>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.coverSlide}
                        onChange={() => handleSectionToggle('coverSlide')}
                      />
                    }
                    label="Cover Slide (Title, company, date)"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.executiveSummary}
                        onChange={() => handleSectionToggle('executiveSummary')}
                      />
                    }
                    label="Executive Summary (Key metrics & insights)"
                  />
                </FormGroup>
              </Paper>

              <Paper sx={{ p: 2, bgcolor: '#E3F2FD', mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Dashboard & Metrics
                </Typography>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.dashboardMetrics}
                        onChange={() => handleSectionToggle('dashboardMetrics')}
                      />
                    }
                    label="Dashboard Metrics (Total assets, compliance rate)"
                  />
                </FormGroup>
              </Paper>

              <Paper sx={{ p: 2, bgcolor: '#E8F5E9', mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Compliance
                </Typography>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.complianceOverview}
                        onChange={() => handleSectionToggle('complianceOverview')}
                      />
                    }
                    label="Compliance Overview"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.complianceCharts}
                        onChange={() => handleSectionToggle('complianceCharts')}
                      />
                    }
                    label="Compliance Charts (Pie charts, distribution)"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.violationsTable}
                        onChange={() => handleSectionToggle('violationsTable')}
                      />
                    }
                    label={`Violations Table (${data.violations.length} violations)`}
                  />
                </FormGroup>
              </Paper>

              <Paper sx={{ p: 2, bgcolor: '#FFF3E0', mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Strategy
                </Typography>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.strategyMetrics}
                        onChange={() => handleSectionToggle('strategyMetrics')}
                      />
                    }
                    label="Strategy Metrics (Goals, initiatives, ROI)"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.strategyCharts}
                        onChange={() => handleSectionToggle('strategyCharts')}
                      />
                    }
                    label="Strategy Charts (Budget utilization)"
                  />
                </FormGroup>
              </Paper>

              <Paper sx={{ p: 2, bgcolor: '#F3E5F5', mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Vendor Management
                </Typography>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.vendorMetrics}
                        onChange={() => handleSectionToggle('vendorMetrics')}
                      />
                    }
                    label="Vendor Metrics (Cost, SLA compliance)"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.vendorCharts}
                        onChange={() => handleSectionToggle('vendorCharts')}
                      />
                    }
                    label="Vendor Charts"
                  />
                </FormGroup>
              </Paper>

              <Paper sx={{ p: 2, bgcolor: '#FCE4EC', mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Assets & Recommendations
                </Typography>
                <FormGroup>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.assetInventory}
                        onChange={() => handleSectionToggle('assetInventory')}
                      />
                    }
                    label={`Asset Inventory (${data.assets.length} assets)`}
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={sections.recommendations}
                        onChange={() => handleSectionToggle('recommendations')}
                      />
                    }
                    label="Recommendations & Next Steps"
                  />
                </FormGroup>
              </Paper>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Preview Info */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            What's Included in Your Presentation
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Chip
                icon={<Check />}
                label={`${selectedCount} Slides`}
                color="primary"
                sx={{ width: '100%' }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Chip
                icon={<Check />}
                label="Live Data from Database"
                color="success"
                sx={{ width: '100%' }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Chip
                icon={<Check />}
                label="Charts & Tables"
                color="info"
                sx={{ width: '100%' }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Chip
                icon={<Download />}
                label="PowerPoint Format (.pptx)"
                color="secondary"
                sx={{ width: '100%' }}
              />
            </Grid>
          </Grid>

          <Alert severity="info" sx={{ mt: 2 }}>
            <strong>Tip:</strong> The presentation is generated from live data in your database.
            Make sure all your data is up-to-date before generating the report.
            You can customize the title, company name, and report date above.
          </Alert>
        </CardContent>
      </Card>
    </Box>
  )
}

export default PPTGenerator
