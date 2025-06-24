# DeepSeek Integration Guide

This guide explains how to use DeepSeek as an alternative LLM provider in the chat bot application.

## Overview

The application now supports both OpenAI and DeepSeek as LLM providers. The system can automatically detect which provider to use based on available API keys, or you can explicitly configure your preferred provider.

## Features

- **Automatic Provider Detection**: The system automatically uses DeepSeek if a DeepSeek API key is available
- **Fallback Support**: Falls back to OpenAI if DeepSeek is not available
- **Explicit Configuration**: You can explicitly set which provider to use
- **Model Flexibility**: Supports different models for each provider

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# LLM Configuration
LLM_PROVIDER=deepseek          # or "openai" for explicit provider selection
LLM_MODEL=deepseek-chat        # or "gpt-3.5-turbo" for OpenAI
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# DeepSeek Configuration
DEEPSEEK_API_KEY=your-deepseek-api-key-here

# OpenAI Configuration (fallback)
OPENAI_API_KEY=your-openai-api-key-here
```

### Provider Selection Logic

The system uses the following logic to select a provider:

1. **Explicit Configuration**: If `LLM_PROVIDER` is set and the corresponding API key is available, use that provider
2. **Auto-Detection**: If no explicit provider is set:
   - Use DeepSeek if `DEEPSEEK_API_KEY` is available and `langchain-deepseek` is installed
   - Fall back to OpenAI if `OPENAI_API_KEY` is available
3. **Error**: If no valid API key is found, raise an error

## Installation

### Install DeepSeek Package

```bash
pip install langchain-deepseek
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Get DeepSeek API Key

1. Visit [DeepSeek API](https://api-docs.deepseek.com/)
2. Create an account and get your API key
3. Add the API key to your environment variables

## Supported Models

### DeepSeek Models

- `deepseek-chat`: General purpose chat model (recommended)
- `deepseek-reasoner`: Advanced reasoning model (DeepSeek-R1)

### OpenAI Models (Fallback)

- `gpt-3.5-turbo`: Fast and cost-effective
- `gpt-4`: More capable but slower and more expensive
- `gpt-4-turbo`: Latest GPT-4 variant

## Usage Examples

### Using DeepSeek Explicitly

```bash
# Set environment variables
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export LLM_PROVIDER="deepseek"
export LLM_MODEL="deepseek-chat"

# Start the application
python -m app.main
```

### Auto-Detection Mode

```bash
# Set only the API key, let the system auto-detect
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Start the application
python -m app.main
```

### Testing the Integration

Use the provided test script:

```bash
# Set your API key
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Run the test
python test_deepseek_integration.py
```

## Code Examples

### Basic Usage

```python
from app.services.llm import get_llm, generate_llm_response
from langchain_core.messages import HumanMessage

# Get LLM instance (automatically detects provider)
llm = get_llm()

# Generate response
messages = [HumanMessage(content="Hello, how are you?")]
result = await generate_llm_response(llm, messages)
print(result['response'])
```

### Provider Detection

```python
from app.services.llm import _determine_provider

# Check which provider will be used
provider = _determine_provider()
print(f"Using provider: {provider}")
```

## Configuration in Different Environments

### Development

```bash
# .env.development
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-dev-deepseek-key
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.8
```

### Production

```bash
# .env.production
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-prod-deepseek-key
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
```

### Docker Configuration

Update your `docker-compose.yml`:

```yaml
services:
  chat:
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LLM_PROVIDER=deepseek
      - LLM_MODEL=deepseek-chat
```

## Troubleshooting

### Common Issues

#### "langchain-deepseek not installed"

```bash
pip install langchain-deepseek
```

#### "No valid API key found"

Make sure you have set either `DEEPSEEK_API_KEY` or `OPENAI_API_KEY`:

```bash
export DEEPSEEK_API_KEY="your-api-key"
# or
export OPENAI_API_KEY="your-api-key"
```

#### "Unsupported LLM provider"

Check your `LLM_PROVIDER` setting. Valid values are:
- `openai`
- `deepseek`

### Debugging

Enable debug logging to see provider selection:

```bash
export LOG_LEVEL=DEBUG
python -m app.main
```

You should see logs like:
```
INFO: DeepSeek API key found, using DeepSeek provider
INFO: Using DeepSeek provider
INFO: Initializing LLM with model deepseek-chat
```

## Performance Considerations

### DeepSeek vs OpenAI

| Feature | DeepSeek | OpenAI |
|---------|----------|--------|
| Cost | Generally lower | Higher |
| Speed | Competitive | Fast |
| Quality | High quality | Industry standard |
| Reasoning | Excellent (R1 model) | Good |

### Best Practices

1. **Use DeepSeek for cost-sensitive applications**
2. **Use OpenAI for maximum compatibility**
3. **Set appropriate temperature values** (0.7 is a good default)
4. **Monitor token usage** for cost optimization
5. **Use caching** for repeated queries

## Migration from OpenAI

To migrate from OpenAI to DeepSeek:

1. **Get DeepSeek API key**
2. **Install langchain-deepseek**: `pip install langchain-deepseek`
3. **Update environment variables**:
   ```bash
   DEEPSEEK_API_KEY=your-deepseek-key
   LLM_PROVIDER=deepseek
   LLM_MODEL=deepseek-chat
   ```
4. **Test the integration** using the test script
5. **Deploy with new configuration**

## API Compatibility

Both providers use the same LangChain interface, so your existing code will work without changes. The `generate_llm_response` function works identically with both providers.

## Support

For issues related to:
- **DeepSeek API**: Check [DeepSeek documentation](https://api-docs.deepseek.com/)
- **LangChain integration**: Check [LangChain DeepSeek docs](https://python.langchain.com/docs/integrations/chat/deepseek/)
- **Application issues**: Check the application logs and test script output