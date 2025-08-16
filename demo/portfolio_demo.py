import asyncio
import sys
import os

# BUNU EKLE - Import'lardan ÖNCE!
sys.path.append('/Users/omersoy/Desktop/ai-seo-blog-generator')

# ŞİMDİ import'lar çalışır
from agents.content_writer import ContentWriterAgent
from agents.publisher import PublisherAgent
from services.gemini_service import GeminiService
# portfolio_demo.py
import asyncio
import sys
import os

# Path fix
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import with error handling
try:
    from agents.content_writer import ContentWriterAgent
    from agents.publisher import PublisherAgent
    from services.gemini_service import GeminiService
except ImportError as e:
    print(f"Import error: {e}")
    print("Using simplified version...")
    
    # Simplified ContentWriter
    class ContentWriterAgent:
        def __init__(self, gemini):
            self.gemini = gemini
            
        async def _write_article_introduction(self, **kwargs):
            prompt = f"Write a compelling introduction about {kwargs.get('product_name', 'AI Security')}"
            response = await self.gemini.generate_content(prompt)
            return {"introduction": {"content": response}}
            
        async def _write_main_content_sections(self, **kwargs):
            prompt = f"Write detailed main content about {kwargs.get('product_name', 'AI Security')}"
            response = await self.gemini.generate_content(prompt)
            return {"main_content": {"content": response}}
            
        async def _write_article_conclusion(self, **kwargs):
            prompt = f"Write a conclusion about {kwargs.get('product_name', 'AI Security')}"
            response = await self.gemini.generate_content(prompt)
            return {"conclusion": {"content": response}}
            
        async def _finalize_article_structure(self, **kwargs):
            intro = kwargs.get('introduction', {}).get('introduction', {}).get('content', '')
            main = kwargs.get('main_content', {}).get('main_content', {}).get('content', '')
            conclusion = kwargs.get('conclusion', {}).get('conclusion', {}).get('content', '')
            
            complete_article = f"{intro}\n\n{main}\n\n{conclusion}"
            
            return {
                "final_article": {
                    "complete_article": complete_article,
                    "article_metrics": {
                        "total_word_count": len(complete_article.split())
                    }
                }
            }

async def create_portfolio_post():
    """Portfolio için tek seferlik blog post oluştur"""
    
    gemini = GeminiService()
    
    # Sadece Content Writer kullan (4-5 API call)
    writer = ContentWriterAgent(gemini)
    
    # Optimized mock data - gerçekçi görünsün
    mock_input = {
        "product_name": "AI-Powered Smart Home Security System",
        "niche": "Smart Home Technology",
        "target_audience": "Homeowners interested in advanced security",
        "content_plan": {
            "keyword_placement": {
                "keyword_placement": {
                    "primary_keywords": ["smart home security", "AI security system", "home automation"],
                    "secondary_keywords": ["wireless cameras", "motion detection", "mobile alerts"]
                }
            }
        },
        "seo_optimization": {
            "meta_optimization": {
                "meta_optimization": {
                    "meta_recommendations": {
                        "title_tags": ["Best AI Smart Home Security Systems 2024 - Complete Guide"],
                        "meta_descriptions": ["Discover how AI-powered security systems protect your home. Compare features, prices, and installation guides."]
                    }
                }
            }
        }
    }
    
    # Sadece kritik metodları çağır (API tasarrufu)
    print("📝 Creating portfolio content...")
    
    # Introduction (1 API call)
    intro = await writer._write_article_introduction(**mock_input)
    
    # Main content (1 API call) 
    main = await writer._write_main_content_sections(
        introduction=intro,
        **mock_input
    )
    
    # Conclusion (1 API call)
    conclusion = await writer._write_article_conclusion(
        introduction=intro,
        main_content=main,
        **mock_input
    )
    
    # Final assembly (1 API call)
    final = await writer._finalize_article_structure(
        introduction=intro,
        main_content=main,
        conclusion=conclusion,
        faq_section={"faq_section": {"content": ""}},  # Skip FAQ
        **mock_input
    )
    
    print("✅ Content created!")
    print(f"Word count: {final['final_article']['article_metrics']['total_word_count']}")
    
    # WordPress'e yayınla
    wp_config = {
        "url": "http://localhost/wordpress",
        "username": "admin", 
        "password": "2025*Ommer."
    }
    
    publisher = PublisherAgent(gemini, wp_config)
    result = await publisher.execute({
        "content_writer": {
            "final_article": final["final_article"]  # Doğru yapı
        }
    })
    
    if result.success:
        pub_data = result.data['publication_summary']
        print(f"🎉 Published to WordPress!")
        print(f"📌 Post URL: {pub_data['post_url']}")
        print(f"✏️ Edit URL: {pub_data['edit_url']}")
    
    return result

# Çalıştır
if __name__ == "__main__":
    asyncio.run(create_portfolio_post())