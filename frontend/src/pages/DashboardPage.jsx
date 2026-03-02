import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { BarChart3, Clock, Shield, TrendingUp, ExternalLink, Search } from 'lucide-react'
import { getAnalyses } from '../services/apiService'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { DashboardSkeleton } from '../components/ui/Skeleton'

function DashboardPage() {
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadAnalyses()
  }, [])

  const loadAnalyses = async () => {
    try {
      setLoading(true)
      const data = await getAnalyses(50)
      setAnalyses(data.analyses || [])
    } catch (err) {
      console.error(err)
      toast.error(err.message || 'Failed to load analyses')
    } finally {
      setLoading(false)
    }
  }

  const filteredAnalyses = analyses.filter(analysis =>
    analysis.url?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const stats = {
    total: analyses.length,
    completed: analyses.filter(a => a.status === 'completed').length,
    failed: analyses.filter(a => a.status === 'failed').length,
    running: analyses.filter(a => a.status === 'running').length,
  }

  const getStatusBadge = (status) => {
    const configs = {
      completed: { variant: 'success', label: 'Completed' },
      failed: { variant: 'danger', label: 'Failed' },
      running: { variant: 'info', label: 'Running' },
    }
    const config = configs[status] || { variant: 'default', label: status }
    return <Badge variant={config.variant}>{config.label}</Badge>
  }

  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A'
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white tracking-tight">
            Analysis Dashboard
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mt-2">
            View and manage your phishing analysis history
          </p>
        </div>
        <button
          onClick={loadAnalyses}
          disabled={loading}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          aria-label="Refresh analyses"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <DashboardSkeleton />
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: 'Total Analyses', value: stats.total, icon: BarChart3, color: 'primary' },
              { label: 'Completed', value: stats.completed, icon: Shield, color: 'green' },
              { label: 'Running', value: stats.running, icon: Clock, color: 'blue' },
              { label: 'Failed', value: stats.failed, icon: TrendingUp, color: 'red' },
            ].map((stat) => (
              <Card key={stat.label} hover className="glass-card dark:bg-dark-card/50">
                <Card.Content className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{stat.label}</p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
                    </div>
                    <div className={`w-12 h-12 bg-${stat.color}-100 dark:bg-${stat.color}-900/30 rounded-xl flex items-center justify-center`}>
                      <stat.icon className={`w-6 h-6 text-${stat.color}-600 dark:text-${stat.color}-400`} aria-hidden="true" />
                    </div>
                  </div>
                </Card.Content>
              </Card>
            ))}
          </div>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
              <Search className="w-5 h-5" aria-hidden="true" />
            </div>
            <input
              type="text"
              placeholder="Search analysis history..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-white/60 dark:bg-dark-card/60 backdrop-blur-md border border-white/20 dark:border-dark-border/20 rounded-2xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500/50 transition-all duration-300 placeholder:text-gray-400 text-gray-900 dark:text-white"
              aria-label="Search analyses"
            />
          </div>

          {/* Analyses Table */}
          <div className="glass-card overflow-hidden">
            <div className="p-6 border-b border-gray-100/50 dark:border-gray-700/50">
              <h2 className="text-xl font-heading font-semibold text-gray-900 dark:text-white">Recent Analyses</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {filteredAnalyses.length} {filteredAnalyses.length === 1 ? 'analysis' : 'analyses'} found
              </p>
            </div>

            {filteredAnalyses.length === 0 ? (
              <div className="p-16 text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-50 dark:bg-gray-800 rounded-full mb-6">
                  <Shield className="w-10 h-10 text-gray-300 dark:text-gray-600" aria-hidden="true" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No analyses found</h3>
                <p className="text-gray-500 dark:text-gray-400 max-w-sm mx-auto mb-8">
                  {searchTerm ? 'Try adjusting your search terms to find what you\'re looking for.' : 'Get started by analyzing your first URL.'}
                </p>
                {!searchTerm && (
                  <button
                    onClick={() => window.location.href = '/'}
                    className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition-all shadow-lg shadow-primary-500/30 hover:shadow-primary-500/50 hover:-translate-y-0.5"
                  >
                    Start New Analysis
                  </button>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50/50 dark:bg-gray-800/50 border-b border-gray-100/50 dark:border-gray-700/50">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Target URL
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Date Analyzed
                      </th>
                      <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100/50 dark:divide-gray-700/50">
                    {filteredAnalyses.map((analysis) => (
                      <tr
                        key={analysis.analysis_id}
                        className="hover:bg-primary-50/30 dark:hover:bg-primary-900/10 transition-colors group"
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3 max-w-lg">
                            <div className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 group-hover:border-primary-200 dark:group-hover:border-primary-800 transition-colors">
                              <ExternalLink className="w-4 h-4 text-gray-400 dark:text-gray-500 group-hover:text-primary-500 transition-colors" aria-hidden="true" />
                            </div>
                            <span className="text-sm font-medium text-gray-900 dark:text-gray-200 truncate font-mono">
                              {analysis.url}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(analysis.status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                            <Clock className="w-4 h-4" aria-hidden="true" />
                            {formatDate(analysis.timestamp)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <a
                            href={`/api/results/${analysis.analysis_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-sm font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 hover:underline decoration-2 underline-offset-4 transition-all"
                          >
                            View Report
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default DashboardPage
