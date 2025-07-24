# SQL Chatbot UI Design System Guide

## 🎨 Design Philosophy

### Core Principles
1. **Clarity Over Cleverness** - Every UI element should have an obvious purpose
2. **Progressive Disclosure** - Show only what's needed, when it's needed
3. **Forgiveness** - Allow users to undo/redo actions, confirm destructive operations
4. **Consistency** - Similar actions should look and behave similarly
5. **Accessibility First** - WCAG 2.1 AA compliance minimum

### Visual Identity
- **Personality**: Professional yet approachable, technical but not intimidating
- **Mood**: Dark, sophisticated, focused
- **Inspiration**: Modern code editors (VS Code) meets conversational AI (ChatGPT)

## 🎯 Design Constraints

### Technical Constraints
```yaml
Framework: React + TypeScript + Tailwind CSS
Theme: Dark mode only (for v1)
Responsive: Desktop-first, tablet-friendly, mobile-aware
Performance: First paint < 1.5s, TTI < 3s
Accessibility: Keyboard navigable, screen reader compatible
Browser Support: Chrome/Edge 90+, Firefox 88+, Safari 14+
```

### Visual Constraints
```yaml
Color Palette:
  - Backgrounds: #0f172a to #1e293b (dark blue-grays)
  - Primary: #0ea5e9 (bright blue)
  - Text: #f8fafc (primary), #cbd5e1 (secondary), #64748b (muted)
  - Success: #22c55e
  - Error: #ef4444
  - Warning: #f59e0b

Typography:
  - Font Family: Inter (sans), JetBrains Mono (code)
  - Scale: 12/14/16/18/24/32px
  - Line Heights: 1.5 (body), 1.2 (headings), 1.6 (code)

Spacing:
  - Base Unit: 4px
  - Scale: 4/8/12/16/24/32/48/64px

Borders:
  - Radius: 4px (small), 8px (medium), 12px (large), 16px (xl)
  - Width: 1px only
  - Color: rgba(255,255,255,0.1)
```

## 🏗️ Component Specifications

### 1. Chat Interface Container
**Prompt for AI Assistant:**
```
Create a chat interface container with:
- Full viewport height (100vh)
- Three-column layout: sidebar (collapsible), main chat, settings panel (hidden by default)
- Main chat area takes remaining space
- Smooth transitions when panels open/close
- Background: gradient from #0f172a to #1e293b
- Subtle noise texture overlay for depth
```

### 2. Message Components
**Prompt for AI Assistant:**
```
Design chat message bubbles with:
- Clear visual distinction between user (right-aligned, primary color) and assistant (left-aligned, darker)
- Avatar icons (user initials or robot icon)
- Timestamp on hover
- Copy button for code blocks
- Smooth entrance animation (fade + slide up)
- Max-width: 80% of container
- Code blocks: syntax highlighted, dark theme, copy button, filename label
- Tables: responsive, sortable headers, zebra striping, hover states
```

### 3. Query Input Area
**Prompt for AI Assistant:**
```
Build a sophisticated query input with:
- Expandable textarea (min 2 rows, max 10 rows)
- Glowing blue border on focus
- Character count indicator (fade in when > 200 chars)
- Send button (arrow icon) that rotates on hover
- Keyboard shortcuts displayed subtly (Enter to send, Shift+Enter for new line)
- Loading state: pulsing border animation
- Error state: red border with shake animation
- Autocomplete dropdown for table/column names (fuzzy search)
```

### 4. SQL Preview Modal
**Prompt for AI Assistant:**
```
Create a non-intrusive SQL preview with:
- Slide-up animation from bottom
- Semi-transparent backdrop (blur effect)
- Syntax-highlighted SQL with line numbers
- "Run Query" and "Edit" buttons
- Estimated row count and execution time
- Copy SQL button
- Keyboard shortcut hints (Cmd/Ctrl+Enter to run)
- Smooth dismiss animation on escape/click outside
```

