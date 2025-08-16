"""
SEO Optimizer Agent - AI SEO Blog Generator

Bu agent SEO technical optimization yapar:
- Meta tags optimization (title, description, keywords)
- Schema markup planning
- Technical SEO recommendations
- Page speed optimization
- Mobile SEO considerations
- URL structure optimization
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re

# Python path fix
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse, ToolMixin
from services.gemini_service import GeminiService


class SEOOptimizerAgent(BaseAgent, ToolMixin):
   """
   SEO Optimizer Agent - Dördüncü pipeline agent'ı
   
   Görevleri:
   - Technical SEO optimization planning
   - Meta tags optimization (title, description, keywords)
   - Schema markup recommendations
   - Page speed optimization strategies
   - Mobile SEO considerations
   - URL structure optimization
   - Featured snippet targeting
   """
   
   def __init__(self, gemini_service: GeminiService):
       config = AgentConfig(
           name="seo_optimizer",
           description="Optimizes content for technical SEO, meta tags, and search engine performance",
           max_retries=3,
           timeout_seconds=120,
           temperature=0.4,  # More analytical approach for SEO
           reasoning_enabled=True
       )
       
       BaseAgent.__init__(self, config, gemini_service)
       ToolMixin.__init__(self)
       
       # SEO optimization araçları
       self._register_seo_optimization_tools()
       
       self.logger.info("SEOOptimizerAgent initialized")
   
   def _register_seo_optimization_tools(self):
       """SEO optimization araçlarını kaydet"""
       self.available_tools.update({
           "optimize_meta_tags": self._optimize_meta_tags,
           "plan_schema_markup": self._plan_schema_markup,
           "optimize_url_structure": self._optimize_url_structure,
           "plan_technical_seo": self._plan_technical_seo,
           "optimize_for_featured_snippets": self._optimize_for_featured_snippets,
           "plan_mobile_seo": self._plan_mobile_seo,
           "analyze_page_speed_factors": self._analyze_page_speed_factors
       })
   
   async def _optimize_meta_tags(self, **kwargs) -> Dict[str, Any]:
       """Meta tags optimization tool"""
       content_plan = kwargs.get("content_plan", {})
       keyword_data = kwargs.get("keyword_analysis", {})
       product_name = kwargs.get("product_name", "")
       target_audience = kwargs.get("target_audience", "")
       
       # Extract keywords and content info
       primary_keywords = []
       title_from_plan = ""
       
       if content_plan:
           # Get content outline info
           outline = content_plan.get("content_outline", {})
           structure = outline.get("content_outline", {}).get("structure", {})
           title_from_plan = structure.get("title", "")
           
           # Get keyword placement info
           placement = content_plan.get("keyword_placement", {})
           placement_data = placement.get("keyword_placement", {})
           primary_keywords = placement_data.get("primary_keywords", [])
       
       if keyword_data and not primary_keywords:
           # Fallback to keyword analysis data
           primary_selection = keyword_data.get("primary_selection", {})
           primary_keywords = [kw.get('keyword', kw) if isinstance(kw, dict) else kw 
                             for kw in primary_selection.get("keyword_selection", {}).get("primary_keywords", [])]
       
       prompt = f"""
       Optimize meta tags for maximum SEO performance and click-through rates.
       
       Product: {product_name}
       Target Audience: {target_audience}
       Current Title from Plan: {title_from_plan}
       Primary Keywords: {', '.join(primary_keywords[:5])}
       
       Create comprehensive meta tag optimization covering:
       
       1. TITLE TAG OPTIMIZATION:
       - Include primary keyword naturally (preferably at the beginning)
       - Keep within 50-60 characters for full display
       - Make it compelling and click-worthy
       - Include benefit or value proposition
       - Avoid keyword stuffing
       - Create 3-5 title variations for testing
       
       2. META DESCRIPTION OPTIMIZATION:
       - Include primary and secondary keywords naturally
       - Keep within 150-160 characters
       - Create compelling call-to-action
       - Highlight unique value proposition
       - Address user intent and pain points
       - Include emotional triggers or benefits
       - Create 2-3 description variations
       
       3. META KEYWORDS (Legacy Support):
       - List 5-10 most relevant keywords
       - Include primary, secondary, and long-tail variations
       - Separate with commas
       - Avoid over-optimization
       
       4. OPEN GRAPH (Social Media) OPTIMIZATION:
       - OG:title (can be different from title tag)
       - OG:description (can be longer than meta description)
       - OG:image recommendations
       - OG:type and other relevant properties
       
       5. TWITTER CARD OPTIMIZATION:
       - Twitter:title
       - Twitter:description  
       - Twitter:image
       - Twitter:card type recommendation
       
       6. ADDITIONAL META TAGS:
       - Canonical URL structure
       - Robots meta tag recommendations
       - Author and publisher information
       - Article publication/modification dates
       - Language and region targeting
       
       7. CTR OPTIMIZATION STRATEGIES:
       - Emotional triggers in titles
       - Number and year inclusion
       - Power words usage
       - Question-based titles
       - Benefit-focused descriptions
       
       8. SERP FEATURE TARGETING:
       - Title optimization for featured snippets
       - Description formatting for rich snippets
       - FAQ markup consideration
       - Review stars potential
       
       For each meta element, provide:
       - Exact recommended text
       - Character count
       - SEO optimization rationale
       - CTR improvement potential
       - A/B testing suggestions
       
       Focus on creating meta tags that rank well AND get clicked.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a meta tag optimization specialist focused on both search rankings and click-through rates.",
           user_prompt=prompt,
           reasoning_context="Optimizing meta tags for maximum SEO performance and user engagement"
       )
       
       # Parse and structure meta tag recommendations
       meta_recommendations = self._parse_meta_tags(response['response'])
       
       return {
           "meta_optimization": {
               "optimization_strategy": response['response'],
               "meta_recommendations": meta_recommendations,
               "primary_keywords_used": primary_keywords[:5],
               "optimization_focus": [
                   "Title tag CTR optimization",
                   "Meta description engagement",
                   "Social media optimization",
                   "SERP feature targeting",
                   "Mobile-friendly formatting"
               ],
               "testing_recommendations": [
                   "A/B test title variations",
                   "Test description CTAs",
                   "Monitor CTR improvements",
                   "Track ranking changes"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _parse_meta_tags(self, meta_text: str) -> Dict[str, Any]:
       """Parse meta tag recommendations from AI response"""
       meta_data = {
           "title_tags": [],
           "meta_descriptions": [],
           "meta_keywords": [],
           "open_graph": {},
           "twitter_cards": {},
           "additional_meta": {}
       }
       
       try:
           lines = meta_text.split('\n')
           current_section = None
           
           for line in lines:
               line = line.strip()
               if not line:
                   continue
               
               # Detect sections
               if 'title' in line.lower() and ('tag' in line.lower() or 'optimization' in line.lower()):
                   current_section = 'title'
               elif 'description' in line.lower() and 'meta' in line.lower():
                   current_section = 'description'
               elif 'keyword' in line.lower() and 'meta' in line.lower():
                   current_section = 'keywords'
               elif 'open graph' in line.lower() or 'og:' in line.lower():
                   current_section = 'og'
               elif 'twitter' in line.lower():
                   current_section = 'twitter'
               
               # Extract content based on section
               if current_section == 'title' and ('"' in line or line.startswith('-')):
                   title = line.strip('"-* ').strip()
                   if len(title) > 10 and len(title) <= 70:
                       meta_data["title_tags"].append(title)
               
               elif current_section == 'description' and ('"' in line or line.startswith('-')):
                   desc = line.strip('"-* ').strip()
                   if len(desc) > 20 and len(desc) <= 200:
                       meta_data["meta_descriptions"].append(desc)
               
               elif current_section == 'keywords' and (',' in line or line.startswith('-')):
                   keywords = line.strip('"-* ').strip()
                   if ',' in keywords:
                       meta_data["meta_keywords"].extend([kw.strip() for kw in keywords.split(',')])
       
       except Exception as e:
           self.logger.warning(f"Failed to parse meta tags: {e}")
       
       return meta_data
   
   async def _plan_schema_markup(self, **kwargs) -> Dict[str, Any]:
       """Schema markup planning tool"""
       content_plan = kwargs.get("content_plan", {})
       product_name = kwargs.get("product_name", "")
       niche = kwargs.get("niche", "")
       
       # Extract content type and structure info
       content_type = "Article"  # Default
       sections_info = ""
       
       if content_plan:
           sections = content_plan.get("content_sections", {})
           sections_info = sections.get("content_sections", {}).get("section_design", "")[:300]
       
       prompt = f"""
       Plan comprehensive Schema markup for {product_name} in {niche} niche.
       
       Content Type: SEO-optimized blog article/guide
       Product Focus: {product_name}
       Content Structure Info: {sections_info}
       
       Design Schema markup strategy covering:
       
       1. CORE SCHEMA TYPES:
       
       a) Article Schema (Primary):
       - @type: Article or BlogPosting
       - headline (optimized title)
       - description (meta description)
       - author information
       - publisher details
       - datePublished and dateModified
       - mainEntityOfPage
       - image array with proper sizing
       
       b) Product Schema (if applicable):
       - @type: Product
       - name, description, brand
       - offers with price and availability
       - aggregateRating if reviews exist
       - review schema integration
       - manufacturer information
       
       c) FAQ Schema (if FAQ section exists):
       - @type: FAQPage
       - mainEntity array with questions/answers
       - acceptedAnswer with upvoteCount
       - dateCreated for each FAQ
       
       d) HowTo Schema (if guide/tutorial):
       - @type: HowTo
       - name and description
       - step-by-step instructions
       - totalTime and estimatedCost
       - tool and supply requirements
       
       2. ORGANIZATION SCHEMA:
       - Company/brand information
       - logo and contact details
       - social media profiles
       - sameAs property for authority
       
       3. BREADCRUMB SCHEMA:
       - Proper navigation hierarchy
       - position and item properties
       - URL structure optimization
       
       4. IMAGE SCHEMA:
       - Proper image object formatting
       - Multiple image sizes for different devices
       - Caption and description optimization
       - Copyright and license information
       
       5. REVIEW/RATING SCHEMA (if applicable):
       - aggregateRating with ratingValue
       - review count and distribution
       - individual review schema
       - reviewer information
       
       6. LOCAL BUSINESS (if applicable):
       - address and contact information
       - opening hours and location
       - geo coordinates
       - service area definitions
       
       7. STRUCTURED DATA OPTIMIZATION:
       - Rich snippet opportunities
       - Featured snippet targeting
       - Voice search optimization
       - Mobile-first considerations
       
       8. IMPLEMENTATION RECOMMENDATIONS:
       - JSON-LD vs Microdata comparison
       - Placement in HTML structure
       - Testing and validation tools
       - Google Search Console monitoring
       
       For each Schema type, provide:
       - Complete JSON-LD code example
       - Required vs optional properties
       - SEO benefit explanation
       - Implementation priority level
       
       Focus on Schema types that will generate rich snippets and improve search visibility.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a structured data specialist focused on Schema markup for maximum search visibility.",
           user_prompt=prompt,
           reasoning_context="Planning comprehensive Schema markup for rich snippet optimization"
       )
       
       return {
           "schema_markup": {
               "markup_strategy": response['response'],
               "recommended_schemas": [
                   "Article/BlogPosting (Primary)",
                   "Product (if applicable)",
                   "FAQ (if FAQ section)",
                   "HowTo (if guide format)",
                   "Organization (Publisher)",
                   "Breadcrumb (Navigation)"
               ],
               "implementation_priority": [
                   "Article Schema (High)",
                   "Organization Schema (High)", 
                   "FAQ Schema (Medium)",
                   "Product Schema (Medium)",
                   "Image Schema (Low)",
                   "Review Schema (Low)"
               ],
               "rich_snippet_targets": [
                   "Featured snippets",
                   "FAQ rich results",
                   "Article rich results",
                   "Product rich results",
                   "Image rich results"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _optimize_url_structure(self, **kwargs) -> Dict[str, Any]:
       """URL structure optimization tool"""
       content_plan = kwargs.get("content_plan", {})
       keyword_data = kwargs.get("keyword_analysis", {})
       product_name = kwargs.get("product_name", "")
       
       # Extract primary keyword for URL
       primary_keyword = ""
       if keyword_data:
           primary_selection = keyword_data.get("primary_selection", {})
           primary_keywords = primary_selection.get("keyword_selection", {}).get("primary_keywords", [])
           if primary_keywords:
               primary_keyword = primary_keywords[0].get('keyword', primary_keywords[0]) if isinstance(primary_keywords[0], dict) else primary_keywords[0]
       
       prompt = f"""
       Optimize URL structure for {product_name} targeting keyword: {primary_keyword}
       
       Current Context:
       - Product: {product_name}
       - Primary Keyword: {primary_keyword}
       - Content Type: SEO blog article/guide
       
       Create comprehensive URL optimization strategy covering:
       
       1. PRIMARY URL OPTIMIZATION:
       - Include primary keyword in URL slug
       - Keep URL length under 60 characters
       - Use hyphens (-) instead of underscores
       - Avoid unnecessary parameters
       - Make URL readable and descriptive
       - Create 3-5 URL variations for consideration
       
       2. URL STRUCTURE BEST PRACTICES:
       - Follow logical hierarchy (/category/subcategory/article)
       - Use lowercase letters only
       - Remove stop words (a, an, the, and, or, but)
       - Avoid special characters and spaces
       - Include target year if relevant (2024, 2025)
       
       3. SEO-FRIENDLY URL PATTERNS:
       - Keyword-rich but natural
       - Descriptive of content topic
       - Easy to remember and type
       - Suitable for social sharing
       - Mobile-friendly formatting
       
       4. URL VARIATIONS FOR TESTING:
       Create multiple URL options:
       - Short and focused version
       - Descriptive version with modifiers
       - Question-based version (if applicable)
       - Benefit-focused version
       - Year/date-specific version
       
       5. CANONICAL URL STRATEGY:
       - Define primary canonical URL
       - Handle parameter variations
       - Mobile vs desktop considerations
       - HTTPS enforcement
       - WWW vs non-WWW preference
       
       6. BREADCRUMB URL MAPPING:
       - Logical category structure
       - Parent page relationships
       - Navigation hierarchy optimization
       - User experience considerations
       
       7. INTERNAL LINKING URL STRATEGY:
       - Anchor text optimization for URL
       - Related content URL patterns
       - Category and tag URL structure
       - Cross-linking opportunities
       
       8. TECHNICAL URL CONSIDERATIONS:
       - 301 redirect planning if URL changes
       - URL parameter handling
       - Dynamic vs static URL benefits
       - Server-side URL optimization
       
       For each URL recommendation, provide:
       - Exact URL structure
       - Character count
       - SEO benefit explanation
       - User experience impact
       - Implementation difficulty
       
       Focus on URLs that are both SEO-optimized and user-friendly.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a URL optimization specialist focused on SEO performance and user experience.",
           user_prompt=prompt,
           reasoning_context="Optimizing URL structure for search visibility and usability"
       )
       
       # Generate URL variations based on primary keyword
       url_variations = self._generate_url_variations(primary_keyword, product_name)
       
       return {
           "url_optimization": {
               "optimization_strategy": response['response'],
               "url_variations": url_variations,
               "primary_keyword_used": primary_keyword,
               "url_best_practices": [
                   "Include target keyword",
                   "Keep under 60 characters",
                   "Use hyphens for spaces",
                   "Remove stop words",
                   "Use lowercase only",
                   "Make it descriptive"
               ],
               "technical_considerations": [
                   "Canonical URL setup",
                   "301 redirect planning",
                   "Parameter handling",
                   "HTTPS enforcement",
                   "Mobile optimization"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _generate_url_variations(self, primary_keyword: str, product_name: str) -> List[Dict[str, Any]]:
       """Generate URL variations based on keyword and product"""
       if not primary_keyword:
           return []
       
       # Clean keyword for URL
       clean_keyword = re.sub(r'[^a-zA-Z0-9\s-]', '', primary_keyword.lower())
       url_keyword = re.sub(r'\s+', '-', clean_keyword.strip())
       
       # Clean product name
       clean_product = re.sub(r'[^a-zA-Z0-9\s-]', '', product_name.lower())
       url_product = re.sub(r'\s+', '-', clean_product.strip())
       
       variations = [
           {
               "url": f"/blog/{url_keyword}",
               "type": "Keyword-focused",
               "length": len(f"/blog/{url_keyword}"),
               "seo_score": "High"
           },
           {
               "url": f"/guide/{url_keyword}-guide",
               "type": "Guide-specific",
               "length": len(f"/guide/{url_keyword}-guide"),
               "seo_score": "High"
           },
           {
               "url": f"/blog/best-{url_keyword}-2024",
               "type": "Year-specific",
               "length": len(f"/blog/best-{url_keyword}-2024"),
               "seo_score": "Medium"
           },
           {
               "url": f"/reviews/{url_product}-review",
               "type": "Review-focused",
               "length": len(f"/reviews/{url_product}-review"),
               "seo_score": "Medium"
           },
           {
               "url": f"/blog/{url_keyword}-buying-guide",
               "type": "Buying guide",
               "length": len(f"/blog/{url_keyword}-buying-guide"),
               "seo_score": "High"
           }
       ]
       
       return variations
   
   async def _plan_technical_seo(self, **kwargs) -> Dict[str, Any]:
       """Technical SEO planning tool"""
       content_plan = kwargs.get("content_plan", {})
       
       # Extract content info for technical planning
       estimated_length = 2000
       if content_plan:
           outline = content_plan.get("content_outline", {})
           estimated_length = outline.get("content_outline", {}).get("estimated_word_count", 2000)
       
       prompt = f"""
       Plan comprehensive technical SEO optimization strategy.
       
       Content Context:
       - Estimated Content Length: {estimated_length} words
       - Content Type: SEO blog article/guide
       - Target: High search rankings and user experience
       
       Create technical SEO strategy covering:
       
       1. PAGE SPEED OPTIMIZATION:
       - Image optimization recommendations (WebP format, lazy loading)
       - CSS and JavaScript optimization
       - Server response time targets
       - Content Delivery Network (CDN) recommendations
       - Caching strategy implementation
       - Critical rendering path optimization
       
       2. MOBILE SEO OPTIMIZATION:
       - Mobile-first indexing considerations
       - Responsive design requirements
       - Touch-friendly interface elements
       - Mobile page speed targets
       - AMP (Accelerated Mobile Pages) considerations
       - Mobile usability testing recommendations
       
       3. CORE WEB VITALS OPTIMIZATION:
       - Largest Contentful Paint (LCP) targets
       - First Input Delay (FID) optimization
       - Cumulative Layout Shift (CLS) prevention
       - First Contentful Paint (FCP) improvements
       - Time to Interactive (TTI) optimization
       
       4. CRAWLABILITY AND INDEXING:
       - XML sitemap inclusion strategy
       - Robots.txt optimization
       - Internal linking structure for crawlers
       - Canonical URL implementation
       - Noindex/nofollow tag usage guidelines
       
       5. SECURITY AND TECHNICAL FOUNDATION:
       - HTTPS implementation requirements
       - Security headers optimization
       - SSL certificate best practices
       - Mixed content prevention
       - Server security considerations
       
       6. STRUCTURED DATA IMPLEMENTATION:
       - JSON-LD placement recommendations
       - Schema markup validation process
       - Rich snippet testing procedures
       - Google Search Console monitoring
       
       7. INTERNATIONAL SEO (if applicable):
       - Hreflang implementation
       - Language and region targeting
       - Subdomain vs subdirectory strategy
       - Cultural localization considerations
       
       8. MONITORING AND ANALYTICS:
       - Google Search Console setup
       - Google Analytics 4 configuration
       - Performance monitoring tools
       - SEO audit checklist
       - Regular technical health checks
       
       9. ACCESSIBILITY AND USER EXPERIENCE:
       - WCAG 2.1 AA compliance
       - Alt text for images
       - Proper heading structure
       - Keyboard navigation support
       - Screen reader compatibility
       
       10. CONTENT DELIVERY OPTIMIZATION:
       - Gzip compression implementation
       - Browser caching policies
       - Database query optimization
       - Third-party script management
       - Resource prioritization
       
       For each technical aspect, provide:
       - Implementation priority (High/Medium/Low)
       - Expected impact on SEO
       - Implementation difficulty
       - Monitoring recommendations
       - Success metrics
       
       Focus on technical factors that will significantly impact search rankings and user experience.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a technical SEO specialist focused on website performance and search optimization.",
           user_prompt=prompt,
           reasoning_context="Planning comprehensive technical SEO strategy for optimal search performance"
       )
       
       return {
           "technical_seo": {
               "technical_strategy": response['response'],
               "optimization_priorities": [
                   "Page speed optimization (High)",
                   "Mobile-first optimization (High)",
                   "Core Web Vitals (High)",
                   "Crawlability setup (Medium)",
                   "Security implementation (Medium)",
                   "Accessibility compliance (Medium)"
               ],
               "implementation_checklist": [
                   "Image optimization and WebP conversion",
                   "CSS/JS minification and compression",
                   "Mobile responsiveness testing",
                   "Core Web Vitals measurement",
                   "XML sitemap generation",
                   "HTTPS and security headers",
                   "Schema markup validation",
                   "Analytics and Search Console setup"
               ],
               "monitoring_tools": [
                   "Google PageSpeed Insights",
                   "Google Search Console",
                   "GTmetrix performance testing",
                   "Mobile-Friendly Test",
                   "Structured Data Testing Tool",
                   "Google Analytics 4"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _optimize_for_featured_snippets(self, **kwargs) -> Dict[str, Any]:
       """Featured snippets optimization tool"""
       content_plan = kwargs.get("content_plan", {})
       keyword_data = kwargs.get("keyword_analysis", {})
       
       # Extract long-tail keywords for snippet targeting
       long_tail_keywords = []
       if keyword_data:
           long_tail_expansion = keyword_data.get("long_tail_expansion", {})
           long_tail_keywords = long_tail_expansion.get("long_tail_expansion", {}).get("expanded_keywords", [])[:10]
       
       # Extract header structure for snippet optimization
       header_structure = ""
       if content_plan:
           headers = content_plan.get("header_hierarchy", {})
           header_structure = str(headers.get("header_hierarchy", {}).get("optimized_headers", []))[:300]
       
       prompt = f"""
       Optimize content for featured snippets and rich results.
       
       Target Long-tail Keywords: {', '.join(long_tail_keywords)}
       Content Header Structure: {header_structure}
       
       Create featured snippet optimization strategy covering:
       
       1. PARAGRAPH SNIPPETS OPTIMIZATION:
       - 40-60 word answer paragraphs
       - Direct question answering format
       - Clear, concise definitions
       - Step-by-step explanations
       - Comparison statements
       - Problem-solution formats
       
       2. LIST SNIPPETS OPTIMIZATION:
       - Numbered lists for process/steps
       - Bulleted lists for features/benefits
       - Ranked lists (best, top, most)
       - Checklist formats
       - Ingredient or component lists
       - Comparison lists
       
       3. TABLE SNIPPETS OPTIMIZATION:
       - Comparison tables (vs, compared to)
       - Feature specification tables
       - Pricing comparison tables
       - Size/dimension tables
       - Rating/scoring tables
       - Timeline or schedule tables
       
       4. QUESTION-BASED OPTIMIZATION:
       Target these question patterns:
       - "What is [keyword]?"
       - "How to [keyword]?"
       - "Why [keyword]?"
       - "When to [keyword]?"
       - "Where to [keyword]?"
       - "Which [keyword]?"
       - "Best [keyword] for..."
       
       5. CONTENT STRUCTURE FOR SNIPPETS:
       - Clear H2/H3 question headings
       - Immediate answer after heading
       - Supporting details follow
       - Bullet points for clarity
       - Numbered steps for processes
       - Bold key terms and phrases
       
       6. FAQ SECTION OPTIMIZATION:
       - Common questions in target niche
       - Concise 2-3 sentence answers
       - Question format in headings
       - Schema markup for FAQ
       - Long-tail keyword integration
       
       7. VOICE SEARCH OPTIMIZATION:
       - Conversational question formats
       - Natural language answers
       - "Near me" optimizations (if applicable)
       - Complete sentence responses
       - Local context integration
       
       8. RICH RESULT OPPORTUNITIES:
       - Recipe rich results (if applicable)
       - Product rich results
       - Review/rating rich results
       - Event rich results
       - Video rich results
       - Image rich results
       
       9. CONTENT FORMATTING FOR SNIPPETS:
       - Clear paragraph breaks
       - Strategic use of headers
       - Bullet point formatting
       - Number list formatting
       - Table structure optimization
       - Image placement considerations
       
       10. MONITORING AND OPTIMIZATION:
       - Track snippet performance
       - A/B test snippet content
       - Monitor competitor snippets
       - Update content for snippet changes
       - Use Search Console data
       
       For each snippet type, provide:
       - Specific content format examples
       - Target keyword integration
       - Character/word count guidelines
       - HTML structure recommendations
       - Success measurement methods
       
       Focus on snippet types most likely to be triggered by target keywords.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a featured snippet optimization specialist focused on capturing position zero in search results.",
           user_prompt=prompt,
           reasoning_context="Optimizing content structure and format for featured snippet capture"
       )
       
       return {
           "featured_snippets": {
               "snippet_strategy": response['response'],
               "target_snippet_types": [
                   "Paragraph snippets (definitions, explanations)",
                   "List snippets (steps, features, benefits)",
                   "Table snippets (comparisons, specifications)",
                   "FAQ snippets (common questions)",
                   "Video snippets (how-to content)"
               ],
               "question_targets": [
                   f"What is {kw}?" for kw in long_tail_keywords[:3]
               ] + [
                   f"How to {kw}?" for kw in long_tail_keywords[3:6]
               ],
               "formatting_guidelines": [
                   "40-60 words for paragraph snippets",
                   "Clear H2/H3 question headings",
                   "Immediate answers after headings",
                   "Bullet points for list snippets",
                   "Numbered steps for processes",
                   "Bold key terms and phrases"
               ],
               "monitoring_recommendations": [
                   "Track snippet rankings weekly",
                   "Monitor competitor snippet content",
                   "A/B test answer formats",
                   "Update content based on performance",
                   "Use Search Console for insights"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _plan_mobile_seo(self, **kwargs) -> Dict[str, Any]:
       """Mobile SEO planning tool"""
       content_plan = kwargs.get("content_plan", {})
       
       prompt = f"""
       Plan comprehensive mobile SEO optimization strategy.
       
       Content Context:
       - Content Type: SEO blog article/guide
       - Target: Mobile-first indexing optimization
       - Focus: User experience and search performance
       
       Create mobile SEO strategy covering:
       
       1. MOBILE-FIRST INDEXING OPTIMIZATION:
       - Content parity between mobile and desktop
       - Mobile viewport meta tag implementation
       - Touch-friendly interface design
       - Mobile navigation optimization
       - Button and link sizing for touch
       
       2. MOBILE PAGE SPEED OPTIMIZATION:
       - Target Core Web Vitals for mobile
       - Image optimization for mobile devices
       - CSS/JS optimization for mobile
       - Critical resource prioritization
       - Lazy loading implementation
       - AMP consideration analysis
       
       3. RESPONSIVE DESIGN REQUIREMENTS:
       - Flexible grid system implementation
       - Scalable image and media handling
       - Readable font sizes without zooming
       - Proper spacing for touch interactions
       - Horizontal scrolling elimination
       
       4. MOBILE USER EXPERIENCE:
       - Simplified navigation structure
       - Quick access to important content
       - Minimal form field requirements
       - Easy-to-tap call-to-action buttons
       - Thumb-friendly interface design
       - Reduced cognitive load
       
       5. MOBILE CONTENT OPTIMIZATION:
       - Shorter paragraphs for mobile reading
       - Scannable content structure
       - Mobile-friendly table alternatives
       - Collapsible sections for long content
       -- Vertical content flow optimization
       - Mobile-specific heading hierarchy
       
       6. MOBILE TECHNICAL SEO:
       - Mobile sitemap optimization
       - Mobile-specific canonical URLs
       - App indexing (if applicable)
       - Mobile-friendly testing automation
       - Mobile crawlability verification
       - Mobile redirect handling
       
       7. LOCAL MOBILE SEO (if applicable):
       - "Near me" search optimization
       - Local business schema markup
       - Click-to-call functionality
       - Location-based content optimization
       - Mobile maps integration
       - Local review optimization
       
       8. MOBILE CONVERSION OPTIMIZATION:
       - Streamlined checkout process
       - Mobile-optimized forms
       - One-click purchasing options
       - Mobile payment integration
       - Trust signals for mobile users
       - Reduced friction elements
       
       9. MOBILE ANALYTICS AND MONITORING:
       - Mobile-specific Google Analytics setup
       - Mobile usability monitoring
       - Mobile Core Web Vitals tracking
       - Mobile search performance analysis
       - User behavior flow analysis
       
       10. MOBILE CONTENT DELIVERY:
       - Mobile-optimized CDN setup
       - Progressive web app considerations
       - Offline content availability
       - Mobile caching strategies
       - Bandwidth optimization
       
       For each mobile aspect, provide:
       - Implementation priority level
       - Expected impact on mobile SEO
       - User experience improvements
       - Technical requirements
       - Testing methodologies
       
       Focus on mobile optimizations that will improve both search rankings and user engagement.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a mobile SEO specialist focused on mobile-first indexing and user experience optimization.",
           user_prompt=prompt,
           reasoning_context="Planning comprehensive mobile SEO strategy for optimal mobile search performance"
       )
       
       return {
           "mobile_seo": {
               "mobile_strategy": response['response'],
               "optimization_priorities": [
                   "Mobile-first indexing compliance (High)",
                   "Mobile page speed optimization (High)",
                   "Touch-friendly interface design (High)",
                   "Responsive design implementation (Medium)",
                   "Mobile content optimization (Medium)",
                   "Local mobile SEO (Low - if applicable)"
               ],
               "core_requirements": [
                   "Viewport meta tag implementation",
                   "Touch-friendly button sizing (44px minimum)",
                   "Readable text without zooming (16px minimum)",
                   "No horizontal scrolling",
                   "Fast mobile loading (under 3 seconds)",
                   "Mobile-friendly navigation"
               ],
               "testing_checklist": [
                   "Google Mobile-Friendly Test",
                   "PageSpeed Insights mobile score",
                   "Core Web Vitals mobile metrics",
                   "Mobile usability in Search Console",
                   "Real device testing",
                   "Mobile simulator testing"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _analyze_page_speed_factors(self, **kwargs) -> Dict[str, Any]:
       """Page speed analysis and optimization tool"""
       content_plan = kwargs.get("content_plan", {})
       
       # Extract content complexity for speed analysis
       estimated_length = 2000
       estimated_images = 5
       
       if content_plan:
           outline = content_plan.get("content_outline", {})
           estimated_length = outline.get("content_outline", {}).get("estimated_word_count", 2000)
           # Estimate images based on content length (roughly 1 image per 400 words)
           estimated_images = max(int(estimated_length / 400), 3)
       
       prompt = f"""
       Analyze and optimize page speed factors for SEO performance.
       
       Content Specifications:
       - Estimated Content Length: {estimated_length} words
       - Estimated Images: {estimated_images} images
       - Content Type: SEO blog article with rich media
       
       Create comprehensive page speed optimization strategy covering:
       
       1. CORE WEB VITALS OPTIMIZATION:
       
       a) Largest Contentful Paint (LCP) - Target: <2.5s
       - Hero image optimization strategies
       - Above-the-fold content prioritization
       - Server response time optimization
       - Resource loading prioritization
       - CDN implementation benefits
       
       b) First Input Delay (FID) - Target: <100ms
       - JavaScript execution optimization
       - Third-party script management
       - Main thread blocking prevention
       - Code splitting strategies
       - Browser caching optimization
       
       c) Cumulative Layout Shift (CLS) - Target: <0.1
       - Image and video dimension specifications
       - Font loading optimization
       - Ad space reservation
       - Dynamic content handling
       - CSS layout stability
       
       2. IMAGE OPTIMIZATION STRATEGY:
       - WebP format conversion benefits
       - Image compression without quality loss
       - Responsive image sizing
       - Lazy loading implementation
       - Critical image prioritization
       - Alt text optimization for SEO
       
       3. RESOURCE OPTIMIZATION:
       - CSS minification and combining
       - JavaScript minification and deferring
       - HTML minification
       - Font optimization and preloading
       - Third-party resource audit
       - Critical resource identification
       
       4. CACHING STRATEGIES:
       - Browser caching policies
       - Server-side caching implementation
       - CDN caching configuration
       - Database query optimization
       - Static asset caching
       - Dynamic content caching
       
       5. SERVER OPTIMIZATION:
       - Server response time targets (<200ms)
       - Database optimization
       - Server-side compression (Gzip/Brotli)
       - HTTP/2 implementation benefits
       - Server location optimization
       
       6. CONTENT DELIVERY OPTIMIZATION:
       - CDN setup and configuration
       - Geographic content distribution
       - Edge caching strategies
       - Bandwidth optimization
       - Progressive loading implementation
       
       7. MOBILE SPEED OPTIMIZATION:
       - Mobile-specific optimizations
       - Touch delay elimination
       - Mobile image optimization
       - Mobile CSS optimization
       - App-like performance targets
       
       8. MONITORING AND MEASUREMENT:
       - PageSpeed Insights regular testing
       - Google Search Console Core Web Vitals
       - Real User Monitoring (RUM) setup
       - GTmetrix performance tracking
       - Lighthouse CI integration
       
       9. TECHNICAL IMPLEMENTATION:
       - Critical rendering path optimization
       - Resource hints (preload, prefetch, preconnect)
       - Service worker implementation
       - Progressive web app features
       - Offline functionality considerations
       
       10. PERFORMANCE BUDGET:
       - Total page size targets (<1MB initial load)
       - Image size budgets
       - JavaScript bundle size limits
       - CSS file size optimization
       - Third-party resource limits
       
       For each optimization area, provide:
       - Specific implementation steps
       - Expected performance improvements
       - Implementation difficulty level
       - SEO impact assessment
       - Monitoring recommendations
       
       Focus on optimizations that will have the greatest impact on both Core Web Vitals and SEO rankings.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a page speed optimization specialist focused on Core Web Vitals and SEO performance.",
           user_prompt=prompt,
           reasoning_context="Analyzing page speed factors for optimal search performance and user experience"
       )
       
       return {
           "page_speed": {
               "speed_strategy": response['response'],
               "core_web_vitals_targets": {
                   "LCP": "<2.5 seconds (Good)",
                   "FID": "<100 milliseconds (Good)",
                   "CLS": "<0.1 (Good)"
               },
               "optimization_priorities": [
                   "Image optimization and WebP conversion (High)",
                   "CSS/JS minification and compression (High)",
                   "Server response time optimization (High)",
                   "Browser caching implementation (Medium)",
                   "CDN setup and configuration (Medium)",
                   "Third-party script optimization (Medium)"
               ],
               "performance_budget": {
                   "total_page_size": "<1MB initial load",
                   "images_total": f"<500KB for {estimated_images} images",
                   "javascript_total": "<200KB",
                   "css_total": "<100KB",
                   "fonts_total": "<100KB"
               },
               "monitoring_tools": [
                   "Google PageSpeed Insights",
                   "Google Search Console (Core Web Vitals)",
                   "GTmetrix",
                   "Lighthouse CI",
                   "WebPageTest",
                   "Real User Monitoring (RUM)"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def process(self, input_data: Dict[Any, Any]) -> AgentResponse:
       """SEO Optimizer Agent ana işlem süreci"""
       
       self._update_progress(5, "processing", "Starting SEO optimization")
       
       all_reasoning = []
       seo_optimization_data = {}
       
       try:
           # 1. Meta tags optimization
           self._update_progress(15, "processing", "Optimizing meta tags")
           meta_result = await self.call_tool("optimize_meta_tags", **input_data)
           seo_optimization_data["meta_optimization"] = meta_result
           all_reasoning.extend(meta_result.get("reasoning", []))
           
           # 2. Schema markup planning
           self._update_progress(25, "processing", "Planning schema markup")
           schema_result = await self.call_tool("plan_schema_markup", **input_data)
           seo_optimization_data["schema_markup"] = schema_result
           all_reasoning.extend(schema_result.get("reasoning", []))
           
           # 3. URL structure optimization
           self._update_progress(40, "processing", "Optimizing URL structure")
           url_result = await self.call_tool("optimize_url_structure", **input_data)
           seo_optimization_data["url_optimization"] = url_result
           all_reasoning.extend(url_result.get("reasoning", []))
           
           # 4. Technical SEO planning
           self._update_progress(55, "processing", "Planning technical SEO")
           technical_result = await self.call_tool("plan_technical_seo", **input_data)
           seo_optimization_data["technical_seo"] = technical_result
           all_reasoning.extend(technical_result.get("reasoning", []))
           
           # 5. Featured snippets optimization
           self._update_progress(70, "processing", "Optimizing for featured snippets")
           snippets_result = await self.call_tool("optimize_for_featured_snippets", **input_data)
           seo_optimization_data["featured_snippets"] = snippets_result
           all_reasoning.extend(snippets_result.get("reasoning", []))
           
           # 6. Mobile SEO planning
           self._update_progress(85, "processing", "Planning mobile SEO")
           mobile_result = await self.call_tool("plan_mobile_seo", **input_data)
           seo_optimization_data["mobile_seo"] = mobile_result
           all_reasoning.extend(mobile_result.get("reasoning", []))
           
           # 7. Page speed analysis
           self._update_progress(95, "processing", "Analyzing page speed factors")
           speed_result = await self.call_tool("analyze_page_speed_factors", **input_data)
           seo_optimization_data["page_speed"] = speed_result
           all_reasoning.extend(speed_result.get("reasoning", []))
           
           # 8. SEO optimization summary
           self._update_progress(98, "processing", "Finalizing SEO optimization")
           
           # Calculate average confidence
           confidences = [
               meta_result.get("confidence", 80),
               schema_result.get("confidence", 80),
               url_result.get("confidence", 80),
               technical_result.get("confidence", 80),
               snippets_result.get("confidence", 80),
               mobile_result.get("confidence", 80),
               speed_result.get("confidence", 80)
           ]
           avg_confidence = sum(confidences) / len(confidences)
           
           # Create comprehensive SEO optimization summary
           seo_summary = {
               "optimization_completed": True,
               "optimization_areas": 7,
               "avg_confidence": avg_confidence,
               "optimization_timestamp": datetime.now().isoformat(),
               "key_optimizations": [
                   "Meta tags and title optimization",
                   "Schema markup implementation",
                   "URL structure optimization",
                   "Technical SEO foundation",
                   "Featured snippets targeting",
                   "Mobile-first optimization",
                   "Page speed optimization"
               ],
               "implementation_priorities": [
                   "Meta tags (Immediate)",
                   "URL structure (Immediate)",
                   "Technical SEO (High)",
                   "Schema markup (High)",
                   "Mobile optimization (High)",
                   "Page speed (Medium)",
                   "Featured snippets (Medium)"
               ],
               "expected_seo_benefits": [
                   "Improved search rankings",
                   "Higher click-through rates",
                   "Better Core Web Vitals scores",
                   "Enhanced mobile performance",
                   "Rich snippet opportunities",
                   "Technical SEO foundation",
                   "User experience improvements"
               ]
           }
           
           seo_optimization_data["seo_summary"] = seo_summary
           
           return AgentResponse(
               success=True,
               data=seo_optimization_data,
               reasoning=all_reasoning,
               errors=[],
               processing_time=0.0,
               metadata={
                   "agent_name": self.config.name,
                   "confidence": avg_confidence,
                   "optimization_areas": seo_summary["optimization_areas"],
                   "optimization_stages": 7
               }
           )
           
       except Exception as e:
           self.logger.error(f"SEO optimization failed: {str(e)}")
           return AgentResponse(
               success=False,
               data={},
               reasoning=all_reasoning,
               errors=[str(e)],
               processing_time=0.0,
               metadata={
                   "agent_name": self.config.name,
                   "failure_reason": str(e)
               }
           )


# Test function
async def test_seo_optimizer():
   """SEO Optimizer Agent test function"""
   print("Testing SEO Optimizer Agent")
   print("=" * 50)
   
   # Services
   from services.gemini_service import GeminiService
   
   gemini = GeminiService()
   
   # Mock content plan data (simulating input from Content Planner)
   mock_content_plan = {
       "content_outline": {
           "content_outline": {
               "structure": {
                   "title": "Best Wireless Gaming Headset Guide 2024",
                   "main_sections": [
                       {"title": "What Makes a Great Gaming Headset"},
                       {"title": "Top Wireless Gaming Headsets Review"},
                       {"title": "How to Choose the Right Gaming Headset"}
                   ],
                   "total_sections": 3
               },
               "estimated_word_count": 2500
           }
       },
       "keyword_placement": {
           "keyword_placement": {
               "primary_keywords": ["wireless gaming headset", "best gaming headset"],
               "secondary_keywords": ["gaming audio", "wireless headset"],
               "long_tail_keywords": ["best wireless gaming headset 2024", "gaming headset buying guide"]
           }
       }
   }
   
   # Mock keyword analysis data
   mock_keyword_analysis = {
       "primary_selection": {
           "keyword_selection": {
               "primary_keywords": [
                   {"keyword": "wireless gaming headset", "search_volume": 8100, "difficulty": 45},
                   {"keyword": "best gaming headset", "search_volume": 12000, "difficulty": 52}
               ]
           }
       },
       "long_tail_expansion": {
           "long_tail_expansion": {
               "expanded_keywords": [
                   "best wireless gaming headset 2024",
                   "wireless gaming headset review",
                   "how to choose gaming headset",
                   "gaming headset buying guide"
               ]
           }
       }
   }
   
   # Test input
   test_input = {
       "product_name": "Wireless Gaming Headset",
       "niche": "gaming accessories",
       "target_audience": "PC and console gamers aged 18-35",
       "content_plan": mock_content_plan,
       "keyword_analysis": mock_keyword_analysis
   }
   
   # Progress callback
   def progress_callback(agent_name, progress, status, current_step):
       print(f"[{agent_name}] {progress}% - {status}: {current_step}")
   
   # Test agent
   agent = SEOOptimizerAgent(gemini)
   agent.set_progress_callback(progress_callback)
   
   result = await agent.execute(test_input)
   
   print("\nSEO Optimization Results:")
   print("-" * 30)
   print(f"Success: {result.success}")
   print(f"Data Keys: {list(result.data.keys())}")
   print(f"Optimization Areas: {result.metadata.get('optimization_areas', 'N/A')}")
   print(f"Confidence: {result.metadata.get('confidence', 'N/A'):.1f}%")
   print(f"Processing Time: {result.processing_time:.2f}s")
   
   if result.errors:
       print(f"Errors: {result.errors}")
   
   # Show sample results
   if result.success and result.data:
       summary = result.data.get("seo_summary", {})
       print(f"\nSEO Optimization Summary:")
       print(f"- Optimization Areas: {summary.get('optimization_areas', 0)}")
       print(f"- Average Confidence: {summary.get('avg_confidence', 0):.1f}%")
       print(f"- Key Optimizations: {len(summary.get('key_optimizations', []))}")
       
       # Show sample meta optimization
       if "meta_optimization" in result.data:
           meta_opt = result.data["meta_optimization"].get("meta_optimization", {})
           meta_recs = meta_opt.get("meta_recommendations", {})
           print(f"\nMeta Tags Sample:")
           titles = meta_recs.get("title_tags", [])
           if titles:
               print(f"- Sample Title: {titles[0]}")
           descriptions = meta_recs.get("meta_descriptions", [])
           if descriptions:
               print(f"- Sample Description: {descriptions[0][:100]}...")
       
       # Show URL variations
       if "url_optimization" in result.data:
           url_opt = result.data["url_optimization"].get("url_optimization", {})
           url_vars = url_opt.get("url_variations", [])
           print(f"\nURL Variations Sample:")
           for i, var in enumerate(url_vars[:3]):
               print(f"- Option {i+1}: {var.get('url', 'N/A')} ({var.get('type', 'N/A')})")
   
   return result


if __name__ == "__main__":
   # Test çalıştır
   result = asyncio.run(test_seo_optimizer())
   print(f"\nSEO Optimizer test completed!")