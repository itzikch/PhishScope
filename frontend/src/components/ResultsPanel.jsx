import {
  Shield, AlertTriangle, CheckCircle, XCircle,
  FileCode, Network, Eye, Download, ExternalLink,
  ChevronDown, ChevronUp
} from 'lucide-react'
import { useState } from 'react'
import Card from './ui/Card'
import Badge from './ui/Badge'
import Alert from './ui/Alert'
import Button from './ui/Button'
import VirusTotalCard from './VirusTotalCard'

function ResultsPanel({ results }) {
  const [expandedSections, setExpandedSections] = useState({
    dom: false,
    javascript: false,
    network: false,
  })

  if (!results) return null

  const findings = results.findings || {}
  const aiAnalysis = findings.ai_analysis || {}
  const assessment = aiAnalysis.phishing_assessment || {}

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const getVerdictConfig = (verdict) => {
    if (verdict?.includes('High Risk')) {
      return {
        variant: 'danger',
        icon: XCircle,
        color: 'red',
        bgClass: 'bg-red-50 border-red-200',
        textClass: 'text-red-900',
      }
    }
    if (verdict?.includes('Medium Risk')) {
      return {
        variant: 'warning',
        icon: AlertTriangle,
        color: 'yellow',
        bgClass: 'bg-yellow-50 border-yellow-200',
        textClass: 'text-yellow-900',
      }
    }
    return {
      variant: 'success',
      icon: CheckCircle,
      color: 'green',
      bgClass: 'bg-green-50 border-green-200',
      textClass: 'text-green-900',
    }
  }

  const verdictConfig = getVerdictConfig(assessment.verdict)

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header with URL */}
      <Card>
        <Card.Content className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Complete</h2>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <ExternalLink className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
              <span className="truncate font-mono">{results.url}</span>
            </div>
          </div>
          <Button
            variant="secondary"
            size="sm"
            leftIcon={<Download className="w-4 h-4" />}
            onClick={() => window.open(`/api/report/${results.analysis_id}`, '_blank')}
          >
            Download Report
          </Button>
        </Card.Content>
      </Card>

      {/* Error State */}
      {results.error && (
        <Alert variant="warning" title="Analysis Completed with Issues">
          <div className="space-y-2">
            <p className="font-medium">The page could not be fully analyzed:</p>
            <p className="text-sm">{results.error}</p>
            <p className="text-sm text-gray-600 mt-2">
              This may occur if the site is blocking automated access, is offline, or has connection issues.
              Partial results may still be available below.
            </p>
          </div>
        </Alert>
      )}

      {/* AI Assessment Card */}
      {assessment.verdict && (
        <Card className="border-2 border-gray-200">
          <Card.Content className="p-6">
            <div className={`rounded-xl border-2 p-6 ${verdictConfig.bgClass}`}>
              <div className="flex items-start gap-4">
                <div className={`flex-shrink-0 w-12 h-12 bg-${verdictConfig.color}-100 rounded-xl flex items-center justify-center`}>
                  <verdictConfig.icon className={`w-6 h-6 text-${verdictConfig.color}-600`} aria-hidden="true" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className={`text-2xl font-bold ${verdictConfig.textClass}`}>
                      {assessment.verdict}
                    </h3>
                    <Badge variant={verdictConfig.variant} size="lg">
                      {assessment.confidence}% Confidence
                    </Badge>
                  </div>
                  {assessment.reasoning && (
                    <p className={`text-sm ${verdictConfig.textClass} opacity-90 leading-relaxed`}>
                      {assessment.reasoning}
                    </p>
                  )}
                </div>
              </div>

              {/* Key Indicators */}
              {assessment.key_indicators?.length > 0 && (
                <div className="mt-6 pt-6 border-t border-current/10">
                  <h4 className={`font-semibold ${verdictConfig.textClass} mb-3 flex items-center gap-2`}>
                    <Shield className="w-4 h-4" aria-hidden="true" />
                    Key Indicators
                  </h4>
                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {assessment.key_indicators.map((indicator, i) => (
                      <li key={i} className={`flex items-start gap-2 text-sm ${verdictConfig.textClass}`}>
                        <span className="text-current/60 mt-0.5">•</span>
                        <span>{indicator}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Card.Content>
        </Card>
      )}

      {/* VirusTotal Analysis */}
      <VirusTotalCard url={results.url} />

      {/* Detailed Findings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* DOM Analysis */}
        <FindingCard
          title="DOM Analysis"
          icon={FileCode}
          iconColor="blue"
          expanded={expandedSections.dom}
          onToggle={() => toggleSection('dom')}
          stats={[
            { label: 'Forms Found', value: findings.dom?.forms_count || 0 },
            { label: 'Password Fields', value: findings.dom?.password_fields?.length || 0 },
            { label: 'Hidden Inputs', value: findings.dom?.hidden_inputs?.length || 0 },
          ]}
          details={findings.dom}
        />

        {/* JavaScript Analysis */}
        <FindingCard
          title="JavaScript Analysis"
          icon={FileCode}
          iconColor="purple"
          expanded={expandedSections.javascript}
          onToggle={() => toggleSection('javascript')}
          stats={[
            { label: 'Inline Scripts', value: findings.javascript?.inline_scripts_count || 0 },
            { label: 'External Scripts', value: findings.javascript?.external_scripts_count || 0 },
            { label: 'Suspicious Patterns', value: findings.javascript?.suspicious_patterns?.length || 0 },
          ]}
          details={findings.javascript}
        />

        {/* Network Analysis */}
        <FindingCard
          title="Network Analysis"
          icon={Network}
          iconColor="green"
          expanded={expandedSections.network}
          onToggle={() => toggleSection('network')}
          stats={[
            { label: 'Total Requests', value: findings.network?.total_requests || 0 },
            { label: 'POST Requests', value: findings.network?.post_requests?.length || 0 },
            { label: 'Exfiltration Risks', value: findings.network?.exfiltration_candidates?.length || 0 },
          ]}
          details={findings.network}
        />
      </div>

      {/* Screenshot */}
      {results.analysis_id && (
        <Card>
          <Card.Header>
            <div className="flex items-center gap-2">
              <Eye className="w-5 h-5 text-gray-600" aria-hidden="true" />
              <Card.Title>Page Screenshot</Card.Title>
            </div>
            <Card.Description>
              Visual capture of the analyzed page at the time of inspection
            </Card.Description>
          </Card.Header>
          <Card.Content>
            <div className="rounded-lg overflow-hidden border-2 border-gray-200 bg-gray-50">
              <img
                src={`/api/screenshot/${results.analysis_id}`}
                alt="Page screenshot"
                className="w-full h-auto"
                onError={(e) => {
                  e.target.parentElement.innerHTML = `
                    <div class="p-12 text-center">
                      <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-200 rounded-full mb-4">
                        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                      </div>
                      <p class="text-gray-600 font-medium mb-1">Screenshot Not Available</p>
                      <p class="text-sm text-gray-500">The page could not be captured. This may occur if the site blocked access or failed to load.</p>
                    </div>
                  `
                }}
              />
            </div>
          </Card.Content>
        </Card>
      )}
    </div>
  )
}

// Reusable Finding Card Component
function FindingCard({ title, icon: Icon, iconColor, stats, expanded, onToggle, details }) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    purple: 'bg-purple-100 text-purple-600',
    green: 'bg-green-100 text-green-600',
  }

  return (
    <Card hover className="h-full">
      <Card.Content className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className={`w-10 h-10 rounded-lg ${colorClasses[iconColor]} flex items-center justify-center`}>
            <Icon className="w-5 h-5" aria-hidden="true" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>

        <div className="space-y-3">
          {stats.map((stat, i) => (
            <div key={i} className="flex justify-between items-center">
              <span className="text-sm text-gray-600">{stat.label}</span>
              <Badge variant={stat.value > 0 ? 'primary' : 'default'}>
                {stat.value}
              </Badge>
            </div>
          ))}
        </div>

        {details && (
          <button
            onClick={onToggle}
            className="mt-4 w-full flex items-center justify-center gap-2 text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors"
            aria-expanded={expanded}
          >
            {expanded ? 'Show Less' : 'Show Details'}
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        )}

        {expanded && details && (
          <div className="mt-4 pt-4 border-t border-gray-200 animate-slide-down">
            <pre className="text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-48">
              {JSON.stringify(details, null, 2)}
            </pre>
          </div>
        )}
      </Card.Content>
    </Card>
  )
}

export default ResultsPanel