### 5. Data Table Display
**Prompt for AI Assistant:**
```
Design a data table component with:
- Sticky header with sort indicators
- Alternating row colors (very subtle)
- Hover state: highlight entire row
- Column resize handles
- Pagination controls (sleek, icon-based)
- Export dropdown (CSV, JSON) with download animation
- Loading skeleton (animated gradient)
- Empty state: friendly illustration + helpful message
- Cell truncation with tooltip on hover
- Numeric columns: right-aligned, monospace font
```

### 6. Schema Explorer Sidebar
**Prompt for AI Assistant:**
```
Build a collapsible schema explorer with:
- Smooth slide animation (transform + opacity)
- Tree structure with expand/collapse animations
- Search/filter input at top
- Database > Schema > Table > Column hierarchy
- Icons for different data types
- Hover: show data type, nullable, key info
- Click to insert into query input
- Drag handle for resizing
- Minimized state: icon rail with tooltips
```

### 7. Settings Panel
**Prompt for AI Assistant:**
```
Create a settings panel that slides in from the right with:
- Grouped sections with subtle separators
- Toggle switches with smooth animations
- Input fields with inline validation
- "Test Connection" button with real-time feedback
- Auto-save indicator
- Keyboard navigation support
- Smooth backdrop fade
- Escape key to close
```

### 8. Loading States
**Prompt for AI Assistant:**
```
Design multiple loading states:
- Query execution: animated SQL icon with rotating segments
- Message sending: dots animation (...)
- Table loading: skeleton screens with shimmer effect
- Connection testing: circular progress with percentage
- Schema loading: cascading fade-in effect
All animations should be smooth, not jarring, under 2 seconds
```

### 9. Error States
**Prompt for AI Assistant:**
```
Create friendly error states with:
- Icon + message + action button layout
- Soft red background (#ef444420)
- Helpful suggestions based on error type
- Retry button with countdown
- "Report Issue" link (subtle)
- Fade in animation
- Auto-dismiss option for non-critical errors
```

### 10. Empty States
**Prompt for AI Assistant:**
```
Design engaging empty states with:
- Custom illustrations (abstract, geometric)
- Encouraging copy ("Let's explore your data!")
- Sample queries as clickable chips
- Subtle animation (floating elements)
- Quick action buttons
- Different states for: no connection, no data, no results
```

## 🎭 Micro-interactions

### Hover Effects
```
- Buttons: slight brightness increase + subtle shadow
- Links: underline slides in from left
- Cards: elevate with shadow + slight scale (1.02)
- Icons: rotate or pulse depending on context
- Table rows: highlight with smooth color transition
```

### Click Feedback
```
- Buttons: scale down slightly (0.98) then back
- Toggles: smooth slide with color transition
- Tabs: underline slides to new position
- Copy buttons: icon change + success toast
```

### Transitions
```
- Default: 200ms ease-out
- Modals: 300ms ease-out
- Page transitions: 400ms ease-in-out
- Hover: 150ms ease-out
- Loading: 2s ease-in-out (looping)
```

## 🎯 Responsive Behavior

### Breakpoints
```scss
// Desktop first approach
$desktop: 1280px;  // Full experience
$laptop: 1024px;   // Slightly condensed
$tablet: 768px;    // Hide sidebar by default
$mobile: 640px;    // Stack everything, simplified UI
```

### Responsive Rules
```
Desktop (>1280px):
- All panels visible
- Full feature set
- Hover interactions enabled

Laptop (1024-1280px):
- Narrower sidebar
- Compact table display
- Settings panel overlays chat

Tablet (768-1024px):
- Sidebar collapsed by default
- Simplified query input
- Touch-friendly tap targets (44px min)

Mobile (<768px):
- Single column layout
- Bottom sheet pattern for modals
- Swipe gestures for navigation
- Larger fonts and buttons
```

## 🚀 Performance Guidelines

