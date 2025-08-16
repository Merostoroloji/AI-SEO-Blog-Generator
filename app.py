"""
Streamlit UI for AI SEO Blog Generator
Professional interface for blog generation with multiple AI models
"""

import streamlit as st
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page config
st.set_page_config(
    page_title="AI SEO Blog Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []
if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {}
if 'wordpress_config' not in st.session_state:
    st.session_state.wordpress_config = {}

# AI Service Classes
class AIServiceFactory:
    """Factory for creating AI service instances"""
    
    @staticmethod
    def create_service(model_type: str, api_key: str):
        """Create appropriate AI service based on model type"""
        
        if model_type == "Gemini":
            return GeminiService(api_key)
        elif model_type == "GPT-4":
            return GPTService(api_key)
        elif model_type == "Claude":
            return ClaudeService(api_key)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

class GeminiService:
    """Google Gemini AI Service"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gemini-1.5-flash"
    
    async def generate_content(self, prompt: str) -> str:
        """Generate content using Gemini"""
        import aiohttp
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    error = await response.text()
                    raise Exception(f"Gemini API error: {error}")

class GPTService:
    """OpenAI GPT Service"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gpt-4-turbo-preview"
    
    async def generate_content(self, prompt: str) -> str:
        """Generate content using GPT-4"""
        import aiohttp
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert SEO content writer."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    error = await response.text()
                    raise Exception(f"GPT API error: {error}")

class ClaudeService:
    """Anthropic Claude Service"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "claude-3-opus-20240229"
    
    async def generate_content(self, prompt: str) -> str:
        """Generate content using Claude"""
        import aiohttp
        
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 4000,
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['content'][0]['text']
                else:
                    error = await response.text()
                    raise Exception(f"Claude API error: {error}")

class BlogGenerator:
    """Main blog generation logic"""
    
    def __init__(self, ai_service):
        self.ai_service = ai_service
    
    async def generate_blog(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate blog content based on configuration"""
        
        # Build prompt
        prompt = self._build_prompt(config)
        
        # Generate content
        content = await self.ai_service.generate_content(prompt)
        
        # Parse and structure content
        result = {
            "title": self._extract_title(content),
            "content": content,
            "word_count": len(content.split()),
            "keywords": config['keywords'],
            "target_audience": config['target_audience'],
            "generated_at": datetime.now().isoformat()
        }
        
        return result
    
    def _build_prompt(self, config: Dict[str, Any]) -> str:
        """Build generation prompt from config"""
        
        keywords = ", ".join(config['keywords'])
        
        prompt = f"""
        Write a comprehensive {config['content_length']}-word SEO-optimized blog article.
        
        Topic: {config['topic']}
        Target Audience: {config['target_audience']}
        Keywords to include: {keywords}
        Tone: {config['tone']}
        
        Structure:
        1. Compelling introduction with main keyword
        2. Well-organized main sections with H2 headers
        3. Detailed explanations and examples
        4. Conclusion with call-to-action
        
        Requirements:
        - Use keywords naturally throughout
        - Include specific data and examples
        - Make it engaging and valuable
        - Format with proper HTML tags (h1, h2, h3, p, ul, li)
        - Optimize for featured snippets
        
        Generate the complete article now:
        """
        
        return prompt
    
    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        import re
        
        # Try to find H1 tag
        h1_match = re.search(r'<h1>(.*?)</h1>', content, re.IGNORECASE)
        if h1_match:
            return h1_match.group(1)
        
        # Try to find first line
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                return line.strip()[:100]
        
        return "Untitled Article"

class WordPressPublisher:
    """WordPress publishing functionality"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
    
    async def publish(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Publish content to WordPress"""
        import aiohttp
        import base64
        
        # Prepare authentication
        credentials = f"{self.config['username']}:{self.config['password']}"
        auth_header = base64.b64encode(credentials.encode()).decode('ascii')
        
        # API endpoint
        url = f"{self.config['url']}/wp-json/wp/v2/posts"
        
        # Post data
        post_data = {
            "title": content['title'],
            "content": content['content'],
            "status": self.config.get('status', 'draft'),
            "excerpt": content.get('excerpt', '')
        }
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=post_data, headers=headers) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    return {
                        "success": True,
                        "post_id": data.get("id"),
                        "post_url": data.get("link"),
                        "edit_url": f"{self.config['url']}/wp-admin/post.php?post={data.get('id')}&action=edit"
                    }
                else:
                    error = await response.text()
                    return {
                        "success": False,
                        "error": error
                    }

