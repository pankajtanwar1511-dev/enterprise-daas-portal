# UI/UX Design Guidelines
## Enterprise DaaS Governance Portal

**Version:** 1.0
**Date:** February 2026

---

## Design Philosophy

**Principle 1: Executive-Grade Professionalism**
Clean, corporate aesthetic suitable for C-suite presentation

**Principle 2: Information Density**
Maximum insight with minimum clutter - data-driven dashboards

**Principle 3: Intuitive Navigation**
Users accomplish tasks without training

**Principle 4: Accessibility First**
WCAG 2.1 AA compliance minimum

**Principle 5: Performance**
<2 second page load, responsive interactions

---

## Color Palette

### Primary Colors

```
Corporate Blue (Primary)
#1976D2 - Buttons, headers, primary actions
RGB(25, 118, 210)

Dark Blue (Text/Headers)
#0D47A1 - Main headings, emphasis
RGB(13, 71, 161)

Light Blue (Hover/Selected)
#BBDEFB - Row selection, hover states
RGB(187, 222, 251)
```

### Secondary Colors

```
Steel Grey (Secondary)
#546E7A - Secondary text, borders
RGB(84, 110, 122)

Light Grey (Backgrounds)
#F5F5F5 - Page background, cards
RGB(245, 245, 245)

White (Cards/Surfaces)
#FFFFFF - Card backgrounds, surfaces
RGB(255, 255, 255)
```

### Status Colors

```
Success Green
#4CAF50 - Compliant, approved, active
RGB(76, 175, 80)

Warning Yellow/Amber
#FF9800 - Warnings, pending, deprecated
RGB(255, 152, 0)

Error Red
#F44336 - Non-compliant, rejected, critical
RGB(244, 67, 54)

Info Blue
#2196F3 - Informational messages
RGB(33, 150, 243)
```

---

## Typography

### Font Family

**Primary:** `'Roboto', 'Helvetica Neue', sans-serif`
**Monospace (code/IDs):** `'Roboto Mono', 'Courier New', monospace`

### Font Scales

```
H1 (Page Title): 32px, weight 300, color #0D47A1
H2 (Section Header): 24px, weight 400, color #0D47A1
H3 (Subsection): 20px, weight 500, color #546E7A
H4 (Card Title): 18px, weight 500, color #0D47A1
Body: 14px, weight 400, color #212121
Caption/Helper: 12px, weight 400, color #757575
```

---

## Layout Structure

### Application Shell

```
┌──────────────────────────────────────────────────────┐
│  Header (64px height)                                │
│  Logo | Navigation | User Profile                    │
├────────┬─────────────────────────────────────────────┤
│ Side   │  Main Content Area                          │
│ Nav    │                                             │
│ (240px)│  Breadcrumb > Current Page                  │
│        │                                             │
│        │  [Page Title]                               │
│        │                                             │
│        │  [Dashboard/Content]                        │
│        │                                             │
│        │                                             │
│        │                                             │
└────────┴─────────────────────────────────────────────┘
```

### Grid System

- **Container Width:** Max 1440px, centered
- **Grid:** 12-column responsive grid
- **Gutters:** 24px between columns
- **Margins:** 24px left/right on desktop, 16px on mobile

---

## Component Library

### 1. Cards

**Standard Card:**
```
┌─────────────────────────────────────────┐
│ Card Title                    [Icon]    │
├─────────────────────────────────────────┤
│                                         │
│  Content area with padding:16px         │
│                                         │
│  [Action Button]                        │
└─────────────────────────────────────────┘

Style:
- Background: #FFFFFF
- Border: 1px solid #E0E0E0
- Border-radius: 8px
- Box-shadow: 0 2px 4px rgba(0,0,0,0.1)
```

**Metric Card (Dashboard):**
```
┌─────────────────────────────┐
│ 95.7%            ↑ +2.3%   │
│ Compliance Rate             │
└─────────────────────────────┘

Style:
- Metric: 36px, weight 700, color based on status
- Label: 14px, weight 400, color #757575
- Trend: 12px, weight 500, color based on direction
```

---

### 2. Buttons

**Primary Button:**
```css
background: #1976D2
color: #FFFFFF
border-radius: 4px
padding: 10px 24px
font-size: 14px
font-weight: 500
text-transform: uppercase
box-shadow: 0 2px 4px rgba(0,0,0,0.2)

hover: background #1565C0
active: background #0D47A1
```

