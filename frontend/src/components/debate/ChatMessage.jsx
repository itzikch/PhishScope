import { Shield, Scale } from 'lucide-react'

/**
 * ChatMessage - Displays an agent's argument as a chat message bubble
 * 
 * @param {Object} props
 * @param {string} props.role - Agent role: 'prosecutor' or 'defense'
 * @param {number} props.round - Round number (1 or 2)
 * @param {string} props.content - Agent's argument text
 * @param {boolean} props.isStreaming - Whether content is still being received
 */
function ChatMessage({ role, round, content, isStreaming = false }) {
  const isProsecutor = role === 'prosecutor'
  
  const config = {
    prosecutor: {
      align: 'left',
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      borderColor: 'border-red-200 dark:border-red-800',
      textColor: 'text-red-900 dark:text-red-100',
      accentColor: 'bg-red-500',
      icon: Shield,
      iconBg: 'bg-red-100 dark:bg-red-900/40',
      iconColor: 'text-red-600 dark:text-red-400',
      label: '🔴 Prosecutor',
    },
    defense: {
      align: 'right',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      borderColor: 'border-blue-200 dark:border-blue-800',
      textColor: 'text-blue-900 dark:text-blue-100',
      accentColor: 'bg-blue-500',
      icon: Scale,
      iconBg: 'bg-blue-100 dark:bg-blue-900/40',
      iconColor: 'text-blue-600 dark:text-blue-400',
      label: '🟢 Defense',
    },
  }
  
  const style = config[role] || config.defense
  
  return (
    <div className={`flex ${isProsecutor ? 'justify-start' : 'justify-end'} mb-6 animate-slide-up`}>
      <div className={`flex gap-3 max-w-4xl ${isProsecutor ? 'flex-row' : 'flex-row-reverse'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full ${style.iconBg} flex items-center justify-center shadow-md`}>
          <style.icon className={`w-5 h-5 ${style.iconColor}`} aria-hidden="true" />
        </div>
        
        {/* Message Bubble */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className={`flex items-center gap-2 mb-2 ${isProsecutor ? 'flex-row' : 'flex-row-reverse'}`}>
            <span className={`text-sm font-bold ${style.textColor}`}>
              {style.label}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Round {round}{round === 2 ? ' (Rebuttal)' : ''}
            </span>
            {isStreaming && (
              <div className="flex gap-1">
                <span className={`w-1.5 h-1.5 ${style.accentColor} rounded-full animate-pulse`} />
                <span className={`w-1.5 h-1.5 ${style.accentColor} rounded-full animate-pulse delay-75`} />
                <span className={`w-1.5 h-1.5 ${style.accentColor} rounded-full animate-pulse delay-150`} />
              </div>
            )}
          </div>
          
          {/* Message Content */}
          <div className={`
            ${style.bgColor} ${style.borderColor}
            border-2 rounded-2xl p-5 shadow-md
            ${isProsecutor ? 'rounded-tl-sm' : 'rounded-tr-sm'}
          `}>
            {content ? (
              <div className={`${style.textColor} text-sm leading-relaxed`}>
                {formatMessageContent(content)}
              </div>
            ) : (
              <div className="flex items-center gap-2 text-gray-400 dark:text-gray-500 italic text-sm">
                <span className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Typing...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Format message content with proper structure
 */
function formatMessageContent(content) {
  const lines = content.split('\n')
  
  return lines.map((line, i) => {
    let trimmed = line.trim()
    
    if (!trimmed) return <br key={i} />
    
    // Remove all markdown asterisks for cleaner display
    trimmed = trimmed.replace(/\*\*/g, '')
    
    // Section headers (lines that were wrapped in ** or are all caps with colons)
    if (trimmed.match(/^[A-Z\s]+:/) || trimmed.match(/^###/)) {
      const headerText = trimmed.replace(/^###\s*/, '')
      return (
        <div key={i} className="font-bold text-base mt-4 mb-2 first:mt-0 border-b border-current/20 pb-1">
          {headerText}
        </div>
      )
    }
    
    // Main bullet points
    if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
      const bulletText = trimmed.replace(/^[-•]\s*/, '')
      return (
        <div key={i} className="flex items-start gap-3 my-2.5">
          <span className="mt-1 opacity-70 font-bold">•</span>
          <span className="flex-1 leading-relaxed">{bulletText}</span>
        </div>
      )
    }
    
    // Sub-bullets (indented)
    if (line.match(/^\s{2,}-/)) {
      const subBulletText = trimmed.replace(/^-\s*/, '')
      return (
        <div key={i} className="flex items-start gap-2 my-2 pl-6">
          <span className="text-xs mt-1 opacity-60">◦</span>
          <span className="flex-1 text-sm opacity-90 leading-relaxed">{subBulletText}</span>
        </div>
      )
    }
    
    // Regular paragraph text
    return <div key={i} className="my-2 leading-relaxed">{trimmed}</div>
  })
}

export default ChatMessage

// Made with Bob
