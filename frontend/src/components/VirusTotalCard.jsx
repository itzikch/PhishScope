
import { useState, useEffect } from 'react'
import { Shield, AlertTriangle, CheckCircle, ExternalLink, Loader2, Info } from 'lucide-react'
import Card from './ui/Card'
import Badge from './ui/Badge'

export default function VirusTotalCard({ url }) {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (url) {
            fetchVTData()
        }
    }, [url])

    const fetchVTData = async () => {
        setLoading(true)
        setError(null)
        try {
            // First try to get existing report
            let response = await fetch(`/api/virustotal/report?url=${encodeURIComponent(url)}`)

            if (response.status === 404) {
                // If not found, trigger scan
                const scanResponse = await fetch('/api/virustotal/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                })
                if (!scanResponse.ok) throw new Error('Failed to initiate scan')

                // Wait a bit then retry report (polling would be better but simple for now)
                await new Promise(r => setTimeout(r, 3000))
                response = await fetch(`/api/virustotal/report?url=${encodeURIComponent(url)}`)
            }

            if (!response.ok) {
                if (response.status === 503) {
                    setError('VirusTotal integration not configured')
                    setLoading(false)
                    return
                }
                throw new Error('Failed to fetch VirusTotal data')
            }

            const result = await response.json()
            setData(result.data)
        } catch (err) {
            console.error(err)
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    if (error === 'VirusTotal integration not configured') return null

    if (loading) {
        return (
            <Card>
                <Card.Content className="p-6">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-blue-50 dark:bg-blue-900/20 rounded-xl flex items-center justify-center">
                            <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Checking VirusTotal...</h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Querying threat intelligence database</p>
                        </div>
                    </div>
                </Card.Content>
            </Card>
        )
    }

    if (error) {
        return (
            <Card>
                <Card.Content className="p-6">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-red-50 dark:bg-red-900/20 rounded-xl flex items-center justify-center">
                            <AlertTriangle className="w-6 h-6 text-red-500" />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">VirusTotal Unavailable</h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{error}</p>
                        </div>
                    </div>
                </Card.Content>
            </Card>
        )
    }

    if (!data) return null

    const stats = data.attributes.last_analysis_stats
    const malicious = stats.malicious
    const suspicious = stats.suspicious
    const harmless = stats.harmless + stats.undetected
    const total = malicious + suspicious + harmless

    const isMalicious = malicious > 0 || suspicious > 0
    const detectionRatio = `${malicious}/${total}`

    const threatLevel = malicious > 2 ? 'high' : (malicious > 0 || suspicious > 0 ? 'medium' : 'safe')

    const variantConfig = {
        high: { color: 'red', bg: 'bg-red-50 dark:bg-red-900/20', icon: Shield, text: 'text-red-700 dark:text-red-400' },
        medium: { color: 'amber', bg: 'bg-amber-50 dark:bg-amber-900/20', icon: AlertTriangle, text: 'text-amber-700 dark:text-amber-400' },
        safe: { color: 'emerald', bg: 'bg-emerald-50 dark:bg-emerald-900/20', icon: CheckCircle, text: 'text-emerald-700 dark:text-emerald-400' }
    }[threatLevel]

    const Icon = variantConfig.icon

    return (
        <Card className="border-l-4" style={{ borderLeftColor: `var(--color-${variantConfig.color}-500)` }}>
            <Card.Content className="p-6">
                <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 ${variantConfig.bg} rounded-xl flex items-center justify-center`}>
                            <Icon className={`w-6 h-6 text-${variantConfig.color}-600 dark:text-${variantConfig.color}-400`} />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                VirusTotal Analysis
                                <Badge variant={threatLevel === 'safe' ? 'success' : 'danger'}>
                                    {malicious > 0 ? 'Malicious' : 'Clean'}
                                </Badge>
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                Community Score: <span className="font-medium text-gray-900 dark:text-gray-200">{data.attributes.reputation}</span>
                            </p>
                        </div>
                    </div>

                    <a
                        href={`https://www.virustotal.com/gui/url/${data.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 transition-colors"
                    >
                        Full Report
                        <ExternalLink className="w-4 h-4" />
                    </a>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="p-4 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-100 dark:border-red-900/20">
                        <div className="text-sm text-red-600 dark:text-red-400 font-medium mb-1">Malicious</div>
                        <div className="text-2xl font-bold text-red-700 dark:text-red-300">{malicious}</div>
                    </div>
                    <div className="p-4 bg-amber-50 dark:bg-amber-900/10 rounded-xl border border-amber-100 dark:border-amber-900/20">
                        <div className="text-sm text-amber-600 dark:text-amber-400 font-medium mb-1">Suspicious</div>
                        <div className="text-2xl font-bold text-amber-700 dark:text-amber-300">{suspicious}</div>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/10 rounded-xl border border-green-100 dark:border-green-900/20">
                        <div className="text-sm text-green-600 dark:text-green-400 font-medium mb-1">Clean</div>
                        <div className="text-2xl font-bold text-green-700 dark:text-green-300">{harmless}</div>
                    </div>
                </div>

                {malicious > 0 && (
                    <div className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                        <span className="font-semibold text-gray-900 dark:text-white">Detections: </span>
                        {Object.entries(data.attributes.last_analysis_results)
                            .filter(([_, result]) => result.category === 'malicious')
                            .map(([engine]) => engine)
                            .slice(0, 5)
                            .join(', ')}
                        {Object.values(data.attributes.last_analysis_results).filter(r => r.category === 'malicious').length > 5 && ' ...and more'}
                    </div>
                )}
            </Card.Content>
        </Card>
    )
}
