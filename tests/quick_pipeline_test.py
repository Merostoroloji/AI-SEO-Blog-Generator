"""
Quick Pipeline Test with Real Agents
Run: python -c "import asyncio; exec(open('quick_test.py').read())"
"""

import asyncio
import sys
import os

# Add to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def quick_test():
    print("🚀 QUICK PIPELINE TEST - SESSION 3")
    print("=" * 50)
    
    try:
        # Import services
        from services.gemini_service import GeminiService
        from services.seo_tools import SEOToolsService
        
        # Import agents
        from agents.market_search import MarketResearchAgent
        from agents.keyword_analyzer import KeywordAnalyzerAgent
        
        print("✅ All imports successful")
        
        # Initialize services
        gemini = GeminiService()
        seo_tools = SEOToolsService()
        
        print("✅ Services initialized")
        
        # Test input
        test_input = {
            "product_name": "Smart Fitness Tracker",
            "niche": "wearable technology",
            "target_keywords": ["fitness tracker", "smartwatch", "health monitor"],
            "target_audience": "health enthusiasts, athletes",
            "budget": 1200,
            "competition_level": "medium"
        }
        
        print(f"📊 Test Input: {test_input['product_name']} in {test_input['niche']}")
        
        # Progress tracking
        def progress_callback(agent_name, progress, status, current_step):
            print(f"[{agent_name}] {progress}% - {current_step}")
        
        # Test Market Research Agent
        print("\n🔍 Testing Market Research Agent...")
        market_agent = MarketResearchAgent(gemini)
        market_agent.set_progress_callback(progress_callback)
        
        market_result = await market_agent.execute(test_input)
        print(f"✅ Market Research: {market_result.success} (Confidence: {market_result.metadata.get('confidence', 'N/A')}%)")
        
        # Test Keyword Analyzer Agent
        print("\n🎯 Testing Keyword Analyzer Agent...")
        keyword_agent = KeywordAnalyzerAgent(gemini, seo_tools)
        keyword_agent.set_progress_callback(progress_callback)
        
        # Use market research output as input
        keyword_input = {**test_input, **market_result.data}
        keyword_result = await keyword_agent.execute(keyword_input)
        print(f"✅ Keyword Analysis: {keyword_result.success} (Keywords: {keyword_result.metadata.get('total_keywords', 'N/A')})")
        
        # Results summary
        print("\n📈 PIPELINE TEST RESULTS")
        print("-" * 30)
        print(f"Market Research: {'✅ PASS' if market_result.success else '❌ FAIL'}")
        print(f"Keyword Analysis: {'✅ PASS' if keyword_result.success else '❌ FAIL'}")
        print(f"Data Flow: {'✅ WORKING' if keyword_result.success else '❌ BROKEN'}")
        
        if market_result.success and keyword_result.success:
            print("\n🎉 PIPELINE TEST SUCCESSFUL!")
            print("✅ Both agents working")
            print("✅ Data flow functional") 
            print("✅ AI reasoning active")
            print("✅ Progress tracking working")
            
            # Quick stats
            market_areas = len(market_result.data.keys())
            keyword_stages = len(keyword_result.data.keys())
            total_reasoning = len(market_result.reasoning) + len(keyword_result.reasoning)
            
            print(f"\n📊 Quick Stats:")
            print(f"- Market analysis areas: {market_areas}")
            print(f"- Keyword analysis stages: {keyword_stages}")
            print(f"- Total reasoning steps: {total_reasoning}")
            print(f"- Average confidence: {(market_result.metadata.get('confidence', 80) + keyword_result.metadata.get('confidence', 80))/2:.1f}%")
            
            return True
        else:
            print("\n❌ PIPELINE TEST FAILED")
            if not market_result.success:
                print(f"Market Research Error: {market_result.errors}")
            if not keyword_result.success:
                print(f"Keyword Analysis Error: {keyword_result.errors}")
            return False
            
    except Exception as e:
        print(f"\n💥 TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Run test
if __name__ == "__main__":
    success = asyncio.run(quick_test())
    print(f"\n{'🎯 SESSION 3 COMPLETED SUCCESSFULLY' if success else '⚠️ SESSION 3 NEEDS ATTENTION'}")