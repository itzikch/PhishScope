import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'

/**
 * RiskMeter - Visual representation of risk score (0-100)
 * 
 * @param {Object} props
 * @param {number} props.score - Risk score from 0 (safe) to 100 (dangerous)
 * @param {boolean} props.animated - Whether to animate the fill
 */
function RiskMeter({ score = 0, animated = true }) {
  // Clamp score between 0 and 100
  const clampedScore = Math.max(0, Math.min(100, score))
  
  // Determine risk level and colors
  const riskLevel = getRiskLevel(clampedScore)
  
  return (
    <div className="w-full">
      {/* Risk Level Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <riskLevel.icon 
            className={`w-5 h-5 ${riskLevel.iconColor}`} 
            aria-hidden="true" 
          />
          <span className={`text-sm font-semibold ${riskLevel.textColor}`}>
            {riskLevel.label}
          </span>
        </div>
        <span className={`text-2xl font-bold ${riskLevel.textColor}`}>
          {clampedScore}/100
        </span>
      </div>

      {/* Progress Bar */}
      <div className="relative h-8 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
        {/* Gradient Fill */}
        <div
          className={`
            h-full rounded-full transition-all duration-1000 ease-out
            ${animated ? 'animate-fill-width' : ''}
          `}
          style={{
            width: `${clampedScore}%`,
            background: getRiskGradient(clampedScore),
          }}
        >
          {/* Shine Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
        </div>

        {/* Score Label Inside Bar */}
        {clampedScore > 15 && (
          <div className="absolute inset-0 flex items-center px-3">
            <span className="text-xs font-bold text-white drop-shadow-md">
              Risk Score: {clampedScore}
            </span>
          </div>
        )}
      </div>

      {/* Risk Scale Labels */}
      <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
        <span>0 - Safe</span>
        <span>50 - Suspicious</span>
        <span>100 - Dangerous</span>
      </div>
    </div>
  )
}

/**
 * Get risk level configuration based on score
 */
function getRiskLevel(score) {
  if (score >= 70) {
    return {
      label: 'High Risk',
      icon: XCircle,
      iconColor: 'text-red-600 dark:text-red-400',
      textColor: 'text-red-700 dark:text-red-400',
      bgColor: 'bg-red-500',
    }
  } else if (score >= 40) {
    return {
      label: 'Medium Risk',
      icon: AlertTriangle,
      iconColor: 'text-yellow-600 dark:text-yellow-400',
      textColor: 'text-yellow-700 dark:text-yellow-400',
      bgColor: 'bg-yellow-500',
    }
  } else {
    return {
      label: 'Low Risk',
      icon: CheckCircle,
      iconColor: 'text-green-600 dark:text-green-400',
      textColor: 'text-green-700 dark:text-green-400',
      bgColor: 'bg-green-500',
    }
  }
}

/**
 * Get gradient color based on risk score
 */
function getRiskGradient(score) {
  if (score >= 70) {
    // High risk: red gradient
    return 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)'
  } else if (score >= 40) {
    // Medium risk: yellow/orange gradient
    return 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)'
  } else {
    // Low risk: green gradient
    return 'linear-gradient(90deg, #10b981 0%, #059669 100%)'
  }
}

export default RiskMeter

// Made with Bob
