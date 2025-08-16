"""
Content Planner Agent - AI SEO Blog Generator

Bu agent content planning ve structure optimization yapar:
- Content outline ve structure planning
- H1-H6 header hierarchy optimization
- Keyword placement strategy
- Content sections planning
- Internal linking opportunities
- CTA positioning strategy
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


class ContentPlannerAgent(BaseAgent, ToolMixin):
   """
   Content Planner Agent - Üçüncü pipeline agent'ı
   
   Görevleri:
   - Content outline ve structure planning
   - SEO-optimized header hierarchy
   - Keyword placement strategy
   - Content sections planning
   - Internal linking strategy
   - CTA positioning optimization
   """
   
   def __init__(self, gemini_service: GeminiService):
       config = AgentConfig(
           name="content_planner",
           description="Plans content structure, hierarchy, and keyword placement for SEO optimization",
           max_retries=3,
           timeout_seconds=150,
           temperature=0.6,  # Balanced creativity and structure
           reasoning_enabled=True
       )
       
       BaseAgent.__init__(self, config, gemini_service)
       ToolMixin.__init__(self)
       
       # Content planning araçları
       self._register_content_planning_tools()
       
       self.logger.info("ContentPlannerAgent initialized")
   
   def _register_content_planning_tools(self):
       """Content planning araçlarını kaydet"""
       self.available_tools.update({
           "analyze_content_requirements": self._analyze_content_requirements,
           "create_content_outline": self._create_content_outline,
           "optimize_header_hierarchy": self._optimize_header_hierarchy,
           "plan_keyword_placement": self._plan_keyword_placement,
           "design_content_sections": self._design_content_sections,
           "plan_internal_linking": self._plan_internal_linking,
           "position_cta_elements": self._position_cta_elements
       })
   
   async def _analyze_content_requirements(self, **kwargs) -> Dict[str, Any]:
       """Content requirements analysis tool"""
       keyword_data = kwargs.get("keyword_analysis", {})
       product_name = kwargs.get("product_name", "")
       target_audience = kwargs.get("target_audience", "")
       niche = kwargs.get("niche", "")
       
       # Extract keyword information
       primary_keywords = []
       intent_distribution = {}
       
       if keyword_data:
           primary_selection = keyword_data.get("primary_selection", {})
           intent_analysis = keyword_data.get("intent_analysis", {})
           
           primary_keywords = primary_selection.get("keyword_selection", {}).get("primary_keywords", [])[:10]
           intent_distribution = intent_analysis.get("intent_analysis", {}).get("distribution", {})
       
       primary_kw_list = [kw.get('keyword', kw) if isinstance(kw, dict) else kw for kw in primary_keywords]
       
       prompt = f"""
       Analyze content requirements for {product_name} in {niche} niche.
       
       Target Audience: {target_audience}
       Primary Keywords: {', '.join(primary_kw_list)}
       
       Search Intent Distribution:
       - Informational: {intent_distribution.get('informational', 0)} keywords
       - Commercial: {intent_distribution.get('commercial', 0)} keywords
       - Transactional: {intent_distribution.get('transactional', 0)} keywords
       - Navigational: {intent_distribution.get('navigational', 0)} keywords
       
       Analyze and recommend:
       
       1. CONTENT TYPE REQUIREMENTS:
       - Optimal content format (guide, review, comparison, tutorial)
       - Content length recommendation (1500-3000 words)
       - Content depth level needed
       - Technical complexity appropriate for audience
       
       2. CONTENT STRUCTURE NEEDS:
       - Required sections based on search intent
       - Information hierarchy priorities
       - User journey considerations
       - Conversion funnel positioning
       
       3. AUDIENCE ENGAGEMENT STRATEGY:
       - Content tone and style recommendations
       - Engagement elements needed (images, videos, interactive)
       - Trust signals and credibility factors
       - Pain points to address
       
       4. SEO CONTENT REQUIREMENTS:
       - Featured snippet optimization opportunities
       - FAQ sections needed
       - Schema markup recommendations
       - E-A-T considerations
       
       5. COMPETITIVE POSITIONING:
       - Content differentiation strategy
       - Unique value proposition integration
       - Gap analysis for comprehensive coverage
       - Authority building elements
       
       Provide specific, actionable content requirements that will maximize SEO performance and user engagement.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a content strategist specializing in SEO-optimized content planning.",
           user_prompt=prompt,
           reasoning_context="Analyzing content requirements for optimal SEO performance"
       )
       
       return {
           "content_requirements": {
               "analysis": response['response'],
               "primary_keywords_analyzed": primary_kw_list,
               "intent_distribution": intent_distribution,
               "target_specs": {
                   "product": product_name,
                   "audience": target_audience,
                   "niche": niche
               }
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _create_content_outline(self, **kwargs) -> Dict[str, Any]:
       """Content outline creation tool"""
       content_requirements = kwargs.get("content_requirements", {})
       keyword_data = kwargs.get("keyword_analysis", {})
       product_name = kwargs.get("product_name", "")
       
       # Extract keywords for outline
       primary_keywords = []
       long_tail_keywords = []
       
       if keyword_data:
           primary_selection = keyword_data.get("primary_selection", {})
           long_tail_expansion = keyword_data.get("long_tail_expansion", {})
           
           primary_keywords = primary_selection.get("keyword_selection", {}).get("primary_keywords", [])[:8]
           long_tail_keywords = long_tail_expansion.get("long_tail_expansion", {}).get("expanded_keywords", [])[:15]
       
       primary_kw_list = [kw.get('keyword', kw) if isinstance(kw, dict) else kw for kw in primary_keywords]
       
       prompt = f"""
       Create a comprehensive content outline for {product_name}.
       
       Primary Keywords to Target: {', '.join(primary_kw_list)}
       Long-tail Keywords: {', '.join(long_tail_keywords[:10])}
       
       Content Requirements Analysis:
       {content_requirements.get('analysis', 'No specific requirements provided')}
       
       Create a detailed content outline with this structure:
       
       1. COMPELLING TITLE (H1):
       - Include primary keyword naturally
       - Promise clear value/benefit
       - Create urgency or curiosity
       - Keep under 60 characters for SEO
       
       2. INTRODUCTION SECTION (150-200 words):
       - Hook with pain point or benefit
       - Preview what reader will learn
       - Include primary keyword early
       - Set expectations and credibility
       
       3. MAIN CONTENT SECTIONS (H2 headers):
       Create 6-8 main sections covering:
       - Problem identification and solution
       - Product features and benefits analysis
       - Buying guide or how-to information
       - Comparison with alternatives
       - Use cases and applications
       - Technical specifications or details
       - Pricing and value analysis
       - User experience and reviews
       
       4. SUPPORTING SUBSECTIONS (H3 headers):
       For each main section, include 2-4 subsections that:
       - Target long-tail keywords
       - Address specific user questions
       - Provide detailed information
       - Include actionable advice
       
       5. CONVERSION ELEMENTS:
       - Strategic CTA placement points
       - Trust signals and social proof
       - FAQ section (2-3 questions)
       - Summary and next steps
       
       6. CONCLUSION SECTION:
       - Recap key benefits
       - Clear call-to-action
       - Additional resources
       - Final persuasive elements
       
       For each section, specify:
       - Target word count
       - Primary keyword to focus on
       - Content purpose and goal
       - Key points to cover
       
       Make the outline comprehensive, logical, and optimized for both users and search engines.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a content outline specialist creating SEO-optimized article structures.",
           user_prompt=prompt,
           reasoning_context="Creating comprehensive content outline for maximum SEO impact"
       )
       
       # Parse outline structure from response
       outline_structure = self._parse_outline_structure(response['response'])
       
       return {
           "content_outline": {
               "detailed_outline": response['response'],
               "structure": outline_structure,
               "target_keywords": primary_kw_list,
               "supporting_keywords": long_tail_keywords[:10],
               "estimated_word_count": self._estimate_word_count(outline_structure)
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _parse_outline_structure(self, outline_text: str) -> Dict[str, Any]:
       """Parse outline text into structured format"""
       structure = {
           "title": "",
           "introduction": {},
           "main_sections": [],
           "conclusion": {},
           "total_sections": 0
       }
       
       try:
           lines = outline_text.split('\n')
           current_section = None
           current_subsections = []
           
           for line in lines:
               line = line.strip()
               if not line:
                   continue
               
               # Look for title/H1
               if any(keyword in line.lower() for keyword in ['title', 'h1', 'headline']):
                   if ':' in line:
                       structure["title"] = line.split(':', 1)[1].strip()
               
               # Look for H2 main sections
               if line.startswith('##') or 'H2' in line or any(phrase in line.lower() for phrase in ['main section', 'section:']):
                   if current_section:
                       current_section["subsections"] = current_subsections
                       structure["main_sections"].append(current_section)
                   
                   current_section = {
                       "title": line.replace('##', '').replace('H2:', '').strip(),
                       "subsections": []
                   }
                   current_subsections = []
               
               # Look for H3 subsections
               elif line.startswith('###') or 'H3' in line:
                   if current_section:
                       current_subsections.append(line.replace('###', '').replace('H3:', '').strip())
           
           # Add last section
           if current_section:
               current_section["subsections"] = current_subsections
               structure["main_sections"].append(current_section)
           
           structure["total_sections"] = len(structure["main_sections"])
           
       except Exception as e:
           self.logger.warning(f"Failed to parse outline structure: {e}")
       
       return structure
   
   def _estimate_word_count(self, structure: Dict[str, Any]) -> int:
       """Estimate total word count based on structure"""
       base_count = 200  # Introduction
       base_count += 150  # Conclusion
       
       # Main sections (300-400 words each)
       main_sections = len(structure.get("main_sections", []))
       base_count += main_sections * 350
       
       # Subsections (100-150 words each)
       total_subsections = sum(len(section.get("subsections", [])) for section in structure.get("main_sections", []))
       base_count += total_subsections * 125
       
       return base_count
   
   async def _optimize_header_hierarchy(self, **kwargs) -> Dict[str, Any]:
       """Header hierarchy optimization tool"""
       content_outline = kwargs.get("content_outline", {})
       primary_keywords = kwargs.get("primary_keywords", [])
       
       if not content_outline:
           return {"error": "No content outline provided"}
       
       outline_text = content_outline.get("detailed_outline", "")
       structure = content_outline.get("structure", {})
       
       prompt = f"""
       Optimize header hierarchy for SEO and user experience.
       
       Current Content Structure:
       - Total Main Sections: {structure.get('total_sections', 0)}
       - Title: {structure.get('title', 'Not defined')}
       
       Primary Keywords: {', '.join([kw.get('keyword', kw) if isinstance(kw, dict) else kw for kw in primary_keywords[:5]])}
       
       Content Outline:
       {outline_text[:1000]}...
       
       Create optimized header hierarchy following these SEO best practices:
       
       1. H1 OPTIMIZATION:
       - Only one H1 per page (the title)
       - Include primary keyword naturally
       - Keep between 20-60 characters
       - Make it compelling and click-worthy
       - Ensure it matches search intent
       
       2. H2 STRUCTURE (Main Sections):
       - Use for main topic divisions
       - Include primary/secondary keywords naturally
       - Maintain logical content flow
       - 6-8 H2s maximum for readability
       - Each H2 should be descriptive and specific
       
       3. H3 SUBSECTIONS:
       - Support each H2 with 2-4 H3s
       - Target long-tail keywords
       - Address specific user questions
       - Maintain parallel structure
       - Include action words when appropriate
       
       4. H4-H6 USAGE:
       - H4 for detailed breakdowns under H3s
       - H5-H6 for specific lists or examples
       - Avoid going too deep (H4 maximum recommended)
       - Maintain content hierarchy logic
       
       5. KEYWORD DISTRIBUTION:
       - Primary keyword in H1 and 1-2 H2s
       - Secondary keywords in remaining H2s
       - Long-tail keywords in H3s
       - Avoid keyword stuffing
       - Maintain natural language flow
       
       6. USER EXPERIENCE OPTIMIZATION:
       - Headers should be scannable
       - Promise clear value in each header
       - Use parallel structure and tense
       - Include numbers where appropriate
       - Make headers descriptive, not clever
       
       Provide the complete optimized header hierarchy with:
       - Exact header text for each level
       - Target keyword for each header
       - Estimated word count for each section
       - SEO optimization notes
       
       Make headers compelling for users while maximizing SEO value.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a SEO header optimization specialist focused on both search rankings and user experience.",
           user_prompt=prompt,
           reasoning_context="Optimizing header hierarchy for maximum SEO impact and readability"
       )
       
       # Parse optimized headers
       optimized_headers = self._parse_header_hierarchy(response['response'])
       
       return {
           "header_hierarchy": {
               "optimized_headers": optimized_headers,
               "optimization_strategy": response['response'],
               "seo_guidelines_applied": [
                   "Single H1 with primary keyword",
                   "6-8 H2s for main sections",
                   "2-4 H3s per H2 section",
                   "Keyword distribution optimization",
                   "User experience focus"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _parse_header_hierarchy(self, hierarchy_text: str) -> List[Dict[str, Any]]:
       """Parse header hierarchy from AI response"""
       headers = []
       
       try:
           lines = hierarchy_text.split('\n')
           
           for line in lines:
               line = line.strip()
               if not line:
                   continue
               
               # Detect header level
               level = 0
               if line.startswith('# ') or 'H1:' in line:
                   level = 1
               elif line.startswith('## ') or 'H2:' in line:
                   level = 2
               elif line.startswith('### ') or 'H3:' in line:
                   level = 3
               elif line.startswith('#### ') or 'H4:' in line:
                   level = 4
               
               if level > 0:
                   # Clean header text
                   header_text = line
                   for prefix in ['# ', '## ', '### ', '#### ', 'H1:', 'H2:', 'H3:', 'H4:']:
                       header_text = header_text.replace(prefix, '').strip()
                   
                   headers.append({
                       "level": level,
                       "text": header_text,
                       "target_keyword": "",  # Will be extracted if specified
                       "estimated_words": 200 if level <= 2 else 100
                   })
       
       except Exception as e:
           self.logger.warning(f"Failed to parse header hierarchy: {e}")
       
       return headers
   
   async def _plan_keyword_placement(self, **kwargs) -> Dict[str, Any]:
       """Keyword placement strategy tool"""
       header_hierarchy = kwargs.get("header_hierarchy", {})
       keyword_data = kwargs.get("keyword_analysis", {})
       content_outline = kwargs.get("content_outline", {})
       
       # Extract keyword information
       primary_keywords = []
       secondary_keywords = []
       long_tail_keywords = []
       
       if keyword_data:
           primary_selection = keyword_data.get("primary_selection", {})
           long_tail_expansion = keyword_data.get("long_tail_expansion", {})
           
           kw_selection = primary_selection.get("keyword_selection", {})
           primary_keywords = kw_selection.get("primary_keywords", [])[:5]
           secondary_keywords = kw_selection.get("secondary_keywords", [])[:10]
           long_tail_keywords = long_tail_expansion.get("long_tail_expansion", {}).get("expanded_keywords", [])[:15]
       
       primary_kw_list = [kw.get('keyword', kw) if isinstance(kw, dict) else kw for kw in primary_keywords]
       secondary_kw_list = [kw.get('keyword', kw) if isinstance(kw, dict) else kw for kw in secondary_keywords]
       
       prompt = f"""
       Create comprehensive keyword placement strategy for SEO optimization.
       
       Primary Keywords (High Priority): {', '.join(primary_kw_list)}
       Secondary Keywords (Medium Priority): {', '.join(secondary_kw_list)}
       Long-tail Keywords (Supporting): {', '.join(long_tail_keywords[:10])}
       
       Content Structure Overview:
       {header_hierarchy.get('optimization_strategy', 'No header structure provided')[:500]}
       
       Create detailed keyword placement strategy covering:
       
       1. PRIMARY KEYWORD PLACEMENT:
       - H1 (Title): Natural integration with primary keyword
       - First paragraph: Include within first 100 words
       - H2 headers: 1-2 headers should include primary keyword
       - Throughout content: 1-2% keyword density target
       - Meta elements: Title tag and description optimization
       
       2. SECONDARY KEYWORD DISTRIBUTION:
       - H2 headers: Distribute across remaining main sections
       - H3 subheaders: Natural integration in subsections
       - Content body: Support primary keyword context
       - Image alt text: Include in relevant image descriptions
       - Internal links: Use as anchor text variations
       
       3. LONG-TAIL KEYWORD STRATEGY:
       - H3 and H4 headers: Target specific long-tail phrases
       - FAQ section: Address long-tail question keywords
       - Content body: Natural integration throughout
       - Featured snippet optimization: Target question-based long-tails
       - Schema markup: Include in structured data
       
       4. KEYWORD DENSITY GUIDELINES:
       - Primary keyword: 1-2% density (avoid over-optimization)
       - Secondary keywords: 0.5-1% density each
       - Long-tail keywords: Natural mention frequency
       - LSI keywords: Include semantic variations
       - Synonym usage: Maintain content natural flow
       
       5. CONTENT SECTION MAPPING:
       For each main content section, specify:
       - Primary keyword focus for the section
       - Supporting secondary keywords
       - Long-tail keyword opportunities
       - Natural integration strategies
       - Contextual keyword variations
       
       6. SEO OPTIMIZATION TACTICS:
       - Title tag optimization (primary keyword + modifier)
       - Meta description keyword inclusion
       - URL slug optimization
       - Image file names and alt text
       - Internal linking anchor text strategy
       
       7. NATURAL LANGUAGE INTEGRATION:
       - Avoid keyword stuffing penalties
       - Use synonyms and related terms
       - Maintain content readability
       - Focus on user experience first
       - Include conversational keyword variations
       
       Provide specific placement recommendations for each section of the content with exact keyword integration examples.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a SEO keyword placement specialist focused on natural integration and search optimization.",
           user_prompt=prompt,
           reasoning_context="Creating comprehensive keyword placement strategy for content optimization"
       )
       
       # Calculate keyword density targets
       estimated_words = content_outline.get("estimated_word_count", 2000)
       keyword_targets = {
           "primary_keyword_mentions": max(int(estimated_words * 0.015), 3),  # 1.5% density
           "secondary_keyword_mentions": max(int(estimated_words * 0.008), 2),  # 0.8% density per keyword
           "long_tail_mentions": 1  # Natural mentions
       }
       
       return {
           "keyword_placement": {
               "placement_strategy": response['response'],
               "keyword_targets": keyword_targets,
               "primary_keywords": primary_kw_list,
               "secondary_keywords": secondary_kw_list[:5],
               "long_tail_keywords": long_tail_keywords[:10],
               "density_guidelines": {
                   "primary": "1-2%",
                   "secondary": "0.5-1% each",
                   "long_tail": "Natural mentions"
               }
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _design_content_sections(self, **kwargs) -> Dict[str, Any]:
       """Content sections design tool"""
       content_outline = kwargs.get("content_outline", {})
       keyword_placement = kwargs.get("keyword_placement", {})
       product_name = kwargs.get("product_name", "")
       target_audience = kwargs.get("target_audience", "")
       
       structure = content_outline.get("structure", {})
       main_sections = structure.get("main_sections", [])
       
       prompt = f"""
       Design detailed content sections for {product_name} targeting {target_audience}.
       
       Content Structure:
       - Total Sections: {len(main_sections)}
       - Estimated Length: {content_outline.get('estimated_word_count', 2000)} words
       
       Main Sections Overview:
       {json.dumps([section.get('title', 'Untitled') for section in main_sections], indent=2)}
       
       Keyword Strategy:
       {keyword_placement.get('placement_strategy', 'No keyword strategy provided')[:300]}
       
       Design comprehensive content sections with:
       
       1. INTRODUCTION SECTION (200-250 words):
       - Compelling hook addressing main pain point
       - Clear value proposition and benefits preview
       - Primary keyword integration in first paragraph
       - Trust signals and credibility establishment
       - Reading roadmap for user expectations
       
       2. MAIN CONTENT SECTIONS:
       For each main section, provide:
       
       a) SECTION PURPOSE & GOAL:
       - What specific user need does this address
       - How it supports the overall content objective
       - Search intent fulfillment strategy
       
       b) CONTENT STRUCTURE (300-500 words per section):
       - Opening statement with section keyword
       - 3-4 key points or benefits to cover
       - Supporting details and explanations
       - Examples, statistics, or case studies
       - Practical tips or actionable advice
       
       c) ENGAGEMENT ELEMENTS:
       - Visual content opportunities (images, charts)
       - Interactive elements (checklists, tools)
       - Trust signals (testimonials, reviews)
       - Authority building elements (expert quotes)
       
       d) SEO OPTIMIZATION:
       - Target keyword integration points
       - Long-tail keyword opportunities
       - Internal linking anchor text suggestions
       - Featured snippet optimization potential
       
       3. SUPPORTING SUBSECTIONS:
       For each H3 subsection:
       - Specific topic focus (100-150 words)
       - Long-tail keyword targeting
       - Detailed explanations or how-to steps
       - User question addressing
       
       4. CONVERSION OPTIMIZATION:
       - Strategic CTA placement throughout content
       - Trust building and social proof integration
       - Objection handling within relevant sections
       - Value reinforcement and benefit restating
       
       5. CONCLUSION SECTION (150-200 words):
       - Key takeaways summary
       - Primary benefit reinforcement
       - Clear next step or call-to-action
       - Additional resource recommendations
       
       6. FAQ SECTION (Optional but Recommended):
       - 3-5 common user questions
       - Long-tail keyword targeting opportunities
       - Featured snippet optimization
       - Comprehensive answer format
       
       For each section, specify:
       - Target word count
       - Primary content goal
       - Key points to cover
       - SEO optimization notes
       - User engagement strategy
       
       Create sections that are comprehensive, engaging, and optimized for both users and search engines.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a content section designer specializing in comprehensive, SEO-optimized article structures.",
           user_prompt=prompt,
           reasoning_context="Designing detailed content sections for maximum user engagement and SEO performance"
       )
       
       return {
           "content_sections": {
               "section_design": response['response'],
               "section_count": len(main_sections),
               "total_estimated_words": content_outline.get('estimated_word_count', 2000),
               "design_principles": [
                   "User-first content approach",
                   "SEO optimization integration",
                   "Conversion element placement",
                   "Engagement optimization",
                   "Authority building focus"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _plan_internal_linking(self, **kwargs) -> Dict[str, Any]:
       """Internal linking strategy tool"""
       content_sections = kwargs.get("content_sections", {})
       keyword_placement = kwargs.get("keyword_placement", {})
       keyword_data = kwargs.get("keyword_analysis", {})
       
       # Extract content clusters for linking
       content_clusters = {}
       if keyword_data:
           clusters = keyword_data.get("content_clusters", {})
           content_clusters = clusters.get("content_clusters", {})
       
       prompt = f"""
       Create comprehensive internal linking strategy for SEO optimization and user experience.
       
       Content Structure:
       {content_sections.get('section_design', 'No section design provided')[:500]}
       
       Keyword Strategy:
       Primary Keywords: {', '.join(keyword_placement.get('keyword_placement', {}).get('primary_keywords', []))}
       Secondary Keywords: {', '.join(keyword_placement.get('keyword_placement', {}).get('secondary_keywords', []))}
       
       Content Clusters Information:
       {str(content_clusters)[:300] if content_clusters else 'No cluster information available'}
       
       Design internal linking strategy covering:
       
       1. PILLAR CONTENT STRATEGY:
       - Identify this content's role in topic cluster
       - Hub and spoke linking architecture
       - Authority page linking opportunities
       - Topic cluster connection points
       
       2. CONTEXTUAL LINKING OPPORTUNITIES:
       - Relevant internal pages to link to
       - Anchor text optimization strategies
       - Link placement within content flow
       - Supporting content recommendations
       
       3. KEYWORD-BASED LINKING:
       - Primary keyword anchor text variations
       - Secondary keyword linking opportunities
       - Long-tail keyword internal links
       - Semantic keyword link variations
       
       4. SECTION-SPECIFIC LINKING:
       For each main content section, recommend:
       - 1-2 relevant internal links
       - Natural anchor text suggestions
       - Strategic placement within content
       - Supporting page recommendations
       
       5. USER JOURNEY OPTIMIZATION:
       - Funnel-aware linking strategy
       - Related content recommendations
       - Cross-selling opportunity links
       - Educational content connections
       
       6. LINK EQUITY DISTRIBUTION:
       - High-value page linking priorities
       - Authority building link strategies
       - Deep page visibility improvement
       - Link juice flow optimization
       
       7. TECHNICAL LINKING BEST PRACTICES:
       - Optimal link density (2-5 links per 1000 words)
       - dofollow link strategy
       - Link opening behavior (same window)
       - Mobile-friendly link placement
       
       8. CONTENT RELATIONSHIP MAPPING:
       - Related articles and guides
       - Product/service page connections
       - Category and tag page linking
       - Resource and tool page integration
       
       9. SUPPORTING CONTENT RECOMMENDATIONS:
       - Additional articles needed for cluster
       - Content gaps to fill with future articles
       - Link earning content opportunities
       - Authority building content ideas
       
       Provide specific internal linking recommendations with:
       - Exact anchor text suggestions
       - Optimal placement locations
       - Target page recommendations
       - SEO benefit explanations
       
       Focus on creating a natural, user-friendly linking structure that enhances both SEO and user experience.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are an internal linking strategist specializing in SEO optimization and user experience enhancement.",
           user_prompt=prompt,
           reasoning_context="Creating comprehensive internal linking strategy for content cluster optimization"
       )
       
       return {
           "internal_linking": {
               "linking_strategy": response['response'],
               "linking_principles": [
                   "Natural contextual placement",
                   "Keyword-optimized anchor text",
                   "User journey enhancement",
                   "Authority building focus",
                   "Topic cluster integration"
               ],
               "recommended_link_density": "2-5 links per 1000 words",
               "focus_areas": [
                   "Pillar content connections",
                   "Supporting article links",
                   "Product/service integration",
                   "Educational resource linking"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def _position_cta_elements(self, **kwargs) -> Dict[str, Any]:
       """CTA positioning strategy tool"""
       content_sections = kwargs.get("content_sections", {})
       target_audience = kwargs.get("target_audience", "")
       product_name = kwargs.get("product_name", "")
       
       prompt = f"""
       Design strategic CTA (Call-to-Action) positioning for {product_name} targeting {target_audience}.
       
       Content Structure Overview:
       {content_sections.get('section_design', 'No section design provided')[:400]}
       
       Create comprehensive CTA strategy covering:
       
       1. CTA PLACEMENT STRATEGY:
       - Introduction CTA (soft, awareness-focused)
       - Mid-content CTAs (engagement-focused)
       - Conclusion CTA (conversion-focused)
       - Sidebar/floating CTAs (persistent visibility)
       
       2. CTA TYPES AND PURPOSES:
       
       a) SOFT CTAs (Top of Funnel):
       - Newsletter signup offers
       - Free resource downloads
       - Educational content access
       - Community joining
       b) MEDIUM CTAs (Middle of Funnel):
       - Product demonstration requests
       - Free trial or consultation offers
       - Comparison guide downloads
       - Webinar or workshop registrations
       
       c) HARD CTAs (Bottom of Funnel):
       - Purchase/buy now buttons
       - Quote request forms
       - Contact sales team
       - Add to cart actions
       
       3. CONTENT-SPECIFIC CTA PLACEMENT:
       For each major content section, recommend:
       - Optimal CTA type for that section
       - Natural integration within content flow
       - Value proposition for that stage
       - Supporting trust signals needed
       
       4. CTA MESSAGING OPTIMIZATION:
       - Benefit-focused copy variations
       - Urgency and scarcity elements
       - Social proof integration
       - Risk reversal statements
       
       5. VISUAL CTA DESIGN RECOMMENDATIONS:
       - Button colors and styling
       - Size and prominence guidelines
       - Mobile optimization considerations
       - Visual hierarchy maintenance
       
       6. CONVERSION FUNNEL ALIGNMENT:
       - Awareness stage CTAs (informational)
       - Consideration stage CTAs (comparison)
       - Decision stage CTAs (purchase)
       - Retention stage CTAs (upsell)
       
       7. TRUST BUILDING ELEMENTS:
       - Security badges and guarantees
       - Customer testimonials near CTAs
       - Money-back guarantee mentions
       - Social proof indicators
       
       8. A/B TESTING RECOMMENDATIONS:
       - CTA copy variations to test
       - Placement alternatives
       - Color and design variations
       - Timing and frequency tests
       
       Provide specific CTA recommendations including:
       - Exact CTA copy suggestions
       - Optimal placement locations
       - Visual design guidelines
       - Conversion optimization tips
       
       Focus on creating CTAs that feel natural within the content while maximizing conversion potential.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a conversion optimization specialist focused on strategic CTA placement and messaging.",
           user_prompt=prompt,
           reasoning_context="Designing comprehensive CTA strategy for maximum conversion optimization"
       )
       
       return {
           "cta_positioning": {
               "cta_strategy": response['response'],
               "cta_types": {
                   "soft": "Newsletter, free resources, educational content",
                   "medium": "Demos, trials, consultations, guides",
                   "hard": "Purchase, quote requests, contact sales"
               },
               "placement_guidelines": [
                   "Introduction: Soft CTA for engagement",
                   "Mid-content: Medium CTAs at natural breaks",
                   "Conclusion: Hard CTA for conversion",
                   "Sidebar: Persistent visibility options"
               ],
               "optimization_focus": [
                   "Benefit-driven messaging",
                   "Trust signal integration",
                   "Mobile-friendly design",
                   "Natural content flow"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   async def process(self, input_data: Dict[Any, Any]) -> AgentResponse:
       """Content Planner Agent ana işlem süreci"""
       
       self._update_progress(5, "processing", "Starting content planning")
       
       all_reasoning = []
       content_plan_data = {}
       
       try:
           # 1. Content requirements analysis
           self._update_progress(15, "processing", "Analyzing content requirements")
           requirements_result = await self.call_tool("analyze_content_requirements", **input_data)
           content_plan_data["content_requirements"] = requirements_result
           all_reasoning.extend(requirements_result.get("reasoning", []))
           
           # 2. Content outline creation
           self._update_progress(25, "processing", "Creating content outline")
           outline_result = await self.call_tool("create_content_outline", 
                                               content_requirements=requirements_result.get("content_requirements", {}),
                                               **input_data)
           content_plan_data["content_outline"] = outline_result
           all_reasoning.extend(outline_result.get("reasoning", []))
           
           # 3. Header hierarchy optimization
           self._update_progress(40, "processing", "Optimizing header hierarchy")
           # Extract primary keywords for header optimization
           primary_keywords = []
           if "keyword_analysis" in input_data:
               kw_data = input_data["keyword_analysis"]
               primary_selection = kw_data.get("primary_selection", {})
               primary_keywords = primary_selection.get("keyword_selection", {}).get("primary_keywords", [])
           
           header_result = await self.call_tool("optimize_header_hierarchy",
                                              content_outline=outline_result.get("content_outline", {}),
                                              primary_keywords=primary_keywords)
           content_plan_data["header_hierarchy"] = header_result
           all_reasoning.extend(header_result.get("reasoning", []))
           
           # 4. Keyword placement planning
           self._update_progress(55, "processing", "Planning keyword placement")
           placement_result = await self.call_tool("plan_keyword_placement",
                                                 header_hierarchy=header_result.get("header_hierarchy", {}),
                                                 content_outline=outline_result.get("content_outline", {}),
                                                 **input_data)
           content_plan_data["keyword_placement"] = placement_result
           all_reasoning.extend(placement_result.get("reasoning", []))
           
           # 5. Content sections design
           self._update_progress(70, "processing", "Designing content sections")
           sections_result = await self.call_tool("design_content_sections",
                                                content_outline=outline_result.get("content_outline", {}),
                                                keyword_placement=placement_result.get("keyword_placement", {}),
                                                **input_data)
           content_plan_data["content_sections"] = sections_result
           all_reasoning.extend(sections_result.get("reasoning", []))
           
           # 6. Internal linking strategy
           self._update_progress(85, "processing", "Planning internal linking")
           linking_result = await self.call_tool("plan_internal_linking",
                                               content_sections=sections_result.get("content_sections", {}),
                                               keyword_placement=placement_result.get("keyword_placement", {}),
                                               **input_data)
           content_plan_data["internal_linking"] = linking_result
           all_reasoning.extend(linking_result.get("reasoning", []))
           
           # 7. CTA positioning strategy
           self._update_progress(95, "processing", "Positioning CTA elements")
           cta_result = await self.call_tool("position_cta_elements",
                                           content_sections=sections_result.get("content_sections", {}),
                                           **input_data)
           content_plan_data["cta_positioning"] = cta_result
           all_reasoning.extend(cta_result.get("reasoning", []))
           
           # 8. Planning summary
           self._update_progress(98, "processing", "Finalizing content plan")
           
           # Calculate average confidence
           confidences = [
               requirements_result.get("confidence", 80),
               outline_result.get("confidence", 80),
               header_result.get("confidence", 80),
               placement_result.get("confidence", 80),
               sections_result.get("confidence", 80),
               linking_result.get("confidence", 80),
               cta_result.get("confidence", 80)
           ]
           avg_confidence = sum(confidences) / len(confidences)
           
           # Create comprehensive planning summary
           planning_summary = {
               "plan_completed": True,
               "estimated_content_length": outline_result.get("content_outline", {}).get("estimated_word_count", 2000),
               "total_sections_planned": outline_result.get("content_outline", {}).get("structure", {}).get("total_sections", 0),
               "keyword_placement_targets": placement_result.get("keyword_placement", {}).get("keyword_targets", {}),
               "avg_confidence": avg_confidence,
               "planning_timestamp": datetime.now().isoformat(),
               "content_type": "SEO-optimized blog article",
               "optimization_focus": [
                   "Header hierarchy optimization",
                   "Strategic keyword placement", 
                   "Internal linking strategy",
                   "CTA conversion optimization",
                   "User experience enhancement"
               ]
           }
           
           content_plan_data["planning_summary"] = planning_summary
           
           return AgentResponse(
               success=True,
               data=content_plan_data,
               reasoning=all_reasoning,
               errors=[],
               processing_time=0.0,
               metadata={
                   "agent_name": self.config.name,
                   "confidence": avg_confidence,
                   "content_length": planning_summary["estimated_content_length"],
                   "sections_planned": planning_summary["total_sections_planned"],
                   "planning_stages": 7
               }
           )
           
       except Exception as e:
           self.logger.error(f"Content planning failed: {str(e)}")
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
async def test_content_planner():
   """Content Planner Agent test function"""
   print("Testing Content Planner Agent")
   print("=" * 50)
   
   # Services
   from services.gemini_service import GeminiService
   
   gemini = GeminiService()
   
   # Mock keyword analysis data (simulating input from Keyword Analyzer)
   mock_keyword_analysis = {
       "primary_selection": {
           "keyword_selection": {
               "primary_keywords": [
                   {"keyword": "wireless gaming headset", "search_volume": 8100, "difficulty": 45},
                   {"keyword": "best gaming headset", "search_volume": 12000, "difficulty": 52},
                   {"keyword": "gaming headset wireless", "search_volume": 5400, "difficulty": 38},
                   {"keyword": "wireless headset gaming", "search_volume": 3600, "difficulty": 35}
               ],
               "secondary_keywords": [
                   {"keyword": "gaming audio", "search_volume": 2900, "difficulty": 28},
                   {"keyword": "wireless gaming audio", "search_volume": 1800, "difficulty": 25}
               ]
           }
       },
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
       },
       "intent_analysis": {
           "intent_analysis": {
               "distribution": {
                   "informational": 15,
                   "commercial": 25,
                   "transactional": 8,
                   "navigational": 2
               }
           }
       },
       "content_clusters": {
           "content_clusters": {
               "cluster_strategy": "3-5 main content pillars recommended"
           }
       }
   }
   
   # Test input
   test_input = {
       "product_name": "Wireless Gaming Headset",
       "niche": "gaming accessories",
       "target_audience": "PC and console gamers aged 18-35",
       "keyword_analysis": mock_keyword_analysis,
       "budget": 2000
   }
   
   # Progress callback
   def progress_callback(agent_name, progress, status, current_step):
       print(f"[{agent_name}] {progress}% - {status}: {current_step}")
   
   # Test agent
   agent = ContentPlannerAgent(gemini)
   agent.set_progress_callback(progress_callback)
   
   result = await agent.execute(test_input)
   
   print("\nContent Planning Results:")
   print("-" * 30)
   print(f"Success: {result.success}")
   print(f"Data Keys: {list(result.data.keys())}")
   print(f"Content Length: {result.metadata.get('content_length', 'N/A')} words")
   print(f"Sections Planned: {result.metadata.get('sections_planned', 'N/A')}")
   print(f"Confidence: {result.metadata.get('confidence', 'N/A'):.1f}%")
   print(f"Processing Time: {result.processing_time:.2f}s")
   
   if result.errors:
       print(f"Errors: {result.errors}")
   
   # Show sample results
   if result.success and result.data:
       summary = result.data.get("planning_summary", {})
       print(f"\nPlanning Summary:")
       print(f"- Estimated Length: {summary.get('estimated_content_length', 0)} words")
       print(f"- Total Sections: {summary.get('total_sections_planned', 0)}")
       print(f"- Average Confidence: {summary.get('avg_confidence', 0):.1f}%")
       print(f"- Optimization Focus: {len(summary.get('optimization_focus', []))} areas")
       
       # Show a sample of content outline
       if "content_outline" in result.data:
           outline = result.data["content_outline"].get("content_outline", {})
           structure = outline.get("structure", {})
           print(f"\nContent Structure Sample:")
           print(f"- Title: {structure.get('title', 'Not defined')}")
           print(f"- Main Sections: {len(structure.get('main_sections', []))}")
   
   return result


if __name__ == "__main__":
   # Test çalıştır
   result = asyncio.run(test_content_planner())
   print(f"\nContent Planner test completed!")