### Animation Performance
```
- Use transform and opacity only
- Avoid animating layout properties
- GPU acceleration for smooth 60fps
- Reduce motion for accessibility preference
- Lazy load heavy components
```

### Loading Strategy
```
1. Show skeleton immediately
2. Load critical content first
3. Progressive enhancement for features
4. Virtualize long lists (>100 items)
5. Debounce search inputs (300ms)
```

## 📝 Copy Guidelines

### Tone of Voice
- **Friendly but professional** - "Let's explore your data" not "Sup, wanna query?"
- **Clear and concise** - "Connection failed" not "Unable to establish database connectivity"
- **Encouraging** - "Try asking about your sales data" not "Enter query"
- **Human** - "I'll help you write that query" not "Processing natural language input"

### Error Messages
```yaml
Connection Error: "Couldn't connect to Snowflake. Check your credentials and try again."
Query Error: "That query didn't work. Try selecting specific columns like 'SELECT name, revenue FROM sales'"
Timeout: "This is taking longer than usual. Try limiting your results with 'LIMIT 100'"
Permission: "You don't have access to that table. Ask your admin for permission."
```

### Empty States
```yaml
No Connection: "Connect your Snowflake database to start exploring"
No Results: "No data found. Try adjusting your filters or date range"
First Time: "Ask me anything about your data! Try 'Show me sales from last month'"
```

## 🎨 Special Effects

### Glassmorphism Elements
```css
/* For modals and floating panels */
background: rgba(15, 23, 42, 0.8);
backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.1);
```

### Glow Effects
```css
/* For focus states and CTAs */
box-shadow:
  0 0 20px rgba(14, 165, 233, 0.5),
  inset 0 0 20px rgba(14, 165, 233, 0.1);
```

### Gradient Borders
```css
/* For premium feel on important elements */
background: linear-gradient(#1e293b, #1e293b) padding-box,
           linear-gradient(45deg, #0ea5e9, #7dd3fc) border-box;
border: 2px solid transparent;
```

## 🔧 Implementation Prompts

### Initial Setup
```
"Create a Tailwind config with a dark theme color palette based on slate/sky colors,
Inter font family, and custom animations for fadeIn, slideUp, and pulse effects"
```

### Main Layout
```
"Build a responsive dashboard layout with collapsible sidebar, main content area,
and slide-out settings panel. Use CSS Grid for desktop and flexbox for mobile"
```

### Chat Components
```
"Create message components that support markdown, code highlighting (Prism.js),
tables, and LaTeX math. Include smooth scroll-to-bottom and message animations"
```

### Data Visualization
```
"Implement a responsive data table with virtual scrolling for performance,
column sorting, filtering, and CSV export. Style with subtle borders and hover states"
```

### Polish
```
"Add micro-interactions: button hover effects, smooth transitions, loading skeletons,
and success/error toast notifications. Ensure all animations respect prefers-reduced-motion"
```

## 🎯 Quality Checklist

Before considering the UI complete, ensure:

- [ ] All interactive elements have hover, active, and focus states
- [ ] Keyboard navigation works throughout the app
- [ ] Loading states exist for every async operation
- [ ] Error states are helpful, not frustrating
- [ ] Animations are smooth and purposeful
- [ ] Text remains readable at all sizes
- [ ] Touch targets are at least 44x44px
- [ ] Color contrast meets WCAG AA standards
- [ ] The app feels fast, even when it's working hard
- [ ] The interface delights without being distracting

## 🌟 The "Wow" Factors

1. **Smart Autocomplete** - As users type, show intelligent suggestions based on their schema
2. **Query History** - Beautiful timeline view of past queries with results
3. **Keyboard Shortcuts** - Power user features (Cmd+K for command palette)
4. **Data Insights** - Automatic chart suggestions based on query results
5. **Collaborative Features** - Share queries with team members with beautiful preview cards
6. **Theme Customization** - Let users tweak accent colors while maintaining accessibility

Remember: The goal is to make data querying feel less like writing SQL and more like having a conversation with a knowledgeable colleague.
