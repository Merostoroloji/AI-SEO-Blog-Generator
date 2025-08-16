# portfolio_final.py - Çalışan final versiyon
import asyncio
import sys
import os
import aiohttp
import base64
import json
from datetime import datetime

sys.path.append('/Users/omersoy/Desktop/ai-seo-blog-generator')

from services.gemini_service import GeminiService

async def create_portfolio_post():
    """Portfolio için profesyonel blog post oluştur"""
    
    print("🚀 AI SEO Blog Generator - Portfolio Demo")
    print("=" * 50)
    
    gemini = GeminiService()
    
    # Professional prompt
    prompt = """
    Write a comprehensive 2000+ word SEO-optimized blog article about "AI-Powered Smart Home Security Systems".
    
    Structure:
    1. Compelling introduction with the main keyword
    2. What are AI-Powered Security Systems?
    3. Key Features and Technologies
    4. Benefits Over Traditional Systems
    5. Top Products in 2024
    6. Installation and Setup Guide
    7. Cost Analysis
    8. Privacy and Security Considerations
    9. Future Trends
    10. Conclusion with call-to-action
    
    Include:
    - Use keywords naturally: "smart home security", "AI security system", "home automation"
    - Professional tone
    - Specific examples and data points
    - Actionable advice
    
    Format with proper HTML tags (h2, h3, p, ul, li).
    """
    
    print("📝 Generating professional content...")
    
    try:
        content = await gemini.generate_content(prompt)
        word_count = len(content.split())
        print(f"✅ Generated {word_count} words")
        
        # WordPress'e yayınla
        wp_config = {
            "url": "http://localhost/wordpress",
            "username": "admin",
            "password": "2025*Ommer."
        }
        
        auth = base64.b64encode(f"{wp_config['username']}:{wp_config['password']}".encode()).decode()
        
        url = f"{wp_config['url']}/wp-json/wp/v2/posts"
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        
        # Professional meta data
        post_data = {
            "title": "AI-Powered Smart Home Security Systems: Complete Guide 2024",
            "content": content,
            "excerpt": "Discover how AI is revolutionizing home security. Compare top systems, understand key features, and learn how to protect your home with cutting-edge technology.",
            "status": "publish",  # Direkt yayınla
            "categories": [],  # Kategori ID'leri
            "tags": [],  # Tag ID'leri
            "featured_media": 0  # Featured image ID
        }
        
        print("📤 Publishing to WordPress...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(post_data), headers=headers) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    
                    print("\n" + "="*50)
                    print("🎉 SUCCESSFULLY PUBLISHED!")
                    print("="*50)
                    print(f"📌 Post ID: {data['id']}")
                    print(f"🔗 Live URL: {data['link']}")
                    print(f"✏️ Edit URL: {wp_config['url']}/wp-admin/post.php?post={data['id']}&action=edit")
                    print("="*50)
                    
                    # Portfolio için bilgiler
                    print("\n📸 PORTFOLIO SCREENSHOTS:")
                    print("1. Take screenshot of the live post")
                    print("2. Take screenshot of WordPress admin")
                    print("3. Take screenshot of this terminal output")
                    
                    print("\n📋 UPWORK PORTFOLIO DESCRIPTION:")
                    print("-" * 40)
                    print("Title: AI-Powered SEO Blog Generator")
                    print("\nDescription:")
                    print("Developed an automated blog generation system using:")
                    print("• Python async architecture")
                    print("• Google Gemini AI integration")
                    print("• WordPress REST API")
                    print("• SEO optimization techniques")
                    print(f"• Generated {word_count}+ words in {datetime.now().strftime('%B %Y')}")
                    print("\nResult: Professional, SEO-optimized content published automatically")
                    
                    return data
                else:
                    print(f"❌ Failed: {resp.status}")
                    print(await resp.text())
                    
    except Exception as e:
        if "quota" in str(e).lower():
            print("❌ API Quota exceeded!")
            print("\n💡 Solutions:")
            print("1. Use a different Google account for new API key")
            print("2. Wait 24 hours for quota reset")
            print("3. Use the instant_portfolio.py script with static content")
        else:
            print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    asyncio.run(create_portfolio_post())