# Main UI
def main():
    # Header
    st.markdown('<h1 class="main-header"> AI SEO Blog Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Generate professional SEO-optimized blog posts with AI</p>', unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # AI Model Selection
        st.subheader(" AI Model")
        model_type = st.selectbox(
            "Select AI Model",
            ["Gemini", "GPT-4", "Claude"],
            help="Choose which AI model to use for content generation"
        )
        
        # API Key Input
        api_key = st.text_input(
            f"{model_type} API Key",
            type="password",
            value=st.session_state.api_keys.get(model_type, ""),
            help=f"Enter your {model_type} API key"
        )
        
        if api_key:
            st.session_state.api_keys[model_type] = api_key
        
        # WordPress Configuration
        st.subheader(" WordPress Settings")
        
        wp_url = st.text_input(
            "WordPress URL",
            value=st.session_state.wordpress_config.get('url', 'http://localhost/wordpress'),
            help="Your WordPress site URL"
        )
        
        wp_username = st.text_input(
            "Username",
            value=st.session_state.wordpress_config.get('username', 'admin')
        )
        
        wp_password = st.text_input(
            "Password",
            type="password",
            value=st.session_state.wordpress_config.get('password', '')
        )
        
        wp_status = st.selectbox(
            "Post Status",
            ["draft", "publish"],
            help="Choose whether to save as draft or publish immediately"
        )
        
        # Save WordPress config
        st.session_state.wordpress_config = {
            'url': wp_url,
            'username': wp_username,
            'password': wp_password,
            'status': wp_status
        }
        
        # Advanced Settings
        with st.expander(" Advanced Settings"):
            temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7)
            max_retries = st.number_input("Max Retries", 1, 5, 3)
            timeout = st.number_input("Timeout (seconds)", 30, 300, 60)
    
    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Content Configuration")
        
        # Topic and Keywords
        topic = st.text_input(
            " Topic",
            placeholder="e.g., AI-Powered Smart Home Security Systems",
            help="Main topic for your blog post"
        )
        
        keywords_input = st.text_area(
            " Keywords (one per line)",
            placeholder="smart home security\nAI security system\nhome automation",
            height=100,
            help="Enter target keywords, one per line"
        )
        
        keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]
        
        # Target Audience
        target_audience = st.text_input(
            " Target Audience",
            placeholder="e.g., Homeowners interested in advanced security",
            help="Describe your target audience"
        )
        
        # Content Settings
        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            content_length = st.select_slider(
                "📏 Content Length",
                options=[500, 1000, 1500, 2000, 2500, 3000],
                value=2000,
                format_func=lambda x: f"{x} words"
            )
        
        with col1_2:
            tone = st.selectbox(
                "🎭 Tone",
                ["Professional", "Conversational", "Academic", "Casual", "Persuasive"]
            )
        
        # Generate Button
        st.markdown("---")
        
        if st.button(" Generate Blog Post", type="primary", use_container_width=True):
            if not api_key:
                st.error("⚠️ Please enter an API key in the sidebar")
            elif not topic:
                st.error("⚠️ Please enter a topic")
            elif not keywords:
                st.error("⚠️ Please enter at least one keyword")
            else:
                with st.spinner("🔄 Generating content..."):
                    try:
                        # Create configuration
                        config = {
                            'topic': topic,
                            'keywords': keywords,
                            'target_audience': target_audience,
                            'content_length': content_length,
                            'tone': tone
                        }
                        
                        # Create AI service
                        ai_service = AIServiceFactory.create_service(model_type, api_key)
                        
                        # Generate content
                        generator = BlogGenerator(ai_service)
                        
                        # Run async generation
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(generator.generate_blog(config))
                        
                        # Store in session state
                        st.session_state.generated_content = result
                        st.session_state.generation_history.append(result)
                        
                        st.success("✅ Content generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Generation failed: {str(e)}")
    
    with col2:
        st.header(" Generation Stats")
        
        # Display metrics
        if st.session_state.generated_content:
            content = st.session_state.generated_content
            
            st.metric("Word Count", content['word_count'])
            st.metric("Keywords Used", len(content['keywords']))
            st.metric("Generated At", content['generated_at'][:10])
            
            # Publish to WordPress button
            if st.button("Publish to WordPress", use_container_width=True):
                if not st.session_state.wordpress_config.get('password'):
                    st.error("⚠️ Please configure WordPress settings")
                else:
                    with st.spinner("📤 Publishing..."):
                        try:
                            publisher = WordPressPublisher(st.session_state.wordpress_config)
                            
                            # Run async publish
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            pub_result = loop.run_until_complete(publisher.publish(content))
                            
                            if pub_result['success']:
                                st.success("✅ Published to WordPress!")
                                st.info(f"🔗 [View Post]({pub_result['post_url']})")
                                st.info(f"✏️ [Edit Post]({pub_result['edit_url']})")
                            else:
                                st.error(f"❌ Publishing failed: {pub_result['error']}")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        # History
        st.header(" Generation History")
        if st.session_state.generation_history:
            for i, item in enumerate(reversed(st.session_state.generation_history[-5:])):
                with st.expander(f"{item['title'][:50]}..."):
                    st.write(f"**Words:** {item['word_count']}")
                    st.write(f"**Time:** {item['generated_at'][:16]}")
                    st.write(f"**Keywords:** {', '.join(item['keywords'][:3])}")
    
    # Generated Content Display
    if st.session_state.generated_content:
        st.markdown("---")
        st.header("📄 Generated Content")
        
        content = st.session_state.generated_content
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([" Preview", " HTML", " SEO Analysis", " Export"])
        
        with tab1:
            st.subheader(content['title'])
            st.markdown(content['content'], unsafe_allow_html=True)
        
        with tab2:
            st.code(content['content'], language='html')
        
        with tab3:
            # SEO Analysis
            st.subheader("SEO Analysis")
            
            col3_1, col3_2, col3_3 = st.columns(3)
            
            with col3_1:
                st.metric("Word Count", content['word_count'])
                
            with col3_2:
                # Calculate keyword density
                text_lower = content['content'].lower()
                total_density = sum(text_lower.count(kw.lower()) for kw in content['keywords'])
                st.metric("Keyword Mentions", total_density)
                
            with col3_3:
                # Readability score (simple estimation)
                sentences = content['content'].count('.') + content['content'].count('!') + content['content'].count('?')
                avg_sentence_length = content['word_count'] / max(sentences, 1)
                readability = "Good" if avg_sentence_length < 20 else "Complex"
                st.metric("Readability", readability)
            
            # Keyword distribution
            st.subheader("Keyword Distribution")
            for keyword in content['keywords']:
                count = text_lower.count(keyword.lower())
                density = (count / content['word_count']) * 100 if content['word_count'] > 0 else 0
                st.progress(min(density / 3, 1.0), text=f"{keyword}: {count} times ({density:.1f}%)")
        
        with tab4:
            # Export options
            st.subheader("Export Options")
            
            # Download as HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{content['title']}</title>
                <meta charset="UTF-8">
            </head>
            <body>
                <h1>{content['title']}</h1>
                {content['content']}
            </body>
            </html>
            """
            
            st.download_button(
                label=" Download as HTML",
                data=html_content,
                file_name=f"{content['title'][:30]}.html",
                mime="text/html"
            )
            
            # Download as JSON
            st.download_button(
                label=" Download as JSON",
                data=json.dumps(content, indent=2),
                file_name=f"{content['title'][:30]}.json",
                mime="application/json"
            )
            
            # Copy to clipboard button (using st.code for easy copying)
            st.subheader("Copy Content")
            st.code(content['content'], language='html')

if __name__ == "__main__":
    main()