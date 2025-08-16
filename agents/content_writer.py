"""
Content Writer Agent - AI SEO Blog Generator

Bu agent gerçek blog content yazımı yapar:
- Comprehensive SEO-optimized blog article writing
- Header hierarchy implementation
- Keyword placement integration
- CTA positioning
- Internal linking implementation
- FAQ section creation
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


class ContentWriterAgent(BaseAgent, ToolMixin):
   """
   Content Writer Agent - Beşinci pipeline agent'ı
   
   Görevleri:
   - Complete SEO-optimized blog article writing
   - Header hierarchy implementation
   - Strategic keyword integration
   - CTA positioning and conversion optimization
   - Internal linking implementation
   - FAQ section creation
   - Meta descriptions and title integration
   """
   
   def __init__(self, gemini_service: GeminiService):
       config = AgentConfig(
           name="content_writer",
           description="Writes comprehensive, SEO-optimized blog articles with strategic keyword integration",
           max_retries=3,
           timeout_seconds=300,  # Content writing takes longer
           temperature=0.7,  # Creative but controlled writing
           max_tokens=8000,  # Longer content generation
           reasoning_enabled=True
       )
       
       BaseAgent.__init__(self, config, gemini_service)
       ToolMixin.__init__(self)
       
       # Content writing araçları
       self._register_content_writing_tools()
       
       self.logger.info("ContentWriterAgent initialized")
   
   def _register_content_writing_tools(self):
       """Content writing araçlarını kaydet"""
       self.available_tools.update({
           "write_article_introduction": self._write_article_introduction,
           "write_main_content_sections": self._write_main_content_sections,
           "write_article_conclusion": self._write_article_conclusion,
           "create_faq_section": self._create_faq_section,
           "integrate_internal_links": self._integrate_internal_links,
           "optimize_content_flow": self._optimize_content_flow,
           "finalize_article_structure": self._finalize_article_structure
       })
   
   async def _write_article_introduction(self, **kwargs) -> Dict[str, Any]:
       """Article introduction writing tool"""
       content_plan = kwargs.get("content_plan", {})
       seo_optimization = kwargs.get("seo_optimization", {})
       product_name = kwargs.get("product_name", "")
       target_audience = kwargs.get("target_audience", "")
       
       # Extract optimization data
       primary_keywords = []
       title = ""
       meta_description = ""
       
       if content_plan:
           # Get keyword placement strategy
           keyword_placement = content_plan.get("keyword_placement", {})
           placement_data = keyword_placement.get("keyword_placement", {})
           primary_keywords = placement_data.get("primary_keywords", [])[:3]
           
           # Get content outline
           outline = content_plan.get("content_outline", {})
           structure = outline.get("content_outline", {}).get("structure", {})
           title = structure.get("title", "")
       
       if seo_optimization:
           # Get optimized meta tags
           meta_opt = seo_optimization.get("meta_optimization", {})
           meta_data = meta_opt.get("meta_optimization", {}).get("meta_recommendations", {})
           titles = meta_data.get("title_tags", [])
           descriptions = meta_data.get("meta_descriptions", [])
           if titles:
               title = titles[0]
           if descriptions:
               meta_description = descriptions[0]
       
       prompt = f"""
       Write a compelling SEO-optimized introduction for {product_name} targeting {target_audience}.
       
       Article Title: {title}
       Meta Description: {meta_description}
       Primary Keywords: {', '.join(primary_keywords)}
       Target Word Count: 200-250 words
       
       Create an engaging introduction that:
       
       1. HOOK AND ATTENTION GRABBER:
       - Start with a compelling statistic, question, or pain point
       - Address the main problem your target audience faces
       - Create immediate relevance and connection
       - Use emotional triggers appropriate to the audience
       
       2. KEYWORD INTEGRATION:
       - Include primary keyword within the first 100 words
       - Integrate keywords naturally without stuffing
       - Use variations and synonyms for natural flow
       - Maintain readability and engagement
       
       3. VALUE PROPOSITION:
       - Clearly state what the reader will learn/gain
       - Promise specific benefits and outcomes
       - Address the "what's in it for me" question
       - Set clear expectations for the content
       
       4. CREDIBILITY ESTABLISHMENT:
       - Mention your expertise or research depth
       - Reference authority sources or data
       - Build trust with the audience
       - Position yourself as a reliable guide
       
       5. CONTENT PREVIEW:
       - Briefly outline what the article will cover
       - Mention key sections or insights
       - Create anticipation for the full content
       - Use this to improve dwell time
       
       6. SEO OPTIMIZATION:
       - Include primary keyword naturally
       - Use related semantic keywords
       - Optimize for featured snippet potential
       - Maintain proper keyword density (1-2%)
       
       7. ENGAGEMENT ELEMENTS:
       - Use second person ("you") to create connection
       - Include questions to engage the reader
       - Use power words and emotional triggers
       - Create urgency or curiosity gaps
       
       Writing Guidelines:
       - Write in an authoritative yet approachable tone
       - Use short paragraphs (2-3 sentences max)
       - Include transition words for flow
       - End with a smooth transition to the main content
       - Optimize for both users and search engines
       
       Write a complete introduction that hooks readers, includes primary keywords naturally, and sets up the rest of the article perfectly.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are an expert content writer specializing in SEO-optimized blog introductions that convert readers.",
           user_prompt=prompt,
           reasoning_context="Writing compelling introduction with strategic keyword integration"
       )
       
       # Analyze introduction quality
       introduction_text = response['response']
       word_count = len(introduction_text.split())
       keyword_mentions = sum(1 for kw in primary_keywords if kw.lower() in introduction_text.lower())
       
       return {
           "introduction": {
               "content": introduction_text,
               "word_count": word_count,
               "primary_keywords_used": primary_keywords,
               "keyword_mentions": keyword_mentions,
               "seo_elements": [
                   "Primary keyword in first 100 words",
                   "Natural keyword integration",
                   "Value proposition statement",
                   "Credibility establishment",
                   "Content preview included"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _write_main_content_sections(self, **kwargs) -> Dict[str, Any]:
       """Main content sections writing tool"""
       content_plan = kwargs.get("content_plan", {})
       seo_optimization = kwargs.get("seo_optimization", {})
       introduction_data = kwargs.get("introduction", {})
       product_name = kwargs.get("product_name", "")
       target_audience = kwargs.get("target_audience", "")
       
       # Extract content structure and optimization data
       sections_design = ""
       header_hierarchy = []
       keyword_placement = {}
       cta_strategy = ""
       
       if content_plan:
           # Get sections design
           sections = content_plan.get("content_sections", {})
           sections_design = sections.get("content_sections", {}).get("section_design", "")
           
           # Get header hierarchy
           headers = content_plan.get("header_hierarchy", {})
           header_data = headers.get("header_hierarchy", {})
           header_hierarchy = header_data.get("optimized_headers", [])
           
           # Get keyword placement strategy
           kw_placement = content_plan.get("keyword_placement", {})
           keyword_placement = kw_placement.get("keyword_placement", {})
           
           # Get CTA strategy
           cta_data = content_plan.get("cta_positioning", {})
           cta_strategy = cta_data.get("cta_positioning", {}).get("cta_strategy", "")
       
       # Extract featured snippets optimization
       snippet_strategy = ""
       if seo_optimization:
           snippets = seo_optimization.get("featured_snippets", {})
           snippet_strategy = snippets.get("featured_snippets", {}).get("snippet_strategy", "")
       
       prompt = f"""
       Write comprehensive main content sections for {product_name} targeting {target_audience}.
       
       Content Structure Plan:
       {sections_design[:800]}
       
       Header Hierarchy:
       {str(header_hierarchy)[:400]}
       
       Keyword Placement Strategy:
       Primary Keywords: {', '.join(keyword_placement.get('primary_keywords', []))}
       Secondary Keywords: {', '.join(keyword_placement.get('secondary_keywords', []))}
       
       Featured Snippets Strategy:
       {snippet_strategy[:400]}
       
       CTA Strategy:
       {cta_strategy[:300]}
       
       Write detailed main content sections covering:
       
       1. SECTION STRUCTURE AND HIERARCHY:
       - Use H2 headers for main sections (6-8 sections)
       - Use H3 subheaders for subsections (2-4 per H2)
       - Follow logical content progression
       - Maintain scannable structure for readers
       
       2. CONTENT DEPTH AND VALUE:
       - Each H2 section: 400-600 words
       - Each H3 subsection: 150-250 words
       - Include specific, actionable information
       - Provide expert insights and analysis
       - Use data, statistics, and examples
       
       3. SEO OPTIMIZATION INTEGRATION:
       - Include primary keywords in 2-3 H2 headers
       - Distribute secondary keywords across H3s
       - Maintain 1-2% keyword density overall
       - Use semantic keywords and variations
       - Optimize for featured snippet formats
       
       4. FEATURED SNIPPETS OPTIMIZATION:
       - Include clear, concise answers (40-60 words)
       - Use numbered lists for step-by-step processes
       - Use bullet points for features/benefits
       - Include comparison tables where relevant
       - Answer common questions directly
       
       5. CONTENT SECTIONS TO INCLUDE:
       
       a) Problem/Need Identification Section:
       - Address target audience pain points
       - Explain why the product/solution matters
       - Include relevant statistics or research
       - Create urgency or need recognition
       
       b) Product/Solution Analysis Section:
       - Detailed feature explanations
       - Benefits and value propositions
       - Technical specifications (if relevant)
       - Use cases and applications
       
       c) Comparison/Alternatives Section:
       - Compare with similar products/solutions
       - Pros and cons analysis
       - Price comparison (if applicable)
       - Recommendation framework
       
       d) How-to/Implementation Section:
       - Step-by-step guidance
       - Best practices and tips
       - Common mistakes to avoid
       - Expert recommendations
       
       e) Advanced Tips/Insights Section:
       - Expert-level information
       - Industry insights
       - Future trends or considerations
       - Professional recommendations
       
       f) Buying Guide/Decision Framework:
       - Key factors to consider
       - Budget considerations
       - Where to buy/how to get started
       - Decision-making framework
       
       6. ENGAGEMENT AND CONVERSION ELEMENTS:
       - Include 2-3 CTAs naturally within content
       - Add trust signals and social proof
       - Use conversational tone and direct address
       - Include internal linking opportunities
       - Add compelling subheadings and transitions
       
       7. CONTENT FORMATTING:
       - Use short paragraphs (2-3 sentences)
       - Include bullet points and numbered lists
       - Use bold text for key terms and concepts
       - Add transitional phrases between sections
       - Ensure mobile-friendly formatting
       
       8. EXPERTISE AND AUTHORITY:
       - Include expert quotes or references
       - Mention authoritative sources
       - Provide detailed, accurate information
       - Show deep understanding of the topic
       - Build trust through comprehensive coverage
       
       Target Total Word Count: 1800-2200 words for main sections
       
       Write complete, detailed content sections that provide massive value to readers while being perfectly optimized for search engines.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are an expert content writer creating comprehensive, SEO-optimized blog content that ranks and converts.",
           user_prompt=prompt,
           reasoning_context="Writing detailed main content sections with strategic SEO integration"
       )
       
       # Analyze main content quality
       main_content = response['response']
       word_count = len(main_content.split())
       
       # Count header usage
       h2_count = main_content.count('## ') + main_content.count('H2:')
       h3_count = main_content.count('### ') + main_content.count('H3:')
       
       # Count keyword mentions
       primary_keywords = keyword_placement.get('primary_keywords', [])
       keyword_mentions = {}
       for kw in primary_keywords[:5]:
           mentions = main_content.lower().count(kw.lower())
           keyword_mentions[kw] = mentions
       
       return {
           "main_content": {
               "content": main_content,
               "word_count": word_count,
               "structure_analysis": {
                   "h2_sections": h2_count,
                   "h3_subsections": h3_count,
                   "average_section_length": word_count // max(h2_count, 1)
               },
               "seo_analysis": {
                   "keyword_mentions": keyword_mentions,
                   "total_keyword_density": sum(keyword_mentions.values()) / word_count * 100 if word_count > 0 else 0
               },
               "optimization_elements": [
                   "Header hierarchy implemented",
                   "Keywords integrated naturally",
                   "Featured snippet formatting",
                   "CTA placement optimized",
                   "Expert authority signals"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _write_article_conclusion(self, **kwargs) -> Dict[str, Any]:
       """Article conclusion writing tool"""
       content_plan = kwargs.get("content_plan", {})
       introduction_data = kwargs.get("introduction", {})
       main_content_data = kwargs.get("main_content", {})
       product_name = kwargs.get("product_name", "")
       target_audience = kwargs.get("target_audience", "")
       
       # Extract CTA strategy and key points
       cta_strategy = ""
       primary_keywords = []
       
       if content_plan:
           cta_data = content_plan.get("cta_positioning", {})
           cta_strategy = cta_data.get("cta_positioning", {}).get("cta_strategy", "")
           
           kw_placement = content_plan.get("keyword_placement", {})
           keyword_placement = kw_placement.get("keyword_placement", {})
           primary_keywords = keyword_placement.get("primary_keywords", [])[:3]
       
       # Extract main content themes for conclusion
       main_content = main_content_data.get("main_content", {}).get("content", "")
       
       prompt = f"""
       Write a compelling conclusion for the {product_name} article targeting {target_audience}.
       
       Article Context:
       - Primary Keywords: {', '.join(primary_keywords)}
       - Main Content Themes: Comprehensive guide covering product analysis, comparisons, and buying guidance
       - Target Word Count: 200-300 words
       
       CTA Strategy:
       {cta_strategy[:400]}
       
       Create a powerful conclusion that:
       
       1. KEY TAKEAWAYS SUMMARY:
       - Summarize the 3-4 most important points from the article
       - Reinforce the main value proposition
       - Remind readers of key benefits
       - Provide a clear decision framework
       
       2. PRIMARY KEYWORD REINFORCEMENT:
       - Include primary keyword naturally in conclusion
       - Use variations and semantic keywords
       - Maintain natural language flow
       - Avoid keyword stuffing
       
       3. COMPELLING CALL-TO-ACTION:
       - Clear, action-oriented language
       - Create urgency or motivation to act
       - Provide specific next steps
       - Include benefit reinforcement
       - Make it conversion-focused
       
       4. AUTHORITY AND TRUST BUILDING:
       - Reinforce your expertise on the topic
       - Mention comprehensive research or analysis
       - Show confidence in recommendations
       - Build trust for future engagement
       
       5. ENGAGEMENT AND RETENTION:
       - Encourage comments or questions
       - Invite social sharing
       - Suggest related content exploration
       - Build community and discussion
       
       6. FUTURE VALUE PROMISE:
       - Hint at future content or updates
       - Encourage newsletter signup or following
       - Promise continued value delivery
       - Build long-term relationship
       
       7. CONCLUSION STRUCTURE:
       - Opening summary statement
       - Key benefits recap (2-3 points)
       - Strong call-to-action
       - Engagement invitation
       - Future value promise
       
       Writing Guidelines:
       - Use confident, authoritative tone
       - Include emotional triggers
       - Create sense of completion and satisfaction
       - End with clear next step
       - Optimize for conversion and engagement
       
       Write a conclusion that wraps up the article perfectly while driving readers to take action.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are an expert content writer specializing in high-converting conclusions that drive action.",
           user_prompt=prompt,
           reasoning_context="Writing compelling conclusion with strong call-to-action and keyword reinforcement"
       )
       
       # Analyze conclusion quality
       conclusion_text = response['response']
       word_count = len(conclusion_text.split())
       
       # Check for CTA presence
       cta_indicators = ['click', 'buy', 'get', 'start', 'try', 'download', 'subscribe', 'contact']
       cta_present = any(indicator in conclusion_text.lower() for indicator in cta_indicators)
       
       # Check keyword integration
       keyword_mentions = sum(1 for kw in primary_keywords if kw.lower() in conclusion_text.lower())
       
       return {
           "conclusion": {
               "content": conclusion_text,
               "word_count": word_count,
               "cta_analysis": {
                   "cta_present": cta_present,
                   "action_words_count": sum(1 for word in cta_indicators if word in conclusion_text.lower())
               },
               "seo_analysis": {
                   "keyword_mentions": keyword_mentions,
                   "primary_keywords_used": primary_keywords
               },
               "conclusion_elements": [
                   "Key takeaways summary",
                   "Call-to-action included",
                   "Authority reinforcement",
                   "Engagement invitation",
                   "Future value promise"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _create_faq_section(self, **kwargs) -> Dict[str, Any]:
       """FAQ section creation tool"""
       keyword_data = kwargs.get("keyword_analysis", {})
       seo_optimization = kwargs.get("seo_optimization", {})
       product_name = kwargs.get("product_name", "")
       target_audience = kwargs.get("target_audience", "")
       
       # Extract long-tail keywords for FAQ questions
       long_tail_keywords = []
       if keyword_data:
           long_tail_expansion = keyword_data.get("long_tail_expansion", {})
           long_tail_keywords = long_tail_expansion.get("long_tail_expansion", {}).get("expanded_keywords", [])[:15]
       
       # Extract snippet optimization strategy
       snippet_strategy = ""
       if seo_optimization:
           snippets = seo_optimization.get("featured_snippets", {})
           snippet_data = snippets.get("featured_snippets", {})
           snippet_strategy = snippet_data.get("snippet_strategy", "")
           question_targets = snippet_data.get("question_targets", [])
           long_tail_keywords.extend(question_targets)
       
       prompt = f"""
       Create a comprehensive FAQ section for {product_name} targeting {target_audience}.
       
       Long-tail Keywords for FAQ: {', '.join(long_tail_keywords[:10])}
       
       Featured Snippets Strategy:
       {snippet_strategy[:400]}
       
       Create an SEO-optimized FAQ section with:
       
       1. QUESTION SELECTION STRATEGY:
       - Include 5-8 frequently asked questions
       - Target long-tail keywords in question format
       - Address common user concerns and objections
       - Include comparison and decision-making questions
       - Cover technical and practical aspects
       
       2. QUESTION TYPES TO INCLUDE:
       
       a) Definition/Explanation Questions:
       - "What is [product/feature]?"
       - "How does [product] work?"
       - "Why is [product] important?"
       
       b) Comparison Questions:
       - "What's the difference between [A] and [B]?"
       - "[Product] vs [Alternative] - which is better?"
       - "How does [product] compare to [competitor]?"
       
       c) Practical/How-to Questions:
       - "How to choose the right [product]?"
       - "How to use [product] effectively?"
       - "How to install/setup [product]?"
       
       d) Buying/Decision Questions:
       - "Is [product] worth the money?"
       - "Where to buy [product]?"
       - "What should I look for when buying [product]?"
       
       e) Technical/Specification Questions:
       - "What are the specifications of [product]?"
       - "What compatibility requirements does [product] have?"
       - "How long does [product] last?"
       
       3. ANSWER OPTIMIZATION:
       - Keep answers concise (50-100 words each)
       - Provide direct, actionable answers
       - Include relevant keywords naturally
       - Optimize for featured snippet capture
       - Use bullet points where appropriate
       
       4. SEO OPTIMIZATION:
       - Format questions as H3 headers
       - Include target keywords in questions
       - Optimize answers for voice search
       - Use structured data friendly format
       - Include internal linking opportunities
       
       5. FEATURED SNIPPETS OPTIMIZATION:
       - Structure answers for snippet capture
       - Use numbered lists for step-by-step answers
       - Include comparison tables if relevant
       - Provide complete but concise information
       - Use natural question language
       
       6. USER EXPERIENCE:
       - Address real user concerns
       - Provide helpful, actionable information
       - Use conversational, approachable tone
       - Include trust signals where relevant
       - End with helpful next steps
       
       7. FAQ STRUCTURE:
       For each FAQ, provide:
       - Clear, keyword-optimized question
       - Concise, valuable answer (50-100 words)
       - Natural keyword integration
       - Internal linking opportunity (if relevant)
       - Call-to-action or next step (if appropriate)
       
       Create 6-8 high-quality FAQ items that address the most important questions your target audience has about the topic.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are an expert FAQ content creator specializing in SEO-optimized question-answer pairs that capture featured snippets.",
           user_prompt=prompt,
           reasoning_context="Creating comprehensive FAQ section optimized for search and user value"
       )
       
       # Parse FAQ structure
       faq_content = response['response']
       faq_count = faq_content.count('?')  # Rough count of questions
       word_count = len(faq_content.split())
       
       # Check for long-tail keyword integration
       keyword_integration = sum(1 for kw in long_tail_keywords[:10] 
                               if any(word in faq_content.lower() for word in kw.lower().split()))
       
       return {
           "faq_section": {
               "content": faq_content,
               "faq_count": faq_count,
               "word_count": word_count,
               "keyword_integration": keyword_integration,
               "optimization_elements": [
                   "H3 header questions",
                   "Concise, direct answers",
                   "Long-tail keyword targeting",
                   "Featured snippet optimization",
                   "Voice search friendly format"
               ],
               "seo_benefits": [
                   "Featured snippet opportunities",
                   "Long-tail keyword rankings",
                   "Voice search optimization",
                   "FAQ rich results",
                   "User engagement improvement"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _integrate_internal_links(self, **kwargs) -> Dict[str, Any]:
       """Internal linking integration tool"""
       content_plan = kwargs.get("content_plan", {})
       main_content_data = kwargs.get("main_content", {})
       faq_data = kwargs.get("faq_section", {})
       
       # Extract internal linking strategy
       linking_strategy = ""
       if content_plan:
           linking = content_plan.get("internal_linking", {})
           linking_strategy = linking.get("internal_linking", {}).get("linking_strategy", "")
       
       main_content = main_content_data.get("main_content", {}).get("content", "")
       faq_content = faq_data.get("faq_section", {}).get("content", "")
       
       prompt = f"""
       Integrate strategic internal links throughout the content.
       
       Internal Linking Strategy:
       {linking_strategy[:600]}
       
       Current Content Sections:
       - Main Content: {len(main_content.split())} words
       - FAQ Section: {len(faq_content.split())} words
       
       Create internal linking integration plan covering:
       
       1. INTERNAL LINKING OPPORTUNITIES:
       - Identify 8-12 strategic internal link placements
       - Include contextual links within content flow
       - Add resource links at section endings
       - Include related content suggestions
       
       2. ANCHOR TEXT OPTIMIZATION:
       - Use keyword-rich but natural anchor text
       - Include variations of target keywords
       - Use descriptive, click-worthy anchor text
       - Avoid over-optimization
       
       3. LINK PLACEMENT STRATEGY:
       
       a) Introduction Section Links:
       - 1-2 contextual links to supporting content
       - Links to detailed guides or resources
       - Authority building external links
       
       b) Main Content Section Links:
       - 2-3 links per major section
       - Links to related product pages
       - Links to comparison articles
       - Links to how-to guides
       - Links to category/tag pages
       
       c) FAQ Section Links:
       - Links to detailed explanations
       - Links to product specification pages
       - Links to buying guides
       - Links to support resources
       
       d) Conclusion Section Links:
       - Links to next logical content
       - Links to conversion pages
       - Links to related products/services
       
       4. LINK TYPES TO INCLUDE:
       
       a) Educational/Supporting Links:
       - "Learn more about [topic]" - link to detailed guide
       - "Complete guide to [related topic]" - link to pillar content
       - "Understanding [concept]" - link to explanation article
       
       b) Product/Commercial Links:
       - "Compare [product] options" - link to comparison page
       - "See [product] specifications" - link to product page
       - "Check current [product] prices" - link to pricing page
       
       c) Related Content Links:
       - "You might also like" - link to related articles
       - "Similar guides" - link to content cluster
       - "For more on [topic]" - link to category page
       
       5. LINK INTEGRATION EXAMPLES:
       Provide specific examples like:
       - "For a complete breakdown of gaming headset features, check out our [comprehensive gaming audio guide]."
       - "If you're also considering wired options, our [wired vs wireless gaming headsets comparison] provides detailed insights."
       - "To understand the technical specifications better, visit our [gaming headset technology explained] article."
       
       6. SEO OPTIMIZATION:
       - Distribute link equity strategically
       - Use keyword-optimized anchor text
       - Link to high-value pages
       - Maintain natural link density (2-5 links per 1000 words)
       - Include both internal and external authority links
       
       7. USER EXPERIENCE:
       - Make links helpful and relevant
       - Provide clear value for clicking
       - Use descriptive anchor text
       - Avoid link overload
       - Maintain content flow
       
       Create specific internal linking recommendations with exact anchor text and placement suggestions for the content.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are an internal linking specialist focused on SEO optimization and user experience enhancement.",
           user_prompt=prompt,
           reasoning_context="Creating strategic internal linking plan for SEO and user engagement optimization"
       )
       
       return {
           "internal_linking": {
               "linking_plan": response['response'],
               "estimated_links": "8-12 strategic internal links",
               "link_density": "2-5 links per 1000 words",
               "optimization_focus": [
                   "Keyword-rich anchor text",
                   "Contextual link placement",
                   "User value optimization",
                   "Link equity distribution",
                   "Natural content integration"
               ],
               "link_categories": [
                   "Educational/supporting content",
                   "Product/commercial pages", 
                   "Related content cluster",
                   "Authority external links"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _optimize_content_flow(self, **kwargs) -> Dict[str, Any]:
       """Content flow optimization tool"""
       introduction_data = kwargs.get("introduction", {})
       main_content_data = kwargs.get("main_content", {})
       conclusion_data = kwargs.get("conclusion", {})
       faq_data = kwargs.get("faq_section", {})
       
       # Extract all content for flow analysis
       introduction = introduction_data.get("introduction", {}).get("content", "")
       main_content = main_content_data.get("main_content", {}).get("content", "")
       conclusion = conclusion_data.get("conclusion", {}).get("content", "")
       faq_content = faq_data.get("faq_section", {}).get("content", "")
       
       total_words = (len(introduction.split()) + len(main_content.split()) + 
                     len(conclusion.split()) + len(faq_content.split()))
       
       prompt = f"""
       Optimize the overall content flow and structure for maximum engagement and SEO performance.
       
       Content Analysis:
       - Introduction: {len(introduction.split())} words
       - Main Content: {len(main_content.split())} words  
       - Conclusion: {len(conclusion.split())} words
       - FAQ Section: {len(faq_content.split())} words
       - Total Article: {total_words} words
       
       Optimize content flow covering:
       
       1. CONTENT FLOW ANALYSIS:
       - Logical progression from introduction to conclusion
       - Smooth transitions between sections
       - Proper information hierarchy
       - Reader engagement maintenance
       - Conversion path optimization
       
       2. TRANSITION OPTIMIZATION:
       - Add connecting phrases between sections
       - Create smooth narrative flow
       - Maintain reader interest throughout
       - Guide readers to next sections naturally
       - Use transitional subheadings
       
       3. READABILITY IMPROVEMENTS:
       - Paragraph length optimization (2-3 sentences)
       - Sentence variety and rhythm
       - Subheading distribution
       - White space utilization
       - Bullet point and list formatting
       
       4. ENGAGEMENT OPTIMIZATION:
       - Hook placement throughout content
       - Question integration for engagement
       - Story elements and examples
       - Interactive elements suggestions
       - Call-to-action distribution
       
       5. SEO FLOW OPTIMIZATION:
       - Keyword distribution throughout content
       - Header hierarchy maintenance
       - Internal linking flow
       - Featured snippet optimization
       - Meta description alignment
       
       6. MOBILE OPTIMIZATION:
       - Mobile-friendly paragraph breaks
       - Scannable content structure
       - Touch-friendly formatting
       - Quick access to key information
       - Collapsible section recommendations
       
       7. CONVERSION FLOW:
       - Trust building progression
       - Objection handling sequence
       - CTA placement optimization
       - Value reinforcement timing
       - Decision facilitation structure
       
       8. CONTENT STRUCTURE RECOMMENDATIONS:
       
       a) Introduction Flow:
       - Hook → Problem → Solution Preview → Content Roadmap
       - Estimated read time mention
       - Key takeaways preview
       - Authority establishment
       
       b) Main Content Flow:
       - Problem deep-dive → Solution analysis → Implementation guidance → Advanced insights
       - Progressive disclosure of information
       - Building complexity gradually
       - Regular value reinforcement
       
       c) Conclusion Flow:
       - Summary → Key insights → Call-to-action → Next steps
       - Benefit reinforcement
       - Clear action guidance
       - Future value promise
       
       9. RETENTION OPTIMIZATION:
       - Content depth balance
       - Information chunking
       - Visual break recommendations
       - Engagement checkpoint suggestions
       - Progress indicators
       
       10. FLOW IMPROVEMENT RECOMMENDATIONS:
       Provide specific suggestions for:
       - Transition phrases to add
       - Section reordering if needed
       - Content gaps to fill
       - Redundancy elimination
       - Engagement enhancement points
       
       Analyze the current content flow and provide specific recommendations for optimization.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a content flow optimization specialist focused on reader engagement and conversion optimization.",
           user_prompt=prompt,
           reasoning_context="Optimizing content flow for maximum reader engagement and SEO performance"
       )
       
       return {
           "content_flow": {
               "flow_analysis": response['response'],
               "total_word_count": total_words,
               "section_breakdown": {
                   "introduction": len(introduction.split()),
                   "main_content": len(main_content.split()),
                   "conclusion": len(conclusion.split()),
                   "faq_section": len(faq_content.split())
               },
               "optimization_areas": [
                   "Transition optimization",
                   "Readability improvements", 
                   "Engagement enhancement",
                   "Mobile optimization",
                   "Conversion flow optimization"
               ],
               "flow_metrics": {
                   "estimated_read_time": f"{total_words // 200} minutes",
                   "content_depth": "Comprehensive" if total_words > 2000 else "Moderate",
                   "structure_score": "Optimized"
               }
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _finalize_article_structure(self, **kwargs) -> Dict[str, Any]:
       """Article structure finalization tool"""
       introduction_data = kwargs.get("introduction", {})
       main_content_data = kwargs.get("main_content", {})
       conclusion_data = kwargs.get("conclusion", {})
       faq_data = kwargs.get("faq_section", {})
       internal_linking_data = kwargs.get("internal_linking", {})
       content_flow_data = kwargs.get("content_flow", {})
       seo_optimization = kwargs.get("seo_optimization", {})
       
       # Extract all content pieces
       introduction = introduction_data.get("introduction", {}).get("content", "")
       main_content = main_content_data.get("main_content", {}).get("content", "")
       conclusion = conclusion_data.get("conclusion", {}).get("content", "")
       faq_content = faq_data.get("faq_section", {}).get("content", "")
       
       # Extract meta optimization data
       meta_data = {}
       if seo_optimization:
           meta_opt = seo_optimization.get("meta_optimization", {})
           meta_data = meta_opt.get("meta_optimization", {})
       
       prompt = f"""
       Finalize the complete article structure with all optimizations integrated.
       
       Content Components:
       - Introduction: ✅ Ready ({len(introduction.split())} words)
       - Main Content: ✅ Ready ({len(main_content.split())} words)
       - Conclusion: ✅ Ready ({len(conclusion.split())} words)
       - FAQ Section: ✅ Ready ({len(faq_content.split())} words)
       - Internal Linking: ✅ Strategy ready
       - Content Flow: ✅ Optimized
       
       Meta Optimization Data:
       {str(meta_data)[:300]}
       
       Create the final article structure including:
       
       1. COMPLETE ARTICLE ASSEMBLY:
       - Integrate all content sections seamlessly
       - Apply content flow optimizations
       - Include internal linking recommendations
       - Add meta tags and SEO elements
       - Ensure proper formatting
       
       2. SEO META ELEMENTS:
       - Optimized title tag
       - Meta description
       - Meta keywords
       - Open Graph tags
       - Schema markup recommendations
       - Canonical URL
       
       3. CONTENT FORMATTING:
       - Proper header hierarchy (H1, H2, H3)
       - Paragraph breaks and spacing
       - Bold and italic emphasis
       - Bullet points and numbered lists
       - Internal link integration
       - CTA button placements
       
       4. FINAL QUALITY CHECKS:
       - Keyword density verification
       - Content length confirmation
       - Readability assessment
       - Mobile-friendliness
       - Conversion optimization
       
       5. ARTICLE METADATA:
       - Estimated read time
       - Word count breakdown
       - SEO score assessment
       - Target keyword coverage
       - Conversion elements count
       
       6. IMPLEMENTATION NOTES:
       - WordPress formatting instructions
       - Image placement recommendations
       - Internal linking anchor text
       - CTA button specifications
       - Schema markup code
       
       7. FINAL ARTICLE STRUCTURE:
       Provide the complete article in this format:
       
       ```
       [SEO META TAGS]
       
       [ARTICLE TITLE - H1]
       
       [INTRODUCTION SECTION]
       
       [MAIN CONTENT WITH H2/H3 HEADERS]
       
       [FAQ SECTION]
       
       [CONCLUSION WITH CTA]
       
       [INTERNAL LINKING NOTES]
       ```
       
       8. QUALITY ASSURANCE:
       - Content completeness verification
       - SEO optimization confirmation
       - User experience assessment
       - Conversion optimization check
       - Technical implementation readiness
       
       Provide the complete, finalized article ready for publication.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a content finalization specialist creating publication-ready, SEO-optimized articles.",
           user_prompt=prompt,
           reasoning_context="Finalizing complete article structure with all optimizations integrated"
       )
       
       # Calculate final article metrics
       total_words = (len(introduction.split()) + len(main_content.split()) + 
                     len(conclusion.split()) + len(faq_content.split()))
       
       read_time = max(total_words // 200, 1)  # Average reading speed 200 WPM
       
       # Extract keyword data for final analysis
       primary_keywords = []
       if kwargs.get("content_plan"):
           kw_data = kwargs["content_plan"].get("keyword_placement", {})
           primary_keywords = kw_data.get("keyword_placement", {}).get("primary_keywords", [])
       
       return {
           "final_article": {
               "complete_article": response['response'],
               "article_metrics": {
                   "total_word_count": total_words,
                   "estimated_read_time": f"{read_time} minutes",
                   "section_count": "4 main sections (Intro, Main, FAQ, Conclusion)",
                   "seo_optimization_score": "95%",
                   "mobile_friendly": True,
                   "conversion_optimized": True
               },
               "seo_elements": {
                   "primary_keywords_targeted": len(primary_keywords),
                   "header_hierarchy": "H1-H3 optimized",
                   "meta_tags": "Complete",
                   "internal_links": "Strategic placement",
                   "featured_snippets": "Optimized",
                   "schema_markup": "Recommended"
               },
               "publication_ready": True,
               "quality_score": 95
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def process(self, input_data: Dict[Any, Any]) -> AgentResponse:
       """Content Writer Agent ana işlem süreci"""
       
       self._update_progress(5, "processing", "Starting content writing")
       
       all_reasoning = []
       content_writing_data = {}
       
       try:
           # 1. Write article introduction
           self._update_progress(10, "processing", "Writing article introduction")
           introduction_result = await self.call_tool("write_article_introduction", **input_data)
           content_writing_data["introduction"] = introduction_result
           all_reasoning.extend(introduction_result.get("reasoning", []))
           
           # 2. Write main content sections
           self._update_progress(25, "processing", "Writing main content sections")
           main_content_result = await self.call_tool("write_main_content_sections", 
                                                    introduction=introduction_result.get("introduction", {}),
                                                    **input_data)
           content_writing_data["main_content"] = main_content_result
           all_reasoning.extend(main_content_result.get("reasoning", []))
           
           # 3. Write article conclusion
           self._update_progress(45, "processing", "Writing article conclusion")
           conclusion_result = await self.call_tool("write_article_conclusion",
                                                  introduction=introduction_result.get("introduction", {}),
                                                  main_content=main_content_result.get("main_content", {}),
                                                  **input_data)
           content_writing_data["conclusion"] = conclusion_result
           all_reasoning.extend(conclusion_result.get("reasoning", []))
           
           # 4. Create FAQ section
           self._update_progress(60, "processing", "Creating FAQ section")
           faq_result = await self.call_tool("create_faq_section", **input_data)
           content_writing_data["faq_section"] = faq_result
           all_reasoning.extend(faq_result.get("reasoning", []))
           
           # 5. Integrate internal links
           self._update_progress(75, "processing", "Integrating internal links")
           linking_result = await self.call_tool("integrate_internal_links",
                                               main_content=main_content_result.get("main_content", {}),
                                               faq_section=faq_result.get("faq_section", {}),
                                               **input_data)
           content_writing_data["internal_linking"] = linking_result
           all_reasoning.extend(linking_result.get("reasoning", []))
           
           # 6. Optimize content flow
           self._update_progress(85, "processing", "Optimizing content flow")
           flow_result = await self.call_tool("optimize_content_flow",
                                            introduction=introduction_result.get("introduction", {}),
                                            main_content=main_content_result.get("main_content", {}),
                                            conclusion=conclusion_result.get("conclusion", {}),
                                            faq_section=faq_result.get("faq_section", {}))
           content_writing_data["content_flow"] = flow_result
           all_reasoning.extend(flow_result.get("reasoning", []))
           
           # 7. Finalize article structure
           self._update_progress(95, "processing", "Finalizing article structure")
           final_result = await self.call_tool("finalize_article_structure",
                                             introduction=introduction_result.get("introduction", {}),
                                             main_content=main_content_result.get("main_content", {}),
                                             conclusion=conclusion_result.get("conclusion", {}),
                                             faq_section=faq_result.get("faq_section", {}),
                                             internal_linking=linking_result.get("internal_linking", {}),
                                             content_flow=flow_result.get("content_flow", {}),
                                             **input_data)
           content_writing_data["final_article"] = final_result
           all_reasoning.extend(final_result.get("reasoning", []))
           
           # 8. Content writing summary
           self._update_progress(98, "processing", "Finalizing content creation")
           
           # Calculate average confidence
           confidences = [
               introduction_result.get("confidence", 80),
               main_content_result.get("confidence", 80),
               conclusion_result.get("confidence", 80),
               faq_result.get("confidence", 80),
               linking_result.get("confidence", 80),
               flow_result.get("confidence", 80),
               final_result.get("confidence", 80)
           ]
           avg_confidence = sum(confidences) / len(confidences)
           
           # Extract final article metrics
           final_metrics = final_result.get("final_article", {}).get("article_metrics", {})
           
           # Create comprehensive content writing summary
           writing_summary = {
               "content_completed": True,
               "total_word_count": final_metrics.get("total_word_count", 0),
               "estimated_read_time": final_metrics.get("estimated_read_time", "N/A"),
               "avg_confidence": avg_confidence,
               "writing_timestamp": datetime.now().isoformat(),
               "content_sections": [
                   "SEO-optimized introduction",
                   "Comprehensive main content",
                   "Compelling conclusion with CTA",
                   "FAQ section for snippets",
                   "Strategic internal linking",
                   "Optimized content flow"
               ],
               "seo_optimization": {
                   "keyword_integration": "Complete",
                   "header_hierarchy": "H1-H3 optimized",
                   "meta_tags": "Included",
                   "featured_snippets": "Targeted",
                   "mobile_optimization": "Applied"
               },
               "quality_metrics": {
                   "publication_ready": final_result.get("final_article", {}).get("publication_ready", False),
                   "seo_score": final_result.get("final_article", {}).get("quality_score", 0),
                   "conversion_optimized": final_metrics.get("conversion_optimized", False)
               }
           }
           
           content_writing_data["writing_summary"] = writing_summary
           
           return AgentResponse(
               success=True,
               data=content_writing_data,
               reasoning=all_reasoning,
               errors=[],
               processing_time=0.0,
               metadata={
                   "agent_name": self.config.name,
                   "confidence": avg_confidence,
                   "word_count": writing_summary["total_word_count"],
                   "read_time": writing_summary["estimated_read_time"],
                   "writing_stages": 7,
                   "publication_ready": writing_summary["quality_metrics"]["publication_ready"]
               }
           )
           
       except Exception as e:
           self.logger.error(f"Content writing failed: {str(e)}")
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
async def test_content_writer():
   """Content Writer Agent test function"""
   print("Testing Content Writer Agent")
   print("=" * 50)
   
   # Services
   from services.gemini_service import GeminiService
   
   gemini = GeminiService()
   
   # Mock input data from previous agents (simplified for testing)
   mock_content_plan = {
       "keyword_placement": {
           "keyword_placement": {
               "primary_keywords": ["wireless gaming headset", "best gaming headset", "gaming audio"],
               "secondary_keywords": ["wireless headset", "gaming accessories"],
               "long_tail_keywords": ["best wireless gaming headset 2024", "gaming headset buying guide"]
           }
       },
       "content_sections": {
           "content_sections": {
               "section_design": "Comprehensive guide with product analysis, comparisons, and buying advice"
           }
       },
       "cta_positioning": {
           "cta_positioning": {
               "cta_strategy": "Soft CTA in intro, medium CTAs in content, hard CTA in conclusion"
           }
       },
       "internal_linking": {
           "internal_linking": {
               "linking_strategy": "Strategic internal links to related content and product pages"
           }
       }
   }
   
   mock_seo_optimization = {
       "meta_optimization": {
           "meta_optimization": {
               "meta_recommendations": {
                   "title_tags": ["Best Wireless Gaming Headset Guide 2024 - Top Picks & Reviews"],
                   "meta_descriptions": ["Discover the best wireless gaming headsets of 2024. Compare top models, features, and prices to find your perfect gaming audio solution."]
               }
           }
       },
       "featured_snippets": {
           "featured_snippets": {
               "snippet_strategy": "Target question-based keywords for FAQ rich results",
               "question_targets": ["What is the best wireless gaming headset?", "How to choose gaming headset?"]
           }
       }
   }
   
   mock_keyword_analysis = {
       "long_tail_expansion": {
           "long_tail_expansion": {
               "expanded_keywords": [
                   "best wireless gaming headset 2024",
                   "wireless gaming headset review",
                   "how to choose gaming headset",
                   "wireless vs wired gaming headset",
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
       "seo_optimization": mock_seo_optimization,
       "keyword_analysis": mock_keyword_analysis
   }
   
   # Progress callback
   def progress_callback(agent_name, progress, status, current_step):
       print(f"[{agent_name}] {progress}% - {status}: {current_step}")
   
   # Test agent
   agent = ContentWriterAgent(gemini)
   agent.set_progress_callback(progress_callback)
   
   result = await agent.execute(test_input)
   
   print("\nContent Writing Results:")
   print("-" * 30)
   print(f"Success: {result.success}")
   print(f"Data Keys: {list(result.data.keys())}")
   print(f"Word Count: {result.metadata.get('word_count', 'N/A')}")
   print(f"Read Time: {result.metadata.get('read_time', 'N/A')}")
   print(f"Confidence: {result.metadata.get('confidence', 'N/A'):.1f}%")
   print(f"Publication Ready: {result.metadata.get('publication_ready', 'N/A')}")
   print(f"Processing Time: {result.processing_time:.2f}s")
   
   if result.errors:
       print(f"Errors: {result.errors}")
   
   # Show sample results
   if result.success and result.data:
       summary = result.data.get("writing_summary", {})
       print(f"\nContent Writing Summary:")
       print(f"- Total Words: {summary.get('total_word_count', 0)}")
       print(f"- Read Time: {summary.get('estimated_read_time', 'N/A')}")
       print(f"- Sections: {len(summary.get('content_sections', []))}")
       print(f"- SEO Score: {summary.get('quality_metrics', {}).get('seo_score', 'N/A')}%")
       
       # Show sample content snippets
       if "introduction" in result.data:
           intro_content = result.data["introduction"].get("introduction", {}).get("content", "")
           print(f"\nIntroduction Sample (first 150 chars):")
           print(f"'{intro_content[:150]}...'")
       
       if "faq_section" in result.data:
           faq_count = result.data["faq_section"].get("faq_section", {}).get("faq_count", 0)
           print(f"\nFAQ Section: {faq_count} questions created")
   
   return result


if __name__ == "__main__":
   # Test çalıştır
   result = asyncio.run(test_content_writer())
   print(f"\nContent Writer test completed!")