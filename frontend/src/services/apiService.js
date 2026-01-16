const API_BASE = import.meta.env.VITE_API_URL || ''

export async function analyzeUrl(url) {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Analysis failed')
  }

  return response.json()
}

export async function getResults(analysisId) {
  const response = await fetch(`${API_BASE}/api/results/${analysisId}`)

  if (!response.ok) {
    throw new Error('Failed to get results')
  }

  return response.json()
}

export async function getAnalyses(limit = 20) {
  const response = await fetch(`${API_BASE}/api/analyses?limit=${limit}`)

  if (!response.ok) {
    throw new Error('Failed to get analyses')
  }

  return response.json()
}

export async function getReport(analysisId) {
  const response = await fetch(`${API_BASE}/api/report/${analysisId}`)

  if (!response.ok) {
    throw new Error('Failed to get report')
  }

  return response.json()
}
