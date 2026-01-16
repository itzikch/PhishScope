import { useState, useEffect } from 'react'
import { getAnalyses } from '../services/apiService'

function DashboardPage() {
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalyses()
  }, [])

  const loadAnalyses = async () => {
    try {
      const data = await getAnalyses()
      setAnalyses(data.analyses || [])
    } catch (err) {
      console.error('Failed to load analyses:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const colors = {
      completed: 'bg-green-100 text-green-800',
      running: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h1 className="text-xl font-semibold text-gray-900">Recent Analyses</h1>
        </div>

        {analyses.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            No analyses yet. Start by analyzing a URL.
          </div>
        ) : (
          <div className="divide-y">
            {analyses.map((analysis) => (
              <div key={analysis.analysis_id} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 truncate max-w-md">
                      {analysis.url}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(analysis.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(analysis.status)}`}>
                    {analysis.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
