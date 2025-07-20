// ABOUTME: Chevron down arrow icon component
// ABOUTME: Reusable SVG icon with customizable props

import type { SVGProps } from 'react';

export function ChevronDownIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      {...props}
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  );
}
