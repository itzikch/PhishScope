import { useState } from 'react'

function UrlInput({ onAnalyze, loading }) {
  const [url, setUrl] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (url.trim()) {
      onAnalyze(url.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-4">
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://suspicious-site.example.com"
        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
        disabled={loading}
        required
      />
      <button
        type="submit"
        disabled={loading || !url.trim()}
        className="px-6 py-2 bg-cyan-600 text-white rounded-lg font-medium hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
    </form>
  )
}

export default UrlInput
