"""
Base Agent Test Script
Test base_agent.py functionality with mock data
"""

import asyncio
import sys
import os

# Path fix for tests/ directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Now import from agents and services
from agents.base_agent import TestAgent, GeminiService


async def test_base_agent():
    """Base Agent'ı test et"""
    print("🚀 Starting Base Agent Test...")
    print("=" * 50)
    
    # Mock Gemini Service (gerçek API anahtarı olmadan test için)
    gemini_service = GeminiService()
    
    # Test Agent oluştur
    agent = TestAgent(gemini_service)
    
    # Progress callback test
    def progress_callback(agent_name, progress, status, current_step):
        print(f" {agent_name}: {progress}% - {status} - {current_step}")
    
    # Event callback test
    def event_callback(agent_name, event_type, data, timestamp):
        print(f"🔔 Event: {agent_name} -> {event_type} at {timestamp}")
    
    # Callback'leri set et
    agent.set_progress_callback(progress_callback)
    agent.set_event_callback(event_callback)
    
    # Test data
    test_input = {
        "product_name": "Wireless Bluetooth Headphones",
        "niche": "audio electronics",
        "target_keywords": ["bluetooth headphones", "wireless audio", "noise canceling"],
        "budget": 1000,
        "competition_level": "medium"
    }
    
    print(f" Input Data: {test_input}")
    print("\n Starting Agent Execution...")
    print("-" * 30)
    
    # Agent'ı çalıştır
    result = await agent.execute(test_input)
    
    print("\n" + "=" * 50)
    print(" TEST RESULTS:")
    print("=" * 50)
    
    print(f" Success: {result.success}")
    print(f"  Processing Time: {result.processing_time:.2f}s")
    print(f" Reasoning Steps: {len(result.reasoning)}")
    
    if result.reasoning:
        print("\n🔍 Chain of Thought:")
        for i, step in enumerate(result.reasoning, 1):
            print(f"  {i}. {step}")
    
    if result.data:
        print(f"\n📊 Output Data Keys: {list(result.data.keys())}")
        for key, value in result.data.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")
    
    if result.errors:
        print(f"\n Errors: {result.errors}")
    
    if result.metadata:
        print(f"\n Metadata: {result.metadata}")
    
    # Agent status test
    print("\n" + "=" * 50)
    print(" AGENT STATUS:")
    print("=" * 50)
    status = agent.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    return result


async def test_tool_system():
    """Tool system'ı test et"""
    print("\n" + "=" * 50)
    print("🔧 TESTING TOOL SYSTEM:")
    print("=" * 50)
    
    gemini_service = GeminiService()
    agent = TestAgent(gemini_service)
    
    # Available tools listele
    print(f"🛠️  Available Tools: {list(agent.available_tools.keys())}")
    
    # Her tool'u test et
    test_tools = [
        ("search_web", {"query": "bluetooth headphones review", "max_results": 3}),
        ("analyze_competitor", {"domain": "example.com"}),
        ("get_keyword_metrics", {"keywords": ["bluetooth headphones", "wireless audio"]}),
        ("validate_content", {"content": "This is a test content for validation."})
    ]
    
    for tool_name, kwargs in test_tools:
        try:
            print(f"\n🔧 Testing {tool_name}...")
            result = await agent.call_tool(tool_name, **kwargs)
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")


async def main():
    """Ana test fonksiyonu"""
    try:
        # Base agent test
        await test_base_agent()
        
        # Tool system test
        await test_tool_system()
        
        print("\n" + "🎉" * 20)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎉" * 20)
        
        print("\n Next Steps:")
        print("1.  Base Agent working perfectly")
        print("2.  Ready to create keyword_scorer.py")
        print("3.  Then pipeline/orchestrator.py")
        print("4.  Then specific agents (market_research.py, etc.)")
        
    except Exception as e:
        print(f"\n TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Test'i çalıştır
    asyncio.run(main())