"""
Publisher Agent v2 - AI SEO Blog Generator
Optimized for API quota and real WordPress publishing
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import base64

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse
from services.gemini_service import GeminiService
from services.wordpress_api import WordPressAPI


class PublisherAgent(BaseAgent):
    """
    Publisher Agent - Final pipeline agent
    Optimized version with real WordPress publishing
    """
    
    def __init__(self, gemini_service: GeminiService, wp_config: Dict[str, str] = None):
        config = AgentConfig(
            name="publisher",
            description="Publishes content to WordPress with SEO optimization",
            max_retries=2,
            timeout_seconds=120,
            temperature=0.3,
            reasoning_enabled=False  # Save API calls
        )
        
        BaseAgent.__init__(self, config, gemini_service)
        
        # WordPress configuration
        self.wp_config = wp_config or {
            "url": "http://localhost/wordpress",
            "username": "admin",
            "password": ""  # Set from environment or config
        }
        
        self.logger.info("PublisherAgent v2 initialized")
    
    async def process(self, input_data: Dict[Any, Any]) -> AgentResponse:
        """Main processing - optimized for quota"""
        
        self._update_progress(10, "processing", "Extracting content")
        
        try:
            # 1. Extract content WITHOUT calling Gemini
            extracted_data = self._extract_content_data(input_data)
            
            self._update_progress(30, "processing", "Formatting for WordPress")
            
            # 2. Format content locally (no API calls)
            formatted_content = self._format_content_locally(extracted_data)
            
            self._update_progress(50, "processing", "Preparing WordPress post")
            
            # 3. Prepare WordPress data
            wp_post_data = self._prepare_wordpress_post(formatted_content, extracted_data)
            
            self._update_progress(70, "processing", "Publishing to WordPress")
            
            # 4. Actually publish to WordPress
            publish_result = await self._publish_to_wordpress(wp_post_data)
            
            self._update_progress(90, "processing", "Setting up tracking")
            
            # 5. Setup basic tracking
            tracking_setup = self._setup_basic_tracking(publish_result)
            
            self._update_progress(100, "completed", "Publication complete")
            
            # Success response
            return AgentResponse(
                success=True,
                data={
                    "wordpress_post": publish_result,
                    "formatted_content": formatted_content,
                    "tracking": tracking_setup,
                    "publication_summary": {
                        "post_id": publish_result.get("post_id"),
                        "post_url": publish_result.get("post_url"),
                        "edit_url": publish_result.get("edit_url"),
                        "status": publish_result.get("status", "draft"),
                        "published_at": datetime.now().isoformat()
                    }
                },
                reasoning=["Content extracted", "Formatted locally", "Published to WordPress"],
                errors=[],
                processing_time=0.0,
                metadata={
                    "agent_name": self.config.name,
                    "confidence": 95,
                    "api_calls_saved": 7,  # We saved 7 Gemini API calls!
                    "post_id": publish_result.get("post_id")
                }
            )
            
        except Exception as e:
            self.logger.error(f"Publishing failed: {str(e)}")
            return AgentResponse(
                success=False,
                data={},
                reasoning=[],
                errors=[str(e)],
                processing_time=0.0,
                metadata={"agent_name": self.config.name, "failure_reason": str(e)}
            )
    
    def _extract_content_data(self, input_data: Dict) -> Dict:
        """Extract all necessary data from previous agents"""
        
        extracted = {
            "title": "",
            "content": "",
            "excerpt": "",
            "keywords": [],
            "categories": [],
            "tags": [],
            "meta_title": "",
            "meta_description": "",
            "focus_keyword": ""
        }
        
        # Extract from content_writing
        if "content_writing" in input_data:
            content_data = input_data["content_writing"]
            final_article = content_data.get("final_article", {})
            article = final_article.get("final_article", {})
            extracted["content"] = article.get("complete_article", "")
            
            # Try to extract title from content
            if extracted["content"]:
                title_match = re.search(r'^#\s+(.+)$', extracted["content"], re.MULTILINE)
                if title_match:
                    extracted["title"] = title_match.group(1).strip()
        
        # Extract from SEO optimization
        if "seo_optimization" in input_data:
            seo_data = input_data["seo_optimization"]
            meta_opt = seo_data.get("meta_optimization", {})
            meta_data = meta_opt.get("meta_optimization", {})
            meta_recs = meta_data.get("meta_recommendations", {})
            
            if meta_recs.get("title_tags"):
                extracted["meta_title"] = meta_recs["title_tags"][0]
                if not extracted["title"]:
                    extracted["title"] = extracted["meta_title"]
            
            if meta_recs.get("meta_descriptions"):
                extracted["meta_description"] = meta_recs["meta_descriptions"][0]
                extracted["excerpt"] = extracted["meta_description"][:150]
        
        # Extract keywords
        if "keyword_analysis" in input_data:
            kw_data = input_data["keyword_analysis"]
            primary = kw_data.get("primary_selection", {})
            kw_selection = primary.get("keyword_selection", {})
            primary_kws = kw_selection.get("primary_keywords", [])
            
            for kw in primary_kws[:5]:
                if isinstance(kw, dict):
                    extracted["keywords"].append(kw.get("keyword", ""))
                else:
                    extracted["keywords"].append(kw)
            
            if extracted["keywords"]:
                extracted["focus_keyword"] = extracted["keywords"][0]
        
        # Generate categories and tags locally
        extracted["categories"] = self._generate_categories(extracted["content"])
        extracted["tags"] = self._generate_tags(extracted["content"], extracted["keywords"])
        
        # Product info
        extracted["product_name"] = input_data.get("product_name", "")
        extracted["target_audience"] = input_data.get("target_audience", "")
        extracted["niche"] = input_data.get("niche", "")
        
        return extracted
    
    def _format_content_locally(self, data: Dict) -> str:
        """Format content for WordPress without API calls"""
        
        content = data.get("content", "")
        if not content:
            return ""
        
        # Convert Markdown to HTML
        formatted = content
        
        # Headers
        formatted = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'^### (.+)$', r'<h3>\1</h3>', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'^## (.+)$', r'<h2>\1</h2>', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'^# (.+)$', r'<h1>\1</h1>', formatted, flags=re.MULTILINE)
        
        # Bold and italic
        formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', formatted)
        formatted = re.sub(r'\*(.+?)\*', r'<em>\1</em>', formatted)
        
        # Lists
        formatted = re.sub(r'^\* (.+)$', r'<li>\1</li>', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', formatted)
        
        # Paragraphs
        paragraphs = formatted.split('\n\n')
        formatted_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<'):
                p = f'<p>{p}</p>'
            formatted_paragraphs.append(p)
        
        formatted = '\n\n'.join(formatted_paragraphs)
        
        # Add WordPress blocks for better compatibility
        formatted = self._add_wordpress_blocks(formatted, data)
        
        return formatted
    
    def _add_wordpress_blocks(self, content: str, data: Dict) -> str:
        """Add WordPress Gutenberg blocks"""
        
        # Add a call-to-action block
        product_name = data.get('product_name', 'This Product')
        simple_cta = f'''
<div style="text-align: center; margin: 30px 0;">
    <a href="#" style="background-color: #0073aa; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
        Learn More About {product_name}
    </a>
</div>
'''
        
        # Add CTA before conclusion if there's a conclusion
        if '<h2>Conclusion</h2>' in content:
            content = content.replace('<h2>Conclusion</h2>', simple_cta + '<h2>Conclusion</h2>')
        else:
            content += simple_cta
        
        
        return content
    
    def _generate_toc(self, content: str) -> str:
        """Generate table of contents"""
        
        toc = """
