# Multi-Agent Debate Mode

PhishScope now includes an **adversarial debate system** where three AI agents analyze URLs through structured argumentation.

## Overview

Instead of a single AI assessment, the debate mode uses three specialized agents:

1. **🔴 Prosecutor** - Argues the site IS phishing
2. **🟢 Defense Attorney** - Argues the site IS legitimate  
3. **⚖️ Judge** - Makes final ruling after hearing both sides

## How It Works

### Debate Flow

```
1. Page Scraping → Collect evidence
2. Prosecutor Round 1 → Opening arguments (phishing indicators)
3. Defense Round 1 → Opening arguments (legitimacy indicators)
4. Prosecutor Round 2 → Rebuttal to defense
5. Defense Round 2 → Rebuttal to prosecution
6. Judge's Ruling → Final verdict with risk score (0-100)
```

### Real-Time Streaming

The debate streams live via **Server-Sent Events (SSE)**, allowing you to watch the analysis unfold in real-time.

## Architecture

### Backend (Python)

**New Files:**
- `src/phishscope/llm/prompts/debate_prompts.py` - Prompts for each agent
- `src/phishscope/llm/debate_orchestrator.py` - Orchestrates the 5-round debate
- `src/phishscope/api/main.py` - Added `/api/analyze/debate` SSE endpoint

**Key Components:**

```python
# Debate Orchestrator
class DebateOrchestrator:
    async def run_debate_streaming(url, page_load, dom, js, network):
        # Yields SSE events as each agent responds
        yield {"event": "scrape_done", "data": {...}}
        yield {"event": "agent", "data": {"role": "prosecutor", "round": 1, ...}}
        yield {"event": "agent", "data": {"role": "defense", "round": 1, ...}}
        # ... more rounds
        yield {"event": "verdict", "data": {...}}
        yield {"event": "done"}
```

**Intelligence Report:**

The system builds a structured intelligence report from analysis findings:
- URL analysis (SSL, redirects, domain info)
- Page metadata (title, description)
- Suspicious indicators (auto-detected red flags)
- Forms and input fields
- JavaScript patterns
- Network traffic
- Page errors

This report is provided to all agents as evidence.

### Frontend (React)

**New Components:**

```
frontend/src/components/debate/
├── AgentCard.jsx       # Displays agent arguments
├── StepBar.jsx         # 6-step progress indicator
├── RiskMeter.jsx       # Visual risk score (0-100)
├── ScrapeCard.jsx      # Page intelligence display
└── VerdictBadge.jsx    # Final verdict with styling
```

**New Page:**
- `frontend/src/pages/DebateAnalysisPage.jsx` - Full debate UI with SSE handling

**Navigation:**
- Added "Debate" tab in main navigation
- Route: `/debate`

## Usage

### Via Web UI

1. Navigate to **Debate** tab in the navigation bar
2. Enter a URL to analyze
3. Watch the debate unfold in real-time
4. View final verdict with risk score

### Via API

**Endpoint:** `POST /api/analyze/debate`

**Request:**
```json
{
  "url": "https://example.com",
  "debate_mode": true
}
```

**Response:** Server-Sent Events stream

```
event: scrape_done
data: {"url": "...", "ssl": true, "forms_count": 1, ...}

event: agent
data: {"role": "prosecutor", "round": 1, "content": "🔴 PROSECUTION — Round 1:\n- Suspicious domain..."}

event: agent
data: {"role": "defense", "round": 1, "content": "🟢 DEFENSE — Round 1:\n- Valid SSL certificate..."}

event: agent
data: {"role": "prosecutor", "round": 2, "content": "🔴 PROSECUTION — Round 2 (Rebuttal):\n..."}

event: agent
data: {"role": "defense", "round": 2, "content": "🟢 DEFENSE — Round 2 (Rebuttal):\n..."}

event: agent
data: {"role": "judge", "round": 0, "content": "⚖️ JUDGE'S RULING:\n..."}

event: verdict
data: {"verdict": "PHISHING", "risk_score": 85, "confidence": 90, "reasoning": "..."}

event: done
```

