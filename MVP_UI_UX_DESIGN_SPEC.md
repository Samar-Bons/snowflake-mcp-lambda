# CSV Data Chat MVP - UI/UX Design Specification

**Version:** 1.0
**Date:** January 2025
**Status:** Ready for Implementation
**Target:** Complete frontend rebuild for CSV-first data chat experience

---

## 🎯 Design Philosophy & MVP Focus

### Core Principles
- **CSV-First Experience** - Upload CSV files instantly, no account required
- **30-Second Productivity** - From landing to first query in under 30 seconds
- **Natural Language First** - Chat interface that feels conversational and intuitive
- **Schema Transparency** - Always show users what data they're working with
- **Progressive Disclosure** - Advanced features available but not overwhelming

### Visual Identity
- **Professional Data Tool** - Clean, trustworthy interface for data analysis
- **Dark Theme Excellence** - Leverage your existing design system's dark theme
- **Conversational AI** - Chat-first interface with clear AI assistant persona
- **Data Confidence** - Visual cues that build trust in data processing

---

## 🎨 Design System Foundation

### Color Palette (From Your Style Guide)
```css
/* Primary Dark Theme */
--color-primary-dark: #0a0a0a        /* Main background */
--color-secondary-dark: #1a1a1a      /* Card backgrounds */
--color-surface: #2a2a2a             /* Elevated surfaces */

/* Blue & Purple Accents (Tailwind 400/600) */
--color-blue-primary: #60a5fa        /* blue-400 - Primary actions */
--color-blue-secondary: #2563eb      /* blue-600 - Hover states */
--color-purple-primary: #a78bfa      /* purple-400 - Assistant accent */
--color-purple-secondary: #9333ea    /* purple-600 - Purple interactions */

/* Text Colors */
--color-light-primary: #f9fafb       /* Primary text */
--color-light-secondary: #e5e7eb     /* Secondary text */
--color-light-muted: #9ca3af         /* Muted text */
--color-light-subtle: #6b7280        /* Subtle text */

/* Status Colors */
--color-success: #10b981             /* File upload success */
--color-warning: #f59e0b             /* Processing warnings */
--color-error: #ef4444               /* Upload errors */
```

### Typography Scale (Inter Font Family)
- **Hero Text**: 48px/tight - Landing page headlines
- **Page Titles**: 36px/normal - Section headers
- **Card Titles**: 24px/normal - Component headers
- **Body Large**: 18px/relaxed - Important descriptions
- **Body Regular**: 16px/normal - Default text
- **Body Small**: 14px/normal - Secondary information
- **Caption**: 12px/normal - Metadata, timestamps

### Spacing System (4px Grid)
```css
--space-1: 4px    --space-2: 8px    --space-3: 12px   --space-4: 16px
--space-6: 24px   --space-8: 32px   --space-12: 48px  --space-16: 64px
```

---

## 📱 Page Structure & User Flow

### 1. Landing Page - "Upload & Chat"

#### Hero Section
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              "Chat with Your CSV Data"                     │
│     Upload any CSV file and ask questions in plain English │
│                                                             │
│    ┌─────────────────────────────────────────────────┐    │
│    │  📁 Drop your CSV file here or click to browse │    │
│    │                                               │    │
│    │  ✓ No signup required  ✓ Files stay private    │    │
│    │  ✓ Up to 100MB        ✓ Auto-deleted in 24h    │    │
│    │                                               │    │
│    │            [Browse Files] [Try Sample]          │    │
│    └─────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Design Elements:**
- **Full-height hero** with gradient background (primary-dark to secondary-dark)
- **Large file upload zone** (400px wide, 200px tall) with dashed border
- **Trust indicators** below upload zone in light muted text
- **Sample data option** for immediate demo experience
- **Floating theme toggle** in top-right corner

#### Upload States
```css
/* Default State */
.upload-zone {
  border: 2px dashed var(--color-light-subtle);
  background: var(--color-secondary-dark);
  border-radius: var(--radius-lg);
  transition: all var(--transition-normal);
}

/* Drag Hover State */
.upload-zone--drag-over {
  border-color: var(--color-blue-primary);
  background: rgba(96, 165, 250, 0.05);
  transform: scale(1.02);
}

/* Upload Progress */
.upload-progress {
  background: linear-gradient(90deg,
    var(--color-blue-primary) 0%,
    var(--color-purple-primary) 100%
  );
  height: 4px;
  border-radius: 2px;
}
```

