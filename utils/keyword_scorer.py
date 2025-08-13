"""
Keyword Value Scoring Algorithm for AI SEO Blog Generator

Bu modül keyword'lerin değerini hesaplar ve scoring yapar:
- Search Volume: 40%
- Keyword Difficulty: 30% 
- CPC: 20%
- Google Trends: 10%

Her keyword için 0-100 arası bir skor üretir.
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics


@dataclass
class KeywordMetrics:
    """Keyword metrikleri için veri yapısı"""
    keyword: str
    search_volume: int
    keyword_difficulty: float  # 0-100
    cpc: float  # USD
    trend_score: float  # 0-100
    competition: str  # "low", "medium", "high"
    last_updated: datetime


@dataclass
class KeywordScore:
    """Keyword skoru sonuç yapısı"""
    keyword: str
    total_score: float  # 0-100
    component_scores: Dict[str, float]
    grade: str  # A+, A, B+, B, C+, C, D
    recommendation: str
    metrics: KeywordMetrics


class KeywordScorer:
    """
    Keyword değer hesaplama ve scoring sistemi
    
    Scoring Ağırlıkları:
    - Search Volume: 40% (trafiği temsil eder)
    - Keyword Difficulty: 30% (rekabet zorluğu)
    - CPC: 20% (ticari değer)
    - Google Trends: 10% (trend momentum)
    """
    
    # Scoring ağırlıkları
    WEIGHTS = {
        'search_volume': 0.40,
        'keyword_difficulty': 0.30,
        'cpc': 0.20,
        'trend': 0.10
    }
    
    # Grade thresholds
    GRADE_THRESHOLDS = {
        'A+': 90,
        'A': 80,
        'B+': 70,
        'B': 60,
        'C+': 50,
        'C': 40,
        'D': 0
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Normalizasyon için benchmark değerler
        self.benchmarks = {
            'high_volume': 100000,     # Yüksek arama hacmi
            'medium_volume': 10000,    # Orta arama hacmi
            'low_volume': 1000,        # Düşük arama hacmi
            'high_cpc': 10.0,          # Yüksek CPC ($)
            'medium_cpc': 2.0,         # Orta CPC ($)
            'low_cpc': 0.5            # Düşük CPC ($)
        }
    
    def normalize_search_volume(self, volume: int) -> float:
        """
        Arama hacmini 0-100 arasında normalize eder
        
        Logaritmik ölçekleme kullanır çünkü arama hacmi exponential dağılır
        """
        if volume <= 0:
            return 0.0
        
        # Logaritmik normalizasyon
        log_volume = math.log10(max(volume, 1))
        log_high = math.log10(self.benchmarks['high_volume'])
        
        # 0-100 arası scale et
        normalized = (log_volume / log_high) * 100
        
        return min(normalized, 100.0)
    
    def normalize_keyword_difficulty(self, difficulty: float) -> float:
        """
        Keyword difficulty'yi tersine çevirir (düşük difficulty = yüksek skor)
        
        Difficulty 0-100 arası gelir, biz tersine çeviriyoruz
        """
        if difficulty < 0:
            difficulty = 0
        elif difficulty > 100:
            difficulty = 100
        
        # Ters çevirme: düşük difficulty = yüksek skor
        return 100 - difficulty
    
    def normalize_cpc(self, cpc: float) -> float:
        """
        CPC değerini 0-100 arasında normalize eder
        
        Yüksek CPC = yüksek ticari değer = yüksek skor
        """
        if cpc <= 0:
            return 0.0
        
        # CPC için logaritmik scaling
        if cpc >= self.benchmarks['high_cpc']:
            return 100.0
        elif cpc >= self.benchmarks['medium_cpc']:
            # Medium-High arası linear interpolation
            ratio = (cpc - self.benchmarks['medium_cpc']) / (self.benchmarks['high_cpc'] - self.benchmarks['medium_cpc'])
            return 60 + (ratio * 40)  # 60-100 arası
        elif cpc >= self.benchmarks['low_cpc']:
            # Low-Medium arası linear interpolation
            ratio = (cpc - self.benchmarks['low_cpc']) / (self.benchmarks['medium_cpc'] - self.benchmarks['low_cpc'])
            return 20 + (ratio * 40)  # 20-60 arası
        else:
            # Very low CPC
            ratio = cpc / self.benchmarks['low_cpc']
            return ratio * 20  # 0-20 arası
    
    def calculate_trend_score(self, trend_data: Any) -> float:
        """
        Google Trends verisinden trend skoru hesaplar
        
        Args:
            trend_data: Trend verisi (basit implementation için 0-100 arası değer)
        """
        if isinstance(trend_data, (int, float)):
            return max(0, min(100, float(trend_data)))
        
        # Gelecekte Google Trends API entegrasyonu için
        # trend_data kompleks veri yapısı olabilir
        if isinstance(trend_data, dict):
            if 'score' in trend_data:
                return max(0, min(100, float(trend_data['score'])))
            elif 'values' in trend_data:
                # Son 3 ayın ortalaması
                values = trend_data['values'][-12:]  # Son 12 hafta
                return statistics.mean(values) if values else 50.0
        
        # Default: orta değer
        return 50.0
    
    def calculate_keyword_score(self, metrics: KeywordMetrics) -> KeywordScore:
        """
        Ana keyword scoring algoritması
        
        Args:
            metrics: Keyword metrikleri
            
        Returns:
            KeywordScore: Hesaplanmış keyword skoru
        """
        
        # Her component için skor hesapla
        volume_score = self.normalize_search_volume(metrics.search_volume)
        difficulty_score = self.normalize_keyword_difficulty(metrics.keyword_difficulty)
        cpc_score = self.normalize_cpc(metrics.cpc)
        trend_score = self.calculate_trend_score(metrics.trend_score)
        
        # Ağırlıklı toplam hesapla
        total_score = (
            volume_score * self.WEIGHTS['search_volume'] +
            difficulty_score * self.WEIGHTS['keyword_difficulty'] +
            cpc_score * self.WEIGHTS['cpc'] +
            trend_score * self.WEIGHTS['trend']
        )
        
        # Component scores
        component_scores = {
            'search_volume': volume_score,
            'keyword_difficulty': difficulty_score,
            'cpc': cpc_score,
            'trend': trend_score
        }
        
        # Grade hesapla
        grade = self._calculate_grade(total_score)
        
        # Recommendation oluştur
        recommendation = self._generate_recommendation(total_score, component_scores, metrics)
        
        return KeywordScore(
            keyword=metrics.keyword,
            total_score=total_score,
            component_scores=component_scores,
            grade=grade,
            recommendation=recommendation,
            metrics=metrics
        )
    
    def _calculate_grade(self, score: float) -> str:
        """Skordan grade hesaplar"""
        for grade, threshold in self.GRADE_THRESHOLDS.items():
            if score >= threshold:
                return grade
        return 'D'
    
    def _generate_recommendation(self, total_score: float, component_scores: Dict[str, float], metrics: KeywordMetrics) -> str:
        """Skor ve metriklere göre recommendation üretir"""
        
        recommendations = []
        
        # Genel skor değerlendirmesi
        if total_score >= 80:
            recommendations.append("Excellent keyword - high priority target")
        elif total_score >= 60:
            recommendations.append("Good keyword - consider targeting")
        elif total_score >= 40:
            recommendations.append("Moderate keyword - may be worth targeting")
        else:
            recommendations.append("Low-value keyword - consider alternatives")
        
        # Component-specific öneriler
        if component_scores['search_volume'] < 30:
            recommendations.append("Low search volume - consider long-tail variations")
        
        if component_scores['keyword_difficulty'] < 40:
            recommendations.append("High competition - may be difficult to rank")
        
        if component_scores['cpc'] > 80:
            recommendations.append("High commercial value - good for monetization")
        elif component_scores['cpc'] < 20:
            recommendations.append("Low commercial intent - focus on traffic volume")
        
        if component_scores['trend'] < 30:
            recommendations.append("Declining trend - monitor performance closely")
        elif component_scores['trend'] > 70:
            recommendations.append("Rising trend - opportunity for growth")
        
        return " | ".join(recommendations)
    
    def score_keyword_list(self, keywords_metrics: List[KeywordMetrics]) -> List[KeywordScore]:
        """
        Keyword listesini toplu olarak skorlar
        
        Args:
            keywords_metrics: Keyword metrikleri listesi
            
        Returns:
            List[KeywordScore]: Skorlanmış keyword'ler (yüksek skordan düşüğe)
        """
        scores = []
        
        for metrics in keywords_metrics:
            try:
                score = self.calculate_keyword_score(metrics)
                scores.append(score)
                self.logger.debug(f"Scored '{metrics.keyword}': {score.total_score:.1f} ({score.grade})")
            except Exception as e:
                self.logger.error(f"Failed to score keyword '{metrics.keyword}': {str(e)}")
        
        # Skorlara göre sırala (yüksekten düşüğe)
        scores.sort(key=lambda x: x.total_score, reverse=True)
        
        return scores
    
    def get_top_keywords(self, keyword_scores: List[KeywordScore], count: int = 10, min_grade: str = 'C') -> List[KeywordScore]:
        """
        En iyi keyword'leri filtreler
        
        Args:
            keyword_scores: Skorlanmış keyword'ler
            count: Döndürülecek keyword sayısı
            min_grade: Minimum grade threshold
            
        Returns:
            List[KeywordScore]: Filtrelenmiş top keyword'ler
        """
        min_score = self.GRADE_THRESHOLDS[min_grade]
        
        filtered = [
            score for score in keyword_scores 
            if score.total_score >= min_score
        ]
        
        return filtered[:count]
    
    def generate_keyword_report(self, keyword_scores: List[KeywordScore]) -> Dict[str, Any]:
        """
        Keyword analiz raporu oluşturur
        
        Returns:
            Dict: Detaylı analiz raporu
        """
        if not keyword_scores:
            return {"error": "No keyword scores provided"}
        
        total_keywords = len(keyword_scores)
        avg_score = statistics.mean([score.total_score for score in keyword_scores])
        
        # Grade dağılımı
        grade_distribution = {}
        for score in keyword_scores:
            grade = score.grade
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # En iyi ve en kötü keyword'ler
        best_keywords = keyword_scores[:5]
        worst_keywords = keyword_scores[-5:]
        
        # Component analizi
        avg_components = {
            component: statistics.mean([score.component_scores[component] for score in keyword_scores])
            for component in ['search_volume', 'keyword_difficulty', 'cpc', 'trend']
        }
        
        return {
            "summary": {
                "total_keywords": total_keywords,
                "average_score": round(avg_score, 2),
                "grade_distribution": grade_distribution
            },
            "top_keywords": [
                {
                    "keyword": score.keyword,
                    "score": round(score.total_score, 2),
                    "grade": score.grade,
                    "recommendation": score.recommendation
                }
                for score in best_keywords
            ],
            "bottom_keywords": [
                {
                    "keyword": score.keyword,
                    "score": round(score.total_score, 2),
                    "grade": score.grade
                }
                for score in worst_keywords
            ],
            "component_analysis": {
                component: round(score, 2)
                for component, score in avg_components.items()
            },
            "recommendations": self._generate_overall_recommendations(avg_components, grade_distribution)
        }
    
    def _generate_overall_recommendations(self, avg_components: Dict[str, float], grade_distribution: Dict[str, int]) -> List[str]:
        """Genel öneriler üretir"""
        recommendations = []
        
        # Component bazlı öneriler
        if avg_components['search_volume'] < 40:
            recommendations.append("Consider targeting higher volume keywords or focus on long-tail strategy")
        
        if avg_components['keyword_difficulty'] < 50:
            recommendations.append("High competition detected - consider less competitive alternatives")
        
        if avg_components['cpc'] < 30:
            recommendations.append("Low commercial intent - supplement with high-value keywords")
        
        if avg_components['trend'] < 40:
            recommendations.append("Declining trends detected - research emerging keywords")
        
        # Grade dağılımı bazlı öneriler
        high_grade_count = grade_distribution.get('A+', 0) + grade_distribution.get('A', 0)
        total_keywords = sum(grade_distribution.values())
        
        if high_grade_count / total_keywords < 0.2:
            recommendations.append("Low percentage of high-value keywords - expand research")
        
        return recommendations


# Utility functions
def create_sample_metrics(keyword: str, volume: int, difficulty: float, cpc: float, trend: float) -> KeywordMetrics:
    """Test için sample metrics oluşturur"""
    return KeywordMetrics(
        keyword=keyword,
        search_volume=volume,
        keyword_difficulty=difficulty,
        cpc=cpc,
        trend_score=trend,
        competition="medium",
        last_updated=datetime.now()
    )


# Test ve örnek kullanım
if __name__ == "__main__":
    print("Keyword Scorer Test")
    print("=" * 50)
    
    # Scorer instance
    scorer = KeywordScorer()
    
    # Test keyword'leri
    test_keywords = [
        create_sample_metrics("bluetooth headphones", 50000, 75, 3.5, 80),
        create_sample_metrics("wireless earbuds", 30000, 60, 4.2, 90),
        create_sample_metrics("noise canceling headphones", 15000, 70, 5.1, 75),
        create_sample_metrics("gaming headset", 25000, 55, 2.8, 85),
        create_sample_metrics("running headphones", 8000, 45, 1.9, 70),
        create_sample_metrics("budget bluetooth headphones", 5000, 40, 1.2, 60),
        create_sample_metrics("premium wireless headphones", 3000, 80, 8.5, 65),
        create_sample_metrics("workout earbuds", 4500, 35, 2.1, 95)
    ]
    
    # Keyword'leri skorla
    scores = scorer.score_keyword_list(test_keywords)
    
    # Sonuçları göster
    print("KEYWORD SCORES:")
    print("-" * 80)
    for score in scores:
        print(f"{score.keyword:30} | Score: {score.total_score:5.1f} | Grade: {score.grade:2} | {score.recommendation}")
    
    # Top keywords
    print("\nTOP 5 KEYWORDS:")
    print("-" * 50)
    top_keywords = scorer.get_top_keywords(scores, count=5, min_grade='B')
    for score in top_keywords:
        print(f"{score.keyword} ({score.grade}) - {score.total_score:.1f}")
    
    # Detaylı rapor
    print("\nDETAILED REPORT:")
    print("-" * 50)
    report = scorer.generate_keyword_report(scores)
    
    print(f"Total Keywords: {report['summary']['total_keywords']}")
    print(f"Average Score: {report['summary']['average_score']}")
    print(f"Grade Distribution: {report['summary']['grade_distribution']}")
    
    print("\nComponent Analysis:")
    for component, score in report['component_analysis'].items():
        print(f"  {component}: {score}")
    
    print("\nOverall Recommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")