// ABOUTME: Schema sidebar component for browsing database structure
// ABOUTME: Displays tables and columns in a collapsible navigation panel (placeholder implementation)

import { useState } from 'react';
import { cn } from '../../utils/cn';

interface SchemaItem {
  name: string;
  type: 'database' | 'table' | 'column';
  children?: SchemaItem[];
}

// Mock schema data for now
const mockSchema: SchemaItem[] = [
  {
    name: 'SALES_DB',
    type: 'database',
    children: [
      {
        name: 'CUSTOMERS',
        type: 'table',
        children: [
          { name: 'CUSTOMER_ID', type: 'column' },
          { name: 'NAME', type: 'column' },
          { name: 'EMAIL', type: 'column' },
          { name: 'CREATED_AT', type: 'column' }
        ]
      },
      {
        name: 'ORDERS',
        type: 'table',
        children: [
          { name: 'ORDER_ID', type: 'column' },
          { name: 'CUSTOMER_ID', type: 'column' },
          { name: 'AMOUNT', type: 'column' },
          { name: 'ORDER_DATE', type: 'column' }
        ]
      },
      {
        name: 'PRODUCTS',
        type: 'table',
        children: [
          { name: 'PRODUCT_ID', type: 'column' },
          { name: 'NAME', type: 'column' },
          { name: 'PRICE', type: 'column' },
          { name: 'CATEGORY', type: 'column' }
        ]
      }
    ]
  }
];

interface SchemaSidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

interface SchemaTreeItemProps {
  item: SchemaItem;
  level: number;
}

function SchemaTreeItem({ item, level }: SchemaTreeItemProps) {
  const [isExpanded, setIsExpanded] = useState(level === 0);

  const hasChildren = item.children && item.children.length > 0;

  const getIcon = () => {
    switch (item.type) {
      case 'database':
        return '🗄️';
      case 'table':
        return '📋';
      case 'column':
        return '📝';
      default:
        return '📁';
    }
  };

  return (
    <div>
      <div
        className={cn(
          'flex items-center px-3 py-1 text-sm cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 rounded',
          'text-slate-700 dark:text-slate-300'
        )}
        style={{ paddingLeft: `${12 + level * 16}px` }}
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
      >
        {hasChildren && (
          <span className="mr-1 text-xs">
            {isExpanded ? '▼' : '▶'}
          </span>
        )}
        <span className="mr-2">{getIcon()}</span>
        <span className="truncate">{item.name}</span>
      </div>

      {hasChildren && isExpanded && (
        <div>
          {item.children!.map((child, index) => (
            <SchemaTreeItem
              key={`${child.name}-${index}`}
              item={child}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function SchemaSidebar({ isCollapsed, onToggle }: SchemaSidebarProps) {
  return (
    <div className={cn(
      'bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transition-all duration-300',
      isCollapsed ? 'w-12' : 'w-80'
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
        {!isCollapsed && (
          <h3 className="font-semibold text-slate-900 dark:text-slate-100">
            Schema
          </h3>
        )}
        <button
          onClick={onToggle}
          className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400"
          title={isCollapsed ? 'Expand schema' : 'Collapse schema'}
        >
          <svg
            className={cn('w-5 h-5 transition-transform', isCollapsed ? 'rotate-180' : '')}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="p-2">
          {/* Connection status */}
          <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded">
            <div className="flex items-center text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              <span className="text-green-700 dark:text-green-300">Connected to Snowflake</span>
            </div>
          </div>

          {/* Schema tree */}
          <div className="space-y-1">
            {mockSchema.map((item, index) => (
              <SchemaTreeItem
                key={`${item.name}-${index}`}
                item={item}
                level={0}
              />
            ))}
          </div>

          {/* Footer note */}
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded">
            <p className="text-xs text-blue-700 dark:text-blue-300">
              💡 Tip: Click table and column names in chat for quick reference
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
