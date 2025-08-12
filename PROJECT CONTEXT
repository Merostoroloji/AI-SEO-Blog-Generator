# PROJECT CONTEXT - AI SEO Blog Generator

> **YENİ CHAT'TE BU DOSYAYI CLAUDE'A GÖNDERİN - TÜM CONTEXT'İ HATIRLAR**

##  Proje Özeti
E-ticaret ve ürün tanıtımı odaklı, AI destekli SEO blog içeriği üretim platformu. 7 farklı AI agent'ın pipeline halinde çalışarak yüksek kaliteli, SEO optimize edilmiş makaleler üretir.

##  Temel Kararlar

### Teknik Seçimler
- **Backend**: Python + FastAPI
- **AI Model**: Google AI Studio (Gemini) - ÜCRETSİZ
- **Database**: PostgreSQL + Redis
- **Queue System**: Celery
- **Content Length**: 1500-3000 kelime
- **Language**: İngilizce içerik
- **Monetization**: Tek seferlik ödeme modeli
- **Image Style**: Photography tarzında görseller
- **Tracking**: Haftalık SEO performans takibi

### İş Akışı
1. Kullanıcı ürün/niche bilgisi girer
2. Market Research Agent analiz yapar
3. Keyword Analyzer değerli anahtar kelimeleri bulur
4. Content Structure Agent makale planı oluşturur
5. Content Writer Agent içerik yazar
6. Image Placement Agent görselleri yerleştirir
7. SEO Audit Agent kaliteyi kontrol eder
8. Web arayüzünde önizleme gösterilir
9. Kullanıcı onaylarsa WordPress'e tek tıkla aktarılır
10. Haftalık tracking başlar

##  AI Agent Detayları

### 1. Market Research Agent
- Müşteri analizi
- Pazar trendleri
- Rekabet analizi
- Satış noktaları belirleme

### 2. SEO Keywords Agent  
- Anahtar kelime araştırması
- LSI keywords
- Search intent analizi
- **Keyword Value Scoring**:
  - Search Volume: %40
  - Keyword Difficulty: %30  
  - CPC: %20
  - Google Trends: %10

### 3. Content Structure Agent
- SEO-friendly outline
- H1-H6 hiyerarşi
- CTA yerleşimi
- E-ticaret templates

### 4. Content Writer Agent
- 1500-3000 kelime makale
- Conversion odaklı yazım
- Product reviews/buying guides
- 2 adet FAQ sorusu dahil

### 5. Image Placement Agent
- Optimal görsel konumları
- Photography tarzı görseller
- SEO-friendly alt text
- Dosya adı optimizasyonu

### 6. SEO Audit Agent (YENİ EKLENEN)
- İçerik SEO skoru
- Plagiarism check
- Readability analysis
- Keyword density kontrolü

### 7. Content Refresher Agent (YENİ EKLENEN)
- Performance verilerine göre içerik güncelleme
- Eski makaleleri yenileme
- SEO optimizasyon önerileri

##  Gelişmiş Özellikler

### Pipeline Orchestration
- Event-driven agent communication
- Chain of thought reasoning
- Real-time progress tracking
- Error handling ve recovery

### Kalite Kontrol
- **Copyscape API** - plagiarism detection
- **Flesch-Kincaid** - readability scoring
- **Moz API** - domain authority
- **Google Trends** - keyword trends

### WordPress Entegrasyonu
- REST API ile güvenli bağlantı
- Tek tıkla yayınlama
- Meta tag otomasyonu
- Görsel optimizasyonu

### Dashboard Özellikleri
- Real-time pipeline progress
- SEO performans grafikleri
- Keyword sıralama takibi
- Traffic istatistikleri
- Agent ilerleme çubukları

##  Kritik Dosya Yapısı

```
ai-seo-blog-generator/
├── agents/
│   ├── base_agent.py           # Chain of thought + tool management
│   ├── market_research.py      # Pazar analizi
│   ├── keyword_analyzer.py     # SEO keywords
│   ├── content_structure.py    # Makale planı
│   ├── content_writer.py       # İçerik üretimi
│   ├── image_placement.py      # Görsel yerleştirme
│   ├── seo_audit_agent.py      # SEO audit
│   └── content_refresher.py    # İçerik güncelleme
├── pipeline/
│   ├── orchestrator.py         # Agent pipeline yöneticisi
│   ├── tasks.py               # Celery background tasks
│   └── events.py              # Event-driven communication
├── services/
│   ├── gemini_service.py      # Google AI Studio
│   ├── seo_tools.py           # Gelişmiş SEO metrikleri
│   ├── plagiarism_service.py  # İçerik orijinalliği
│   └── wordpress_service.py   # WP REST API + güncelleme
└── utils/
    ├── keyword_scorer.py      # Keyword değer hesaplama
    ├── quality_checker.py    # İçerik kalite metrikleri
    └── security.py           # Credential şifreleme
```

##  Development Sırası

### Tamamlanan
-  Proje planlaması ve mimari
-  Dosya yapısı tasarımı
-  GitHub repo hazırlığı

### Sonraki Adımlar
1. **gemini_service.py** - Google AI Studio entegrasyonu
2. **base_agent.py** - Agent base class ve chain of thought
3. **keyword_scorer.py** - Keyword değer hesaplama algoritması
4. **pipeline/orchestrator.py** - Agent pipeline yönetimi
5. **market_research.py** - İlk agent implementation
6. **seo_tools.py** - SEO metrics entegrasyonu

##  Önemli Kararlar ve Sebepleri

### Neden Gemini?
- Google AI Studio ile ücretsiz API
- Güçlü reasoning capabilities
- Multi-modal support (text + image)
- Chain of thought için uygun

### Neden Pipeline Yaklaşımı?
- Her agent spesifik göreve odaklanır
- Modüler ve test edilebilir yapı
- Hata durumunda sadece o agent yeniden çalışır
- Event-driven scalability

### Neden WordPress Entegrasyonu?
- Pazarın %40'ı WordPress kullanıyor
- REST API ile kolay entegrasyon
- Mevcut workflow'a minimal impact

##  Keyword Value Scoring Detayı

```python
def calculate_keyword_score(keyword_data):
    search_volume_score = normalize_search_volume(keyword_data['volume']) * 0.4
    difficulty_score = (100 - keyword_data['difficulty']) * 0.3 / 100
    cpc_score = normalize_cpc(keyword_data['cpc']) * 0.2
    trend_score = calculate_trend_score(keyword_data['trend']) * 0.1
    
    return search_volume_score + difficulty_score + cpc_score + trend_score
```

##  Image Generation Stratejisi
- **Style**: Photography (realistic, professional)
- **Placement**: Intro + mid-content + before conclusion
- **Alt Text**: AI-generated, SEO-friendly
- **File Naming**: keyword-based, SEO optimized
- **Format**: WebP for performance

##  Tracking Metrikleri
- **Haftalık kontroller**:
  - Keyword sıralamaları (Google Search Console)
  - Organic traffic growth
  - Click-through rates
  - Domain authority changes
  - Content freshness scores

##  Güvenlik Notları
- WordPress credentials şifreli storage
- API keys environment variables
- User data GDPR compliant
- Secure session management

---