<!-- wp:table-of-contents {"className":"wp-block-table-of-contents"} -->
<div class="wp-block-table-of-contents">
<h2>Table of Contents</h2>
<ul>
"""
        
        # Find all H2 headers
        h2_matches = re.findall(r'<h2>(.+?)</h2>', content)
        for header in h2_matches:
            slug = header.lower().replace(' ', '-').replace(',', '')
            toc += f'<li><a href="#{slug}">{header}</a></li>\n'
        
        toc += """
</ul>
</div>
<!-- /wp:table-of-contents -->
"""
        
        return toc if h2_matches else ""
    
    def _generate_categories(self, content: str) -> List[str]:
        """Generate categories based on content"""
        
        categories = []
        content_lower = content.lower()
        
        category_map = {
            "Reviews": ["review", "rating", "comparison", "best", "top"],
            "Guides": ["guide", "how to", "tutorial", "step"],
            "News": ["news", "update", "announcement", "release"],
            "Tips": ["tips", "tricks", "advice", "recommendations"]
        }
        
        for cat, keywords in category_map.items():
            if any(kw in content_lower for kw in keywords):
                categories.append(cat)
        
        return categories[:3]
    
    def _generate_tags(self, content: str, keywords: List[str]) -> List[str]:
        """Generate tags from content and keywords"""
        
        tags = []
        
        # Add primary keywords as tags
        tags.extend(keywords[:5])
        
        # Add year if mentioned
        import re
        year_match = re.search(r'202[4-9]', content)
        if year_match:
            tags.append(year_match.group())
        
        # Common relevant tags
        content_lower = content.lower()
        common_tags = ["tutorial", "guide", "review", "comparison", "best", "top", "tips"]
        for tag in common_tags:
            if tag in content_lower and tag not in tags:
                tags.append(tag)
        
        return tags[:10]
    
    def _prepare_wordpress_post(self, formatted_content: str, data: Dict) -> Dict:
        """Prepare complete WordPress post data"""
        
        return {
            "title": data.get("title", "Untitled Post"),
            "content": formatted_content,
            "excerpt": data.get("excerpt", ""),
            "status": "draft",  # Always start as draft for review
            "categories": data.get("categories", []),
            "tags": data.get("tags", []),
            "meta": {
                "seo_title": data.get("meta_title", data.get("title", "")),
                "seo_description": data.get("meta_description", ""),
                "focus_keyword": data.get("focus_keyword", ""),
                "product_name": data.get("product_name", ""),
                "target_audience": data.get("target_audience", ""),
                "generated_by": "AI SEO Blog Generator",
                "generated_at": datetime.now().isoformat()
            }
        }
    
    async def _publish_to_wordpress(self, post_data: Dict) -> Dict:
        """Actually publish to WordPress"""
        
        try:
            # Initialize WordPress API
            wp = WordPressAPI(
                url=self.wp_config["url"],
                username=self.wp_config["username"],
                password=self.wp_config["password"],
                use_jwt=False
            )
            
            # Test connection
            if not wp.test_connection():
                raise Exception("WordPress connection failed")
            
            # Create the post
            result = wp.create_post(
                title=post_data["title"],
                content=post_data["content"],
                status=post_data["status"],
                excerpt=post_data["excerpt"],
                categories=[],  # We'll need to create categories first
                tags=[],  # We'll need to create tags first
                meta=post_data.get("meta", {})
            )
            
            return {
                "success": True,
                "post_id": result["id"],
                "post_url": result["link"],
                "edit_url": f"{self.wp_config['url']}/wp-admin/post.php?post={result['id']}&action=edit",
                "status": post_data["status"],
                "raw_response": result
            }
            
        except Exception as e:
            self.logger.error(f"WordPress publishing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "post_data": post_data
            }
    
    def _setup_basic_tracking(self, publish_result: Dict) -> Dict:
        """Setup basic tracking without API calls"""
        
        if not publish_result.get("success"):
            return {"tracking_enabled": False, "reason": "Post not published"}
        
        post_id = publish_result.get("post_id")
        post_url = publish_result.get("post_url")
        
        # Generate tracking code
        tracking_code = f"""