### JavaScript Client Example

```javascript
const response = await fetch('/api/analyze/debate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com' })
})

const reader = response.body.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  
  const text = decoder.decode(value)
  // Parse SSE format: "event: type\ndata: {...}\n\n"
  // Handle each event type
}
```

## Prompt Engineering

Each agent has a carefully crafted prompt:

### Prosecutor Prompt
- Focuses on phishing indicators
- Looks for typosquatting, SSL issues, urgency language
- Cites specific evidence from intelligence report
- Aggressive and thorough

### Defense Prompt
- Focuses on legitimacy indicators
- Looks for proper SSL, professional design, logical purpose
- Addresses prosecutor's concerns
- Fair and evidence-based

### Judge Prompt
- Reviews full debate transcript
- Weighs evidence from both sides
- Provides risk score (0-100)
- Issues verdict: PHISHING / LEGITIMATE / SUSPICIOUS
- Explains reasoning

## Cost Considerations

**Standard Mode:** 1 LLM call per analysis  
**Debate Mode:** 5 LLM calls per analysis (5x cost)

For IBM WatsonX at ~$0.002/1K tokens:
- Standard: ~$0.01 per analysis
- Debate: ~$0.05 per analysis

## Benefits

1. **More Thorough Analysis** - Multiple perspectives reduce blind spots
2. **Transparent Reasoning** - See the full argumentation process
3. **Reduced Bias** - Adversarial structure prevents confirmation bias
4. **Engaging UX** - Real-time debate is more interesting than static results
5. **Educational** - Learn what indicators matter most

## Limitations

1. **Higher Latency** - 5 sequential LLM calls take longer
2. **Higher Cost** - 5x more API calls
3. **Requires LLM** - Won't work without AI configured
4. **Network Dependent** - SSE requires stable connection

## Configuration

Debate mode uses the same LLM configuration as standard mode:

```bash
# .env
LLM_PROVIDER=watsonx  # or rits
WATSONX_API_KEY=your_key
WATSONX_PROJECT_ID=your_project
```

No additional configuration needed.

## Future Enhancements

Potential improvements:
- [ ] Add more agents (Security Expert, UX Analyst)
- [ ] Allow custom debate rounds
- [ ] Save debate transcripts
- [ ] Compare debate vs standard results
- [ ] Add debate replay feature
- [ ] Support multiple LLM providers per agent
- [ ] Add confidence calibration based on historical accuracy

## Technical Notes

### SSE vs WebSockets

We chose Server-Sent Events over WebSockets because:
- Simpler protocol (HTTP-based)
- Automatic reconnection
- Better for one-way server→client streaming
- Works through most proxies/firewalls

### Browser Compatibility

SSE is supported in all modern browsers. For older browsers, consider a polyfill.

### Error Handling

If the stream disconnects:
1. Frontend shows error message
2. Partial results are preserved
3. User can retry analysis

### Performance

- Each LLM call: ~5-15 seconds
- Total debate time: ~30-60 seconds
- Network overhead: minimal (text streaming)

## Troubleshooting

**"LLM service not available"**
- Check LLM_PROVIDER is set correctly
- Verify API keys are valid
- Ensure LLM client initialized successfully

**Stream disconnects mid-debate**
- Check network stability
- Verify server timeout settings
- Check browser console for errors

**Agents give weak arguments**
- Intelligence report may lack evidence
- Try different URLs with more indicators
- Check prompt engineering in `debate_prompts.py`

## Contributing

To modify agent behavior:
1. Edit prompts in `src/phishscope/llm/prompts/debate_prompts.py`
2. Adjust debate flow in `src/phishscope/llm/debate_orchestrator.py`
3. Update UI components in `frontend/src/components/debate/`

## License

Same as PhishScope main project.