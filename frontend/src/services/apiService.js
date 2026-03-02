const API_BASE = 'http://localhost:8070'

export async function analyzeUrl(url) {
  try {
    const response = await fetch(`${API_BASE}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    })

    if (!response.ok) {
      let errorMessage = 'Analysis failed'
      try {
        const error = await response.json()
        errorMessage = error.detail || error.message || errorMessage
      } catch (e) {
        // If response is not JSON, use status text
        errorMessage = `Server error: ${response.status} ${response.statusText}`
      }
      throw new Error(errorMessage)
    }

    return response.json()
  } catch (error) {
    if (error.message) {
      throw error
    }
    throw new Error('Network error: Could not connect to server')
  }
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