### 2. Processing Screen - "Understanding Your Data"

#### Analysis Phase
```
┌─────────────────────────────────────────────────────────────┐
│                Analyzing sample_data.csv                   │
│  ████████████▒▒▒▒▒▒▒▒ 65% Complete                        │
│                                                             │
│  🔍 Detecting columns and data types...                   │
│  📊 Found 1,247 rows with 8 columns                       │
│  ✓ All columns have clear names                            │
│  ⚠️ Date column detected - converting format               │
│                                                             │
│                  [Cancel Upload]                            │
└─────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Real-time progress indicator** with percentage
- **Live status updates** showing what's being processed
- **Data quality feedback** with icons (✓ ⚠️ ❌)
- **File statistics** (rows, columns, size)
- **Cancel option** during processing

### 3. Schema Preview - "Your Data is Ready"

#### Schema Confirmation
```
┌─────────────────────────────────────────────────────────────┐
│                   sample_data.csv                          │
│              1,247 rows • 8 columns • 2.4 MB              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Column Name    │ Type      │ Sample Data            │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ customer_id    │ INTEGER   │ 1, 2, 3, 4, 5...       │  │
│  │ name           │ TEXT      │ John Doe, Jane Smith   │  │
│  │ email          │ TEXT      │ john@ex.com, jane@...  │  │
│  │ signup_date    │ DATE      │ 2023-01-15, 2023-02... │  │
│  │ revenue        │ DECIMAL   │ 1250.00, 890.50...    │  │
│  │ region         │ TEXT      │ North, South, East...  │  │
│  │ status         │ TEXT      │ active, pending...     │  │
│  │ last_login     │ DATETIME  │ 2024-01-10 14:30...   │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│             [Start Chatting] [Upload Different File]       │
└─────────────────────────────────────────────────────────────┘
```

**Schema Table Styling:**
```css
.schema-table {
  background: var(--color-surface);
  border: 1px solid var(--color-surface-elevated);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.schema-table th {
  background: var(--color-surface-elevated);
  color: var(--color-light-primary);
  font-weight: var(--font-weight-medium);
}

.schema-table td {
  color: var(--color-light-secondary);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
```

### 4. Main Chat Interface - "Ask About Your Data"

#### Desktop Layout (1200px+)
```
┌─────────────────────────────────────────────────────────────────────┐
│                               HEADER                                │
├────────────────┬────────────────────────────────────────────────────┤
│                │                                                    │
│   SIDEBAR      │                 CHAT AREA                         │
│   (320px)      │                                                    │
│                │  ┌──────────────────────────────────────────────┐  │
│  📄 Files      │  │ 🤖 Hello! I can help you analyze your CSV   │  │
│  • sample.csv  │  │ data. Try asking:                            │  │
│    (active)    │  │ • "Show me the top 10 customers by revenue" │  │
│  • Upload New  │  │ • "What's the average revenue by region?"   │  │
│                │  │ • "How many customers signed up each month?"│  │
│  📊 Schema     │  └──────────────────────────────────────────────┘  │
│  • customer_id │                                                    │
│  • name        │  ┌──────────────────────────────────────────────┐  │
│  • email       │  │ 👤 Show me top 5 customers by revenue       │  │
│  • revenue     │  └──────────────────────────────────────────────┘  │
│  • region      │                                                    │
│                │  ┌──────────────────────────────────────────────┐  │
│  ⚙️ Settings   │  │ 🤖 I'll find the top customers for you.     │  │
│  • Auto-run: ✓ │  │                                              │  │
│  • Limit: 500  │  │ Generated SQL:                              │  │
│                │  │ ```sql                                       │  │
│                │  │ SELECT name, email, revenue                  │  │
│                │  │ FROM customer_data                           │  │
│                │  │ ORDER BY revenue DESC                        │  │
│                │  │ LIMIT 5;                                     │  │
│                │  │ ```                                          │  │
│                │  │                                              │  │
│                │  │ [Execute Query] [Edit SQL]                   │  │
│                │  └──────────────────────────────────────────────┘  │
│                │                                                    │
│                │  ┌─────────────────────────────────────────────┐   │
│                │  │ 💬 Ask about your data...            [Send] │   │
│                │  └─────────────────────────────────────────────┘   │
│                │                                                    │
├────────────────┴────────────────────────────────────────────────────┤
│                              FOOTER                                │
└─────────────────────────────────────────────────────────────────────┘
```

#### Mobile Layout (< 768px)
```
┌─────────────────────────┐
│        HEADER           │
├─────────────────────────┤
│                         │
│       CHAT AREA         │
│                         │
│ 🤖 Hello! I can help... │
│                         │
│ 👤 Show me top sales    │
│                         │
│ 🤖 Generated SQL:       │
│ ```sql                  │
│ SELECT * FROM...        │
│ ```                     │
│ [Execute] [Edit]        │
│                         │
├─────────────────────────┤
│ 💬 Ask question... 📤   │
├─────────────────────────┤
│ [Files][Schema][Settings]│
└─────────────────────────┘
```

---

## 🎭 Component Specifications

### File Upload Component
```tsx
interface FileUploadProps {
  onUpload: (file: File) => void;
  maxSize: number; // in MB
  acceptedTypes: string[];
  state: 'idle' | 'uploading' | 'processing' | 'success' | 'error';
  progress?: number;
  error?: string;
}

// Usage
<FileUpload
  maxSize={100}
  acceptedTypes={['.csv', '.xlsx']}
  state={uploadState}
  progress={uploadProgress}
  onUpload={handleFileUpload}
  error={uploadError}
/>
```

**Visual States:**
```css
/* Idle State */
.file-upload {
  min-height: 200px;
  border: 2px dashed var(--color-light-subtle);
  border-radius: var(--radius-lg);
  background: var(--color-secondary-dark);
}

/* Drag Active */
.file-upload--drag-active {
  border-color: var(--color-blue-primary);
  background: rgba(96, 165, 250, 0.05);
}

/* Uploading */
.file-upload--uploading {
  border-color: var(--color-blue-primary);
  background: var(--color-surface);
}
```

### Chat Message Components
```tsx
interface ChatMessageProps {
  type: 'user' | 'assistant' | 'system';
  content: string | JSX.Element;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  actions?: JSX.Element;
}

// Assistant message with SQL
<ChatMessage
  type="assistant"
  timestamp={new Date()}
  content={
    <div>
      <p>I'll find the top customers for you.</p>
      <SqlBlock
        query="SELECT name, revenue FROM customers ORDER BY revenue DESC LIMIT 5"
        onExecute={handleExecuteQuery}
        onEdit={handleEditQuery}
      />
    </div>
  }
/>
```

### SQL Block Component
```tsx
interface SqlBlockProps {
  query: string;
  onExecute: (query: string) => void;
  onEdit: (query: string) => void;
  executionTime?: number;
  rowCount?: number;
  status: 'pending' | 'executing' | 'success' | 'error';
}

// Styling
.sql-block {
  background: var(--color-surface);
  border: 1px solid var(--color-surface-elevated);
  border-radius: var(--radius-lg);
  margin: var(--space-4) 0;
}

.sql-block__code {
  background: rgba(0, 0, 0, 0.3);
  padding: var(--space-4);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: var(--font-size-small);
  color: var(--color-light-primary);
}
```

### Data Results Table
```tsx
interface DataResultsProps {
  data: Array<Record<string, any>>;
  columns: Array<{ key: string; label: string; type: 'text' | 'number' | 'date' }>;
  totalRows: number;
  currentPage: number;
  onPageChange: (page: number) => void;
  onSort: (column: string, direction: 'asc' | 'desc') => void;
  onExport: (format: 'csv' | 'json') => void;
}

// Visual styling matches existing table component
.results-table {
  background: var(--color-secondary-dark);
  border: 1px solid var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
```

### Schema Sidebar Component
```tsx
interface SchemaSidebarProps {
  tables: Array<{
    name: string;
    rowCount: number;
    columns: Array<{
      name: string;
      type: string;
      sampleValues: string[];
    }>;
  }>;
  collapsed: boolean;
  onToggle: () => void;
}

// Styling
.schema-sidebar {
  width: 320px;
  background: var(--color-secondary-dark);
  border-right: 1px solid var(--color-surface);
  height: 100vh;
  overflow-y: auto;
}

.schema-sidebar--collapsed {
  width: 64px;
}
```

---

## 📊 Results Display Patterns

### Query Results Layout
```
┌─────────────────────────────────────────────────────────────┐
│  🎯 Query Results                                          │
│                                                             │
│  💬 "Show me top 5 customers by revenue"                  │
│  ⏱️ Executed in 45ms • 5 rows returned                    │
│  📊 Showing 5 of 1,247 total customers                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Name          │ Email           │ Revenue    │ Region │  │
│  ├─────────────────────────────────────────────────────┤  │
│  │ John Smith    │ john@ex.com     │ $15,420   │ North  │  │
│  │ Sarah Johnson │ sarah@ex.com    │ $12,890   │ South  │  │
│  │ Mike Wilson   │ mike@ex.com     │ $11,230   │ East   │  │
│  │ Alice Brown   │ alice@ex.com    │ $9,870    │ West   │  │
│  │ Tom Davis     │ tom@ex.com      │ $8,540    │ North  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  [📥 Export CSV] [📋 Copy Results] [🔄 Run Again]         │
└─────────────────────────────────────────────────────────────┘
```

### Query Confirmation Modal
```
┌─────────────────────────────────────────────────────────────┐
│                    Review SQL Query                         │
│                                                             │
│  Your question: "Show me customers who spent over $10k"    │
│                                                             │
│  Generated SQL:                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ SELECT name, email, revenue                         │  │
│  │ FROM customer_data                                  │  │
│  │ WHERE revenue > 10000                               │  │
│  │ ORDER BY revenue DESC;                              │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ℹ️ This will query 1,247 rows                            │
│  ⚠️ Results limited to first 500 rows                     │
│                                                             │
│             [Cancel]        [Execute Query]                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Interaction Patterns

### File Upload Flow
1. **Landing** → Large, prominent upload zone with clear CTAs
2. **Drag/Drop** → Visual feedback with blue border and background tint
3. **Upload Progress** → Progress bar with percentage and current operation
4. **Processing** → Real-time status updates with icons and descriptions
5. **Schema Preview** → Tabular display of detected columns and sample data
6. **Chat Ready** → Smooth transition to chat interface with welcome message

### Chat Interaction Flow
1. **Welcome** → Assistant introduces capabilities with example queries
2. **User Input** → Natural language input with auto-expanding textarea
3. **Processing** → Typing indicator while LLM generates SQL
4. **SQL Review** → Display generated SQL with execution options
5. **Confirmation** → Optional modal for SQL approval (if auto-run disabled)
6. **Execution** → Loading state while query runs
7. **Results** → Formatted table with metadata and export options
8. **Follow-up** → Input remains active for additional queries

### Error Handling Patterns
```
Upload Errors:
🔴 File too large (>100MB) → "Try a smaller file or contact support for larger datasets"
🔴 Invalid format → "Only CSV and Excel files are supported"
🔴 Processing failed → "File appears corrupted. Please check format and try again"

Query Errors:
🟡 No results found → "Your query returned no results. Try adjusting your criteria"
🔴 Query timeout → "Query took too long. Try a more specific question"
🔴 Invalid SQL → "I had trouble understanding that. Can you rephrase your question?"
```

---

## 📱 Responsive Design Strategy

### Breakpoints
```css
/* Mobile First Approach */
@media (min-width: 768px)  /* Tablet */
@media (min-width: 1024px) /* Desktop */
@media (min-width: 1440px) /* Large Desktop */
```

### Mobile Adaptations (< 768px)
- **Sidebar becomes bottom sheet** accessed via tab bar
- **Upload zone adjusts** to full width with reduced height
- **Chat messages stack** with reduced padding and avatar sizes
- **Tables scroll horizontally** with sticky first column
- **SQL blocks** get horizontal scroll for long queries
- **Modals** become full-screen overlays

### Progressive Enhancement
- **Touch targets** minimum 44px for mobile interaction
- **Hover states** only apply on devices that support hover
- **Keyboard navigation** works throughout the application
- **Screen reader support** with proper ARIA labels

---

## ⚡ Performance Considerations

### Loading States & Feedback
```css
/* Skeleton loading for tables */
.skeleton {
  background: linear-gradient(90deg,
    transparent,
    rgba(255, 255, 255, 0.04),
    transparent
  );
  animation: skeleton-loading 1.5s infinite;
}

/* Typing indicator for chat */
.typing-dots {
  display: flex;
  gap: var(--space-1);
}

.typing-dot {
  width: 4px;
  height: 4px;
  background: var(--color-light-muted);
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite ease-in-out;
}
```

### Optimization Strategies
- **Virtual scrolling** for large result sets (>1000 rows)
- **Lazy loading** of schema information
- **Debounced input** to prevent excessive API calls
- **Chunked file upload** for large CSV files
- **Result pagination** with smooth infinite scroll
- **Connection pooling** indicators for query execution

---

## 🎯 Success Metrics & Validation

### User Experience Goals
- **Upload Success Rate**: 95% of valid CSV files upload successfully
- **Query Success Rate**: 85% of natural language queries generate valid SQL
- **Time to First Query**: 90% of users ask first question within 60 seconds
- **Error Recovery**: 80% of users successfully resolve upload/query errors

### Visual Design Validation
- **Color Contrast**: All text meets WCAG 2.1 AA standards (4.5:1 ratio)
- **Touch Target Size**: All interactive elements minimum 44px
- **Loading Feedback**: No interface state lacks user feedback
- **Responsive Design**: Full functionality across all screen sizes

### Performance Targets
- **File Upload**: 10MB CSV processes in under 15 seconds
- **Query Execution**: 95% of queries complete within 5 seconds
- **Page Load**: Initial render within 2 seconds on 3G connection
- **Chat Response**: LLM generates SQL within 10 seconds

---

## 🔧 Implementation Guidelines

### CSS Architecture
```scss
// Use your existing design system variables
:root {
  /* Import all variables from styleGuide/styles.css */
}

// Component-scoped BEM methodology
.chat-message {
  // Base styles

  &__content {
    // Content styles
  }

  &--user {
    // User variant
  }

  &--assistant {
    // Assistant variant
  }
}
```

### Component Organization
```
src/
├── components/
│   ├── upload/
│   │   ├── FileUploadZone.tsx
│   │   ├── UploadProgress.tsx
│   │   └── SchemaPreview.tsx
│   ├── chat/
│   │   ├── ChatWindow.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── SqlBlock.tsx
│   │   └── TypingIndicator.tsx
│   ├── data/
│   │   ├── ResultsTable.tsx
│   │   ├── SchemaSidebar.tsx
│   │   └── DataExporter.tsx
│   └── ui/ (from existing components)
│       ├── Button.tsx
│       ├── Card.tsx
│       └── Modal.tsx
```

### State Management Strategy
```typescript
interface AppState {
  // File Management
  files: UploadedFile[];
  activeFile: string | null;
  uploadState: UploadState;

  // Chat Interface
  messages: ChatMessage[];
  isTyping: boolean;
  queryHistory: Query[];

  // Data & Schema
  schema: TableSchema[];
  queryResults: QueryResult | null;

  // UI State
  sidebarCollapsed: boolean;
  settings: UserSettings;
}
```

---

This comprehensive UI/UX design specification leverages your existing professional dark theme design system while optimizing for the CSV-first data chat experience. The specification provides detailed component breakdowns, interaction patterns, and implementation guidelines to ensure pixel-perfect execution of the MVP vision.

**Key Differentiators:**
- **Instant productivity** through streamlined CSV upload flow
- **Natural conversation** with your data via chat interface
- **Schema transparency** so users always understand their data
- **Professional aesthetics** using your established design system
- **Mobile-first responsive** design for universal access

Ready for implementation with your existing React + TypeScript + Tailwind CSS stack! 🚀
