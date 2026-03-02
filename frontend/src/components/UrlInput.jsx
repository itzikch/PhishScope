import { useState } from 'react'
import { Search, AlertCircle } from 'lucide-react'
import Button from './ui/Button'

function UrlInput({ onAnalyze, loading }) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')

  const validateUrl = (value) => {
    if (!value.trim()) {
      setError('')
      return false
    }

    try {
      const urlObj = new URL(value)
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        setError('URL must start with http:// or https://')
        return false
      }
      setError('')
      return true
    } catch {
      setError('Please enter a valid URL')
      return false
    }
  }

  const handleChange = (e) => {
    const value = e.target.value
    setUrl(value)
    if (value.trim()) {
      validateUrl(value)
    } else {
      setError('')
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (url.trim() && validateUrl(url)) {
      onAnalyze(url.trim())
    }
  }

  const isValid = url.trim() && !error

  return (
    <form onSubmit={handleSubmit} className="relative group">
      <div className="relative flex items-center">
        <div className="absolute left-6 text-gray-400 group-focus-within:text-primary-500 transition-colors duration-300">
          <Search className={`w-6 h-6 ${error ? 'text-red-400' : ''}`} />
        </div>

        <input
          id="url-input"
          type="url"
          value={url}
          onChange={handleChange}
          placeholder="Enter a suspicious URL to analyze..."
          className={`
            w-full pl-16 pr-36 py-5 text-lg 
            bg-white/60 backdrop-blur-md 
            border-2 rounded-2xl
            transition-all duration-300
            placeholder:text-gray-400
            shadow-glass hover:shadow-glass-hover
            ${error
              ? 'border-red-300 focus:border-red-500 focus:ring-4 focus:ring-red-500/10'
              : 'border-white/40 focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10'
            }
          `}
          required
          disabled={loading}
        />

        <div className="absolute right-3">
          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={loading}
            disabled={!isValid || loading}
            className="rounded-xl shadow-none px-6"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="absolute -bottom-8 left-4 flex items-center gap-1.5 text-sm font-medium text-red-600 animate-slide-down">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Decorative glow effect */}
      <div className="absolute -inset-1 bg-gradient-to-r from-primary-500 to-indigo-500 rounded-2xl opacity-0 group-focus-within:opacity-20 blur-xl transition-opacity duration-300 -z-10" />

      {/* Example URLs */}
      {!url && !loading && (
        <div className="absolute top-full left-0 mt-4 w-full flex justify-center animate-fade-in">
          <div className="flex gap-2 text-sm">
            <span className="text-gray-500 py-1">Try:</span>
            {['https://example.com', 'https://google.com'].map((exampleUrl) => (
              <button
                key={exampleUrl}
                type="button"
                onClick={() => {
                  setUrl(exampleUrl)
                  validateUrl(exampleUrl)
                }}
                className="px-3 py-1 bg-white/40 hover:bg-white/80 border border-white/20 rounded-full text-indigo-600 font-medium transition-all duration-200 hover:scale-105"
              >
                {exampleUrl}
              </button>
            ))}
          </div>
        </div>
      )}
    </form>
  )
}

export default UrlInput
