# debug_portfolio.py - Oluşturun ve çalıştırın
import asyncio
import sys
import os
sys.path.append('/Users/omersoy/Desktop/ai-seo-blog-generator')

from demo.portfolio_demo import create_portfolio_post

async def debug_run():
    """Debug için içeriği göster"""
    
    # Import services
    from services.gemini_service import GeminiService
    from demo.portfolio_demo import ContentWriterAgent
    
    gemini = GeminiService()
    writer = ContentWriterAgent(gemini)
    
    mock_input = {
        "product_name": "AI-Powered Smart Home Security System",
        "niche": "Smart Home Technology",
        "target_audience": "Homeowners interested in advanced security",
    }
    
    print("📝 Creating content...")
    
    # Test introduction
    intro = await writer._write_article_introduction(**mock_input)
    print(f"\n✅ INTRO: {intro['introduction']['content'][:200]}...")
    
    # Test final
    final = await writer._finalize_article_structure(
        introduction=intro,
        main_content={"main_content": {"content": "Test main content"}},
        conclusion={"conclusion": {"content": "Test conclusion"}},
        faq_section={"faq_section": {"content": ""}},
        **mock_input
    )
    
    # CONTENT VAR MI?
    content = final.get('final_article', {}).get('complete_article', '')
    print(f"\n📄 FINAL CONTENT LENGTH: {len(content)}")
    print(f"📄 FINAL CONTENT PREVIEW: {content[:500]}")
    
    if not content:
        print("❌ NO CONTENT GENERATED!")
    else:
        print("✅ Content exists, trying direct WordPress publish...")
        
        # DIRECT WORDPRESS PUBLISH
        import aiohttp
        import base64
        import json
        
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
        
        post_data = {
            "title": "Test Post from Debug Script",
            "content": content if content else "Default test content",
            "status": "draft"
        }
        
        print(f"\n📤 Sending to WordPress...")
        print(f"   Title: {post_data['title']}")
        print(f"   Content length: {len(post_data['content'])}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(post_data), headers=headers) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    print(f"✅ SUCCESS! Post ID: {data['id']}")
                    print(f"📌 URL: {data['link']}")
                else:
                    print(f"❌ Failed: {resp.status}")
                    print(await resp.text())

asyncio.run(debug_run())