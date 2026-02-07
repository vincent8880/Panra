// Panra Icon Component
// Multiple icon options inspired by Polymarket's polygon style

interface PanraIconProps {
  variant?: 'hexagon' | 'arrow' | 'network' | 'shield' | 'graph'
  size?: number
  className?: string
}

export function PanraIcon({ variant = 'hexagon', size = 24, className = '' }: PanraIconProps) {
  const icons = {
    // Option 1: Hexagon with arrow (prediction/forecast)
    hexagon: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path
          d="M12 2L20 7V17L12 22L4 17V7L12 2Z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M9 12L12 9L15 12L12 15L9 12Z"
          fill="currentColor"
        />
        <path
          d="M12 9V6"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>
    ),
    
    // Option 2: Upward trending arrow (growth/prediction)
    arrow: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path
          d="M6 18L18 6"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M14 6H18V10"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle cx="12" cy="12" r="2" fill="currentColor" />
      </svg>
    ),
    
    // Option 3: Network nodes (crowd wisdom)
    network: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <circle cx="12" cy="4" r="2" fill="currentColor" />
        <circle cx="6" cy="12" r="2" fill="currentColor" />
        <circle cx="18" cy="12" r="2" fill="currentColor" />
        <circle cx="12" cy="20" r="2" fill="currentColor" />
        <path
          d="M12 6L6 12M12 6L18 12M6 12L12 18M18 12L12 18"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
    ),
    
    // Option 4: Maasai shield inspired geometric shape
    shield: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path
          d="M12 2L4 6V12C4 16 8 19 12 22C16 19 20 16 20 12V6L12 2Z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M12 8V14M9 11L12 8L15 11"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    
    // Option 5: Trending graph (prediction markets)
    graph: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
        <path
          d="M3 18L9 12L13 16L21 8"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle cx="21" cy="8" r="2" fill="currentColor" />
        <path
          d="M3 3V21H21"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
    ),
  }
  
  return icons[variant] || icons.hexagon
}

// Default export - using hexagon as default (similar to Polymarket's polygon)
export default function PanraLogo({ size = 32, className = '' }: { size?: number; className?: string }) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <PanraIcon variant="hexagon" size={size} className="text-pm-blue" />
      <span className="text-xl font-bold text-pm-text-primary">Panra</span>
    </div>
  )
}

































