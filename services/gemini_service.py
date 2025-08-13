"""
Google AI Studio (Gemini) Integration Service
Handles all AI model interactions for the SEO blog generator
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
load_dotenv()
logger = logging.getLogger(__name__)


class GeminiService:
    """
    Google AI Studio (Gemini) service for AI content generation
    Handles chain of thought reasoning and tool integration
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize models
        self.model_name = os.getenv('GOOGLE_AI_MODEL', 'gemini-pro')
        self.model = genai.GenerativeModel(self.model_name)
        
        # Safety settings for commercial content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Generation config
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.8,
            top_k=40,
            max_output_tokens=8192,
        )
        
        # Rate limiting
        self.last_request_time = None
        self.min_request_interval = 4.0  # 15 requests per minute (free tier)
        
        logger.info(f"GeminiService initialized with model: {self.model_name}")

    async def _rate_limit(self):
        """Implement rate limiting for Gemini API free tier"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.min_request_interval:
                sleep_time = self.min_request_interval - elapsed
                logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
        
        self.last_request_time = datetime.now()

    async def generate_content(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        Generate content using Gemini with context awareness
        
        Args:
            prompt: The main prompt for content generation
            context: Additional context data (keywords, market research, etc.)
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum response length
            
        Returns:
            Generated content as string
        """
        await self._rate_limit()
        
        try:
            # Build enhanced prompt with context
            enhanced_prompt = self._build_enhanced_prompt(prompt, context)
            
            # Configure generation for this request
            config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.8,
                top_k=40,
            )
            
            # Generate content
            response = await asyncio.to_thread(
                self.model.generate_content,
                enhanced_prompt,
                generation_config=config,
                safety_settings=self.safety_settings
            )
            
            if response.candidates and response.candidates[0].content:
                content = response.candidates[0].content.parts[0].text
                logger.info(f"Generated content: {len(content)} characters")
                return content.strip()
            else:
                logger.error("No content generated or content blocked by safety filters")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise

    async def chain_of_thought_reasoning(
        self, 
        task: str, 
        context: Dict[str, Any],
        reasoning_steps: List[str]
    ) -> Dict[str, Any]:
        """
        Implement chain of thought reasoning for complex tasks
        
        Args:
            task: The main task to accomplish
            context: Available context and data
            reasoning_steps: List of reasoning steps to follow
            
        Returns:
            Structured reasoning result with steps and final answer
        """
        await self._rate_limit()
        
        reasoning_prompt = f"""
You are an expert AI agent working on: {task}

Context available:
{json.dumps(context, indent=2)}

Please follow this chain of thought reasoning process:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(reasoning_steps))}

For each step, provide:
1. Your analysis
2. Key insights
3. Data or evidence supporting your conclusion
4. How it connects to the next step

Format your response as JSON with this structure:
{{
    "reasoning_steps": [
        {{
            "step_number": 1,
            "step_description": "...",
            "analysis": "...",
            "insights": ["..."],
            "evidence": "...",
            "confidence_score": 0.85
        }}
    ],
    "final_conclusion": "...",
    "confidence_score": 0.90,
    "recommendations": ["..."]
}}
"""
        
        try:
            response = await self.generate_content(
                reasoning_prompt, 
                context,
                temperature=0.3,  # Lower temperature for reasoning
                max_tokens=6000
            )
            
            # Parse JSON response
            reasoning_result = json.loads(response)
            logger.info(f"Chain of thought completed with {len(reasoning_result.get('reasoning_steps', []))} steps")
            return reasoning_result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse chain of thought response as JSON")
            return {
                "reasoning_steps": [],
                "final_conclusion": response,
                "confidence_score": 0.5,
                "recommendations": []
            }
        except Exception as e:
            logger.error(f"Error in chain of thought reasoning: {str(e)}")
            raise

    async def analyze_market_research(self, niche: str, target_audience: str) -> Dict[str, Any]:
        """Market Research Agent functionality"""
        prompt = f"""
Analyze the market for {niche} targeting {target_audience}.

Provide comprehensive market research including:
1. Target audience demographics and psychographics
2. Market size and growth trends
3. Key competitors and their content strategies
4. Content gaps and opportunities
5. Seasonal trends and timing
6. Customer pain points and motivations
7. Effective sales angles and messaging

Return as JSON with detailed analysis.
"""
        
        context = {"niche": niche, "target_audience": target_audience}
        
        reasoning_steps = [
            "Analyze target audience characteristics",
            "Research market size and trends",
            "Identify key competitors",
            "Find content gaps and opportunities",
            "Determine optimal sales angles"
        ]
        
        return await self.chain_of_thought_reasoning(
            f"Market research for {niche}",
            context,
            reasoning_steps
        )

    async def analyze_keywords(self, niche: str, seed_keywords: List[str]) -> Dict[str, Any]:
        """SEO Keywords Agent functionality"""
        prompt = f"""
Perform keyword analysis for {niche} using these seed keywords: {', '.join(seed_keywords)}

Provide:
1. Primary keywords (high volume, medium competition)
2. Long-tail keywords (specific, low competition)
3. LSI (Latent Semantic Indexing) keywords
4. Commercial intent keywords
5. Question-based keywords for FAQ sections
6. Seasonal keyword opportunities
7. Competitor keyword gaps

For each keyword, estimate:
- Search volume category (high/medium/low)
- Competition level (high/medium/low)
- Commercial intent (high/medium/low)
- Content fit score (how well it fits the niche)

Return as JSON with structured keyword data.
"""
        
        context = {
            "niche": niche,
            "seed_keywords": seed_keywords
        }
        
        reasoning_steps = [
            "Analyze seed keywords for expansion opportunities",
            "Research commercial intent and search behavior",
            "Identify long-tail and LSI keyword variations",
            "Evaluate competition levels and ranking difficulty",
            "Prioritize keywords by value and fit"
        ]
        
        return await self.chain_of_thought_reasoning(
            f"Keyword analysis for {niche}",
            context,
            reasoning_steps
        )

    async def create_content_structure(
        self, 
        target_keywords: List[str], 
        market_research: Dict[str, Any],
        word_count_target: int = 2000
    ) -> Dict[str, Any]:
        """Content Structure Agent functionality"""
        prompt = f"""
Create a comprehensive article structure for target keywords: {', '.join(target_keywords)}

Based on market research insights:
{json.dumps(market_research, indent=2)}

Target word count: {word_count_target} words

Create:
1. SEO-optimized title variations
2. Meta description (155 characters max)
3. Detailed heading structure (H1, H2, H3, H4)
4. Content sections with word count distribution
5. CTA placement recommendations
6. Internal linking opportunities
7. Image placement suggestions
8. FAQ section with 2 relevant questions
9. Schema markup recommendations

Ensure the structure follows E-commerce content best practices and conversion optimization.

Return as JSON with complete structure.
"""
        
        context = {
            "target_keywords": target_keywords,
            "market_research": market_research,
            "word_count_target": word_count_target
        }
        
        reasoning_steps = [
            "Analyze target keywords for content themes",
            "Structure content for user journey and conversions",
            "Plan heading hierarchy for SEO and readability",
            "Determine optimal CTA and image placement",
            "Create FAQ section addressing user concerns"
        ]
        
        return await self.chain_of_thought_reasoning(
            f"Content structure for {', '.join(target_keywords)}",
            context,
            reasoning_steps
        )

    async def write_content(
        self,
        content_structure: Dict[str, Any],
        target_keywords: List[str],
        market_research: Dict[str, Any],
        tone: str = "professional_friendly"
    ) -> Dict[str, Any]:
        """Content Writer Agent functionality"""
        prompt = f"""
Write a comprehensive, SEO-optimized article based on this structure:
{json.dumps(content_structure, indent=2)}

Target keywords: {', '.join(target_keywords)}
Market research: {json.dumps(market_research, indent=2)}
Tone: {tone}

Requirements:
1. Engaging, conversion-focused writing
2. Natural keyword integration (avoid keyword stuffing)
3. E-commerce and product promotion focus
4. Include credible statistics and data where relevant
5. Add compelling CTAs at strategic points
6. Write in a way that builds trust and authority
7. Include comparison tables or bullet points where appropriate
8. Address customer objections and concerns
9. Optimize for featured snippets
10. Include 2 FAQ questions with detailed answers

Write the complete article following the provided structure exactly.
Use markdown formatting for headers and emphasis.

Return as JSON with:
- full_content: Complete article text
- meta_description: SEO meta description
- title: Final optimized title
- word_count: Actual word count
- keyword_density: Estimated density for target keywords
- readability_score: Estimated readability level
"""
        
        context = {
            "content_structure": content_structure,
            "target_keywords": target_keywords,
            "market_research": market_research,
            "tone": tone
        }
        
        reasoning_steps = [
            "Analyze content structure and requirements",
            "Plan content flow for engagement and conversions",
            "Write compelling introduction with hook",
            "Develop main content sections with expertise",
            "Create strong conclusions with clear CTAs",
            "Add FAQ section addressing user concerns"
        ]
        
        return await self.chain_of_thought_reasoning(
            f"Content writing for {', '.join(target_keywords)}",
            context,
            reasoning_steps
        )

    def _build_enhanced_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build enhanced prompt with context and instructions"""
        enhanced_prompt = f"""
