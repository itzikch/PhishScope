import { Globe, Lock, AlertTriangle, CheckCircle, ExternalLink } from 'lucide-react'
import Card from '../ui/Card'
import Badge from '../ui/Badge'

/**
 * ScrapeCard - Displays scraped page metadata and auto-detected flags
 * 
 * @param {Object} props
 * @param {Object} props.data - Scrape data from backend
 */
function ScrapeCard({ data }) {
  if (!data) return null

  const { url, final_url, title, ssl, forms_count, suspicious_indicators = [] } = data

  return (
    <Card className="border-l-4 border-l-blue-500 animate-slide-up">
      <Card.Content className="p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <Globe className="w-6 h-6 text-blue-600 dark:text-blue-400" aria-hidden="true" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-blue-700 dark:text-blue-400">
              🔍 Page Intelligence
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Scraped metadata and initial analysis
            </p>
          </div>
          <CheckCircle className="w-6 h-6 text-green-500" aria-hidden="true" />
        </div>

        {/* URL Info */}
        <div className="space-y-3 mb-4">
          <div>
            <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Target URL
            </label>
            <div className="flex items-center gap-2 mt-1">
              <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0" aria-hidden="true" />
              <code className="text-sm font-mono text-gray-700 dark:text-gray-300 break-all">
                {url}
              </code>
            </div>
          </div>

          {final_url && final_url !== url && (
            <div>
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Final URL (After Redirects)
              </label>
              <div className="flex items-center gap-2 mt-1">
                <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0" aria-hidden="true" />
                <code className="text-sm font-mono text-gray-700 dark:text-gray-300 break-all">
                  {final_url}
                </code>
              </div>
            </div>
          )}

          {title && (
            <div>
              <label className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Page Title
              </label>
              <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">
                {title}
              </p>
            </div>
          )}
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <Lock className={`w-5 h-5 ${ssl ? 'text-green-500' : 'text-red-500'}`} aria-hidden="true" />
            <div>
              <div className="text-xs text-gray-500 dark:text-gray-400">SSL/HTTPS</div>
              <div className={`text-sm font-semibold ${ssl ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                {ssl ? 'Enabled' : 'Disabled'}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <Globe className="w-5 h-5 text-blue-500" aria-hidden="true" />
            <div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Forms Found</div>
              <div className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                {forms_count || 0}
              </div>
            </div>
          </div>
        </div>

        {/* Suspicious Indicators */}
        {suspicious_indicators.length > 0 && (
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-5 h-5 text-yellow-500" aria-hidden="true" />
              <h4 className="font-semibold text-gray-700 dark:text-gray-300">
                Auto-Detected Red Flags
              </h4>
            </div>
            <div className="space-y-2">
              {suspicious_indicators.map((indicator, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <span className="text-yellow-500 mt-0.5">⚠️</span>
                  <span className="text-gray-600 dark:text-gray-400">{indicator}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {suspicious_indicators.length === 0 && (
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <CheckCircle className="w-4 h-4 text-green-500" aria-hidden="true" />
              <span>No automatic red flags detected</span>
            </div>
          </div>
        )}
      </Card.Content>
    </Card>
  )
}

export default ScrapeCard

// Made with Bob
