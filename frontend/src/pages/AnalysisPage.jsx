import { useState } from 'react'
import UrlInput from '../components/UrlInput'
import ResultsPanel from '../components/ResultsPanel'
import { analyzeUrl, getResults } from '../services/apiService'

function AnalysisPage() {
  const [analysisId, setAnalysisId] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async (url) => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      // Start analysis
      const response = await analyzeUrl(url)
      setAnalysisId(response.analysis_id)

      // Poll for results
      await pollResults(response.analysis_id)
    } catch (err) {
      setError(err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const pollResults = async (id, maxAttempts = 60) => {
    for (let i = 0; i < maxAttempts; i++) {
      const result = await getResults(id)

      if (result.status === 'completed' || result.status === 'failed') {
        setResults(result)
        return
      }

      // Wait 2 seconds before next poll
      await new Promise(resolve => setTimeout(resolve, 2000))
    }

    throw new Error('Analysis timed out')
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Phishing Analysis
        </h1>
        <p className="text-gray-600 mb-6">
          Enter a URL to analyze for phishing indicators. The analysis will inspect
          the DOM structure, JavaScript behavior, and network traffic.
        </p>
        <UrlInput onAnalyze={handleAnalyze} loading={loading} />
        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
            {error}
          </div>
        )}
      </div>

      {loading && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
            <span className="ml-3 text-gray-600">Analyzing URL...</span>
          </div>
        </div>
      )}

      {results && <ResultsPanel results={results} />}
    </div>
  )
}

export default AnalysisPage