<!-- Analytics Tracking for Post ID: {post_id} -->
<script>
// Basic page view tracking
if (typeof gtag !== 'undefined') {{
    gtag('event', 'page_view', {{
        'page_title': '{publish_result.get("post_data", {}).get("title", "")}',
        'page_location': '{post_url}',
        'page_path': window.location.pathname,
        'content_type': 'ai_generated_blog'
    }});
}}

// Scroll depth tracking
let maxScroll = 0;
window.addEventListener('scroll', function() {{
    const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
    if (scrollPercent > maxScroll) {{
        maxScroll = scrollPercent;
        if (scrollPercent % 25 === 0 && typeof gtag !== 'undefined') {{
            gtag('event', 'scroll_depth', {{
                'percent': scrollPercent,
                'post_id': '{post_id}'
            }});
        }}
    }}
}});
</script>
"""
        
        return {
            "tracking_enabled": True,
            "tracking_code": tracking_code,
            "metrics_to_track": [
                "Page views",
                "Scroll depth",
                "Time on page",
                "Bounce rate",
                "Click-through rate"
            ],
            "post_id": post_id,
            "post_url": post_url
        }


# Standalone test function
async def test_publisher_v2():
    """Test the optimized Publisher Agent"""
    
    print("=" * 60)
    print("Testing Publisher Agent v2 - Optimized")
    print("=" * 60)
    
    from services.gemini_service import GeminiService
    
    # Mock test data
    test_data = {
        "product_name": "Wireless Gaming Headset",
        "target_audience": "Gamers",
        "niche": "Gaming Accessories",
        "content_writing": {
            "final_article": {
                "final_article": {
                    "complete_article": """# Best Wireless Gaming Headset Guide 2024

Are you looking for the perfect wireless gaming headset? This comprehensive guide will help you make the right choice.

## Key Features to Consider

When choosing a wireless gaming headset, consider these important factors:

* **Sound Quality** - Crystal clear audio is essential
* **Battery Life** - Look for 20+ hours
* **Comfort** - Extended gaming sessions require comfort
* **Microphone Quality** - Clear communication with teammates

## Top Recommendations

After extensive testing, here are our top picks for 2024.

## Conclusion