You are an expert AI agent specializing in SEO-optimized content creation for e-commerce and product promotion.

Current task: {prompt}

"""
        
        if context:
            enhanced_prompt += f"""
Available context:
{json.dumps(context, indent=2)}

"""
        
        enhanced_prompt += """
Guidelines:
- Focus on e-commerce and product promotion content
- Prioritize SEO best practices and user experience
- Ensure content is engaging, trustworthy, and conversion-focused
- Use data-driven insights when available
- Follow Google's E-A-T (Expertise, Authoritativeness, Trustworthiness) guidelines
- Optimize for both search engines and human readers

Please provide detailed, actionable, and high-quality output.
"""
        
        return enhanced_prompt

    async def health_check(self) -> Dict[str, Any]:
        """Check if Gemini service is working properly"""
        try:
            test_response = await self.generate_content(
                "Say 'Gemini service is working correctly' if you can respond.",
                temperature=0.1,
                max_tokens=50
            )
            
            return {
                "status": "healthy",
                "model": self.model_name,
                "response": test_response,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "model": self.model_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Global service instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create global Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service


# Usage example and testing
if __name__ == "__main__":
    async def test_gemini_service():
        """Test the Gemini service functionality"""
        service = get_gemini_service()
        
        # Test health check
        health = await service.health_check()
        print("Health check:", health)
        
        # Test market research
        market_research = await service.analyze_market_research(
            niche="wireless earbuds",
            target_audience="fitness enthusiasts"
        )
        print("Market research completed")
        
        # Test keyword analysis
        keywords = await service.analyze_keywords(
            niche="wireless earbuds",
            seed_keywords=["wireless earbuds", "bluetooth headphones", "sports earbuds"]
        )
        print("Keyword analysis completed")
    
    # Run tests
    asyncio.run(test_gemini_service())