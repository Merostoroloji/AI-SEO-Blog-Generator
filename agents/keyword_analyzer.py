"""
Keyword Analyzer Agent - AI SEO Blog Generator

Bu agent keyword analizi ve optimizasyonu yapar:
- Primary/secondary keyword seçimi
- Keyword difficulty analysis
- Search intent classification
- Long-tail keyword discovery
- Content keyword mapping
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Python path fix
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse, ToolMixin
from services.gemini_service import GeminiService
from services.seo_tools import SEOToolsService, KeywordData


class KeywordAnalyzerAgent(BaseAgent, ToolMixin):
    """
    Keyword Analyzer Agent - İkinci pipeline agent'ı
    
    Görevleri:
    - Keyword research ve expansion
    - Keyword difficulty ve competition analysis
    - Search intent classification
    - Primary/secondary keyword seçimi
    - Content cluster mapping
    """
    
    def __init__(self, gemini_service: GeminiService, seo_tools: SEOToolsService):
        config = AgentConfig(
            name="keyword_analyzer",
            description="Analyzes keywords, search intent, and content opportunities",
            max_retries=3,
            timeout_seconds=180,  # Keyword research zaman alabilir
            temperature=0.5,  # Daha analitik yaklaşım
            reasoning_enabled=True
        )
        
        BaseAgent.__init__(self, config, gemini_service)
        ToolMixin.__init__(self)
        
        self.seo_tools = seo_tools
        
        # Keyword analysis araçları
        self._register_keyword_tools()
        
        self.logger.info("KeywordAnalyzerAgent initialized")
    
    def _register_keyword_tools(self):
        """Keyword analysis araçlarını kaydet"""
        self.available_tools.update({
            "research_seed_keywords": self._research_seed_keywords,
            "analyze_keyword_difficulty": self._analyze_keyword_difficulty,
            "classify_search_intent": self._classify_search_intent,
            "select_primary_keywords": self._select_primary_keywords,
            "expand_long_tail_keywords": self._expand_long_tail_keywords,
            "create_content_clusters": self._create_content_clusters
        })
    
    async def _research_seed_keywords(self, **kwargs) -> Dict[str, Any]:
        """Seed keyword research tool"""
        product_name = kwargs.get("product_name", "")
        niche = kwargs.get("niche", "")
        target_keywords = kwargs.get("target_keywords", [])
        target_audience = kwargs.get("target_audience", "")
        
        # Initial seed keywords oluştur
        seed_keywords = target_keywords.copy()
        
        # AI ile ek seed keywords üret
        prompt = f"""
        Generate comprehensive seed keywords for {product_name} in {niche} niche.
        
        Current keywords: {', '.join(target_keywords)}
        Target audience: {target_audience}
        
        Generate additional seed keywords considering:
        
        1. PRODUCT VARIATIONS:
        - Different product names and synonyms
        - Brand vs generic terms
        - Technical vs common terms
        
        2. USER INTENT KEYWORDS:
        - Informational: "what is", "how to", "guide"
        - Commercial: "best", "review", "comparison"
        - Transactional: "buy", "price", "deal"
        - Navigational: brand names, specific products
        
        3. PROBLEM-SOLUTION KEYWORDS:
        - Problems the product solves
        - Pain points of target audience
        - Solution-focused terms
        
        4. COMPETITOR KEYWORDS:
        - Competitor brand names
        - Alternative products
        - Category terms
        
        5. LONG-TAIL OPPORTUNITIES:
        - Specific use cases
        - Detailed specifications
        - Location-based terms
        
        Provide 30-50 additional seed keywords in a comma-separated list.
        Focus on high-potential keywords that target audience would actually search for.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are a keyword research specialist with deep understanding of search behavior.",
            user_prompt=prompt,
            reasoning_context="Generating comprehensive seed keywords for research"
        )
        
        # AI'dan gelen keyword'leri parse et
        ai_keywords = []
        try:
            # Response'dan keyword'leri extract et
            content = response['response']
            # Basit parsing - virgül ile ayrılmış keyword'leri bul
            for line in content.split('\n'):
                if ',' in line and not line.startswith('-') and not line.startswith('1.'):
                    keywords_in_line = [kw.strip().strip('"').strip("'") for kw in line.split(',')]
                    ai_keywords.extend([kw for kw in keywords_in_line if len(kw) > 2])
        except Exception as e:
            self.logger.warning(f"Failed to parse AI keywords: {e}")
        
        # Tüm seed keywords'leri birleştir
        all_seeds = list(set(seed_keywords + ai_keywords))
        
        # SEO Tools ile keyword research yap
        self.logger.info(f"Researching {len(all_seeds)} seed keywords")
        keyword_data = await self.seo_tools.research_keywords(all_seeds[:20])  # API limit nedeniyle 20'ye sınırla
        
        return {
            "seed_keywords": all_seeds,
            "ai_generated_keywords": ai_keywords,
            "keyword_research_data": [kw.to_dict() for kw in keyword_data],
            "total_keywords_found": len(keyword_data),
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }
    
    async def _analyze_keyword_difficulty(self, **kwargs) -> Dict[str, Any]:
        """Keyword difficulty analysis tool"""
        keyword_data = kwargs.get("keyword_research_data", [])
        
        if not keyword_data:
            return {"error": "No keyword data provided"}
        
        # Keyword'leri difficulty'ye göre kategorize et
        difficulty_categories = {
            "easy": [],      # 0-30 difficulty
            "medium": [],    # 31-60 difficulty  
            "hard": [],      # 61-80 difficulty
            "very_hard": []  # 81-100 difficulty
        }
        
        volume_categories = {
            "low": [],       # 0-1000 volume
            "medium": [],    # 1001-10000 volume
            "high": [],      # 10001-50000 volume
            "very_high": []  # 50000+ volume
        }
        
        for kw in keyword_data:
            difficulty = kw.get('difficulty', 50)
            volume = kw.get('search_volume', 0)
            
            # Difficulty categorization
            if difficulty <= 30:
                difficulty_categories["easy"].append(kw)
            elif difficulty <= 60:
                difficulty_categories["medium"].append(kw)
            elif difficulty <= 80:
                difficulty_categories["hard"].append(kw)
            else:
                difficulty_categories["very_hard"].append(kw)
            
            # Volume categorization  
            if volume <= 1000:
                volume_categories["low"].append(kw)
            elif volume <= 10000:
                volume_categories["medium"].append(kw)
            elif volume <= 50000:
                volume_categories["high"].append(kw)
            else:
                volume_categories["very_high"].append(kw)
        
        # AI ile difficulty analysis ve recommendations
        prompt = f"""
        Analyze keyword difficulty data and provide strategic recommendations.
        
        Keyword Categories by Difficulty:
        - Easy (0-30): {len(difficulty_categories['easy'])} keywords
        - Medium (31-60): {len(difficulty_categories['medium'])} keywords  
        - Hard (61-80): {len(difficulty_categories['hard'])} keywords
        - Very Hard (81-100): {len(difficulty_categories['very_hard'])} keywords
        
        Keyword Categories by Volume:
        - Low (0-1K): {len(volume_categories['low'])} keywords
        - Medium (1K-10K): {len(volume_categories['medium'])} keywords
        - High (10K-50K): {len(volume_categories['high'])} keywords
        - Very High (50K+): {len(volume_categories['very_high'])} keywords
        
        Provide analysis and recommendations for:
        
        1. QUICK WIN OPPORTUNITIES:
        - High volume + low difficulty keywords
        - Content opportunities with fast ranking potential
        
        2. CONTENT STRATEGY RECOMMENDATIONS:
        - Which difficulty levels to target first
        - Content format recommendations for each category
        - Prioritization framework
        
        3. LONG-TERM STRATEGY:
        - Hard keywords to target later
        - Authority building approach
        - Competition analysis
        
        4. CONTENT CALENDAR SUGGESTIONS:
        - Easy keywords for immediate content
        - Medium keywords for ongoing strategy
        - Hard keywords for future authority building
        
        Focus on actionable, data-driven recommendations.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are a SEO strategist specializing in keyword difficulty analysis.",
            user_prompt=prompt,
            reasoning_context="Analyzing keyword difficulty patterns and opportunities"
        )
        
        return {
            "difficulty_analysis": {
                "categories": difficulty_categories,
                "volume_categories": volume_categories,
                "total_keywords": len(keyword_data),
                "analysis": response['response']
            },
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }
    
    async def _classify_search_intent(self, **kwargs) -> Dict[str, Any]:
        """Search intent classification tool"""
        keyword_data = kwargs.get("keyword_research_data", [])
        
        if not keyword_data:
            return {"error": "No keyword data provided"}
        
        # Intent categories
        intent_categories = {
            "informational": [],  # "how to", "what is", "guide"
            "commercial": [],     # "best", "review", "comparison"  
            "transactional": [],  # "buy", "price", "cheap"
            "navigational": []    # brand names, specific products
        }
        
        # Intent classification patterns
        informational_patterns = ["how to", "what is", "why", "guide", "tutorial", "learn", "explain", "definition"]
        commercial_patterns = ["best", "review", "comparison", "vs", "top", "compare", "rating", "recommendation"]
        transactional_patterns = ["buy", "price", "cost", "cheap", "deal", "discount", "order", "purchase", "shop"]
        navigational_patterns = ["brand", "official", "website", "login", "download"]
        
        # Classify keywords
        for kw in keyword_data:
            keyword = kw.get('keyword', '').lower()
            classified = False
            
            # Check informational intent
            for pattern in informational_patterns:
                if pattern in keyword:
                    intent_categories["informational"].append(kw)
                    classified = True
                    break
            
            if not classified:
                # Check commercial intent
                for pattern in commercial_patterns:
                    if pattern in keyword:
                        intent_categories["commercial"].append(kw)
                        classified = True
                        break
            
            if not classified:
                # Check transactional intent
                for pattern in transactional_patterns:
                    if pattern in keyword:
                        intent_categories["transactional"].append(kw)
                        classified = True
                        break
            
            if not classified:
                # Check navigational intent
                for pattern in navigational_patterns:
                    if pattern in keyword:
                        intent_categories["navigational"].append(kw)
                        classified = True
                        break
            
            # Default to informational if no clear pattern
            if not classified:
                intent_categories["informational"].append(kw)
        
        # AI ile intent analysis
        prompt = f"""
        Analyze search intent distribution and provide content strategy recommendations.
        
        Search Intent Distribution:
        - Informational: {len(intent_categories['informational'])} keywords ({len(intent_categories['informational'])/len(keyword_data)*100:.1f}%)
        - Commercial: {len(intent_categories['commercial'])} keywords ({len(intent_categories['commercial'])/len(keyword_data)*100:.1f}%)
        - Transactional: {len(intent_categories['transactional'])} keywords ({len(intent_categories['transactional'])/len(keyword_data)*100:.1f}%)
        - Navigational: {len(intent_categories['navigational'])} keywords ({len(intent_categories['navigational'])/len(keyword_data)*100:.1f}%)
        
        Sample keywords by intent:
        Informational: {[kw.get('keyword') for kw in intent_categories['informational'][:5]]}
        Commercial: {[kw.get('keyword') for kw in intent_categories['commercial'][:5]]}
        Transactional: {[kw.get('keyword') for kw in intent_categories['transactional'][:5]]}
        
        Provide recommendations for:
        
        1. CONTENT FUNNEL STRATEGY:
        - Top of funnel content (informational keywords)
        - Middle of funnel content (commercial keywords)
        - Bottom of funnel content (transactional keywords)
        
        2. CONTENT TYPES BY INTENT:
        - Best content formats for each intent type
        - Blog post structures and approaches
        - CTA strategies for each intent
        
        3. KEYWORD PRIORITIZATION:
        - Which intent types to focus on first
        - Balance recommendations across the funnel
        - Conversion potential analysis
        
        4. CONTENT CALENDAR INTEGRATION:
        - How to sequence content by intent
        - Supporting content recommendations
        - Internal linking strategies
        
        Focus on creating a cohesive content strategy that addresses all search intents.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are a content strategist specializing in search intent optimization.",
            user_prompt=prompt,
            reasoning_context="Analyzing search intent patterns for content strategy"
        )
        
        return {
            "intent_analysis": {
                "categories": intent_categories,
                "distribution": {
                    "informational": len(intent_categories['informational']),
                    "commercial": len(intent_categories['commercial']),
                    "transactional": len(intent_categories['transactional']),
                    "navigational": len(intent_categories['navigational'])
                },
                "strategy": response['response']
            },
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }
    
    async def _select_primary_keywords(self, **kwargs) -> Dict[str, Any]:
        """Primary keyword selection tool"""
        keyword_data = kwargs.get("keyword_research_data", [])
        difficulty_analysis = kwargs.get("difficulty_analysis", {})
        intent_analysis = kwargs.get("intent_analysis", {})
        
        if not keyword_data:
            return {"error": "No keyword data provided"}
        
        # Keyword scoring algorithm
        scored_keywords = []
        
        for kw in keyword_data:
            keyword = kw.get('keyword', '')
            volume = kw.get('search_volume', 0)
            difficulty = kw.get('difficulty', 50)
            cpc = kw.get('cpc', 0)
            
            # Calculate composite score
            # Volume score (0-40 points)
            if volume >= 10000:
                volume_score = 40
            elif volume >= 5000:
                volume_score = 30
            elif volume >= 1000:
                volume_score = 20
            elif volume >= 500:
                volume_score = 10
            else:
                volume_score = 5
            
            # Difficulty score (0-30 points) - lower difficulty = higher score
            if difficulty <= 20:
                difficulty_score = 30
            elif difficulty <= 40:
                difficulty_score = 20
            elif difficulty <= 60:
                difficulty_score = 10
            elif difficulty <= 80:
                difficulty_score = 5
            else:
                difficulty_score = 0
            
            # Commercial value score (0-20 points)
            if cpc >= 5.0:
                commercial_score = 20
            elif cpc >= 2.0:
                commercial_score = 15
            elif cpc >= 1.0:
                commercial_score = 10
            elif cpc >= 0.5:
                commercial_score = 5
            else:
                commercial_score = 0
            
            # Keyword length bonus (0-10 points) - long tail bonus
            word_count = len(keyword.split())
            if word_count >= 4:
                length_score = 10
            elif word_count == 3:
                length_score = 5
            else:
                length_score = 0
            
            total_score = volume_score + difficulty_score + commercial_score + length_score
            
            scored_keywords.append({
                **kw,
                'composite_score': total_score,
                'volume_score': volume_score,
                'difficulty_score': difficulty_score,
                'commercial_score': commercial_score,
                'length_score': length_score
            })
        
        # Sort by composite score
        scored_keywords.sort(key=lambda x: x['composite_score'], reverse=True)
        
        # Select primary keywords (top 10-15)
        primary_keywords = scored_keywords[:15]
        secondary_keywords = scored_keywords[15:30]
        long_tail_keywords = [kw for kw in scored_keywords if len(kw['keyword'].split()) >= 4][:20]
        
        # AI ile primary keyword selection analysis
        primary_kw_list = [kw['keyword'] for kw in primary_keywords]
        prompt = f"""
        Analyze the selected primary keywords and provide strategic recommendations.
        
        Top Primary Keywords (by composite score):
        {json.dumps(primary_kw_list, indent=2)}
        
        Scoring Details for Top 5:
        {json.dumps([{
            'keyword': kw['keyword'],
            'volume': kw['search_volume'],
            'difficulty': kw['difficulty'], 
            'score': kw['composite_score']
        } for kw in primary_keywords[:5]], indent=2)}
        
        Provide analysis for:
        
        1. PRIMARY KEYWORD STRATEGY:
        - Content pillar recommendations
        - Which keywords to target in hero content
        - Keyword clustering opportunities
        
        2. CONTENT PRIORITY RANKING:
        - Which keywords to create content for first
        - Content format recommendations for each
        - Expected traffic potential
        
        3. COMPETITION ANALYSIS:
        - Realistic ranking timeframes
        - Content quality requirements
        - Resource allocation recommendations
        
        4. INTERNAL LINKING STRATEGY:
        - How to connect primary keywords
        - Supporting content recommendations
        - Topic cluster architecture
        
        5. MEASUREMENT & TRACKING:
        - Key metrics to track for each keyword
        - Success benchmarks
        - Timeline expectations
        
        Focus on actionable insights for content creation and SEO strategy.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are a SEO content strategist specializing in keyword prioritization.",
            user_prompt=prompt,
            reasoning_context="Analyzing primary keyword selection and strategy"
        )
        
        return {
            "keyword_selection": {
                "primary_keywords": primary_keywords,
                "secondary_keywords": secondary_keywords,
                "long_tail_keywords": long_tail_keywords,
                "total_analyzed": len(scored_keywords),
                "strategy": response['response']
            },
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }
    
    async def _expand_long_tail_keywords(self, **kwargs) -> Dict[str, Any]:
        """Long-tail keyword expansion tool"""
        primary_keywords = kwargs.get("primary_keywords", [])
        product_name = kwargs.get("product_name", "")
        target_audience = kwargs.get("target_audience", "")
        
        if not primary_keywords:
            return {"error": "No primary keywords provided"}
        
        # AI ile long-tail expansion
        primary_kw_list = [kw.get('keyword', kw) if isinstance(kw, dict) else kw for kw in primary_keywords[:10]]
        
        prompt = f"""
        Generate comprehensive long-tail keyword variations for {product_name}.
        
        Primary Keywords: {', '.join(primary_kw_list)}
        Target Audience: {target_audience}
        
        Create long-tail variations using these strategies:
        
        1. QUESTION-BASED LONG-TAILS:
        - "How to choose [keyword]"
        - "What is the best [keyword]" 
        - "Why [keyword] is important"
        - "When to use [keyword]"
        
        2. PROBLEM-SOLUTION LONG-TAILS:
        - "[keyword] for [specific problem]"
        - "Best [keyword] for [use case]"
        - "[keyword] that [solves problem]"
        
        3. COMPARISON LONG-TAILS:
        - "[keyword] vs [alternative]"
        - "[keyword] compared to [competitor]"
        - "Difference between [keyword] and [alternative]"
        
        4. FEATURE-SPECIFIC LONG-TAILS:
        - "[keyword] with [feature]"
        - "[feature] [keyword]"
        - "[keyword] for [specific need]"
        
        5. AUDIENCE-SPECIFIC LONG-TAILS:
        - "[keyword] for beginners"
        - "Professional [keyword]"
        - "[keyword] for [specific audience segment]"
        
        6. LOCATION-BASED LONG-TAILS:
        - "[keyword] in [location]"
        - "Local [keyword]"
        - "[keyword] near me"
        
        Generate 50-80 long-tail keyword variations.
        Focus on keywords with 3-6 words that have clear search intent.
        Prioritize keywords your target audience would actually search for.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are a long-tail keyword specialist with expertise in search behavior patterns.",
            user_prompt=prompt,
            reasoning_context="Expanding primary keywords into long-tail opportunities"
        )
        
        # Parse long-tail keywords from response
        long_tail_keywords = []
        try:
            content = response['response']
            for line in content.split('\n'):
                line = line.strip()
                if line and ('"' in line or len(line.split()) >= 3):
                    # Extract keywords from quotes or long phrases
                    if '"' in line:
                        import re
                        quotes = re.findall(r'"([^"]*)"', line)
                        long_tail_keywords.extend(quotes)
                    elif len(line.split()) >= 3 and not line.startswith(('1.', '2.', '3.', '-', '*')):
                        long_tail_keywords.append(line)
        except Exception as e:
            self.logger.warning(f"Failed to parse long-tail keywords: {e}")
        
        # Remove duplicates and filter
        long_tail_keywords = list(set([kw.strip().lower() for kw in long_tail_keywords if len(kw.strip()) > 10]))
        
        return {
            "long_tail_expansion": {
                "expanded_keywords": long_tail_keywords,
                "total_generated": len(long_tail_keywords),
                "primary_keywords_used": primary_kw_list,
                "expansion_strategy": response['response']
            },
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }
    
    async def _create_content_clusters(self, **kwargs) -> Dict[str, Any]:
        """Content cluster creation tool"""
        primary_keywords = kwargs.get("primary_keywords", [])
        long_tail_keywords = kwargs.get("long_tail_keywords", [])
        intent_analysis = kwargs.get("intent_analysis", {})
        
        # AI ile content cluster strategy
        primary_kw_list = [kw.get('keyword', kw) if isinstance(kw, dict) else kw for kw in primary_keywords[:10]]
        long_tail_sample = long_tail_keywords[:20] if isinstance(long_tail_keywords, list) else []
        
        prompt = f"""
        Create a comprehensive content cluster strategy for SEO optimization.
        
        Primary Keywords: {', '.join(primary_kw_list)}
        Sample Long-tail Keywords: {', '.join(long_tail_sample)}
        
        Design content clusters using this framework:
        
        1. PILLAR CONTENT STRATEGY:
        - Identify 3-5 main content pillars
        - Map primary keywords to pillars
        - Define pillar page topics and structure
        
        2. CLUSTER CONTENT MAPPING:
        - Group related keywords into clusters
        - Identify supporting content opportunities
        - Plan internal linking structure
        
        3. CONTENT TYPES PER CLUSTER:
        - Hero/pillar pages (comprehensive guides)
        - Supporting blog posts
        - FAQ pages
        - Comparison pages
        - How-to tutorials
        
        4. CONTENT CALENDAR INTEGRATION:
        - Publishing sequence recommendations
        - Content dependencies and prerequisites
        - Seasonal or trending opportunities
        
        5. INTERNAL LINKING STRATEGY:
        - Hub and spoke architecture
        - Anchor text optimization
        - Link equity distribution
        
        6. CONTENT CLUSTER EXAMPLES:
        For each main cluster, provide:
        - Pillar page topic and outline
        - 5-8 supporting content ideas
        - Target keywords for each piece
        - Content format recommendations
        
        Create a actionable content cluster plan that maximizes SEO impact.
        """
        
        response = await self._call_gemini_with_reasoning(
            system_prompt="You are a content architect specializing in SEO content cluster strategies.",
            user_prompt=prompt,
            reasoning_context="Creating content cluster architecture for maximum SEO impact"
        )
        
        return {
            "content_clusters": {
                "cluster_strategy": response['response'],
                "primary_keywords_used": primary_kw_list,
                "supporting_keywords": long_tail_sample,
                "cluster_count": "3-5 main clusters recommended"
            },
            "reasoning": response['reasoning_steps'],
            "confidence": response['confidence']
        }
    
    async def process(self, input_data: Dict[Any, Any]) -> AgentResponse:
        """Keyword Analyzer Agent ana işlem süreci"""
        
        self._update_progress(5, "processing", "Starting keyword analysis")
        
        all_reasoning = []
        keyword_analysis_data = {}
        
        try:
            # 1. Seed keyword research
            self._update_progress(15, "processing", "Researching seed keywords")
            seed_result = await self.call_tool("research_seed_keywords", **input_data)
            keyword_analysis_data["seed_research"] = seed_result
            all_reasoning.extend(seed_result.get("reasoning", []))
            
            # 2. Keyword difficulty analysis
            self._update_progress(30, "processing", "Analyzing keyword difficulty")
            difficulty_result = await self.call_tool("analyze_keyword_difficulty", 
                                                   keyword_research_data=seed_result.get("keyword_research_data", []))
            keyword_analysis_data["difficulty_analysis"] = difficulty_result
            all_reasoning.extend(difficulty_result.get("reasoning", []))
            
            # 3. Search intent classification
            self._update_progress(45, "processing", "Classifying search intent")
            intent_result = await self.call_tool("classify_search_intent",
                                               keyword_research_data=seed_result.get("keyword_research_data", []))
            keyword_analysis_data["intent_analysis"] = intent_result
            all_reasoning.extend(intent_result.get("reasoning", []))
            
            # 4. Primary keyword selection
            self._update_progress(60, "processing", "Selecting primary keywords")
            primary_result = await self.call_tool("select_primary_keywords",
                                                 keyword_research_data=seed_result.get("keyword_research_data", []),
                                                 difficulty_analysis=difficulty_result.get("difficulty_analysis", {}),
                                                 intent_analysis=intent_result.get("intent_analysis", {}))
            keyword_analysis_data["primary_selection"] = primary_result
            all_reasoning.extend(primary_result.get("reasoning", []))
            
            # 5. Long-tail keyword expansion
            self._update_progress(75, "processing", "Expanding long-tail keywords")
            long_tail_result = await self.call_tool("expand_long_tail_keywords",
                                                   primary_keywords=primary_result.get("keyword_selection", {}).get("primary_keywords", []),
                                                   **input_data)
            keyword_analysis_data["long_tail_expansion"] = long_tail_result
            all_reasoning.extend(long_tail_result.get("reasoning", []))
            
            # 6. Content cluster creation
            self._update_progress(90, "processing", "Creating content clusters")
            cluster_result = await self.call_tool("create_content_clusters",
                                                 primary_keywords=primary_result.get("keyword_selection", {}).get("primary_keywords", []),
                                                 long_tail_keywords=long_tail_result.get("long_tail_expansion", {}).get("expanded_keywords", []),
                                                 intent_analysis=intent_result.get("intent_analysis", {}))
            keyword_analysis_data["content_clusters"] = cluster_result
            all_reasoning.extend(cluster_result.get("reasoning", []))
            
            # 7. Analysis summary
            self._update_progress(95, "processing", "Finalizing keyword analysis")
            
            # Confidence skorlarının ortalaması
            confidences = [
                seed_result.get("confidence", 80),
                difficulty_result.get("confidence", 80),
                intent_result.get("confidence", 80),
                primary_result.get("confidence", 80),
                long_tail_result.get("confidence", 80),
                cluster_result.get("confidence", 80)
            ]
            avg_confidence = sum(confidences) / len(confidences)
            
            # Summary
            summary = {
                "analysis_completed": True,
                "total_keywords_analyzed": len(seed_result.get("keyword_research_data", [])),
                "primary_keywords_selected": len(primary_result.get("keyword_selection", {}).get("primary_keywords", [])),
                "long_tail_keywords_generated": len(long_tail_result.get("long_tail_expansion", {}).get("expanded_keywords", [])),
                "avg_confidence": avg_confidence,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            keyword_analysis_data["analysis_summary"] = summary
            
            return AgentResponse(
                success=True,
                data=keyword_analysis_data,
                reasoning=all_reasoning,
                errors=[],
                processing_time=0.0,
                metadata={
                    "agent_name": self.config.name,
                    "confidence": avg_confidence,
                    "total_keywords": summary["total_keywords_analyzed"],
                    "analysis_stages": 6
                }
            )
            
        except Exception as e:
            self.logger.error(f"Keyword analysis failed: {str(e)}")
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


# Test function
async def test_keyword_analyzer():
    """Keyword Analyzer Agent test function"""
    print("Testing Keyword Analyzer Agent")
    print("=" * 50)
    
    # Services
    from services.gemini_service import GeminiService
    from services.seo_tools import SEOToolsService
    
    gemini = GeminiService()
    seo_tools = SEOToolsService()
    
    # Test input
    test_input = {
        "product_name": "Wireless Gaming Headset",
        "niche": "gaming accessories",
        "target_keywords": ["gaming headset", "wireless headset", "gaming audio"],
        "target_audience": "pc gamers, console gamers",
        "budget": 2000
    }
    
    # Progress callback
    def progress_callback(agent_name, progress, status, current_step):
        print(f"[{agent_name}] {progress}% - {status}: {current_step}")
    
    # Test agent
    agent = KeywordAnalyzerAgent(gemini, seo_tools)
    agent.set_progress_callback(progress_callback)
    
    result = await agent.execute(test_input)
    
    print("\nKeyword Analysis Results:")
    print("-" * 30)
    print(f"Success: {result.success}")
    print(f"Data Keys: {list(result.data.keys())}")
    print(f"Total Keywords Analyzed: {result.metadata.get('total_keywords', 'N/A')}")
    print(f"Confidence: {result.metadata.get('confidence', 'N/A')}")
    print(f"Processing Time: {result.processing_time:.2f}s")
    
    if result.errors:
        print(f"Errors: {result.errors}")
    
    # Show sample results
    if result.success and result.data:
        summary = result.data.get("analysis_summary", {})
        print(f"\nAnalysis Summary:")
        print(f"- Primary Keywords: {summary.get('primary_keywords_selected', 0)}")
        print(f"- Long-tail Keywords: {summary.get('long_tail_keywords_generated', 0)}")
        print(f"- Average Confidence: {summary.get('avg_confidence', 0):.1f}%")
    
    return result


if __name__ == "__main__":
    # Test çalıştır
    result = asyncio.run(test_keyword_analyzer())
    print(f"\nKeyword Analyzer test completed!")