**Secondary Button:**
```css
background: transparent
color: #1976D2
border: 1px solid #1976D2
border-radius: 4px
padding: 10px 24px

hover: background #E3F2FD
```

**Icon Button:**
```css
width: 40px
height: 40px
border-radius: 50%
color: #546E7A

hover: background #F5F5F5
```

---

### 3. Tables

**Data Table Style:**
```
Header Row:
- Background: #F5F5F5
- Font-weight: 500
- Color: #0D47A1
- Border-bottom: 2px solid #1976D2

Data Rows:
- Background: #FFFFFF
- Border-bottom: 1px solid #E0E0E0
- Padding: 12px 16px

Row Hover:
- Background: #FAFAFA

Selected Row:
- Background: #E3F2FD
- Border-left: 4px solid #1976D2
```

**Column Widths:**
- ID: 80px
- Name: 250px (flexible)
- Status: 120px
- Date: 140px
- Actions: 100px (fixed)

---

### 4. Status Badges

**Lifecycle Badges:**
```
Draft:     background #FFF3E0, color #E65100, border #FFB74D
Active:    background #E8F5E9, color #2E7D32, border #66BB6A
Deprecated: background #FFF9C4, color #F57F17, border #FDD835
Retired:   background #ECEFF1, color #455A64, border #90A4AE
```

**Compliance Badges:**
```
Compliant:     ✓ background #E8F5E9, color #2E7D32
Non-Compliant: ✗ background #FFEBEE, color #C62828
Warning:       ⚠ background #FFF3E0, color #E65100
```

---

### 5. Forms

**Input Field:**
```css
height: 40px
padding: 8px 12px
border: 1px solid #BDBDBD
border-radius: 4px
font-size: 14px

focus: border-color #1976D2, box-shadow 0 0 0 2px #E3F2FD

error: border-color #F44336

label: font-size 12px, color #546E7A, margin-bottom 4px
```

**Dropdown/Select:**
```css
Same as input field with dropdown icon
Options: max-height 300px, scroll if needed
```