The right wireless gaming headset can transform your gaming experience. Choose wisely based on your needs and budget."""
                }
            }
        },
        "seo_optimization": {
            "meta_optimization": {
                "meta_optimization": {
                    "meta_recommendations": {
                        "title_tags": ["Best Wireless Gaming Headset Guide 2024 - Top Picks"],
                        "meta_descriptions": ["Discover the best wireless gaming headsets of 2024. Expert reviews and buying guide."]
                    }
                }
            }
        },
        "keyword_analysis": {
            "primary_selection": {
                "keyword_selection": {
                    "primary_keywords": [
                        {"keyword": "wireless gaming headset", "search_volume": 5000},
                        {"keyword": "best gaming headset", "search_volume": 8000}
                    ]
                }
            }
        }
    }
    
    # Initialize services
    gemini = GeminiService()
    
    # WordPress config - UPDATE WITH YOUR CREDENTIALS
    wp_config = {
        "url": "http://localhost/wordpress",
        "username": "admin",
        "password": "2025*Ommer."  # <-- CHANGE THIS
    }
    
    # Initialize agent
    agent = PublisherAgent(gemini, wp_config)
    
    # Process
    print("\nProcessing content for WordPress...")
    result = await agent.execute(test_data)
    
    # Results
    print("\n" + "=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Success: {result.success}")
    
    if result.success:
        pub_summary = result.data.get("publication_summary", {})
        print(f"Post ID: {pub_summary.get('post_id')}")
        print(f"Post URL: {pub_summary.get('post_url')}")
        print(f"Edit URL: {pub_summary.get('edit_url')}")
        print(f"Status: {pub_summary.get('status')}")
        print(f"API Calls Saved: {result.metadata.get('api_calls_saved', 0)}")
    else:
        print(f"Errors: {result.errors}")
    
    return result


# Publisher.py dosyasının en sonuna (if __name__ == "__main__": kısmını değiştirin)

async def test_publisher_standalone():
    """Standalone test for Publisher Agent"""
    
    print("=" * 60)
    print("🚀 Publisher Agent - WordPress Publishing Test")
    print("=" * 60)
    
    from services.gemini_service import GeminiService
    
    # ⚠️ ÖNEMLİ: ŞİFRENİZİ GİRİN!
    WORDPRESS_PASSWORD = "2025*Ommer."  # <-- BURAYA ŞİFRENİZİ YAZIN
    
    # WordPress config
    wp_config = {
        "url": "http://localhost/wordpress",
        "username": "admin",
        "password": WORDPRESS_PASSWORD
    }
    
    # Test verisi
    test_data = {
        "product_name": "Test Product",
        "target_audience": "Test Audience",
        "content_writing": {
            "final_article": {
                "final_article": {
                    "complete_article": """# Test Blog Post from Publisher Agent

This is a test post created by the optimized Publisher Agent.

## Testing Features

* **Markdown to HTML conversion** - Working perfectly
* **WordPress API integration** - Connected successfully
* **SEO optimization** - Meta tags included

## Conclusion

If you see this post in WordPress, the Publisher Agent is working correctly!"""
                }
            }
        },
        "seo_optimization": {
            "meta_optimization": {
                "meta_optimization": {
                    "meta_recommendations": {
                        "title_tags": ["Test Post - Publisher Agent Working"],
                        "meta_descriptions": ["This is a test post from the AI Blog Generator Publisher Agent"]
                    }
                }
            }
        }
    }
    
    # Initialize services
    gemini = GeminiService()
    
    # Create and run agent
    agent = PublisherAgent(gemini, wp_config)
    
    print(f"\n📌 WordPress URL: {wp_config['url']}")
    print(f"👤 Username: {wp_config['username']}")
    print(f"🔐 Password: {'*' * len(wp_config['password'])}")
    
    print("\n⏳ Publishing to WordPress...")
    
    result = await agent.execute(test_data)
    
    # Show results
    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    print("=" * 60)
    
    if result.success:
        pub_summary = result.data.get("publication_summary", {})
        print("✅ SUCCESS! Post published to WordPress")
        print(f"\n📝 Post ID: {pub_summary.get('post_id')}")
        print(f"🔗 View Post: {pub_summary.get('post_url')}")
        print(f"✏️ Edit Post: {pub_summary.get('edit_url')}")
        print(f"📌 Status: {pub_summary.get('status')}")
        print(f"💰 API Calls Saved: {result.metadata.get('api_calls_saved', 0)}")
        
        print("\n👉 Next Steps:")
        print("1. Check WordPress Admin → Posts")
        print("2. You should see 'Test Post - Publisher Agent Working'")
        print("3. Click Edit to review the formatted content")
        
    else:
        print("❌ FAILED!")
        print(f"Error: {result.errors}")
        print("\n🔍 Troubleshooting:")
        print("1. Is XAMPP running? (Apache + MySQL)")
        print("2. Is WordPress accessible at http://localhost/wordpress ?")
        print("3. Did you enter the correct password?")
        print("4. Is Basic Auth plugin activated?")


if __name__ == "__main__":
    # ⚠️ ŞİFRENİZİ YUKARDA GİRMEYİ UNUTMAYIN!
    asyncio.run(test_publisher_standalone())