import { useState } from 'react'
import { toast } from 'sonner'
import { Shield, AlertTriangle, CheckCircle, Clock } from 'lucide-react'
import UrlInput from '../components/UrlInput'
import ResultsPanel from '../components/ResultsPanel'
import Card from '../components/ui/Card'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import { analyzeUrl, getResults } from '../services/apiService'
import { ExportButton } from '../components/ExportButton'

function AnalysisPage() {
  const [analysisId, setAnalysisId] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleAnalyze = async (url) => {
    setLoading(true)
    setResults(null)
    toast.dismiss()
    toast.loading('Starting analysis...')
    setProgress(0)

    try {
      // Start analysis
      const response = await analyzeUrl(url)
      setAnalysisId(response.analysis_id)

      // Poll for results with progress updates
      await pollResults(response.analysis_id)

      toast.dismiss()
      toast.success('Analysis completed successfully!')
    } catch (err) {
      console.error(err)
      toast.dismiss()
      toast.error(err.message || 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
      setProgress(0)
    }
  }

  const pollResults = async (id, maxAttempts = 60) => {
    for (let i = 0; i < maxAttempts; i++) {
      // Update progress
      setProgress(Math.min((i / maxAttempts) * 100, 95))

      const result = await getResults(id)

      if (result.status === 'completed' || result.status === 'failed') {
        setProgress(100)
        setResults(result)
        return
      }

      // Wait 2 seconds before next poll
      await new Promise(resolve => setTimeout(resolve, 2000))
    }

    throw new Error('Analysis timed out after 2 minutes')
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Section */}
      <div className="text-center space-y-8 py-12 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary-500/10 rounded-full blur-3xl -z-10 animate-pulse" />

        <div className="inline-flex items-center justify-center p-2 bg-white/50 dark:bg-white/5 backdrop-blur-sm rounded-2xl shadow-sm mb-8 animate-scale-in">
          <div className="p-3 bg-gradient-to-br from-primary-500 to-indigo-600 rounded-xl shadow-lg shadow-primary-500/20">
            <Shield className="w-8 h-8 text-white" aria-hidden="true" />
          </div>
        </div>

        <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-gray-900 dark:text-white max-w-4xl mx-auto leading-tight">
          Advanced Phishing <br />
          <span className="bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent">
            Detection & Analysis
          </span>
        </h1>

        <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed">
          Uncover hidden threats with our evidence-driven analysis engine.
          We inspect DOM structure, JavaScript behavior, and network traffic.
        </p>
      </div>

      {/* Analysis Input Card */}
      <div className="max-w-3xl mx-auto animate-slide-up relative z-10">
        <UrlInput onAnalyze={handleAnalyze} loading={loading} />
      </div>

      {/* Loading State */}
      {loading && (
        <Card className="max-w-3xl mx-auto animate-scale-in glass-card border-primary-100">
          <Card.Content className="py-12">
            <div className="space-y-8">
              <LoadingSpinner size="lg" text="Analyzing URL..." />

              {/* Progress Bar */}
              <div className="space-y-3 px-8">
                <div className="flex justify-between text-sm font-medium text-gray-600 dark:text-gray-300">
                  <span>Analysis Progress</span>
                  <span className="text-primary-600">{Math.round(progress)}%</span>
                </div>
                <div className="h-3 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
                  <div
                    className="h-full bg-gradient-to-r from-primary-500 to-indigo-500 transition-all duration-500 ease-out relative"
                    style={{ width: `${progress}%` }}
                    role="progressbar"
                    aria-valuenow={progress}
                    aria-valuemin="0"
                    aria-valuemax="100"
                  >
                    <div className="absolute inset-0 bg-white/30 animate-[shimmer_2s_infinite]" />
                  </div>
                </div>
              </div>

              {/* Analysis Steps */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 px-4">
                {[
                  { label: 'Loading Page', icon: Clock, active: progress < 30 },
                  { label: 'Analyzing Content', icon: Shield, active: progress >= 30 && progress < 70 },
                  { label: 'Generating Report', icon: CheckCircle, active: progress >= 70 },
                ].map((step, index) => (
                  <div
                    key={step.label}
                    className={`flex flex-col items-center gap-3 p-4 rounded-2xl transition-all duration-300 ${step.active
                      ? 'bg-primary-50/50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 shadow-sm scale-105'
                      : 'bg-transparent border border-transparent opacity-60'
                      }`}
                  >
                    <div className={`p-2.5 rounded-xl ${step.active ? 'bg-white dark:bg-gray-800 shadow-sm' : 'bg-gray-100 dark:bg-gray-800'}`}>
                      <step.icon
                        className={`w-5 h-5 ${step.active ? 'text-primary-600 animate-pulse' : 'text-gray-400'
                          }`}
                        aria-hidden="true"
                      />
                    </div>
                    <span className={`text-sm font-medium ${step.active ? 'text-primary-900 dark:text-primary-100' : 'text-gray-500 dark:text-gray-400'
                      }`}>
                      {step.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </Card.Content>
        </Card>
      )}

      {/* Results */}
      {results && !loading && (
        <div className="animate-slide-up space-y-4">
          <div className="flex justify-end max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <ExportButton analysisData={results} />
          </div>
          <ResultsPanel results={results} />
        </div>
      )}

      {/* Info Cards */}
      {!loading && !results && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto animate-slide-up pt-12">
          {[
            {
              icon: Shield,
              title: 'Safe Execution',
              description: 'URLs are loaded in an isolated sandbox environment with advanced anti-detection measures.',
              color: 'blue',
            },
            {
              icon: AlertTriangle,
              title: 'Deep Inspection',
              description: 'We analyze DOM structure, hidden iframes, and obfuscated JavaScript for zero-day threats.',
              color: 'amber',
            },
            {
              icon: CheckCircle,
              title: 'Actionable Intel',
              description: 'Get detailed reports with screenshot evidence, network logs, and threat confidence scores.',
              color: 'emerald',
            },
          ].map((feature) => (
            <div key={feature.title} className="group p-8 bg-white/60 dark:bg-dark-card/60 backdrop-blur-sm rounded-3xl border border-white/20 dark:border-dark-border/20 shadow-sm hover:shadow-glass-hover hover:-translate-y-1 transition-all duration-300">
              <div className={`inline-flex items-center justify-center w-14 h-14 bg-white dark:bg-gray-800 rounded-2xl shadow-sm mb-6 group-hover:scale-110 transition-transform duration-300`}>
                <feature.icon className={`w-7 h-7 text-${feature.color}-500`} aria-hidden="true" />
              </div>
              <h3 className="text-xl font-heading font-semibold text-gray-900 dark:text-white mb-3 group-hover:text-primary-600 transition-colors">
                {feature.title}
              </h3>
              <p className="text-base text-gray-600 dark:text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AnalysisPage
