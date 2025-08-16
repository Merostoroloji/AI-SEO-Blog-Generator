"""
SEO Tools Service - AI SEO Blog Generator

Bu service SEO araçları ve API'lerini yönetir:
- Keyword research (SEMrush, Ahrefs, Google Keyword Planner)
- Competitor analysis 
- SERP analysis
- Content optimization tools
- SEO metrics tracking
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Import free SEO tools
try:
    from services.free_seo_tools import FreeSEOToolsService, HybridSEOService
    FREE_TOOLS_AVAILABLE = True
except ImportError:
    FREE_TOOLS_AVAILABLE = False
    print("⚠️ free_seo_tools.py not found in services/")

@dataclass
class KeywordData:
    """Keyword bilgi yapısı"""
    keyword: str
    search_volume: int
    difficulty: float
    cpc: float
    competition: str
    trend: List[int]
    related_keywords: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'keyword': self.keyword,
            'search_volume': self.search_volume,
            'difficulty': self.difficulty,
            'cpc': self.cpc,
            'competition': self.competition,
            'trend': self.trend,
            'related_keywords': self.related_keywords
        }


@dataclass
class CompetitorData:
    """Competitor analiz yapısı"""
    domain: str
    authority_score: float
    organic_keywords: int
    organic_traffic: int
    top_keywords: List[str]
    content_gaps: List[str]
    backlink_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'domain': self.domain,
            'authority_score': self.authority_score,
            'organic_keywords': self.organic_keywords,
            'organic_traffic': self.organic_traffic,
            'top_keywords': self.top_keywords,
            'content_gaps': self.content_gaps,
            'backlink_count': self.backlink_count
        }


class SEOToolsService:
    """
    SEO Tools Service
    
    Çeşitli SEO API'lerini entegre eder ve ortak interface sağlar
    """
    
    def __init__(self):
        self.logger = logging.getLogger("SEOToolsService")
        
        # API keys (environment variables'dan alınacak)
        self.semrush_api_key = os.getenv('SEMRUSH_API_KEY')
        self.ahrefs_api_key = os.getenv('AHREFS_API_KEY')
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        
        # Debug için API key kontrolü
        if self.serpapi_key:
            self.logger.info(f"SERPAPI_KEY loaded: {self.serpapi_key[:10]}...")
        else:
            self.logger.warning("SERPAPI_KEY not found in environment variables")
        
        # Free tools integration
        if FREE_TOOLS_AVAILABLE:
            self.free_service = FreeSEOToolsService()
            self.hybrid_service = HybridSEOService()
            self.logger.info("Free SEO Tools integrated successfully")
        else:
            self.free_service = None
            self.hybrid_service = None
            self.logger.warning("Free SEO Tools not available")
        
        # Rate limiting
        self.rate_limits = {
            'semrush': {'calls': 0, 'reset_time': datetime.now()},
            'ahrefs': {'calls': 0, 'reset_time': datetime.now()},
            'serpapi': {'calls': 0, 'reset_time': datetime.now()}
        }
        
        # Mock mode for development
        self.mock_mode = not any([self.semrush_api_key, self.ahrefs_api_key, self.serpapi_key])
        
        # Use free tools flag
        self.use_free_tools = FREE_TOOLS_AVAILABLE  # Otomatik olarak free tools kullan
        
        if self.mock_mode and not self.use_free_tools:
            self.logger.warning("SEO Tools running in MOCK MODE - no real API keys found")
        
        self.logger.info("SEO Tools Service initialized")

    async def _make_api_request(self, url: str, params: Dict[str, Any] = None, 
                               headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Generic API request handler"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"API request failed: {response.status} - {await response.text()}")
                        return {"error": f"API request failed with status {response.status}"}
        
        except asyncio.TimeoutError:
            self.logger.error("API request timed out")
            return {"error": "Request timed out"}
        
        except Exception as e:
            self.logger.error(f"API request error: {str(e)}")
            return {"error": str(e)}
    
    async def research_keywords(self, seed_keywords: List[str], 
                               country: str = "US", language: str = "en") -> List[KeywordData]:
        """
        Keyword research - multiple API sources
        
        Args:
            seed_keywords: Başlangıç keyword'leri
            country: Ülke kodu (US, TR, etc.)
            language: Dil kodu (en, tr, etc.)
        
        Returns:
            List[KeywordData]: Keyword analiz sonuçları
        """
        
        # Use free tools if available
        if self.use_free_tools and self.hybrid_service:
            free_results = await self.hybrid_service.get_keyword_data(seed_keywords)
            
            keyword_data_list = []
            for result in free_results:
                kw_data = KeywordData(
                    keyword=result['keyword'],
                    search_volume=result['metrics']['search_volume_estimate'] // 1000,  # Tahmine çevir
                    difficulty=50.0,  # Default değer
                    cpc=1.5,  # Default değer
                    competition=result['metrics']['competition'],
                    trend=result['trend_data'],
                    related_keywords=result['related']
                )
                keyword_data_list.append(kw_data)
            
            return keyword_data_list
        
        # Fallback to mock mode if no APIs available
        if self.mock_mode:
            return await self._mock_keyword_research(seed_keywords)
        
        all_keywords = []
        
        # SEMrush API ile keyword research
        if self.semrush_api_key:
            semrush_results = await self._semrush_keyword_research(seed_keywords, country)
            all_keywords.extend(semrush_results)
        
        # Ahrefs API ile keyword research
        if self.ahrefs_api_key:
            ahrefs_results = await self._ahrefs_keyword_research(seed_keywords, country)
            all_keywords.extend(ahrefs_results)
        
        # Duplicate'leri temizle ve birleştir
        unique_keywords = {}
        for kw in all_keywords:
            if kw.keyword not in unique_keywords:
                unique_keywords[kw.keyword] = kw
            else:
                # Birden fazla source'dan gelen data'yı birleştir
                existing = unique_keywords[kw.keyword]
                existing.search_volume = max(existing.search_volume, kw.search_volume)
                existing.related_keywords.extend(kw.related_keywords)
                existing.related_keywords = list(set(existing.related_keywords))
        
        return list(unique_keywords.values())
    
    async def _semrush_keyword_research(self, keywords: List[str], country: str) -> List[KeywordData]:
        """SEMrush API ile keyword research"""
        results = []
        
        for keyword in keywords:
            url = "https://api.semrush.com/"
            params = {
                'type': 'phrase_related',
                'key': self.semrush_api_key,
                'phrase': keyword,
                'database': country.lower(),
                'export_columns': 'Ph,Nq,Cp,Co,Kd',
                'display_limit': 100
            }
            
            response = await self._make_api_request(url, params)
            
            if 'error' not in response:
                # SEMrush response'unu parse et
                for item in response.get('data', []):
                    try:
                        kw_data = KeywordData(
                            keyword=item.get('Ph', ''),
                            search_volume=int(item.get('Nq', 0)),
                            difficulty=float(item.get('Kd', 0)),
                            cpc=float(item.get('Cp', 0)),
                            competition=item.get('Co', 'low'),
                            trend=[],  # Trend data ayrı API call gerektirir
                            related_keywords=[]
                        )
                        results.append(kw_data)
                    except (ValueError, KeyError) as e:
                        self.logger.warning(f"Failed to parse SEMrush data: {e}")
                        continue
        
        return results
    
    async def _ahrefs_keyword_research(self, keywords: List[str], country: str) -> List[KeywordData]:
        """Ahrefs API ile keyword research"""
        results = []
        
        for keyword in keywords:
            url = "https://apiv2.ahrefs.com"
            headers = {
                'Authorization': f'Bearer {self.ahrefs_api_key}',
                'Accept': 'application/json'
            }
            params = {
                'target': keyword,
                'country': country.lower(),
                'mode': 'exact'
            }
            
            response = await self._make_api_request(url, params, headers)
            
            if 'error' not in response:
                # Ahrefs response'unu parse et
                for item in response.get('keywords', []):
                    try:
                        kw_data = KeywordData(
                            keyword=item.get('keyword', ''),
                            search_volume=int(item.get('search_volume', 0)),
                            difficulty=float(item.get('difficulty', 0)),
                            cpc=float(item.get('cpc', 0)),
                            competition='medium',  # Ahrefs competition mapping
                            trend=[],
                            related_keywords=[]
                        )
                        results.append(kw_data)
                    except (ValueError, KeyError) as e:
                        self.logger.warning(f"Failed to parse Ahrefs data: {e}")
                        continue
        
        return results
    
    async def _mock_keyword_research(self, keywords: List[str]) -> List[KeywordData]:
        """Mock keyword research for development"""
        mock_keywords = []
        
        for base_keyword in keywords:
            # Her keyword için 5-10 related keyword üret
            variations = [
                f"best {base_keyword}",
                f"{base_keyword} review",
                f"{base_keyword} guide",
                f"how to choose {base_keyword}",
                f"{base_keyword} comparison",
                f"top {base_keyword}",
                f"{base_keyword} tips",
                f"{base_keyword} for beginners"
            ]
            
            for i, variation in enumerate(variations):
                mock_data = KeywordData(
                    keyword=variation,
                    search_volume=1000 + (i * 500),  # Mock volume
                    difficulty=30 + (i * 5),  # Mock difficulty
                    cpc=1.5 + (i * 0.3),  # Mock CPC
                    competition='medium' if i % 2 == 0 else 'high',
                    trend=[100, 120, 110, 150, 130, 140],  # Mock trend
                    related_keywords=[f"{base_keyword} related {j}" for j in range(3)]
                )
                mock_keywords.append(mock_data)
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        return mock_keywords
    
    async def analyze_competitors(self, domain: str, keywords: List[str]) -> CompetitorData:
        """
        Competitor analysis
        
        Args:
            domain: Analiz edilecek domain
            keywords: İlgili keyword'ler
        
        Returns:
            CompetitorData: Competitor analiz sonuçları
        """
        
        if self.mock_mode or self.use_free_tools:
            return await self._mock_competitor_analysis(domain, keywords)
        
        # SEMrush ile competitor analysis
        if self.semrush_api_key:
            return await self._semrush_competitor_analysis(domain, keywords)
        
        # Ahrefs ile competitor analysis
        if self.ahrefs_api_key:
            return await self._ahrefs_competitor_analysis(domain, keywords)
        
        return CompetitorData(
            domain=domain,
            authority_score=0,
            organic_keywords=0,
            organic_traffic=0,
            top_keywords=[],
            content_gaps=[],
            backlink_count=0
        )
    
    async def _mock_competitor_analysis(self, domain: str, keywords: List[str]) -> CompetitorData:
        """Mock competitor analysis"""
        await asyncio.sleep(0.3)  # Simulate API delay
        
        return CompetitorData(
            domain=domain,
            authority_score=75.5,
            organic_keywords=15420,
            organic_traffic=125000,
            top_keywords=keywords[:5] + [f"competitor {kw}" for kw in keywords[:3]],
            content_gaps=[f"missing content for {kw}" for kw in keywords[:3]],
            backlink_count=8500
        )
    
    async def get_serp_analysis(self, keyword: str, location: str = "United States") -> Dict[str, Any]:
        """
        SERP (Search Engine Results Page) analysis
        
        Args:
            keyword: Analiz edilecek keyword
            location: Lokasyon
        
        Returns:
            Dict: SERP analiz sonuçları
        """
        
        # Try SERPAPI first if available
        if self.serpapi_key:
            return await self._serpapi_analysis(keyword, location)
        
        # Use free tools if available
        if self.use_free_tools and self.free_service:
            competitors = await self.free_service.get_serp_competitors(keyword, 10)
            return {
                "keyword": keyword,
                "total_results": await self.free_service.get_search_results_count(keyword),
                "top_10_results": [
                    {
                        "position": i+1,
                        "domain": domain,
                        "url": f"https://{domain}",
                        "title": f"Result from {domain}"
                    }
                    for i, domain in enumerate(competitors)
                ],
                "source": "free_tools"
            }
        
        # Fallback to mock
        return await self._mock_serp_analysis(keyword)
    
    async def _serpapi_analysis(self, keyword: str, location: str) -> Dict[str, Any]:
        """SERPAPI ile SERP analysis"""
        try:
            url = "https://serpapi.com/search"
            params = {
                'q': keyword,
                'location': location,
                'api_key': self.serpapi_key,
                'engine': 'google',
                'hl': 'en',
                'gl': 'us'
            }
            
            response = await self._make_api_request(url, params)
            
            if 'error' not in response:
                # Parse SERPAPI response
                organic_results = response.get('organic_results', [])
                
                return {
                    "keyword": keyword,
                    "total_results": response.get('search_information', {}).get('total_results', 0),
                    "top_10_results": [
                        {
                            "position": result.get('position', i+1),
                            "title": result.get('title', ''),
                            "url": result.get('link', ''),
                            "domain": result.get('displayed_link', ''),
                            "snippet": result.get('snippet', '')
                        }
                        for i, result in enumerate(organic_results[:10])
                    ],
                    "featured_snippets": response.get('answer_box', {}),
                    "people_also_ask": [
                        q.get('question', '') 
                        for q in response.get('people_also_ask', [])
                    ],
                    "related_searches": [
                        s.get('query', '') 
                        for s in response.get('related_searches', [])
                    ],
                    "source": "serpapi"
                }
            else:
                self.logger.error(f"SERPAPI error: {response}")
                return await self._mock_serp_analysis(keyword)
                
        except Exception as e:
            self.logger.error(f"SERPAPI analysis error: {str(e)}")
            return await self._mock_serp_analysis(keyword)
    
    async def _mock_serp_analysis(self, keyword: str) -> Dict[str, Any]:
        """Mock SERP analysis"""
        await asyncio.sleep(0.2)
        
        return {
            "keyword": keyword,
            "total_results": 1250000,
            "top_10_results": [
                {
                    "position": i+1,
                    "title": f"Top result {i+1} for {keyword}",
                    "url": f"https://example{i+1}.com/page",
                    "domain": f"example{i+1}.com",
                    "snippet": f"This is a sample snippet for position {i+1}...",
                    "word_count": 1500 + (i * 100)
                }
                for i in range(10)
            ],
            "featured_snippets": [],
            "people_also_ask": [f"What is {keyword}?", f"How does {keyword} work?"],
            "related_searches": [f"{keyword} guide", f"best {keyword}", f"{keyword} tips"],
            "source": "mock"
        }
    
    async def get_content_optimization_suggestions(self, content: str, 
                                                 target_keywords: List[str]) -> Dict[str, Any]:
        """
        Content optimization suggestions
        
        Args:
            content: Optimize edilecek content
            target_keywords: Hedef keyword'ler
        
        Returns:
            Dict: Optimization önerileri
        """
        
        # Content analysis
        word_count = len(content.split())
        keyword_density = {}
        
        for keyword in target_keywords:
            occurrences = content.lower().count(keyword.lower())
            density = (occurrences / word_count) * 100 if word_count > 0 else 0
            keyword_density[keyword] = {
                'occurrences': occurrences,
                'density': round(density, 2)
            }
        
        # Optimization suggestions
        suggestions = []
        
        for keyword, stats in keyword_density.items():
            if stats['density'] < 1.0:
                suggestions.append(f"Increase '{keyword}' density (currently {stats['density']}%)")
            elif stats['density'] > 3.0:
                suggestions.append(f"Reduce '{keyword}' density (currently {stats['density']}%)")
        
        if word_count < 1000:
            suggestions.append(f"Increase content length (currently {word_count} words)")
        
        return {
            "word_count": word_count,
            "keyword_density": keyword_density,
            "optimization_suggestions": suggestions,
            "seo_score": self._calculate_seo_score(word_count, keyword_density),
            "readability_score": self._calculate_readability_score(content)
        }
    
    def _calculate_seo_score(self, word_count: int, keyword_density: Dict[str, Any]) -> float:
        """SEO score calculation"""
        score = 0
        
        # Word count score (0-30 points)
        if word_count >= 1500:
            score += 30
        elif word_count >= 1000:
            score += 20
        elif word_count >= 500:
            score += 10
        
        # Keyword density score (0-40 points)
        for keyword, stats in keyword_density.items():
            density = stats['density']
            if 1.0 <= density <= 2.5:
                score += 10
            elif 0.5 <= density < 1.0 or 2.5 < density <= 3.0:
                score += 5
        
        # Content structure score (0-30 points) - simplified
        score += 20  # Assuming good structure
        
        return min(score, 100)
    
    def _calculate_readability_score(self, content: str) -> float:
        """Simple readability score calculation"""
        sentences = len([s for s in content.split('.') if s.strip()])
        words = len(content.split())
        
        if sentences == 0:
            return 0
        
        avg_sentence_length = words / sentences
        
        # Simple readability metric (higher is better)
        if avg_sentence_length <= 15:
            return 90
        elif avg_sentence_length <= 20:
            return 80
        elif avg_sentence_length <= 25:
            return 70
        else:
            return 60


# Test function
async def test_seo_tools():
    """SEO Tools Service test function"""
    print("Testing SEO Tools Service")
    print("=" * 50)
    
    service = SEOToolsService()
    
    # API key status
    print("\n📋 API Status:")
    print(f"  SERPAPI: {'✅' if service.serpapi_key else '❌'}")
    print(f"  Free Tools: {'✅' if service.use_free_tools else '❌'}")
    print(f"  Mock Mode: {'✅' if service.mock_mode else '❌'}")
    
    # Test 1: Keyword research
    print("\n1. Testing Keyword Research...")
    keywords = await service.research_keywords(["gaming mouse", "wireless headset"])
    print(f"Found {len(keywords)} keywords")
    if keywords:
        print(f"Sample keyword: {keywords[0].keyword} - Volume: {keywords[0].search_volume}")
    
    # Test 2: Competitor analysis
    print("\n2. Testing Competitor Analysis...")
    competitor = await service.analyze_competitors("example.com", ["gaming mouse"])
    print(f"Domain: {competitor.domain} - Authority: {competitor.authority_score}")
    
    # Test 3: SERP analysis
    print("\n3. Testing SERP Analysis...")
    serp = await service.get_serp_analysis("best gaming mouse")
    print(f"SERP results: {len(serp.get('top_10_results', []))}")
    print(f"Source: {serp.get('source', 'unknown')}")
    
    # Test 4: Content optimization
    print("\n4. Testing Content Optimization...")
    sample_content = "This is a sample content about gaming mouse. The best gaming mouse should have good DPI and comfortable design."
    optimization = await service.get_content_optimization_suggestions(
        sample_content, 
        ["gaming mouse", "DPI"]
    )
    print(f"SEO Score: {optimization['seo_score']}")
    print(f"Suggestions: {len(optimization['optimization_suggestions'])}")
    
    print("\n✅ SEO Tools Service test completed!")


if __name__ == "__main__":
    asyncio.run(test_seo_tools())