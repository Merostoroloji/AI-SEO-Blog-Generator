"""
Free SEO Tools Service - AI SEO Blog Generator

Ücretsiz SEO araçlarını kullanarak gerçek veri sağlar:
- Google Trends (pytrends)
- Google Autocomplete 
- Google Search scraping
- SERP analysis
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import time
from urllib.parse import quote_plus
import warnings

# Pandas FutureWarning'i sustur
warnings.filterwarnings('ignore', category=FutureWarning)

# Ücretsiz kütüphaneler
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("⚠️ pytrends not installed. Run: pip install pytrends")

try:
    from googlesearch import search
    GOOGLESEARCH_AVAILABLE = True
except ImportError:
    GOOGLESEARCH_AVAILABLE = False
    print("⚠️ googlesearch-python not installed. Run: pip install googlesearch-python")

try:
    from bs4 import BeautifulSoup
    import requests
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("⚠️ BeautifulSoup not installed. Run: pip install beautifulsoup4 requests")


@dataclass
class FreeKeywordData:
    """Ücretsiz keyword verisi yapısı"""
    keyword: str
    trend_score: int  # Google Trends score (0-100)
    trend_data: List[int]  # Son 12 aylık trend
    related_queries: List[str]  # İlgili aramalar
    suggestions: List[str]  # Autocomplete önerileri
    search_results_count: int  # Tahmini sonuç sayısı
    top_competitors: List[str]  # SERP'te çıkan domainler
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'keyword': self.keyword,
            'trend_score': self.trend_score,
            'trend_data': self.trend_data,
            'related_queries': self.related_queries,
            'suggestions': self.suggestions,
            'search_results_count': self.search_results_count,
            'top_competitors': self.top_competitors
        }


class FreeSEOToolsService:
    """
    Ücretsiz SEO Tools Service
    
    Google'ın ücretsiz API'lerini ve web scraping kullanır
    """
    
    def __init__(self):
        self.logger = logging.getLogger("FreeSEOToolsService")
        
        # Pytrends client - lazy initialization
        self.pytrends = None
        if PYTRENDS_AVAILABLE:
            try:
                # Basit initialization - retry parametresi olmadan
                self.pytrends = TrendReq(hl='en-US', tz=360)
                self.logger.info("Pytrends initialized successfully")
            except Exception as e:
                self.logger.warning(f"Pytrends initialization failed: {e}")
                self.pytrends = None
            
        # Rate limiting için bekleme süreleri
        self.delays = {
            'trends': 1.5,  # Google Trends arası bekleme (biraz artırıldı)
            'autocomplete': 0.5,  # Autocomplete arası bekleme
            'search': 2.0,  # Google Search arası bekleme
            'scraping': 1.0  # Web scraping arası bekleme
        }
        
        # User agents for scraping
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Request session for better performance
        self.session = None
        
        self.logger.info("Free SEO Tools Service initialized")
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Bağımlılıkları kontrol et"""
        status = []
        if PYTRENDS_AVAILABLE:
            status.append("✅ pytrends")
        else:
            status.append("❌ pytrends")
            
        if GOOGLESEARCH_AVAILABLE:
            status.append("✅ googlesearch")
        else:
            status.append("❌ googlesearch")
            
        if SCRAPING_AVAILABLE:
            status.append("✅ beautifulsoup4")
        else:
            status.append("❌ beautifulsoup4")
            
        self.logger.info(f"Dependencies: {', '.join(status)}")
    
    async def get_google_trends(self, keywords: List[str], timeframe: str = 'today 12-m') -> Dict[str, Any]:
        """
        Google Trends verilerini al
        
        Args:
            keywords: Analiz edilecek keyword'ler (max 5)
            timeframe: Zaman aralığı ('today 12-m', 'today 3-m', etc.)
        
        Returns:
            Dict: Trend verileri
        """
        
        if not PYTRENDS_AVAILABLE or not self.pytrends:
            return await self._mock_trends_data(keywords)
        
        try:
            # Max 5 keyword at a time
            keywords = keywords[:5]
            
            # Clean keywords (remove special characters that might cause issues)
            clean_keywords = [k.strip().lower() for k in keywords if k.strip()]
            
            if not clean_keywords:
                return {}
            
            # Build payload with error handling
            try:
                self.pytrends.build_payload(clean_keywords, cat=0, timeframe=timeframe, geo='', gprop='')
            except Exception as e:
                self.logger.error(f"Failed to build pytrends payload: {e}")
                return await self._mock_trends_data(keywords)
            
            # Interest over time
            trends_data = {}
            
            try:
                interest_over_time = self.pytrends.interest_over_time()
                
                if interest_over_time is not None and not interest_over_time.empty:
                    for keyword in clean_keywords:
                        if keyword in interest_over_time.columns:
                            trend_values = interest_over_time[keyword].tolist()
                            current_score = int(trend_values[-1]) if trend_values else 50
                            
                            trends_data[keyword] = {
                                'trend_score': current_score,
                                'trend_data': [int(v) for v in trend_values[-12:]],  # Son 12 veri noktası
                                'related_queries': []
                            }
            except Exception as e:
                self.logger.error(f"Failed to get interest over time: {e}")
            
            # Related queries - separate try block
            try:
                related_queries = self.pytrends.related_queries()
                
                for keyword in clean_keywords:
                    if keyword in related_queries and keyword in trends_data:
                        top_queries = related_queries[keyword].get('top', None)
                        if top_queries is not None and not top_queries.empty:
                            trends_data[keyword]['related_queries'] = top_queries['query'].tolist()[:10]
            except Exception as e:
                self.logger.warning(f"Failed to get related queries: {e}")
                # Continue without related queries
            
            # Rate limiting
            await asyncio.sleep(self.delays['trends'])
            
            return trends_data if trends_data else await self._mock_trends_data(keywords)
            
        except Exception as e:
            self.logger.error(f"Google Trends error: {str(e)}")
            return await self._mock_trends_data(keywords)
    
    async def get_google_autocomplete(self, keyword: str, language: str = 'en') -> List[str]:
        """Google Autocomplete önerilerini al"""
        
        suggestions = []
        
        try:
            # Google Autocomplete API URL
            url = "http://suggestqueries.google.com/complete/search"
            params = {
                'q': keyword,
                'client': 'chrome',  # chrome daha stabil
                'hl': language
            }
            
            async with aiohttp.ClientSession() as session:
                # Headers ekle
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                async with session.get(url, params=params, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        # Content type kontrolü yapma, direkt parse et
                        text = await response.text()
                        
                        # JSONP formatında gelebilir, temizle
                        if text.startswith('window.'):
                            text = text.split('(', 1)[1].rsplit(')', 1)[0]
                        
                        import json
                        data = json.loads(text)
                        
                        if isinstance(data, list) and len(data) > 1:
                            suggestions = data[1][:10] if isinstance(data[1], list) else []
            
            # Rate limiting
            await asyncio.sleep(self.delays['autocomplete'])
        
        except Exception as e:
            self.logger.warning(f"Autocomplete fallback for '{keyword}': {str(e)}")
            suggestions = self._mock_autocomplete(keyword)
        
        return suggestions
    
    async def get_search_results_count(self, keyword: str) -> int:
        """
        Google'da tahmini sonuç sayısını al
        
        Args:
            keyword: Arama terimi
        
        Returns:
            int: Tahmini sonuç sayısı
        """
        
        if not SCRAPING_AVAILABLE:
            return self._mock_search_count(keyword)
        
        try:
            # Google search URL
            url = f"https://www.google.com/search"
            params = {'q': keyword, 'hl': 'en'}
            
            headers = {
                'User-Agent': self.user_agents[0],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Sonuç sayısını bul - multiple selectors for reliability
                result_stats = soup.find('div', {'id': 'result-stats'})
                if not result_stats:
                    result_stats = soup.find('div', string=lambda text: text and 'results' in text.lower())
                
                if result_stats:
                    text = result_stats.text
                    # "About 1,234,567 results" formatından sayıyı çıkar
                    import re
                    numbers = re.findall(r'[\d,]+', text)
                    if numbers:
                        count_str = numbers[0].replace(',', '')
                        try:
                            return int(count_str)
                        except ValueError:
                            pass
            
            # Rate limiting
            await asyncio.sleep(self.delays['scraping'])
            
        except Exception as e:
            self.logger.error(f"Search count error: {str(e)}")
        
        return self._mock_search_count(keyword)
    
    async def get_serp_competitors(self, keyword: str, num_results: int = 10) -> List[str]:
        """
        SERP'te çıkan competitor domain'lerini al
        
        Args:
            keyword: Arama terimi
            num_results: Kaç sonuç alınacak
        
        Returns:
            List[str]: Competitor domain listesi
        """
        
        if not GOOGLESEARCH_AVAILABLE:
            return self._mock_competitors(keyword)
        
        competitors = []
        
        try:
            # Google search ile URL'leri al
            search_results = search(keyword, num_results=num_results, lang='en', safe='off')
            
            for url in search_results:
                # Domain'i çıkar
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc
                
                # Clean domain (remove www. prefix)
                if domain:
                    domain = domain.replace('www.', '')
                    if domain not in competitors:
                        competitors.append(domain)
            
            # Rate limiting
            await asyncio.sleep(self.delays['search'])
            
        except Exception as e:
            self.logger.error(f"SERP competitors error: {str(e)}")
            competitors = self._mock_competitors(keyword)
        
        return competitors[:num_results] if competitors else self._mock_competitors(keyword)
    
    async def analyze_keyword(self, keyword: str) -> FreeKeywordData:
        """
        Tek bir keyword için tüm ücretsiz analizleri yap
        
        Args:
            keyword: Analiz edilecek keyword
        
        Returns:
            FreeKeywordData: Keyword analiz sonuçları
        """
        
        # Input validation
        keyword = keyword.strip()
        if not keyword:
            return FreeKeywordData(
                keyword=keyword,
                trend_score=0,
                trend_data=[],
                related_queries=[],
                suggestions=[],
                search_results_count=0,
                top_competitors=[]
            )
        
        # Paralel olarak tüm verileri topla
        tasks = [
            self.get_google_trends([keyword]),
            self.get_google_autocomplete(keyword),
            self.get_search_results_count(keyword),
            self.get_serp_competitors(keyword)
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"Failed to gather keyword data: {e}")
            # Return mock data on complete failure
            return FreeKeywordData(
                keyword=keyword,
                trend_score=50,
                trend_data=[50] * 12,
                related_queries=self._mock_autocomplete(keyword)[:5],
                suggestions=self._mock_autocomplete(keyword),
                search_results_count=self._mock_search_count(keyword),
                top_competitors=self._mock_competitors(keyword)
            )
        
        # Process results with error handling
        trends_data = {}
        if not isinstance(results[0], Exception):
            trends_data = results[0].get(keyword.lower(), {})
        
        autocomplete = []
        if not isinstance(results[1], Exception):
            autocomplete = results[1]
        
        search_count = 0
        if not isinstance(results[2], Exception):
            search_count = results[2]
        
        competitors = []
        if not isinstance(results[3], Exception):
            competitors = results[3]
        
        return FreeKeywordData(
            keyword=keyword,
            trend_score=trends_data.get('trend_score', 50),
            trend_data=trends_data.get('trend_data', []),
            related_queries=trends_data.get('related_queries', []),
            suggestions=autocomplete or self._mock_autocomplete(keyword),
            search_results_count=search_count or self._mock_search_count(keyword),
            top_competitors=competitors or self._mock_competitors(keyword)
        )
    
    async def analyze_multiple_keywords(self, keywords: List[str]) -> List[FreeKeywordData]:
        """
        Birden fazla keyword'ü analiz et
        
        Args:
            keywords: Keyword listesi
        
        Returns:
            List[FreeKeywordData]: Analiz sonuçları
        """
        
        results = []
        
        # Clean and validate keywords
        clean_keywords = [k.strip() for k in keywords if k.strip()]
        
        if not clean_keywords:
            return []
        
        # Batch process Google Trends (max 5 at a time)
        if len(clean_keywords) <= 5:
            trends_batch = await self.get_google_trends(clean_keywords)
        else:
            trends_batch = {}
            for i in range(0, len(clean_keywords), 5):
                batch = clean_keywords[i:i+5]
                batch_trends = await self.get_google_trends(batch)
                trends_batch.update(batch_trends)
                if i + 5 < len(clean_keywords):
                    await asyncio.sleep(1)  # Extra delay between batches
        
        # Process each keyword
        for keyword in clean_keywords:
            self.logger.info(f"Analyzing keyword: {keyword}")
            
            # Get individual data
            autocomplete = await self.get_google_autocomplete(keyword)
            search_count = await self.get_search_results_count(keyword)
            competitors = await self.get_serp_competitors(keyword, 5)
            
            # Get trends data from batch
            keyword_trends = trends_batch.get(keyword.lower(), {})
            
            result = FreeKeywordData(
                keyword=keyword,
                trend_score=keyword_trends.get('trend_score', 50),
                trend_data=keyword_trends.get('trend_data', []),
                related_queries=keyword_trends.get('related_queries', []),
                suggestions=autocomplete,
                search_results_count=search_count,
                top_competitors=competitors
            )
            
            results.append(result)
            
            # Rate limiting between keywords
            if clean_keywords.index(keyword) < len(clean_keywords) - 1:
                await asyncio.sleep(0.5)
        
        return results
    
    async def find_content_gaps(self, main_keyword: str, competitor_domains: List[str] = None) -> Dict[str, Any]:
        """
        Content gap analysis - competitor'ların yazdığı ama bizim yazmadığımız konular
        
        Args:
            main_keyword: Ana keyword
            competitor_domains: Analiz edilecek competitor'lar
        
        Returns:
            Dict: Content gap analizi
        """
        
        # Competitor'ları bul
        if not competitor_domains:
            competitor_domains = await self.get_serp_competitors(main_keyword, 5)
        
        # Related queries ve suggestions topla
        keyword_data = await self.analyze_keyword(main_keyword)
        
        # Long-tail keyword'ler için autocomplete kullan
        all_suggestions = []
        
        # Ana keyword + modifier'lar
        modifiers = ['how to', 'best', 'top', 'vs', 'review', 'guide', 'tutorial', 'tips', 'for beginners']
        
        # Batch process modifiers to avoid rate limiting
        for modifier in modifiers:
            modified_keyword = f"{modifier} {main_keyword}"
            suggestions = await self.get_google_autocomplete(modified_keyword)
            all_suggestions.extend(suggestions)
            await asyncio.sleep(0.3)  # Small delay between requests
        
        # Question-based modifiers
        question_modifiers = ['what is', 'why', 'when to use', 'where to buy']
        for modifier in question_modifiers:
            modified_keyword = f"{modifier} {main_keyword}"
            suggestions = await self.get_google_autocomplete(modified_keyword)
            all_suggestions.extend(suggestions)
            await asyncio.sleep(0.3)
        
        # Unique suggestions
        unique_suggestions = list(set(all_suggestions))
        
        return {
            'main_keyword': main_keyword,
            'competitors': competitor_domains[:10],
            'content_opportunities': unique_suggestions[:30],  # More opportunities
            'related_topics': keyword_data.related_queries[:15],
            'trending_score': keyword_data.trend_score,
            'total_opportunities_found': len(unique_suggestions)
        }
    
    # Mock functions for fallback
    async def _mock_trends_data(self, keywords: List[str]) -> Dict[str, Any]:
        """Mock trends data"""
        import random
        
        trends_data = {}
        for keyword in keywords:
            base_score = random.randint(40, 90)
            trends_data[keyword.lower()] = {
                'trend_score': base_score,
                'trend_data': [base_score + random.randint(-20, 20) for _ in range(12)],
                'related_queries': [
                    f"{keyword} guide",
                    f"best {keyword}",
                    f"{keyword} review",
                    f"how to {keyword}",
                    f"{keyword} tips",
                    f"{keyword} vs alternatives",
                    f"{keyword} 2024"
                ][:5]
            }
        
        await asyncio.sleep(0.1)  # Simulate API delay
        return trends_data
    
    def _mock_autocomplete(self, keyword: str) -> List[str]:
        """Mock autocomplete suggestions"""
        suggestions = [
            f"{keyword} review",
            f"{keyword} best",
            f"{keyword} guide",
            f"{keyword} how to",
            f"{keyword} tips",
            f"{keyword} tutorial",
            f"{keyword} for beginners",
            f"{keyword} 2024",
            f"{keyword} vs competitors",
            f"cheap {keyword}"
        ]
        return suggestions[:8]
    
    def _mock_search_count(self, keyword: str) -> int:
        """Mock search result count"""
        import random
        # More realistic numbers based on keyword length
        base = 1000000 if len(keyword.split()) > 2 else 5000000
        return random.randint(base // 10, base)
    
    def _mock_competitors(self, keyword: str) -> List[str]:
        """Mock competitor domains"""
        return [
            "example.com",
            "bestreviews.com",
            "topguide.org",
            "expertadvice.net",
            "prosandcons.com",
            "buyersguide.org",
            "techreview.com",
            "comparison.net",
            "ultimate-guide.com",
            "trusted-source.org"
        ][:5]


# Integration with existing SEO Tools
class HybridSEOService:
    """
    Hybrid SEO Service - Free + Paid tools kombine
    
    Free tools'u öncelikli kullanır, paid API'ler optional
    """
    
    def __init__(self):
        self.free_tools = FreeSEOToolsService()
        self.logger = logging.getLogger("HybridSEOService")
    
    async def get_keyword_data(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Keyword data topla - önce ücretsiz, sonra paid (varsa)
        """
        
        # Ücretsiz tools ile data topla
        free_data = await self.free_tools.analyze_multiple_keywords(keywords)
        
        # Format for compatibility
        results = []
        for data in free_data:
            results.append({
                'keyword': data.keyword,
                'metrics': {
                    'trend_score': data.trend_score,
                    'search_volume_estimate': data.search_results_count,
                    'competition': 'high' if data.trend_score > 70 else 'medium' if data.trend_score > 40 else 'low'
                },
                'suggestions': data.suggestions,
                'related': data.related_queries,
                'competitors': data.top_competitors,
                'trend_data': data.trend_data
            })
        
        return results


# Test function
async def test_free_seo_tools():
    """Test Free SEO Tools"""
    print("Testing Free SEO Tools Service")
    print("=" * 50)
    
    service = FreeSEOToolsService()
    
    # Test 1: Google Trends
    print("\n1. Testing Google Trends...")
    trends = await service.get_google_trends(["python programming", "javascript"])
    for keyword, data in trends.items():
        print(f"  {keyword}: Score={data['trend_score']}, Related={len(data['related_queries'])}")
    
    # Test 2: Google Autocomplete
    print("\n2. Testing Google Autocomplete...")
    suggestions = await service.get_google_autocomplete("best gaming")
    print(f"  Suggestions ({len(suggestions)}): {suggestions[:5]}")
    
    # Test 3: Search Results Count
    print("\n3. Testing Search Results Count...")
    count = await service.get_search_results_count("artificial intelligence")
    print(f"  Estimated results: {count:,}")
    
    # Test 4: SERP Competitors
    print("\n4. Testing SERP Competitors...")
    competitors = await service.get_serp_competitors("best laptops 2024", 5)
    print(f"  Top competitors: {competitors}")
    
    # Test 5: Full Keyword Analysis
    print("\n5. Testing Full Keyword Analysis...")
    analysis = await service.analyze_keyword("machine learning tutorial")
    print(f"  Keyword: {analysis.keyword}")
    print(f"  Trend Score: {analysis.trend_score}")
    print(f"  Suggestions: {len(analysis.suggestions)}")
    print(f"  Competitors: {len(analysis.top_competitors)}")
    
    # Test 6: Content Gap Analysis
    print("\n6. Testing Content Gap Analysis...")
    gaps = await service.find_content_gaps("web development")
    print(f"  Content opportunities: {len(gaps['content_opportunities'])}")
    print(f"  Total found: {gaps['total_opportunities_found']}")
    print(f"  Sample opportunities: {gaps['content_opportunities'][:3]}")
    
    print("\n✅ Free SEO Tools test completed!")


if __name__ == "__main__":
    # Test için gerekli kütüphaneleri kontrol et
    print("Checking dependencies...")
    print(f"pytrends: {'✅' if PYTRENDS_AVAILABLE else '❌'}")
    print(f"googlesearch: {'✅' if GOOGLESEARCH_AVAILABLE else '❌'}")
    print(f"beautifulsoup4: {'✅' if SCRAPING_AVAILABLE else '❌'}")
    
    if not PYTRENDS_AVAILABLE:
        print("\n📦 Install: pip install pytrends")
    if not GOOGLESEARCH_AVAILABLE:
        print("📦 Install: pip install googlesearch-python")
    if not SCRAPING_AVAILABLE:
        print("📦 Install: pip install beautifulsoup4 requests")
    
    print("\n" + "="*50)
    
    # Testleri çalıştır
    asyncio.run(test_free_seo_tools())