import { Shield, Scale, Gavel } from 'lucide-react'
import Card from '../ui/Card'

/**
 * AgentCard - Displays an agent's argument in the debate
 * 
 * @param {Object} props
 * @param {string} props.role - Agent role: 'prosecutor', 'defense', or 'judge'
 * @param {number} props.round - Round number (1 or 2, 0 for judge)
 * @param {string} props.content - Agent's argument text
 * @param {boolean} props.isStreaming - Whether content is still being received
 */
function AgentCard({ role, round, content, isStreaming = false }) {
  const config = getAgentConfig(role)
  
  return (
    <Card
      className={`border-l-4 ${config.borderClass} animate-slide-up shadow-lg hover:shadow-xl transition-shadow duration-300`}
      hover={false}
    >
      <Card.Content className="p-8">
        {/* Agent Header */}
        <div className="flex items-center gap-4 mb-6 pb-4 border-b-2 border-gray-100 dark:border-gray-700">
          <div className={`w-14 h-14 rounded-xl ${config.bgClass} flex items-center justify-center shadow-md`}>
            <config.icon className={`w-7 h-7 ${config.iconClass}`} aria-hidden="true" />
          </div>
          <div className="flex-1">
            <h3 className={`text-xl font-bold ${config.textClass} tracking-tight`}>
              {config.label}
              {round > 0 && ` — Round ${round}`}
              {round === 2 && ' (Rebuttal)'}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium mt-1">
              {config.description}
            </p>
          </div>
          {isStreaming && (
            <div className="flex gap-1.5">
              <span className="w-2.5 h-2.5 bg-primary-500 rounded-full animate-pulse shadow-sm" />
              <span className="w-2.5 h-2.5 bg-primary-500 rounded-full animate-pulse delay-75 shadow-sm" />
              <span className="w-2.5 h-2.5 bg-primary-500 rounded-full animate-pulse delay-150 shadow-sm" />
            </div>
          )}
        </div>

        {/* Agent Content */}
        <div className={`prose prose-sm max-w-none ${config.proseClass}`}>
          {content ? (
            <div className="text-gray-700 dark:text-gray-300 text-base">
              {formatAgentContent(content)}
            </div>
          ) : (
            <div className="text-gray-400 dark:text-gray-500 italic flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
              Waiting for response...
            </div>
          )}
        </div>
      </Card.Content>
    </Card>
  )
}

/**
 * Get configuration for each agent role
 */
function getAgentConfig(role) {
  const configs = {
    prosecutor: {
      label: '🔴 PROSECUTION',
      description: 'Arguing this is a phishing attempt',
      icon: Shield,
      bgClass: 'bg-red-100 dark:bg-red-900/30',
      iconClass: 'text-red-600 dark:text-red-400',
      textClass: 'text-red-700 dark:text-red-400',
      borderClass: 'border-l-red-500',
      proseClass: 'prose-red',
    },
    defense: {
      label: '🟢 DEFENSE',
      description: 'Arguing this is legitimate',
      icon: Scale,
      bgClass: 'bg-green-100 dark:bg-green-900/30',
      iconClass: 'text-green-600 dark:text-green-400',
      textClass: 'text-green-700 dark:text-green-400',
      borderClass: 'border-l-green-500',
      proseClass: 'prose-green',
    },
    judge: {
      label: '⚖️ JUDGE',
      description: 'Final ruling',
      icon: Gavel,
      bgClass: 'bg-amber-100 dark:bg-amber-900/30',
      iconClass: 'text-amber-600 dark:text-amber-400',
      textClass: 'text-amber-700 dark:text-amber-400',
      borderClass: 'border-l-amber-500',
      proseClass: 'prose-amber',
    },
  }
  
  return configs[role] || configs.judge
}

/**
 * Format agent content to preserve structure
 */
function formatAgentContent(content) {
  // Split into lines and format bullet points
  const lines = content.split('\n')
  
  return lines.map((line, i) => {
    const trimmed = line.trim()
    
    // Skip empty lines
    if (!trimmed) return <br key={i} />
    
    // Format section headers (lines starting with ** or containing only caps and punctuation)
    if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
      const headerText = trimmed.replace(/\*\*/g, '')
      return (
        <div key={i} className="font-bold text-base mt-6 mb-3 pb-2 border-b border-current/20">
          {headerText}
        </div>
      )
    }
    
    // Format bullet points with better styling
    if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
      const bulletText = trimmed.replace(/^[-•]\s*/, '')
      return (
        <div key={i} className="flex items-start gap-3 my-3 pl-2">
          <span className="text-current opacity-70 mt-1 font-bold">•</span>
          <span className="flex-1 leading-relaxed">{bulletText}</span>
        </div>
      )
    }
    
    // Format sub-bullets (lines starting with spaces and dash)
    if (line.match(/^\s{2,}-/)) {
      const subBulletText = trimmed.replace(/^-\s*/, '')
      return (
        <div key={i} className="flex items-start gap-3 my-2 pl-8">
          <span className="text-current opacity-50 mt-1 text-sm">◦</span>
          <span className="flex-1 text-sm leading-relaxed opacity-90">{subBulletText}</span>
        </div>
      )
    }
    
    // Format headers with colons
    if (trimmed.includes(':') && trimmed.split(':')[0].length < 40) {
      const [header, ...rest] = trimmed.split(':')
      return (
        <div key={i} className="font-semibold mt-4 mb-2 text-sm uppercase tracking-wide opacity-80">
          {header}:{rest.join(':')}
        </div>
      )
    }
    
    // Regular paragraph text
    return <div key={i} className="my-2 leading-relaxed">{trimmed}</div>
  })
}

export default AgentCard

// Made with Bob
