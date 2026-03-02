import { useState, useRef, useEffect } from 'react'
import { toast } from 'sonner'
import { ArrowLeft, Gavel } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import UrlInput from '../components/UrlInput'
import Button from '../components/ui/Button'
import Alert from '../components/ui/Alert'
import StepBar from '../components/debate/StepBar'
import ScrapeCard from '../components/debate/ScrapeCard'
import ChatMessage from '../components/debate/ChatMessage'
import JudgePanel from '../components/debate/JudgePanel'

function DebateAnalysisPage() {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [scrapeData, setScrapeData] = useState(null)
  const [messages, setMessages] = useState([])
  const [verdict, setVerdict] = useState(null)
  const [judgeContent, setJudgeContent] = useState(null)
  const [error, setError] = useState(null)
  const [showJudgePanel, setShowJudgePanel] = useState(true)
  const debateEndRef = useRef(null)
  const eventSourceRef = useRef(null)

  // Auto-scroll to latest message
  useEffect(() => {
    if (debateEndRef.current) {
      debateEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, verdict])

  const handleAnalyze = async (targetUrl) => {
    if (!targetUrl) {
      toast.error('Please enter a URL')
      return
    }

    // Reset state
    setUrl(targetUrl)
    setIsAnalyzing(true)
    setCurrentStep(0)
    setScrapeData(null)
    setMessages([])
    setVerdict(null)
    setJudgeContent(null)
    setError(null)
    setShowJudgePanel(true)

    try {
      // Connect to SSE endpoint
      const response = await fetch('/api/analyze/debate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: targetUrl, debate_mode: true }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let currentEventType = 'message' // Track current event type

      // Read stream
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEventType = line.substring(6).trim()
            continue
          }

          if (line.startsWith('data:')) {
            const data = line.substring(5).trim()
            if (!data) continue

            try {
              const eventData = JSON.parse(data)
              handleEvent(currentEventType, eventData)
              // Reset to default after handling
              currentEventType = 'message'
            } catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }

      toast.success('Debate analysis complete!')
    } catch (err) {
      console.error('Analysis error:', err)
      setError(err.message)
      toast.error(`Analysis failed: ${err.message}`)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleEvent = (eventType, data) => {
    console.log('SSE Event:', eventType, data)

    switch (eventType) {
      case 'scrape_done':
        setScrapeData(data)
        setCurrentStep(1)
        break

      case 'agent':
        const { role, round, content } = data
        
        if (role === 'judge') {
          setJudgeContent(content)
          setCurrentStep(5)
        } else {
          setMessages(prev => [...prev, { role, round, content, timestamp: Date.now() }])
          
          // Update step based on agent
          if (role === 'prosecutor' && round === 1) setCurrentStep(1)
          else if (role === 'defense' && round === 1) setCurrentStep(2)
          else if (role === 'prosecutor' && round === 2) setCurrentStep(3)
          else if (role === 'defense' && round === 2) setCurrentStep(4)
        }
        break

      case 'verdict':
        setVerdict(data)
        setCurrentStep(6)
        setShowJudgePanel(true)
        break

      case 'done':
        setIsAnalyzing(false)
        break

      case 'error':
        setError(data.message)
        setIsAnalyzing(false)
        toast.error(data.message)
        break

      default:
        console.log('Unknown event type:', eventType)
    }
  }

  const handleCancel = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    setIsAnalyzing(false)
    toast.info('Analysis cancelled')
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<ArrowLeft className="w-4 h-4" />}
            onClick={() => navigate('/')}
          >
            Back to Standard Analysis
          </Button>
        </div>
        <h1 className="text-4xl font-heading font-bold bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent mb-4">
          🎭 Multi-Agent Debate Analysis
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Watch three AI agents debate whether a URL is phishing. The Prosecutor argues it's malicious,
          the Defense argues it's legitimate, and the Judge makes the final ruling.
        </p>
      </div>

      {/* URL Input */}
      <div className="max-w-3xl mx-auto">
        <UrlInput
          onAnalyze={handleAnalyze}
          isLoading={isAnalyzing}
          disabled={isAnalyzing}
        />
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="danger" title="Analysis Error">
          {error}
        </Alert>
      )}

      {/* Progress Bar */}
      {isAnalyzing && (
        <div className="max-w-4xl mx-auto">
          <StepBar currentStep={currentStep} />
        </div>
      )}

      {/* Judge Panel (Fixed at top when verdict available) */}
      {verdict && showJudgePanel && (
        <JudgePanel
          verdict={verdict}
          judgeContent={judgeContent}
          isVisible={true}
          onDismiss={() => setShowJudgePanel(false)}
        />
      )}

      {/* Floating Button to Show Judge Panel */}
      {verdict && !showJudgePanel && (
        <button
          onClick={() => setShowJudgePanel(true)}
          className="fixed bottom-8 right-8 z-50 p-4 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 hover:scale-110 group"
          aria-label="Show judge's ruling"
        >
          <div className="flex items-center gap-2">
            <Gavel className="w-6 h-6" aria-hidden="true" />
            <span className="hidden group-hover:inline-block text-sm font-semibold whitespace-nowrap">
              View Verdict
            </span>
          </div>
        </button>
      )}

      {/* Debate Content */}
      {(scrapeData || messages.length > 0) && (
        <div className="max-w-6xl mx-auto">
          {/* Scrape Results */}
          {scrapeData && (
            <div className="mb-8">
              <ScrapeCard data={scrapeData} />
            </div>
          )}

          {/* Chat Thread */}
          {messages.length > 0 && (
            <div className="bg-white/50 dark:bg-gray-800/30 rounded-2xl p-6 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50">
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-gray-200 dark:border-gray-700">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Live Debate
                </h3>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {messages.length} {messages.length === 1 ? 'argument' : 'arguments'}
                </span>
              </div>

              {/* Chat Messages */}
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <ChatMessage
                    key={index}
                    role={message.role}
                    round={message.round}
                    content={message.content}
                    isStreaming={index === messages.length - 1 && isAnalyzing && !verdict}
                  />
                ))}
              </div>

              {/* Scroll anchor */}
              <div ref={debateEndRef} />
            </div>
          )}
        </div>
      )}

      {/* Cancel Button */}
      {isAnalyzing && (
        <div className="text-center">
          <Button variant="secondary" onClick={handleCancel}>
            Cancel Analysis
          </Button>
        </div>
      )}
    </div>
  )
}

export default DebateAnalysisPage

// Made with Bob
