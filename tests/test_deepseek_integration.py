#!/usr/bin/env python3
"""
Test script to verify DeepSeek integration works correctly.
This script demonstrates how the LLM service automatically detects and uses DeepSeek when available.
"""

import os
import asyncio
from langchain_core.messages import HumanMessage

# Set up environment for testing
os.environ["LOG_LEVEL"] = "INFO"

# Example configurations - uncomment the one you want to test

# Test with DeepSeek (if you have a DeepSeek API key)
# os.environ["DEEPSEEK_API_KEY"] = "your-deepseek-api-key-here"
# os.environ["LLM_PROVIDER"] = "deepseek"
# os.environ["LLM_MODEL"] = "deepseek-chat"

# Test with OpenAI (if you have an OpenAI API key)
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
# os.environ["LLM_PROVIDER"] = "openai"
# os.environ["LLM_MODEL"] = "gpt-3.5-turbo"

# Auto-detection test (will use whichever API key is available)
# Just set one of the API keys and let the system auto-detect

from app.services.llm import get_llm, generate_llm_response


async def test_llm_integration():
    """Test the LLM integration with both providers."""
    print("Testing LLM Integration...")
    print("=" * 50)
    
    try:
        # Get LLM instance
        llm = get_llm()
        print(f"✅ LLM initialized successfully: {type(llm).__name__}")
        
        # Test message
        messages = [HumanMessage(content="Hello! Please respond with a brief greeting.")]
        
        # Generate response
        print("\n🤖 Generating response...")
        result = await generate_llm_response(llm, messages)
        
        print(f"✅ Response generated successfully!")
        print(f"📝 Response: {result['response']}")
        
        if result.get('metadata'):
            print(f"📊 Metadata: {result['metadata']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Make sure you have set either OPENAI_API_KEY or DEEPSEEK_API_KEY")
        print("   and installed the required packages:")
        print("   - For OpenAI: pip install langchain-openai")
        print("   - For DeepSeek: pip install langchain-deepseek")


def test_provider_detection():
    """Test the provider detection logic."""
    print("\nTesting Provider Detection...")
    print("=" * 50)
    
    from app.services.llm import _determine_provider
    from app.config import settings
    
    print(f"Current settings:")
    print(f"  LLM_PROVIDER: {settings.LLM_PROVIDER}")
    print(f"  OPENAI_API_KEY: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Not set'}")
    print(f"  DEEPSEEK_API_KEY: {'✅ Set' if settings.DEEPSEEK_API_KEY else '❌ Not set'}")
    
    try:
        provider = _determine_provider()
        print(f"\n🎯 Selected provider: {provider}")
    except Exception as e:
        print(f"\n❌ Provider detection failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 DeepSeek Integration Test")
    print("This script tests the automatic provider detection and LLM initialization.")
    print("\nTo test with DeepSeek:")
    print("  1. Set DEEPSEEK_API_KEY environment variable")
    print("  2. Optionally set LLM_PROVIDER=deepseek")
    print("  3. Run: python test_deepseek_integration.py")
    print("\nTo test with OpenAI:")
    print("  1. Set OPENAI_API_KEY environment variable")
    print("  2. Optionally set LLM_PROVIDER=openai")
    print("  3. Run: python test_deepseek_integration.py")
    print("\n" + "=" * 70)
    
    # Test provider detection
    test_provider_detection()
    
    # Test LLM integration
    asyncio.run(test_llm_integration())