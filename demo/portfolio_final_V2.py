# portfolio_with_images.py - Görsel destekli versiyon
import asyncio
import sys
import os
import aiohttp
import base64
import json
from datetime import datetime

sys.path.append('/Users/omersoy/Desktop/ai-seo-blog-generator')

from services.gemini_service import GeminiService

async def get_unsplash_image(keyword="smart home security AI"):
    """Unsplash'tan ücretsiz görsel al"""
    try:
        # Demo access key - kendi key'inizi alın: https://unsplash.com/developers
        access_key = "jXJrnMfQd_LxmkNIaWq6AIV0satcldLlfoTVolv7PtE"  # Buraya kendi key'inizi koyun
        
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": keyword,
            "per_page": 3,
            "orientation": "landscape",
            "order_by": "relevant"
        }
        headers = {"Authorization": f"Client-ID {access_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['results']:
                        # En yüksek kaliteli görseli seç
                        best_image = data['results'][0]
                        return {
                            'url': best_image['urls']['regular'],
                            'alt_text': best_image['alt_description'] or keyword,
                            'photographer': best_image['user']['name']
                        }
    except Exception as e:
        print(f"⚠️  Unsplash error: {e}")
    
    # Fallback: Pixabay veya başka API
    return await get_pixabay_image(keyword)

async def get_pixabay_image(keyword="smart home security"):
    """Pixabay'den ücretsiz görsel al (backup)"""
    try:
        # Pixabay API key - ücretsiz: https://pixabay.com/api/docs/
        api_key = "51816305-329c0f8a3270b18b5a481c271"
        
        url = "https://pixabay.com/api/"
        params = {
            "key": api_key,
            "q": keyword,
            "image_type": "photo",
            "orientation": "horizontal",
            "category": "science",
            "min_width": 1200,
            "per_page": 3
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['hits']:
                        best_image = data['hits'][0]
                        return {
                            'url': best_image['webformatURL'],
                            'alt_text': f"Smart home security system - {keyword}",
                            'photographer': best_image['user']
                        }
    except Exception as e:
        print(f"⚠️  Pixabay error: {e}")
    
    return None

async def upload_image_to_wordpress(image_info, wp_config):
    """Görseli WordPress media library'ye yükle"""
    if not image_info:
        return None
        
    try:
        print(f"📸 Downloading image from: {image_info['url']}")
        
        # Görseli indir
        async with aiohttp.ClientSession() as session:
            async with session.get(image_info['url']) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                else:
                    print(f"❌ Failed to download image: {resp.status}")
                    return None
        
        # WordPress'e yükle
        auth = base64.b64encode(f"{wp_config['username']}:{wp_config['password']}".encode()).decode()
        
        url = f"{wp_config['url']}/wp-json/wp/v2/media"
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Disposition": "attachment; filename=ai-smart-home-security.jpg",
            "Content-Type": "image/jpeg"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=image_data, headers=headers) as resp:
                if resp.status == 201:
                    media_data = await resp.json()
                    print(f"✅ Image uploaded! Media ID: {media_data['id']}")
                    
                    # Alt text ve caption ekle
                    update_url = f"{wp_config['url']}/wp-json/wp/v2/media/{media_data['id']}"
                    update_data = {
                        "alt_text": image_info['alt_text'],
                        "caption": f"Photo by {image_info.get('photographer', 'Unknown')}",
                        "description": "AI-powered smart home security system illustration"
                    }
                    
                    async with session.post(update_url, 
                                          data=json.dumps(update_data), 
                                          headers={"Authorization": f"Basic {auth}", 
                                                 "Content-Type": "application/json"}) as update_resp:
                        if update_resp.status == 200:
                            print("✅ Image metadata updated")
                    
                    return media_data['id']
                else:
                    print(f"❌ Failed to upload image: {resp.status}")
                    error_text = await resp.text()
                    print(f"Error details: {error_text}")
                    
    except Exception as e:
        print(f"❌ Image upload error: {e}")
    
    return None

async def create_portfolio_post_with_images():
    """Portfolio için görsel destekli profesyonel blog post oluştur"""
    
    print("🚀 AI SEO Blog Generator - Portfolio Demo (With Images)")
    print("=" * 60)
    
    gemini = GeminiService()
    
    # Professional prompt with image placeholders
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
    - Professional tone with expert insights
    - Specific examples and real data points
    - Actionable advice and recommendations
    - Technical details but accessible language
    
    Format with proper HTML tags (h2, h3, p, ul, li, strong, em).
    Include sections where images would enhance understanding.
    """
    
    print("📝 Generating professional content...")
    
    try:
        # Content oluştur
        content = await gemini.generate_content(prompt)
        word_count = len(content.split())
        print(f"✅ Generated {word_count} words")
        
        # WordPress config
        wp_config = {
            "url": "http://localhost/wordpress",
            "username": "admin",
            "password": "2025*Ommer."
        }
        
        # Featured image al ve yükle
        print("\n📸 Fetching featured image...")
        image_info = await get_unsplash_image("AI smart home security system")
        
        featured_media_id = 0
        if image_info:
            featured_media_id = await upload_image_to_wordpress(image_info, wp_config)
            if not featured_media_id:
                print("⚠️  Using fallback: no featured image")
        else:
            print("⚠️  No image found, posting without featured image")
        
        # WordPress'e post at
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
            "excerpt": "Discover how AI is revolutionizing home security. Compare top systems, understand key features, and learn how to protect your home with cutting-edge technology in 2024.",
            "status": "publish",
            "featured_media": featured_media_id if featured_media_id else 0,
            "categories": [],  # Kategori ID'leri buraya ekleyin
            "tags": [],  # Tag ID'leri buraya ekleyin
            "meta": {
                "description": "Complete guide to AI-powered smart home security systems. Features, benefits, top products, and installation tips for 2024.",
            }
        }
        
        print("📤 Publishing to WordPress with featured image...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(post_data), headers=headers) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    
                    print("\n" + "="*60)
                    print("🎉 SUCCESSFULLY PUBLISHED WITH IMAGES!")
                    print("="*60)
                    print(f"📌 Post ID: {data['id']}")
                    print(f"🔗 Live URL: {data['link']}")
                    print(f"✏️  Edit URL: {wp_config['url']}/wp-admin/post.php?post={data['id']}&action=edit")
                    if featured_media_id:
                        print(f"🖼️  Featured Image ID: {featured_media_id}")
                    print("="*60)
                    
                    # Portfolio için bilgiler
                    print("\n📸 PORTFOLIO DOCUMENTATION:")
                    print("1. ✅ Live post with featured image")
                    print("2. ✅ WordPress admin screenshot")
                    print("3. ✅ Terminal output screenshot")
                    print("4. ✅ Image in media library")
                    
                    print("\n📋 UPWORK PORTFOLIO DESCRIPTION:")
                    print("-" * 50)
                    print("Title: AI SEO Blog Generator with Auto-Images")
                    print("\nTech Stack:")
                    print("• Python async/await architecture")
                    print("• Google Gemini AI integration")
                    print("• WordPress REST API")
                    print("• Unsplash/Pixabay API integration")
                    print("• Automated image processing")
                    print("• SEO optimization")
                    
                    print(f"\nResults:")
                    print(f"• {word_count}+ words of professional content")
                    print("• Automatically sourced and uploaded featured image")
                    print("• SEO-optimized with proper meta tags")
                    print("• Published live in seconds")
                    print(f"• Completed in {datetime.now().strftime('%B %Y')}")
                    
                    return data
                else:
                    print(f"❌ Failed to publish: {resp.status}")
                    error_text = await resp.text()
                    print(f"Error details: {error_text}")
                    
    except Exception as e:
        if "quota" in str(e).lower():
            print("❌ API Quota exceeded!")
            print("\n💡 Solutions:")
            print("1. Get new Google/Gemini API key")
            print("2. Wait for quota reset")
            print("3. Use different AI service (OpenAI, Claude)")
        else:
            print(f"❌ Error: {e}")
    
    return None

# Hızlı test için statik görsel fonksiyonu
async def quick_image_test():
    """API key yoksa statik görsel ile test"""
    wp_config = {
        "url": "http://localhost/wordpress",
        "username": "admin",
        "password": "2025*Ommer."
    }
    
    # Statik görsel URL (Creative Commons)
    static_image = {
        'url': 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=1200',
        'alt_text': 'Smart home security system with AI technology',
        'photographer': 'Unsplash'
    }
    
    media_id = await upload_image_to_wordpress(static_image, wp_config)
    print(f"Test image upload result: {media_id}")

if __name__ == "__main__":
    # Ana fonksiyon
    asyncio.run(create_portfolio_post_with_images())
    
    # Sadece görsel testi için:
    # asyncio.run(quick_image_test())