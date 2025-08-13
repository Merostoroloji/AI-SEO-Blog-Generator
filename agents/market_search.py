# agents/market_research.py

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse, ToolMixin
from services.gemini_service import GeminiService

class MarketResearchAgent(BaseAgent, ToolMixin):
    """
    Market Research Agent - İlk pipeline agent'ı
    
    Görevleri:
    - Müşteri analizi (target audience deep dive)
    - Pazar trendleri analizi
    - Rekabet analizi (competitor research)
    - Satış noktaları belirleme (unique selling points)
    """
    
    def __init__(self, gemini_service: GeminiService):
        # Agent konfigürasyonu
        config = AgentConfig(
            name="market_research",
            description="Analyzes market, customers, competitors and identifies selling points",
            max_retries=3,
            timeout_seconds=120,
            temperature=0.7,
            reasoning_enabled=True
        )
        
        BaseAgent.__init__(self, config, gemini_service)
        ToolMixin.__init__(self)
        
        # Market research araçları ekle
        self._register_market_tools()
        
        self.logger.info("MarketResearchAgent initialized")

    def _register_market_tools(self):
        """Market research'e özel araçları kaydet"""
        self.available_tools.update({
            "analyze_target_audience": self._analyze_target_audience,
            "research_market_trends": self._research_market_trends,
            "analyze_competitors": self._analyze_competitors,
            "identify_selling_points": self._identify_selling_points
        })

    async def _analyze_target_audience(self, **kwargs) -> Dict[str, Any]:
        """Müşteri analizi tool'u"""
        product_name = kwargs.get("product_name", "")
        target_audience = kwargs.get("target_audience", "")
        niche = kwargs.get("niche", "")
        
        prompt = f"""
        You are a professional market researcher analyzing target customers for {product_name} in the {niche} market.
        
        Target Audience: {target_audience}
        
        Provide detailed customer analysis covering:
        
        1. DEMOGRAPHIC PROFILE:
        - Age range and gender distribution
        - Income levels and spending patterns
        - Geographic locations (primary markets)
        - Education and professional background
        
        2. BEHAVIORAL ANALYSIS:
        - Shopping behaviors and preferences
        - Decision-making factors
        - Brand loyalty patterns
        - Online vs offline purchasing habits
        
        3. PAIN POINTS & MOTIVATIONS:
        - Main problems they face with current solutions
        - What motivates their purchase decisions
        - Price sensitivity analysis
        - Feature priorities
        
        4. CUSTOMER JOURNEY:
        - Awareness stage behaviors
        - Consideration process
        - Purchase triggers
        - Post-purchase expectations
        
        Format as clear, actionable insights.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are an expert customer analyst.",
            user_prompt=prompt,
            reasoning_context="Analyzing target customer demographics and behaviors"
        )
        
        return {
            "customer_analysis": response['response'],
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }

    async def _research_market_trends(self, **kwargs) -> Dict[str, Any]:
        """Pazar trendleri analiz tool'u"""
        product_name = kwargs.get("product_name", "")
        niche = kwargs.get("niche", "")
        target_keywords = kwargs.get("target_keywords", [])
        
        prompt = f"""
        Analyze current market trends for {product_name} in the {niche} industry.
        
        Target Keywords: {', '.join(target_keywords)}
        
        Research and analyze:
        
        1. MARKET SIZE & GROWTH:
        - Current market size and growth rate
        - Future projections (next 2-3 years)
        - Key growth drivers
        - Market saturation level
        
        2. TECHNOLOGY TRENDS:
        - Emerging technologies in the space
        - Innovation opportunities
        - Technical standards and requirements
        - Future tech disruptions
        
        3. CONSUMER BEHAVIOR TRENDS:
        - Shifting preferences and expectations
        - New usage patterns
        - Generational differences
        - Sustainability and ethical concerns
        
        4. PRICING TRENDS:
        - Average price points in the market
        - Price sensitivity analysis
        - Value-based pricing opportunities
        - Discount and promotion patterns
        
        5. DISTRIBUTION TRENDS:
        - Popular sales channels
        - E-commerce vs retail trends
        - Direct-to-consumer opportunities
        - International market expansion
        
        Provide data-backed insights and actionable recommendations.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are a market trend analyst with deep industry knowledge.",
            user_prompt=prompt,
            reasoning_context="Analyzing market trends and future opportunities"
        )
        
        return {
            "market_trends": response['response'],
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }

    async def _analyze_competitors(self, **kwargs) -> Dict[str, Any]:
        """Rekabet analizi tool'u"""
        product_name = kwargs.get("product_name", "")
        niche = kwargs.get("niche", "")
        competition_level = kwargs.get("competition_level", "medium")
        
        prompt = f"""
        Conduct comprehensive competitor analysis for {product_name} in {niche}.
        
        Competition Level: {competition_level}
        
        Analyze:
        
        1. MAIN COMPETITORS:
        - Top 5-7 direct competitors
        - Their market share and positioning
        - Strengths and weaknesses
        - Product feature comparison
        
        2. PRICING ANALYSIS:
        - Competitor pricing strategies
        - Price ranges and positioning
        - Value propositions at different price points
        - Promotional strategies
        
        3. MARKETING STRATEGIES:
        - Content marketing approaches
        - SEO and keyword strategies
        - Social media presence
        - Advertising and promotion tactics
        
        4. PRODUCT STRATEGIES:
        - Feature differentiation
        - Quality positioning
        - Innovation frequency
        - Customer support and services
        
        5. MARKET GAPS:
        - Underserved customer segments
        - Missing features or services
        - Pricing gaps
        - Content and communication gaps
        
        6. COMPETITIVE ADVANTAGES:
        - Areas where we can differentiate
        - Competitor vulnerabilities
        - Market positioning opportunities
        - Content angle opportunities
        
        Focus on actionable competitive intelligence.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are a competitive intelligence analyst.",
            user_prompt=prompt,
            reasoning_context="Analyzing competitive landscape and opportunities"
        )
        
        return {
            "competitor_analysis": response['response'],
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }

    async def _identify_selling_points(self, **kwargs) -> Dict[str, Any]:
        """Satış noktaları belirleme tool'u"""
        product_name = kwargs.get("product_name", "")
        niche = kwargs.get("niche", "")
        target_audience = kwargs.get("target_audience", "")
        budget = kwargs.get("budget", 0)
        
        prompt = f"""
        Identify compelling unique selling points for {product_name}.
        
        Context:
        - Niche: {niche}
        - Target Audience: {target_audience}
        - Budget Range: ${budget}
        
        Develop:
        
        1. UNIQUE VALUE PROPOSITIONS:
        - Primary value proposition (main benefit)
        - Secondary benefits
        - Emotional benefits
        - Functional benefits
        
        2. DIFFERENTIATION FACTORS:
        - What makes this product unique
        - Competitive advantages
        - Technology or feature advantages
        - Service or support advantages
        
        3. CUSTOMER BENEFIT HIERARCHY:
        - Most important benefits (top priority)
        - Nice-to-have benefits
        - Hidden or unexpected benefits
        - Long-term value benefits
        
        4. PROOF POINTS:
        - Credibility indicators
        - Social proof opportunities
        - Performance metrics to highlight
        - Testimonial themes
        
        5. CONTENT ANGLES:
        - Blog post topics that highlight benefits
        - Problem-solution narratives
        - Educational content opportunities
        - Comparison content ideas
        
        6. SEO OPPORTUNITIES:
        - Benefit-focused keywords
        - Problem-solving search terms
        - Comparison search terms
        - Educational search terms
        
        Create compelling, conversion-focused selling points.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are a product marketing strategist focused on conversion optimization.",
            user_prompt=prompt,
            reasoning_context="Identifying unique selling points and value propositions"
        )
        
        return {
            "selling_points": response['response'],
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }

    async def process(self, input_data: Dict[Any, Any]) -> AgentResponse:
        """Market research agent'ının ana işlem süreci"""
        
        self._update_progress(5, "processing", "Starting market research analysis")
        
        all_reasoning = []
        market_data = {}
        
        try:
            # 1. Müşteri analizi
            self._update_progress(20, "processing", "Analyzing target customers")
            customer_result = await self.call_tool("analyze_target_audience", **input_data)
            market_data["customer_analysis"] = customer_result
            all_reasoning.extend(customer_result.get("reasoning", []))
            
            # 2. Pazar trendleri
            self._update_progress(40, "processing", "Researching market trends")
            trends_result = await self.call_tool("research_market_trends", **input_data)
            market_data["market_trends"] = trends_result
            all_reasoning.extend(trends_result.get("reasoning", []))
            
            # 3. Rekabet analizi
            self._update_progress(60, "processing", "Analyzing competitors")
            competitor_result = await self.call_tool("analyze_competitors", **input_data)
            market_data["competitor_analysis"] = competitor_result
            all_reasoning.extend(competitor_result.get("reasoning", []))
            
            # 4. Satış noktaları
            self._update_progress(80, "processing", "Identifying selling points")
            selling_result = await self.call_tool("identify_selling_points", **input_data)
            market_data["selling_points"] = selling_result
            all_reasoning.extend(selling_result.get("reasoning", []))
            
            # 5. Özet ve sentez
            self._update_progress(90, "processing", "Synthesizing market insights")
            
            # Confidence skorlarının ortalaması
            confidences = [
                customer_result.get("confidence", 70),
                trends_result.get("confidence", 70),
                competitor_result.get("confidence", 70),
                selling_result.get("confidence", 70)
            ]
            avg_confidence = sum(confidences) / len(confidences)
            
            # Market research özeti
            market_summary = {
                "research_completed": True,
                "analysis_areas": 4,
                "avg_confidence": avg_confidence,
                "key_insights": {
                    "customer_segments": "Target audience analyzed",
                    "market_opportunities": "Growth trends identified",
                    "competitive_gaps": "Market gaps discovered",
                    "unique_positioning": "Selling points defined"
                },
                "research_timestamp": datetime.now().isoformat()
            }
            
            market_data["market_research_summary"] = market_summary
            
            return AgentResponse(
                success=True,
                data=market_data,
                reasoning=all_reasoning,
                errors=[],
                processing_time=0.0,  # execute() metodunda hesaplanacak
                metadata={
                    "agent_name": self.config.name,
                    "confidence": avg_confidence,
                    "analysis_areas": 4,
                    "total_insights": len(all_reasoning)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Market research failed: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                reasoning=all_reasoning,
                errors=[str(e)],
                processing_time=0.0,
                metadata={
                    "agent_name": self.config.name,
                    "failure_reason": str(e)
                }
            )

# Test fonksiyonu
async def test_market_research():
    """Market Research Agent test fonksiyonu"""
    print("Testing Market Research Agent")
    print("=" * 50)
    
    # Gemini servisini başlat
    gemini = GeminiService()
    
    # Test input
    test_input = {
        "product_name": "Wireless Gaming Mouse",
        "niche": "gaming peripherals",
        "target_keywords": ["gaming mouse", "wireless mouse", "gaming gear"],
        "target_audience": "gamers, pc enthusiasts", 
        "budget": 1500,
        "competition_level": "high"
    }
    
    # Progress callback
    def progress_callback(agent_name, progress, status, current_step):
        print(f"[{agent_name}] {progress}% - {status}: {current_step}")
    
    # Agent'ı oluştur ve çalıştır
    agent = MarketResearchAgent(gemini)
    agent.set_progress_callback(progress_callback)
    
    result = await agent.execute(test_input)
    
    print("\nMarket Research Results:")
    print("-" * 30)
    print(f"Success: {result.success}")
    print(f"Data Keys: {list(result.data.keys())}")
    print(f"Reasoning Steps: {len(result.reasoning)}")
    print(f"Confidence: {result.metadata.get('confidence', 'N/A')}")
    print(f"Processing Time: {result.processing_time:.2f}s")
    
    if result.errors:
        print(f"Errors: {result.errors}")
    
    return result

if __name__ == "__main__":
    # Test çalıştır
    result = asyncio.run(test_market_research())
    print(f"\nTest completed!")