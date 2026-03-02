import { Shield, AlertTriangle, XCircle, HelpCircle } from 'lucide-react'
import Card from '../ui/Card'
import RiskMeter from './RiskMeter'

/**
 * VerdictBadge - Displays the final verdict from the judge
 * 
 * @param {Object} props
 * @param {Object} props.verdict - Verdict data from judge
 */
function VerdictBadge({ verdict }) {
  if (!verdict) return null

  const { verdict: decision, risk_score, reasoning, confidence } = verdict
  const config = getVerdictConfig(decision, risk_score)

  return (
    <Card className={`border-2 ${config.borderClass} animate-scale-in`}>
      <Card.Content className="p-6">
        {/* Verdict Header */}
        <div className={`rounded-xl p-6 ${config.bgClass} mb-6`}>
          <div className="flex items-start gap-4">
            <div className={`flex-shrink-0 w-16 h-16 rounded-xl ${config.iconBgClass} flex items-center justify-center`}>
              <config.icon className={`w-8 h-8 ${config.iconClass}`} aria-hidden="true" />
            </div>
            <div className="flex-1 min-w-0">
              <h2 className={`text-3xl font-bold ${config.textClass} mb-2`}>
                {config.label}
              </h2>
              {reasoning && (
                <p className={`text-sm ${config.textClass} opacity-90 leading-relaxed`}>
                  {reasoning}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Risk Meter */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Risk Assessment
          </h3>
          <RiskMeter score={risk_score || confidence || 50} animated={true} />
        </div>

        {/* Confidence Badge */}
        {confidence !== undefined && (
          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              Judge's Confidence
            </span>
            <span className={`text-lg font-bold ${config.textClass}`}>
              {confidence}%
            </span>
          </div>
        )}
      </Card.Content>
    </Card>
  )
}

/**
 * Get verdict configuration based on decision and risk score
 */
function getVerdictConfig(decision, riskScore = 50) {
  const normalizedDecision = (decision || '').toUpperCase()
  
  // High risk / Phishing
  if (normalizedDecision.includes('PHISHING') || riskScore >= 70) {
    return {
      label: '🚨 PHISHING DETECTED',
      icon: XCircle,
      iconClass: 'text-red-600 dark:text-red-400',
      iconBgClass: 'bg-red-200 dark:bg-red-900/50',
      textClass: 'text-red-700 dark:text-red-400',
      bgClass: 'bg-red-50 dark:bg-red-900/20',
      borderClass: 'border-red-500',
    }
  }
  
  // Medium risk / Suspicious
  if (normalizedDecision.includes('SUSPICIOUS') || (riskScore >= 40 && riskScore < 70)) {
    return {
      label: '⚠️ SUSPICIOUS SITE',
      icon: AlertTriangle,
      iconClass: 'text-yellow-600 dark:text-yellow-400',
      iconBgClass: 'bg-yellow-200 dark:bg-yellow-900/50',
      textClass: 'text-yellow-700 dark:text-yellow-400',
      bgClass: 'bg-yellow-50 dark:bg-yellow-900/20',
      borderClass: 'border-yellow-500',
    }
  }
  
  // Low risk / Legitimate
  if (normalizedDecision.includes('LEGITIMATE') || riskScore < 40) {
    return {
      label: '✅ LEGITIMATE SITE',
      icon: Shield,
      iconClass: 'text-green-600 dark:text-green-400',
      iconBgClass: 'bg-green-200 dark:bg-green-900/50',
      textClass: 'text-green-700 dark:text-green-400',
      bgClass: 'bg-green-50 dark:bg-green-900/20',
      borderClass: 'border-green-500',
    }
  }
  
  // Unknown / Error
  return {
    label: '❓ INCONCLUSIVE',
    icon: HelpCircle,
    iconClass: 'text-gray-600 dark:text-gray-400',
    iconBgClass: 'bg-gray-200 dark:bg-gray-700',
    textClass: 'text-gray-700 dark:text-gray-400',
    bgClass: 'bg-gray-50 dark:bg-gray-800/20',
    borderClass: 'border-gray-500',
  }
}

export default VerdictBadge

// Made with Bob
