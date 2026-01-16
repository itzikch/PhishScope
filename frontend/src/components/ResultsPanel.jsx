function ResultsPanel({ results }) {
  if (!results) return null

  const findings = results.findings || {}
  const aiAnalysis = findings.ai_analysis || {}
  const assessment = aiAnalysis.phishing_assessment || {}

  const getVerdictColor = (verdict) => {
    if (verdict?.includes('High Risk')) return 'text-red-600 bg-red-50'
    if (verdict?.includes('Medium Risk')) return 'text-yellow-600 bg-yellow-50'
    return 'text-green-600 bg-green-50'
  }

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Results</h2>

        {results.error ? (
          <div className="p-4 bg-red-50 text-red-700 rounded-md">
            Error: {results.error}
          </div>
        ) : (
          <>
            {/* AI Assessment */}
            {assessment.verdict && (
              <div className={`p-4 rounded-lg mb-4 ${getVerdictColor(assessment.verdict)}`}>
                <div className="flex items-center justify-between">
                  <span className="font-bold text-lg">{assessment.verdict}</span>
                  <span className="text-sm">Confidence: {assessment.confidence}%</span>
                </div>
                {assessment.reasoning && (
                  <p className="mt-2 text-sm opacity-90">{assessment.reasoning}</p>
                )}
              </div>
            )}

            {/* Key Indicators */}
            {assessment.key_indicators?.length > 0 && (
              <div className="mb-4">
                <h3 className="font-medium text-gray-900 mb-2">Key Indicators</h3>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  {assessment.key_indicators.map((indicator, i) => (
                    <li key={i}>{indicator}</li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>

      {/* Detailed Findings */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* DOM Findings */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-medium text-gray-900 mb-2">DOM Analysis</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <p>Forms: {findings.dom?.forms_count || 0}</p>
            <p>Password Fields: {findings.dom?.password_fields?.length || 0}</p>
            <p>Hidden Inputs: {findings.dom?.hidden_inputs?.length || 0}</p>
          </div>
        </div>

        {/* JavaScript Findings */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-medium text-gray-900 mb-2">JavaScript Analysis</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <p>Inline Scripts: {findings.javascript?.inline_scripts_count || 0}</p>
            <p>External Scripts: {findings.javascript?.external_scripts_count || 0}</p>
            <p>Suspicious Patterns: {findings.javascript?.suspicious_patterns?.length || 0}</p>
          </div>
        </div>

        {/* Network Findings */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-medium text-gray-900 mb-2">Network Analysis</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <p>Total Requests: {findings.network?.total_requests || 0}</p>
            <p>POST Requests: {findings.network?.post_requests?.length || 0}</p>
            <p>Exfiltration Endpoints: {findings.network?.exfiltration_candidates?.length || 0}</p>
          </div>
        </div>
      </div>

      {/* Screenshot */}
      {results.analysis_id && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-medium text-gray-900 mb-2">Screenshot</h3>
          <img
            src={`/api/screenshot/${results.analysis_id}`}
            alt="Page screenshot"
            className="rounded border max-h-96 object-contain"
            onError={(e) => e.target.style.display = 'none'}
          />
        </div>
      )}
    </div>
  )
}

export default ResultsPanel
