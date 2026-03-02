import { Gavel, Scale, X } from 'lucide-react'
import Card from '../ui/Card'
import RiskMeter from './RiskMeter'

/**
 * JudgePanel - Fixed top panel showing judge's final ruling
 *
 * @param {Object} props
 * @param {Object} props.verdict - Verdict data from judge
 * @param {string} props.judgeContent - Judge's full ruling text
 * @param {boolean} props.isVisible - Whether to show the panel
 * @param {Function} props.onDismiss - Callback when panel is dismissed
 */
function JudgePanel({ verdict, judgeContent, isVisible = false, onDismiss }) {
  if (!isVisible) return null

  const { verdict: decision, risk_score, reasoning } = verdict || {}
  const config = getVerdictConfig(decision, risk_score)

  return (
    <div className="sticky top-20 z-30 mb-8 animate-scale-in">
      <Card className={`border-2 ${config.borderClass} shadow-2xl relative`}>
        {/* Close Button */}
        <button
          onClick={onDismiss}
          className="absolute top-4 right-4 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
          aria-label="Dismiss judge panel"
        >
          <X className="w-5 h-5 text-gray-500 group-hover:text-gray-700 dark:text-gray-400 dark:group-hover:text-gray-200" />
        </button>
        
        <Card.Content className="p-6">
          {/* Judge Header */}
          <div className="flex items-center justify-center gap-4 mb-6">
            <div className={`w-16 h-16 rounded-full ${config.iconBg} flex items-center justify-center shadow-lg ring-4 ring-white dark:ring-gray-800`}>
              <Gavel className={`w-8 h-8 ${config.iconColor}`} aria-hidden="true" />
            </div>
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <Scale className="w-6 h-6" aria-hidden="true" />
                Judge's Ruling
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Final Decision
              </p>
            </div>
          </div>

          {/* Verdict Badge */}
          <div className={`${config.bgClass} rounded-xl p-6 mb-6 text-center border-2 ${config.borderClass}`}>
            <div className={`text-4xl font-bold ${config.textClass} mb-2`}>
              {config.label}
            </div>
            {reasoning && (
              <p className={`text-sm ${config.textClass} opacity-90 leading-relaxed max-w-2xl mx-auto`}>
                {reasoning}
              </p>
            )}
          </div>

          {/* Risk Meter */}
          {risk_score !== undefined && (
            <div className="mb-6">
              <RiskMeter score={risk_score} animated={true} />
            </div>
          )}

          {/* Full Ruling (Collapsible) */}
          {judgeContent && (
            <details className="mt-4">
              <summary className="cursor-pointer text-sm font-semibold text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                View Full Ruling
              </summary>
              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg text-sm text-gray-700 dark:text-gray-300 leading-relaxed max-h-96 overflow-y-auto">
                {formatJudgeContent(judgeContent)}
              </div>
            </details>
          )}
        </Card.Content>
      </Card>
    </div>
  )
}

/**
 * Get verdict configuration
 */
function getVerdictConfig(decision, riskScore = 50) {
  const normalizedDecision = (decision || '').toUpperCase()
  
  if (normalizedDecision.includes('PHISHING') || riskScore >= 70) {
    return {
      label: '🚨 PHISHING DETECTED',
      iconColor: 'text-red-600 dark:text-red-400',
      iconBg: 'bg-red-100 dark:bg-red-900/40',
      textClass: 'text-red-700 dark:text-red-400',
      bgClass: 'bg-red-50 dark:bg-red-900/20',
      borderClass: 'border-red-500',
    }
  }
  
  if (normalizedDecision.includes('SUSPICIOUS') || (riskScore >= 40 && riskScore < 70)) {
    return {
      label: '⚠️ SUSPICIOUS SITE',
      iconColor: 'text-yellow-600 dark:text-yellow-400',
      iconBg: 'bg-yellow-100 dark:bg-yellow-900/40',
      textClass: 'text-yellow-700 dark:text-yellow-400',
      bgClass: 'bg-yellow-50 dark:bg-yellow-900/20',
      borderClass: 'border-yellow-500',
    }
  }
  
  if (normalizedDecision.includes('LEGITIMATE') || riskScore < 40) {
    return {
      label: '✅ LEGITIMATE SITE',
      iconColor: 'text-green-600 dark:text-green-400',
      iconBg: 'bg-green-100 dark:bg-green-900/40',
      textClass: 'text-green-700 dark:text-green-400',
      bgClass: 'bg-green-50 dark:bg-green-900/20',
      borderClass: 'border-green-500',
    }
  }
  
  return {
    label: '❓ INCONCLUSIVE',
    iconColor: 'text-gray-600 dark:text-gray-400',
    iconBg: 'bg-gray-100 dark:bg-gray-700',
    textClass: 'text-gray-700 dark:text-gray-400',
    bgClass: 'bg-gray-50 dark:bg-gray-800/20',
    borderClass: 'border-gray-500',
  }
}

/**
 * Format judge content
 */
function formatJudgeContent(content) {
  return content.split('\n').map((line, i) => {
    const trimmed = line.trim()
    if (!trimmed) return <br key={i} />
    return <div key={i} className="my-1">{trimmed}</div>
  })
}

export default JudgePanel

// Made with Bob