**Form Layout:**
- Single column for simplicity
- Label above field
- Helper text below field (12px, color #757575)
- Error text below field (12px, color #F44336)
- Spacing between fields: 16px

---

### 6. Navigation

**Top Navigation:**
```
┌──────────────────────────────────────────────────┐
│ [Logo] Dashboard | Assets | Changes | Reports   │
│                              [User] [Logout]     │
└──────────────────────────────────────────────────┘

Height: 64px
Background: #0D47A1
Text: #FFFFFF
Active item: underline 3px #BBDEFB
```

**Sidebar Navigation:**
```
Width: 240px
Background: #FAFAFA
Items:
  - Icon (24px) + Label
  - Padding: 12px 16px
  - Hover: background #E0E0E0
  - Active: background #E3F2FD, border-left 4px #1976D2
```

**Breadcrumb:**
```
Home > Assets > PROD-HR-DW-v1

Font-size: 12px
Color: #546E7A
Separator: > (color #BDBDBD)
Current: color #0D47A1, font-weight 500
```

---

## Dashboard Design

### Compliance Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  Compliance Dashboard                                   │
├─────────────┬─────────────┬─────────────┬──────────────┤
│ Total Assets│ Compliance  │ Non-Compliant│ Missing Docs │
│    127      │   95.7%     │      6       │      12      │
│             │   ↑ +2.3%   │              │              │
├─────────────┴─────────────┴─────────────┴──────────────┤
│                                                         │
│  Compliance Trend (Line Chart - 90 days)                │
│                                                         │
├───────────────────────────────┬─────────────────────────┤
│                               │                         │
│ Domain Health Matrix (Table)  │ Risk Alerts (List)      │
│                               │                         │
├───────────────────────────────┴─────────────────────────┤
│                                                         │
│ Change Requests by Status (Bar Chart)                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Chart Styling

**Line Charts:**
- Line color: #1976D2
- Line width: 2px
- Grid lines: #E0E0E0, dashed
- Axis labels: 12px, #546E7A
- Data points: circles, 4px radius

**Bar Charts:**
- Bar color: #1976D2
- Spacing: 8px between bars
- Value labels: above bars, 12px

**Pie Charts:**
- Colors: Use status colors for lifecycle states
- Label: outside with connecting line
- Hover: enlarge slice

---

## Responsive Design

### Breakpoints

```
Mobile:  < 600px
Tablet:  600px - 960px
Desktop: > 960px
```

### Mobile Adaptations

**Navigation:**
- Sidebar collapses to hamburger menu
- Top nav shows only logo + menu icon

**Cards:**
- Stack vertically (full width)
- Reduce padding to 12px

**Tables:**
- Horizontal scroll for wide tables
- Consider card view for mobile

**Forms:**
- Full width inputs
- Larger touch targets (44px minimum)

---

## Accessibility

### WCAG 2.1 AA Compliance

**Color Contrast:**
- Text on background: minimum 4.5:1
- Large text (18px+): minimum 3:1
- Status colors meet contrast requirements

**Keyboard Navigation:**
- All interactive elements accessible via Tab
- Focus indicators: 2px blue outline
- Skip navigation link

**Screen Readers:**
- Semantic HTML (nav, main, section, article)
- ARIA labels for icons and actions
- Alt text for all images
- Table headers properly marked

**Form Accessibility:**
- Labels associated with inputs (for/id)
- Error messages announced
- Required fields indicated

---

## Interaction Patterns

### Loading States

**Page Load:**
```
Skeleton screens (grey placeholders)
Duration: <2 seconds
Spinner: circular, 40px, color #1976D2
```

**Button Click:**
```
Disable button
Show spinner inside button
Duration: operation time
Success: Green checkmark (500ms)
Error: Shake animation + error message
```

### Notifications

**Toast Notifications:**
```
Position: top-right
Width: 300px
Duration: 4 seconds (auto-dismiss)
Types:
  - Success: green left border
  - Error: red left border
  - Warning: amber left border
  - Info: blue left border

Include: Icon + Message + Close button
```

### Modals/Dialogs

```
Overlay: rgba(0,0,0,0.5)
Modal:
  - Max-width: 600px
  - Background: #FFFFFF
  - Border-radius: 8px
  - Padding: 24px
  - Box-shadow: 0 8px 16px rgba(0,0,0,0.3)

Header: Title (H4) + Close button
Content: Form or message
Footer: Cancel + Primary action button (right-aligned)
```

---

## Iconography

**Icon Library:** Material Design Icons

**Common Icons:**
- Dashboard: dashboard
- Assets: inventory_2
- Add: add_circle
- Edit: edit
- Delete: delete
- Approve: check_circle
- Reject: cancel
- Warning: warning
- Info: info
- Settings: settings
- Search: search
- Filter: filter_list
- Export: download
- Documentation: description

**Icon Sizes:**
- Small: 18px
- Medium: 24px
- Large: 36px

**Icon Colors:**
- Default: #546E7A
- Primary: #1976D2
- Success: #4CAF50
- Error: #F44336

---

## Animation

**Transition Timing:**
```css
Standard: 200ms ease-in-out
Slow: 300ms ease-in-out
Fast: 100ms ease-in-out
```

**Animated Elements:**
- Button hover: background 200ms
- Card elevation: box-shadow 200ms
- Dropdown open: height 200ms
- Modal appear: opacity + scale 300ms
- Page transition: fade 200ms

**No Animation:**
- Users can disable via accessibility settings
- Respect `prefers-reduced-motion` media query

---

## Data Visualization

### Chart Color Scheme

**Sequential (for metrics over time):**
- Light to Dark blue: #E3F2FD → #1976D2 → #0D47A1

**Categorical (for domains):**
- HR: #E91E63
- FIN: #4CAF50
- OPS: #FF9800
- SALES: #9C27B0
- IT: #2196F3
- DATA: #00BCD4

**Diverging (for compliance score):**
- Red (#F44336) → Yellow (#FFEB3B) → Green (#4CAF50)

---

## Example Page Wireframes

### Asset Registry Page

```
┌──────────────────────────────────────────────────────┐
│ Assets                                               │
│                                                      │
│ [Search box]              [Filter ▼] [+ New Asset]  │
│                                                      │
│ ┌────────────────────────────────────────────────┐  │
│ │ Name          │ Domain │ Env │ Status │ Actions │  │
│ ├────────────────────────────────────────────────┤  │
│ │ PROD-HR-DW-v1 │ HR     │PROD│ Active │ [⋮]     │  │
│ │ QA-FIN-ETL-v2 │ FIN    │ QA │ Active │ [⋮]     │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ Showing 1-20 of 127             [< 1 2 3 4 5 >]     │
└──────────────────────────────────────────────────────┘
```

---

## Approval

**UI/UX Guidelines Approved By:**
- UX Lead: ________________________
- Frontend Lead: ________________________
- Accessibility Officer: ________________________

**Effective Date:** March 1, 2026
