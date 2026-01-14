# PhishScope LLM Provider Configuration

PhishScope supports multiple LLM providers for AI-enhanced phishing analysis. You can easily switch between providers by updating your `.env` file.

## Supported Providers

### 1. IBM WatsonX (watsonx)
IBM's enterprise-grade AI platform with Granite models optimized for security analysis.

**Configuration:**
```bash
LLM_PROVIDER=watsonx
LLM_MODEL=ibm/granite-3-8b-instruct

WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
```

**Getting Credentials:**
1. Sign up at [IBM Cloud](https://cloud.ibm.com/)
2. Create a watsonx.ai project
3. Generate an API key from IAM
4. Copy your Project ID from the project settings

**Available Models:**
- `ibm/granite-3-8b-instruct` - Default, good for security analysis
- `ibm/granite-4-h-small` - Newer, more capable
- `meta-llama/llama-3-3-70b-instruct` - Larger, more powerful
- `mistral-large-2512` - Alternative provider

### 2. RITS OpenAI-Compatible API (rits)
RITS provides OpenAI-compatible API endpoints with support for various models including reasoning models.

**Configuration:**
```bash
LLM_PROVIDER=rits
LLM_MODEL=rits/openai/gpt-oss-120b

RITS_API_KEY=your_api_key_here
RITS_API_BASE_URL=http://your-rits-server:4000
```

**Features:**
- OpenAI-compatible API format
- Support for reasoning models (with `reasoning_content` field)
- Flexible model selection
- Custom deployment support

## Switching Between Providers

To switch providers, simply update the `LLM_PROVIDER` variable in your `.env` file:

### Switch to WatsonX:
```bash
LLM_PROVIDER=watsonx
```

### Switch to RITS:
```bash
LLM_PROVIDER=rits
```

**No code changes required!** PhishScope automatically detects and uses the configured provider.

## Testing Your Configuration

Test your LLM configuration:

```bash
cd PhishScope
python3 -c "
from dotenv import load_dotenv
load_dotenv()

from agents.llm_agent import LLMAgent
from utils.logger import setup_logger

logger = setup_logger()
agent = LLMAgent(logger)

print(f'Provider: {agent.provider}')
print(f'Model: {agent.model_id}')
print(f'Available: {agent.is_available()}')

if agent.is_available():
    result = agent._generate_text('What is phishing?', max_tokens=50)
    print(f'Test Response: {result}')
"
```

## Provider Comparison

| Feature | WatsonX | RITS |
|---------|---------|------|
| **Authentication** | IAM Token | API Key |
| **Model Selection** | IBM Granite, Llama, Mistral | Custom models |
| **Deployment** | IBM Cloud | Self-hosted or cloud |
| **Reasoning Models** | ✓ | ✓ |
| **Enterprise Support** | ✓ | Depends on deployment |
| **Cost** | Pay-per-use | Depends on deployment |

## Advanced Configuration

### Custom Model Override

You can override the default model for any provider:

```bash
LLM_PROVIDER=watsonx
LLM_MODEL=meta-llama/llama-3-3-70b-instruct
```

### Timeout Configuration

Adjust API timeouts in `agents/llm_agent.py`:

```python
response = requests.post(url, headers=headers, json=body, timeout=30)
```

### Temperature and Token Limits

Modify generation parameters in the `_generate_text()` calls:

```python
result = agent._generate_text(
    prompt, 
    max_tokens=800,  # Adjust token limit
    temperature=0.5   # Adjust creativity (0.0-1.0)
)
```

## Troubleshooting

### WatsonX Issues

**Problem:** `Failed to get IAM token`
- **Solution:** Verify your `WATSONX_API_KEY` is correct
- Check your IBM Cloud account is active

**Problem:** `Model unavailable`
- **Solution:** Try a different model from the available list
- Check model availability in your region

### RITS Issues

**Problem:** `RITS API connection test failed`
- **Solution:** Verify `RITS_API_BASE_URL` is accessible
- Check firewall/network settings

**Problem:** `RITS API returned empty content`
- **Solution:** Verify the model name is correct
- Check API server logs for errors

### General Issues

**Problem:** AI analysis shows "Unknown" verdict
- **Solution:** Check the logs for API errors
- Verify your API credentials are valid
- Ensure you have sufficient API quota/credits

**Problem:** Slow response times
- **Solution:** Reduce `max_tokens` parameter
- Use a smaller/faster model
- Check network latency to API endpoint

## Adding New Providers

To add support for a new LLM provider:

1. Add initialization method in `agents/llm_agent.py`:
```python
def _init_your_provider(self):
    # Initialize your provider
    pass
```

2. Add text generation method:
```python
def _generate_text_your_provider(self, prompt, max_tokens, temperature):
    # Call your provider's API
    pass
```

3. Update the `__init__` method to support your provider:
```python
elif self.provider == 'your_provider':
    self._init_your_provider()
```

4. Update `.env.example` with configuration template

5. Update this documentation

## Best Practices

1. **Security:**
   - Never commit `.env` file to version control
   - Rotate API keys regularly
   - Use environment-specific credentials

2. **Performance:**
   - Start with smaller models for testing
   - Use larger models only when needed
   - Cache results when possible

3. **Cost Management:**
   - Monitor API usage
   - Set token limits appropriately
   - Use fallback to rule-based analysis when AI fails

4. **Reliability:**
   - Implement proper error handling
   - Have fallback mechanisms
   - Log all API interactions for debugging

## Support

For provider-specific issues:
- **WatsonX:** [IBM Cloud Support](https://cloud.ibm.com/docs/watson)
- **RITS:** Contact your RITS administrator

For PhishScope issues:
- Open an issue on GitHub
- Check existing documentation
- Review logs in the output directory

---

*Last Updated: 2026-01-13*