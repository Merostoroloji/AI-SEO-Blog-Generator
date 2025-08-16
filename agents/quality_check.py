"""
Quality Checker Agent - AI SEO Blog Generator

Bu agent content quality control ve optimization yapar:
- Content quality analysis ve scoring
- SEO compliance verification
- Readability ve engagement scoring
- Error detection ve correction suggestions
- Plagiarism detection planning
- Final optimization recommendations
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


class QualityCheckerAgent(BaseAgent, ToolMixin):
   """
   Quality Checker Agent - Altıncı pipeline agent'ı
   
   Görevleri:
   - Content quality analysis ve scoring
   - SEO compliance verification
   - Readability ve user experience assessment
   - Error detection ve correction suggestions
   - Plagiarism risk assessment
   - Final optimization recommendations
   - Publication readiness verification
   """
   
   def __init__(self, gemini_service: GeminiService):
       config = AgentConfig(
           name="quality_checker",
           description="Analyzes content quality, SEO compliance, and provides optimization recommendations",
           max_retries=3,
           timeout_seconds=180,
           temperature=0.3,  # Analytical approach for quality assessment
           reasoning_enabled=True
       )
       
       BaseAgent.__init__(self, config, gemini_service)
       ToolMixin.__init__(self)
       
       # Quality checking araçları
       self._register_quality_checking_tools()
       
       self.logger.info("QualityCheckerAgent initialized")
   
   def _register_quality_checking_tools(self):
       """Quality checking araçlarını kaydet"""
       self.available_tools.update({
           "analyze_content_quality": self._analyze_content_quality,
           "verify_seo_compliance": self._verify_seo_compliance,
           "assess_readability": self._assess_readability,
           "detect_content_errors": self._detect_content_errors,
           "evaluate_engagement_factors": self._evaluate_engagement_factors,
           "check_plagiarism_risk": self._check_plagiarism_risk,
           "generate_optimization_recommendations": self._generate_optimization_recommendations
       })
   
   async def _analyze_content_quality(self, **kwargs) -> Dict[str, Any]:
       """Content quality analysis tool"""
       content_data = kwargs.get("content_writing", {})
       seo_optimization = kwargs.get("seo_optimization", {})
       product_name = kwargs.get("product_name", "")
       target_audience = kwargs.get("target_audience", "")
       
       # Extract content from all sections
       final_article = content_data.get("final_article", {})
       article_content = final_article.get("final_article", {}).get("complete_article", "")
       
       # Extract content metrics
       writing_summary = content_data.get("writing_summary", {})
       word_count = writing_summary.get("total_word_count", 0)
       
       # Extract individual sections for detailed analysis
       introduction = content_data.get("introduction", {}).get("introduction", {}).get("content", "")
       main_content = content_data.get("main_content", {}).get("main_content", {}).get("content", "")
       conclusion = content_data.get("conclusion", {}).get("conclusion", {}).get("content", "")
       faq_section = content_data.get("faq_section", {}).get("faq_section", {}).get("content", "")
       
       prompt = f"""
       Analyze comprehensive content quality for {product_name} targeting {target_audience}.
       
       Content Analysis Data:
       - Total Word Count: {word_count}
       - Article Sections: Introduction, Main Content, Conclusion, FAQ
       - Target: High-quality, SEO-optimized blog article
       
       Content Samples for Analysis:
       Introduction ({len(introduction.split())} words): {introduction[:300]}...
       Main Content ({len(main_content.split())} words): {main_content[:400]}...
       Conclusion ({len(conclusion.split())} words): {conclusion[:200]}...
       FAQ Section ({len(faq_section.split())} words): {faq_section[:200]}...
       
       Perform comprehensive content quality analysis covering:
       
       1. CONTENT DEPTH AND VALUE ASSESSMENT:
       - Information comprehensiveness (1-10 scale)
       - Expert-level insights and analysis
       - Actionable advice and practical value
       - Unique perspectives and differentiation
       - Authority and credibility signals
       
       2. CONTENT STRUCTURE QUALITY:
       - Logical flow and organization
       - Header hierarchy effectiveness
       - Paragraph structure and spacing
       - Transition quality between sections
       - Content scaffolding and progression
       
       3. WRITING QUALITY EVALUATION:
       - Grammar and syntax accuracy
       - Vocabulary sophistication and variety
       - Sentence structure diversity
       - Professional tone consistency
       - Brand voice alignment
       
       4. AUDIENCE ALIGNMENT ASSESSMENT:
       - Target audience appropriateness
       - Technical level suitability
       - Language complexity matching
       - Pain point addressing effectiveness
       - User journey consideration
       
       5. ENGAGEMENT FACTOR ANALYSIS:
       - Hook effectiveness in introduction
       - Interest maintenance throughout
       - Storytelling and example integration
       - Interactive elements inclusion
       - Emotional connection creation
       
       6. CONVERSION OPTIMIZATION QUALITY:
       - Call-to-action effectiveness
       - Trust signal integration
       - Objection handling quality
       - Value proposition clarity
       - Persuasion element strength
       
       7. CONTENT COMPLETENESS CHECK:
       - Topic coverage thoroughness
       - Missing information identification
       - Content gap analysis
       - Competitive completeness assessment
       - User question addressing
       
       8. TECHNICAL ACCURACY VERIFICATION:
       - Factual information accuracy
       - Technical detail precision
       - Data and statistics validation
       - Source credibility assessment
       - Expert claim verification
       
       9. CONTENT ORIGINALITY ASSESSMENT:
       - Unique angle and perspective
       - Original insights and analysis
       - Fresh information inclusion
       - Distinctive value proposition
       - Competitive differentiation
       
       10. OVERALL QUALITY SCORING:
       Provide scores (1-100) for:
       - Content Depth: __/100
       - Writing Quality: __/100
       - Structure Quality: __/100
       - Audience Fit: __/100
       - Engagement Factor: __/100
       - Conversion Potential: __/100
       - Technical Accuracy: __/100
       - Originality: __/100
       - Overall Quality Score: __/100
       
       For each area, provide:
       - Specific strengths identified
       - Areas needing improvement
       - Actionable enhancement suggestions
       - Priority level for fixes (High/Medium/Low)
       
       Focus on identifying specific, actionable improvements that will enhance content quality and performance.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a content quality specialist with expertise in evaluating blog articles for SEO performance and user engagement.",
           user_prompt=prompt,
           reasoning_context="Analyzing comprehensive content quality across all dimensions"
       )
       
       # Parse quality scores from response
       quality_scores = self._parse_quality_scores(response['response'])
       
       return {
           "content_quality": {
               "quality_analysis": response['response'],
               "quality_scores": quality_scores,
               "content_metrics": {
                   "total_words": word_count,
                   "section_count": 4,
                   "content_depth": "Comprehensive" if word_count > 2000 else "Standard"
               },
               "assessment_areas": [
                   "Content depth and value",
                   "Structure and organization",
                   "Writing quality",
                   "Audience alignment",
                   "Engagement factors",
                   "Conversion optimization",
                   "Technical accuracy",
                   "Originality"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _parse_quality_scores(self, analysis_text: str) -> Dict[str, int]:
       """Parse quality scores from analysis text"""
       scores = {
           "content_depth": 85,
           "writing_quality": 85,
           "structure_quality": 85,
           "audience_fit": 85,
           "engagement_factor": 85,
           "conversion_potential": 85,
           "technical_accuracy": 85,
           "originality": 85,
           "overall_score": 85
       }
       
       try:
           # Look for score patterns in the text
           score_patterns = [
               (r"Content Depth:\s*(\d+)", "content_depth"),
               (r"Writing Quality:\s*(\d+)", "writing_quality"),
               (r"Structure Quality:\s*(\d+)", "structure_quality"),
               (r"Audience Fit:\s*(\d+)", "audience_fit"),
               (r"Engagement Factor:\s*(\d+)", "engagement_factor"),
               (r"Conversion Potential:\s*(\d+)", "conversion_potential"),
               (r"Technical Accuracy:\s*(\d+)", "technical_accuracy"),
               (r"Originality:\s*(\d+)", "originality"),
               (r"Overall Quality Score:\s*(\d+)", "overall_score")
           ]
           
           for pattern, key in score_patterns:
               match = re.search(pattern, analysis_text)
               if match:
                   scores[key] = min(int(match.group(1)), 100)
           
           # Calculate overall score if not found
           if scores["overall_score"] == 85:
               individual_scores = [v for k, v in scores.items() if k != "overall_score"]
               scores["overall_score"] = int(sum(individual_scores) / len(individual_scores))
       
       except Exception as e:
           self.logger.warning(f"Failed to parse quality scores: {e}")
       
       return scores
   
   async def _verify_seo_compliance(self, **kwargs) -> Dict[str, Any]:
       """SEO compliance verification tool"""
       content_data = kwargs.get("content_writing", {})
       seo_optimization = kwargs.get("seo_optimization", {})
       keyword_data = kwargs.get("keyword_analysis", {})
       
       # Extract SEO elements
       final_article = content_data.get("final_article", {})
       article_content = final_article.get("final_article", {}).get("complete_article", "")
       
       # Extract keyword data
       primary_keywords = []
       if keyword_data:
           primary_selection = keyword_data.get("primary_selection", {})
           primary_keywords = [kw.get('keyword', kw) if isinstance(kw, dict) else kw 
                             for kw in primary_selection.get("keyword_selection", {}).get("primary_keywords", [])][:5]
       
       # Extract meta optimization data
       meta_data = {}
       if seo_optimization:
           meta_opt = seo_optimization.get("meta_optimization", {})
           meta_data = meta_opt.get("meta_optimization", {})
       
       prompt = f"""
       Verify comprehensive SEO compliance for the content.
       
       Primary Keywords: {', '.join(primary_keywords)}
       Content Length: {len(article_content.split())} words
       
       SEO Optimization Data:
       {str(meta_data)[:400]}
       
       Content Sample for SEO Analysis:
       {article_content[:800]}...
       
       Perform detailed SEO compliance verification covering:
       
       1. KEYWORD OPTIMIZATION COMPLIANCE:
       - Primary keyword placement in title, headers, content
       - Keyword density analysis (target: 1-2%)
       - Secondary keyword distribution
       - Long-tail keyword integration
       - Keyword stuffing risk assessment
       - Natural language flow maintenance
       
       2. ON-PAGE SEO ELEMENTS:
       - Title tag optimization (50-60 characters)
       - Meta description optimization (150-160 characters)
       - Header hierarchy (H1, H2, H3) structure
       - URL slug optimization
       - Image alt text optimization
       - Internal linking implementation
       
       3. TECHNICAL SEO COMPLIANCE:
       - Content length adequacy (1500+ words)
       - Mobile-friendly formatting
       - Page speed optimization factors
       - Schema markup readiness
       - Canonical URL setup
       - Robots meta tag appropriateness
       
       4. CONTENT SEO BEST PRACTICES:
       - First paragraph keyword inclusion
       - Semantic keyword usage
       - LSI (Latent Semantic Indexing) keywords
       - Related term integration
       - Topic authority demonstration
       - Expert authorship signals
       
       5. FEATURED SNIPPETS OPTIMIZATION:
       - Question-answer format implementation
       - List and table optimization
       - Definition and explanation clarity
       - FAQ section optimization
       - Snippet-friendly formatting
       
       6. LOCAL SEO CONSIDERATIONS (if applicable):
       - Location-based keyword integration
       - Local business schema markup
       - "Near me" optimization
       - Local intent addressing
       
       7. E-A-T (Expertise, Authoritativeness, Trustworthiness):
       - Expert knowledge demonstration
       - Authoritative source citations
       - Trust signal integration
       - Author credibility establishment
       - Fact verification and accuracy
       
       8. COMPETITIVE SEO ANALYSIS:
       - Competitor content comparison
       - Unique value proposition strength
       - Content gap filling
       - Competitive advantage demonstration
       
       9. SEO COMPLIANCE SCORING:
       Provide scores (1-100) for:
       - Keyword Optimization: __/100
       - On-Page SEO: __/100
       - Technical SEO: __/100
       - Content SEO: __/100
       - Featured Snippets: __/100
       - E-A-T Factors: __/100
       - Overall SEO Score: __/100
       
       10. COMPLIANCE ISSUES AND FIXES:
       For each issue identified, provide:
       - Specific problem description
       - SEO impact assessment
       - Recommended fix/improvement
       - Implementation priority (Critical/High/Medium/Low)
       - Expected improvement impact
       
       Focus on identifying specific SEO compliance issues and providing actionable solutions.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are an SEO compliance specialist with expertise in technical SEO auditing and optimization.",
           user_prompt=prompt,
           reasoning_context="Verifying comprehensive SEO compliance and identifying optimization opportunities"
       )
       
       # Parse SEO scores
       seo_scores = self._parse_seo_scores(response['response'])
       
       # Analyze keyword density
       keyword_density = self._calculate_keyword_density(article_content, primary_keywords)
       
       return {
           "seo_compliance": {
               "compliance_analysis": response['response'],
               "seo_scores": seo_scores,
               "keyword_analysis": {
                   "primary_keywords": primary_keywords,
                   "keyword_density": keyword_density,
                   "content_length": len(article_content.split())
               },
               "compliance_areas": [
                   "Keyword optimization",
                   "On-page SEO elements",
                   "Technical SEO factors",
                   "Content SEO best practices",
                   "Featured snippets optimization",
                   "E-A-T factors"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _parse_seo_scores(self, analysis_text: str) -> Dict[str, int]:
       """Parse SEO scores from analysis text"""
       scores = {
           "keyword_optimization": 85,
           "on_page_seo": 85,
           "technical_seo": 85,
           "content_seo": 85,
           "featured_snippets": 85,
           "eat_factors": 85,
           "overall_seo_score": 85
       }
       
       try:
           score_patterns = [
               (r"Keyword Optimization:\s*(\d+)", "keyword_optimization"),
               (r"On-Page SEO:\s*(\d+)", "on_page_seo"),
               (r"Technical SEO:\s*(\d+)", "technical_seo"),
               (r"Content SEO:\s*(\d+)", "content_seo"),
               (r"Featured Snippets:\s*(\d+)", "featured_snippets"),
               (r"E-A-T Factors:\s*(\d+)", "eat_factors"),
               (r"Overall SEO Score:\s*(\d+)", "overall_seo_score")
           ]
           
           for pattern, key in score_patterns:
               match = re.search(pattern, analysis_text)
               if match:
                   scores[key] = min(int(match.group(1)), 100)
           
           # Calculate overall if not found
           if scores["overall_seo_score"] == 85:
               individual_scores = [v for k, v in scores.items() if k != "overall_seo_score"]
               scores["overall_seo_score"] = int(sum(individual_scores) / len(individual_scores))
       
       except Exception as e:
           self.logger.warning(f"Failed to parse SEO scores: {e}")
       
       return scores
   
   def _calculate_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
       """Calculate keyword density for primary keywords"""
       if not content or not keywords:
           return {}
       
       content_lower = content.lower()
       total_words = len(content.split())
       
       keyword_density = {}
       for keyword in keywords[:5]:  # Top 5 keywords
           if keyword:
               keyword_lower = keyword.lower()
               keyword_count = content_lower.count(keyword_lower)
               density = (keyword_count / total_words) * 100 if total_words > 0 else 0
               keyword_density[keyword] = round(density, 2)
       
       return keyword_density
   
   async def _assess_readability(self, **kwargs) -> Dict[str, Any]:
       """Readability assessment tool"""
       content_data = kwargs.get("content_writing", {})
       target_audience = kwargs.get("target_audience", "")
       
       # Extract content for readability analysis
       final_article = content_data.get("final_article", {})
       article_content = final_article.get("final_article", {}).get("complete_article", "")
       
       # Basic readability metrics calculation
       word_count = len(article_content.split())
       sentence_count = article_content.count('.') + article_content.count('!') + article_content.count('?')
       avg_sentence_length = word_count / max(sentence_count, 1)
       
       prompt = f"""
       Assess comprehensive readability for content targeting {target_audience}.
       
       Content Metrics:
       - Total Words: {word_count}
       - Estimated Sentences: {sentence_count}
       - Average Sentence Length: {avg_sentence_length:.1f} words
       
       Content Sample for Readability Analysis:
       {article_content[:600]}...
       
       Perform detailed readability assessment covering:
       
       1. READING LEVEL ANALYSIS:
       - Flesch Reading Ease estimation (target: 60-70)
       - Flesch-Kincaid Grade Level (target: 8-10)
       - Vocabulary complexity assessment
       - Technical jargon usage evaluation
       - Age-appropriate language check
       
       2. SENTENCE STRUCTURE EVALUATION:
       - Average sentence length analysis (target: 15-20 words)
       - Sentence variety and rhythm
       - Complex vs simple sentence balance
       - Run-on sentence identification
       - Fragment and incomplete sentence detection
       
       3. PARAGRAPH STRUCTURE ASSESSMENT:
       - Average paragraph length (target: 2-4 sentences)
       - Paragraph topic coherence
       - Logical flow between paragraphs
       - White space utilization
       - Visual breathing room adequacy
       
       4. VOCABULARY AND LANGUAGE:
       - Word choice appropriateness for audience
       - Active vs passive voice usage
       - Clear and concise expression
       - Jargon explanation adequacy
       - Transition word effectiveness
       
       5. CONTENT ORGANIZATION:
       - Logical information hierarchy
       - Scannable structure implementation
       - Header and subheader effectiveness
       - Bullet point and list usage
       - Information chunking quality
       
       6. MOBILE READABILITY:
       - Mobile-friendly paragraph breaks
       - Touch-friendly formatting
       - Screen-size appropriate content blocks
       - Thumb-scrolling optimization
       - Quick-scan capability
       
       7. ENGAGEMENT AND CLARITY:
       - Clear main points identification
       - Compelling narrative flow
       - Reader attention maintenance
       - Concept explanation clarity
       - Example and analogy effectiveness
       
       8. AUDIENCE APPROPRIATENESS:
       - Technical level matching target audience
       - Cultural sensitivity and inclusion
       - Industry-specific language usage
       - Generational language preferences
       - Professional vs casual tone balance
       
       9. ACCESSIBILITY CONSIDERATIONS:
       - Screen reader friendliness
       - Clear heading structure
       - Descriptive link text
       - Alt text for images planning
       - Color contrast considerations
       
       10. READABILITY SCORING:
       Provide scores (1-100) for:
       - Reading Level: __/100
       - Sentence Structure: __/100
       - Paragraph Quality: __/100
       - Vocabulary Clarity: __/100
       - Content Organization: __/100
       - Mobile Readability: __/100
       - Overall Readability: __/100
       
       11. IMPROVEMENT RECOMMENDATIONS:
       For each area needing improvement:
       - Specific readability issue
       - Impact on user experience
       - Recommended improvement action
       - Implementation priority
       - Expected readability enhancement
       
       Focus on identifying specific readability improvements that will enhance user experience and engagement.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a readability specialist with expertise in content accessibility and user experience optimization.",
           user_prompt=prompt,
           reasoning_context="Assessing comprehensive content readability for optimal user experience"
       )
       
       # Parse readability scores
       readability_scores = self._parse_readability_scores(response['response'])
       
       return {
           "readability_assessment": {
               "readability_analysis": response['response'],
               "readability_scores": readability_scores,
               "basic_metrics": {
                   "word_count": word_count,
                   "sentence_count": sentence_count,
                   "avg_sentence_length": round(avg_sentence_length, 1),
                   "estimated_read_time": f"{max(word_count // 200, 1)} minutes"
               },
               "assessment_areas": [
                   "Reading level analysis",
                   "Sentence structure evaluation",
                   "Paragraph structure",
                   "Vocabulary clarity",
                   "Content organization",
                   "Mobile readability",
                   "Accessibility factors"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _parse_readability_scores(self, analysis_text: str) -> Dict[str, int]:
       """Parse readability scores from analysis text"""
       scores = {
           "reading_level": 85,
           "sentence_structure": 85,
           "paragraph_quality": 85,
           "vocabulary_clarity": 85,
           "content_organization": 85,
           "mobile_readability": 85,
           "overall_readability": 85
       }
       
       try:
           score_patterns = [
               (r"Reading Level:\s*(\d+)", "reading_level"),
               (r"Sentence Structure:\s*(\d+)", "sentence_structure"),
               (r"Paragraph Quality:\s*(\d+)", "paragraph_quality"),
               (r"Vocabulary Clarity:\s*(\d+)", "vocabulary_clarity"),
               (r"Content Organization:\s*(\d+)", "content_organization"),
               (r"Mobile Readability:\s*(\d+)", "mobile_readability"),
               (r"Overall Readability:\s*(\d+)", "overall_readability")
           ]
           
           for pattern, key in score_patterns:
               match = re.search(pattern, analysis_text)
               if match:
                   scores[key] = min(int(match.group(1)), 100)
           
           # Calculate overall if not found
           if scores["overall_readability"] == 85:
               individual_scores = [v for k, v in scores.items() if k != "overall_readability"]
               scores["overall_readability"] = int(sum(individual_scores) / len(individual_scores))
       
       except Exception as e:
           self.logger.warning(f"Failed to parse readability scores: {e}")
       
       return scores
   
   async def _detect_content_errors(self, **kwargs) -> Dict[str, Any]:
       """Content error detection tool"""
       content_data = kwargs.get("content_writing", {})
       
       # Extract content for error detection
       final_article = content_data.get("final_article", {})
       article_content = final_article.get("final_article", {}).get("complete_article", "")
       
       prompt = f"""
       Detect and analyze potential content errors and issues.
       
       Content for Error Analysis:
       Length: {len(article_content.split())} words
       
       Content Sample:
       {article_content[:800]}...
       
       Perform comprehensive error detection covering:
       
       1. GRAMMAR AND SYNTAX ERRORS:
       - Subject-verb agreement issues
       - Tense consistency problems
       - Pronoun reference errors
       - Punctuation mistakes
       - Capitalization errors
       - Run-on sentences
       - Sentence fragments
       
       2. SPELLING AND TYPOS:
       - Misspelled words identification
       - Commonly confused words (there/their/they're)
       - Homophone errors
       - Typos and keyboard errors
       - Brand name accuracy
       - Technical term spelling
       
       3. FACTUAL ACCURACY CONCERNS:
       - Potentially outdated information
       - Contradictory statements
       - Unsupported claims
       - Missing source citations
       - Technical inaccuracies
       - Statistical errors
       
       4. CONSISTENCY ISSUES:
       - Terminology usage consistency
       - Style guide adherence
       - Formatting inconsistencies
       - Voice and tone variations
       - Brand messaging alignment
       
       5. STRUCTURAL PROBLEMS:
       - Logical flow issues
       - Missing transitions
       - Incomplete thoughts
       - Redundant information
       - Information gaps
       - Poor organization
       
       6. SEO-RELATED ERRORS:
       - Keyword cannibalization
       - Over-optimization indicators
       - Missing internal links
       - Broken external links
       - Poor anchor text usage
       
       7. USER EXPERIENCE ISSUES:
       - Unclear instructions
       - Missing context
       - Confusing explanations
       - Poor call-to-action clarity
       - Navigation problems
       
       8. COMPLIANCE AND LEGAL:
       - Copyright infringement risks
       - Trademark usage issues
       - Disclaimer requirements
       - Privacy policy mentions
       - Legal claim verification
       
       9. ERROR CATEGORIZATION:
       Classify each error by:
       - Error Type: Grammar/Spelling/Factual/Structural/SEO/UX
       - Severity: Critical/High/Medium/Low
       - Impact: Reader Experience/SEO/Legal/Brand
       - Fix Complexity: Simple/Moderate/Complex
       
       10. ERROR REPORT FORMAT:
       For each error found:
       - Location in content (approximate)
       - Error description
       - Current problematic text
       - Suggested correction
       - Reasoning for change
       - Priority level for fixing
       
       Provide a comprehensive error report with specific, actionable corrections.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a content editor specialist with expertise in error detection and content quality assurance.",
           user_prompt=prompt,
           reasoning_context="Detecting and categorizing content errors for quality improvement"
       )
       
       # Parse error categories from response
       error_summary = self._parse_error_summary(response['response'])
       
       return {
           "error_detection": {
               "error_analysis": response['response'],
               "error_summary": error_summary,
               "content_length": len(article_content.split()),
               "error_categories": [
                   "Grammar and syntax",
                   "Spelling and typos",
                   "Factual accuracy",
                   "Consistency issues",
                   "Structural problems",
                   "SEO-related errors",
                   "User experience",
                   "Compliance and legal"
               ],
               "quality_impact": "Medium" if error_summary.get("total_errors", 0) < 10 else "High"
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _parse_error_summary(self, analysis_text: str) -> Dict[str, Any]:
       """Parse error summary from analysis text"""
       summary = {
           "critical_errors": 0,
           "high_errors": 0,
           "medium_errors": 0,
           "low_errors": 0,
           "total_errors": 0,
           "grammar_errors": 0,
           "spelling_errors": 0,
           "factual_errors": 0,
           "structural_errors": 0
       }
       
       try:
           # Count different types of errors mentioned in the text
           critical_count = len(re.findall(r'critical|Critical|CRITICAL', analysis_text, re.IGNORECASE))
           high_count = len(re.findall(r'high priority|High|HIGH', analysis_text, re.IGNORECASE))
           medium_count = len(re.findall(r'medium|Medium|MEDIUM', analysis_text, re.IGNORECASE))
           low_count = len(re.findall(r'low priority|Low|LOW', analysis_text, re.IGNORECASE))
           
           summary.update({
               "critical_errors": min(critical_count, 5),
               "high_errors": min(high_count, 10),
               "medium_errors": min(medium_count, 15),
               "low_errors": min(low_count, 20),
               "total_errors": min(critical_count + high_count + medium_count + low_count, 50)
           })
       
       except Exception as e:
           self.logger.warning(f"Failed to parse error summary: {e}")
       
       return summary
   
   async def _evaluate_engagement_factors(self, **kwargs) -> Dict[str, Any]:
       """Engagement factors evaluation tool"""
       content_data = kwargs.get("content_writing", {})
       target_audience = kwargs.get("target_audience", "")
       
       # Extract content sections for engagement analysis
       introduction = content_data.get("introduction", {}).get("introduction", {}).get("content", "")
       main_content = content_data.get("main_content", {}).get("main_content", {}).get("content", "")
       conclusion = content_data.get("conclusion", {}).get("conclusion", {}).get("content", "")
       
       prompt = f"""
       Evaluate content engagement factors for {target_audience}.
       
       Content Sections Analysis:
       - Introduction: {len(introduction.split())} words
       - Main Content: {len(main_content.split())} words
       - Conclusion: {len(conclusion.split())} words
       
       Introduction Sample: {introduction[:300]}...
       Main Content Sample: {main_content[:400]}...
       Conclusion Sample: {conclusion[:200]}...
       
       Evaluate comprehensive engagement factors covering:
       
       1. HOOK AND ATTENTION GRABBING:
       - Opening line effectiveness
       - Curiosity gap creation
       - Problem identification strength
       - Emotional connection establishment
       - Immediate value demonstration
       
       2. INTEREST MAINTENANCE:
       - Content flow and pacing
       - Variety in content presentation
       - Storytelling element integration
       - Example and case study usage
       - Interactive element inclusion
       
       3. EMOTIONAL ENGAGEMENT:
       - Emotional trigger identification
       - Personal connection creation
       - Empathy and understanding demonstration
       - Motivation and inspiration elements
       - Trust and credibility building
       
       4. VISUAL AND STRUCTURAL ENGAGEMENT:
       - Scannable content structure
       - Visual break optimization
       - Header and subheader appeal
       - Bullet point and list effectiveness
       - White space utilization
       
       5. INTERACTIVE ELEMENTS:
       - Question integration for engagement
       - Call-to-action effectiveness
       - Reader participation encouragement
       - Social sharing potential
       - Comment and discussion promotion
       
       6. VALUE DELIVERY ASSESSMENT:
       - Immediate value provision
       - Progressive value building
       - Actionable insight delivery
       - Problem-solving effectiveness
       - Knowledge gap filling
       
       7. CONVERSATIONAL TONE:
       - Direct address usage ("you")
       - Conversational language style
       - Personal anecdote integration
       - Relatability factor strength
       - Professional yet approachable tone
       
       8. CONTENT VARIETY:
       - Multiple content format usage
       - Information presentation diversity
       - Learning style accommodation
       - Attention span consideration
       - Boredom prevention strategies
       
       9. AUDIENCE CONNECTION:
       - Target audience understanding demonstration
       - Pain point addressing accuracy
       - Language and terminology appropriateness
       - Cultural relevance and sensitivity
       - Community building potential
       
       10. ENGAGEMENT SCORING:
       Provide scores (1-100) for:
       - Hook Effectiveness: __/100
       - Interest Maintenance: __/100
       - Emotional Connection: __/100
       - Visual Engagement: __/100
       - Interactive Elements: __/100
       - Value Delivery: __/100
       - Conversational Tone: __/100
       - Content Variety: __/100
       - Audience Connection: __/100
       - Overall Engagement: __/100
       
       11. ENGAGEMENT ENHANCEMENT RECOMMENDATIONS:
       For each factor, provide:
       - Current strength assessment
       - Improvement opportunities
       - Specific enhancement suggestions
       - Implementation priority
       - Expected engagement impact
       
       Focus on identifying specific ways to increase reader engagement and time-on-page.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are an engagement optimization specialist with expertise in content psychology and user experience.",
           user_prompt=prompt,
           reasoning_context="Evaluating content engagement factors for maximum reader retention"
       )
       
       # Parse engagement scores
       engagement_scores = self._parse_engagement_scores(response['response'])
       
       return {
           "engagement_evaluation": {
               "engagement_analysis": response['response'],
               "engagement_scores": engagement_scores,
               "content_sections": {
                   "introduction_words": len(introduction.split()),
                   "main_content_words": len(main_content.split()),
                   "conclusion_words": len(conclusion.split())
               },
               "engagement_factors": [
                   "Hook and attention grabbing",
                   "Interest maintenance",
                   "Emotional engagement",
                   "Visual and structural",
                   "Interactive elements",
                   "Value delivery",
                   "Conversational tone",
                   "Content variety",
                   "Audience connection"
               ]
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _parse_engagement_scores(self, analysis_text: str) -> Dict[str, int]:
       """Parse engagement scores from analysis text"""
       scores = {
           "hook_effectiveness": 85,
           "interest_maintenance": 85,
           "emotional_connection": 85,
           "visual_engagement": 85,
           "interactive_elements": 85,
           "value_delivery": 85,
           "conversational_tone": 85,
           "content_variety": 85,
           "audience_connection": 85,
           "overall_engagement": 85
       }
       
       try:
           score_patterns = [
               (r"Hook Effectiveness:\s*(\d+)", "hook_effectiveness"),
               (r"Interest Maintenance:\s*(\d+)", "interest_maintenance"),
               (r"Emotional Connection:\s*(\d+)", "emotional_connection"),
               (r"Visual Engagement:\s*(\d+)", "visual_engagement"),
               (r"Interactive Elements:\s*(\d+)", "interactive_elements"),
               (r"Value Delivery:\s*(\d+)", "value_delivery"),
               (r"Conversational Tone:\s*(\d+)", "conversational_tone"),
               (r"Content Variety:\s*(\d+)", "content_variety"),
               (r"Audience Connection:\s*(\d+)", "audience_connection"),
               (r"Overall Engagement:\s*(\d+)", "overall_engagement")
           ]
           
           for pattern, key in score_patterns:
               match = re.search(pattern, analysis_text)
               if match:
                   scores[key] = min(int(match.group(1)), 100)
           
           # Calculate overall if not found
           if scores["overall_engagement"] == 85:
               individual_scores = [v for k, v in scores.items() if k != "overall_engagement"]
               scores["overall_engagement"] = int(sum(individual_scores) / len(individual_scores))
       
       except Exception as e:
           self.logger.warning(f"Failed to parse engagement scores: {e}")
       
       return scores
   
   async def _check_plagiarism_risk(self, **kwargs) -> Dict[str, Any]:
       """Plagiarism risk assessment tool"""
       content_data = kwargs.get("content_writing", {})
       
       # Extract content for plagiarism analysis
       final_article = content_data.get("final_article", {})
       article_content = final_article.get("final_article", {}).get("complete_article", "")
       
       prompt = f"""
       Assess plagiarism risk and content originality.
       
       Content Analysis:
       - Content Length: {len(article_content.split())} words
       - Content Type: SEO blog article
       
       Content Sample for Originality Analysis:
       {article_content[:600]}...
       
       Perform plagiarism risk assessment covering:
       
       1. CONTENT ORIGINALITY ASSESSMENT:
       - Unique perspective and angle analysis
       - Original insights and commentary
       - Fresh information and data inclusion
       - Personal expertise demonstration
       - Distinctive voice and style
       
       2. COMMON CONTENT PATTERNS:
       - Generic phrase usage identification
       - Industry cliché detection
       - Template language recognition
       - Boilerplate content identification
       - Overused expressions analysis
       
       3. PLAGIARISM RISK FACTORS:
       - Direct quotation without attribution
       - Paraphrasing too close to source material
       - Lack of proper source citations
       - Unoriginal content structure
       - Common knowledge vs unique insight balance
       
       4. SOURCE ATTRIBUTION ANALYSIS:
       - Proper citation format usage
       - Source credibility assessment
       - Attribution completeness verification
       - Fair use compliance evaluation
       - Copyright consideration analysis
       
       5. CONTENT UNIQUENESS INDICATORS:
       - Original research or analysis inclusion
       - Personal experience integration
       - Unique data or statistics presentation
       - Novel connections and insights
       - Creative analogies and examples
       
       6. COMPETITIVE DIFFERENTIATION:
       - Unique value proposition strength
       - Competitive content analysis
       - Market gap identification
       - Distinctive expertise demonstration
       - Original angle development
       
       7. PLAGIARISM PREVENTION RECOMMENDATIONS:
       - Proper citation implementation
       - Source diversity improvement
       - Original content enhancement
       - Unique perspective strengthening
       - Attribution best practices
       
       8. ORIGINALITY SCORING:
       Provide scores (1-100) for:
       - Content Originality: __/100
       - Source Attribution: __/100
       - Unique Insights: __/100
       - Plagiarism Risk: __/100 (lower is better)
       - Overall Originality: __/100
       
       9. RISK MITIGATION STRATEGIES:
       - Specific plagiarism risks identified
       - Recommended prevention measures
       - Citation improvement suggestions
       - Originality enhancement opportunities
       - Content differentiation strategies
       
       Note: This is a preliminary assessment. Professional plagiarism detection tools should be used for final verification.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a content originality specialist with expertise in plagiarism detection and content authenticity assessment.",
           user_prompt=prompt,
           reasoning_context="Assessing content originality and plagiarism risk factors"
       )
       
       # Parse originality scores
       originality_scores = self._parse_originality_scores(response['response'])
       
       return {
           "plagiarism_assessment": {
               "originality_analysis": response['response'],
               "originality_scores": originality_scores,
               "content_length": len(article_content.split()),
               "assessment_areas": [
                   "Content originality",
                   "Source attribution",
                   "Unique insights",
                   "Plagiarism risk factors",
                   "Competitive differentiation"
               ],
               "risk_level": self._determine_risk_level(originality_scores.get("plagiarism_risk", 20)),
               "verification_note": "Professional plagiarism detection tools recommended for final verification"
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _parse_originality_scores(self, analysis_text: str) -> Dict[str, int]:
       """Parse originality scores from analysis text"""
       scores = {
           "content_originality": 85,
           "source_attribution": 85,
           "unique_insights": 85,
           "plagiarism_risk": 20,  # Lower is better
           "overall_originality": 85
       }
       
       try:
           score_patterns = [
               (r"Content Originality:\s*(\d+)", "content_originality"),
               (r"Source Attribution:\s*(\d+)", "source_attribution"),
               (r"Unique Insights:\s*(\d+)", "unique_insights"),
               (r"Plagiarism Risk:\s*(\d+)", "plagiarism_risk"),
               (r"Overall Originality:\s*(\d+)", "overall_originality")
           ]
           
           for pattern, key in score_patterns:
               match = re.search(pattern, analysis_text)
               if match:
                   scores[key] = min(int(match.group(1)), 100)
       
       except Exception as e:
           self.logger.warning(f"Failed to parse originality scores: {e}")
       
       return scores
   
   def _determine_risk_level(self, plagiarism_score: int) -> str:
       """Determine plagiarism risk level based on score"""
       if plagiarism_score <= 20:
           return "Low"
       elif plagiarism_score <= 40:
           return "Medium"
       elif plagiarism_score <= 60:
           return "High"
       else:
           return "Critical"
   
   async def _generate_optimization_recommendations(self, **kwargs) -> Dict[str, Any]:
       """Optimization recommendations generation tool"""
       content_quality = kwargs.get("content_quality", {})
       seo_compliance = kwargs.get("seo_compliance", {})
       readability_assessment = kwargs.get("readability_assessment", {})
       error_detection = kwargs.get("error_detection", {})
       engagement_evaluation = kwargs.get("engagement_evaluation", {})
       plagiarism_assessment = kwargs.get("plagiarism_assessment", {})
       
       # Extract all scores for comprehensive analysis
       quality_scores = content_quality.get("content_quality", {}).get("quality_scores", {})
       seo_scores = seo_compliance.get("seo_compliance", {}).get("seo_scores", {})
       readability_scores = readability_assessment.get("readability_assessment", {}).get("readability_scores", {})
       engagement_scores = engagement_evaluation.get("engagement_evaluation", {}).get("engagement_scores", {})
       originality_scores = plagiarism_assessment.get("plagiarism_assessment", {}).get("originality_scores", {})
       
       prompt = f"""
       Generate comprehensive optimization recommendations based on quality analysis results.
       
       Quality Analysis Summary:
       Content Quality Scores: {quality_scores}
       SEO Compliance Scores: {seo_scores}
       Readability Scores: {readability_scores}
       Engagement Scores: {engagement_scores}
       Originality Scores: {originality_scores}
       
       Create comprehensive optimization recommendations covering:
       
       1. PRIORITY OPTIMIZATION MATRIX:
       - Critical improvements (immediate action required)
       - High priority improvements (significant impact)
       - Medium priority improvements (moderate impact)
       - Low priority improvements (minor enhancements)
       
       2. CONTENT QUALITY IMPROVEMENTS:
       - Specific content enhancement suggestions
       - Value addition opportunities
       - Expertise demonstration improvements
       - Authority building recommendations
       - Trust signal integration
       
       3. SEO OPTIMIZATION RECOMMENDATIONS:
       - Keyword optimization improvements
       - On-page SEO enhancements
       - Technical SEO fixes
       - Featured snippet opportunities
       - Schema markup implementations
       
       4. READABILITY ENHANCEMENTS:
       - Sentence structure improvements
       - Paragraph optimization suggestions
       - Vocabulary simplification recommendations
       - Mobile readability enhancements
       - Accessibility improvements
       
       5. ENGAGEMENT OPTIMIZATION:
       - Hook strengthening strategies
       - Interest maintenance improvements
       - Interactive element additions
       - Emotional connection enhancements
       - Call-to-action optimizations
       
       6. ERROR CORRECTIONS:
       - Grammar and spelling fixes
       - Factual accuracy improvements
       - Consistency issue resolutions
       - Structural problem solutions
       - Legal compliance updates
       
       7. ORIGINALITY ENHANCEMENTS:
       - Unique perspective strengthening
       - Original insight additions
       - Source attribution improvements
       - Competitive differentiation strategies
       - Plagiarism risk mitigation
       
       8. IMPLEMENTATION ROADMAP:
       For each recommendation, provide:
       - Specific action item
       - Expected improvement impact
       - Implementation difficulty (Easy/Medium/Hard)
       - Time requirement estimate
       - Success measurement metrics
       
       9. OVERALL QUALITY SCORE CALCULATION:
       - Current overall quality score
       - Potential score after improvements
       - Score improvement breakdown by category
       - Publication readiness assessment
       
       10. FINAL RECOMMENDATIONS:
       - Must-fix items before publication
       - Nice-to-have improvements
       - Future optimization opportunities
       - Monitoring and tracking suggestions
       
       Provide actionable, prioritized recommendations that will maximize content performance and quality.
       """
       
       response = await self._call_gemini_with_reasoning(
           system_prompt="You are a content optimization specialist with expertise in comprehensive content improvement strategies.",
           user_prompt=prompt,
           reasoning_context="Generating comprehensive optimization recommendations based on quality analysis"
       )
       
       # Calculate overall quality score
       overall_score = self._calculate_overall_quality_score(
           quality_scores, seo_scores, readability_scores, engagement_scores, originality_scores
       )
       
       return {
           "optimization_recommendations": {
               "recommendations": response['response'],
               "overall_quality_score": overall_score,
               "score_breakdown": {
                   "content_quality": quality_scores.get("overall_score", 85),
                   "seo_compliance": seo_scores.get("overall_seo_score", 85),
                   "readability": readability_scores.get("overall_readability", 85),
                   "engagement": engagement_scores.get("overall_engagement", 85),
                   "originality": originality_scores.get("overall_originality", 85)
               },
               "optimization_areas": [
                   "Content quality improvements",
                   "SEO optimization",
                   "Readability enhancements",
                   "Engagement optimization",
                   "Error corrections",
                   "Originality enhancements"
               ],
               "publication_ready": overall_score >= 80
           },
           "reasoning": response['reasoning_steps'],
           "confidence": response['confidence']
       }
   
   def _calculate_overall_quality_score(self, quality_scores: Dict, seo_scores: Dict, 
                                      readability_scores: Dict, engagement_scores: Dict, 
                                      originality_scores: Dict) -> int:
       """Calculate weighted overall quality score"""
       try:
           # Weighted scoring system
           weights = {
               "content_quality": 0.25,
               "seo_compliance": 0.25,
               "readability": 0.20,
               "engagement": 0.20,
               "originality": 0.10
           }
           
           scores = {
               "content_quality": quality_scores.get("overall_score", 85),
               "seo_compliance": seo_scores.get("overall_seo_score", 85),
               "readability": readability_scores.get("overall_readability", 85),
               "engagement": engagement_scores.get("overall_engagement", 85),
               "originality": originality_scores.get("overall_originality", 85)
           }
           
           weighted_score = sum(scores[category] * weights[category] for category in weights)
           return int(weighted_score)
       
       except Exception as e:
           self.logger.warning(f"Failed to calculate overall quality score: {e}")
           return 85  # Default score
   
   async def process(self, input_data: Dict[Any, Any]) -> AgentResponse:
       """Quality Checker Agent ana işlem süreci"""
       
       self._update_progress(5, "processing", "Starting quality analysis")
       
       all_reasoning = []
       quality_check_data = {}
       
       try:
           # 1. Content quality analysis
           self._update_progress(15, "processing", "Analyzing content quality")
           quality_result = await self.call_tool("analyze_content_quality", **input_data)
           quality_check_data["content_quality"] = quality_result
           all_reasoning.extend(quality_result.get("reasoning", []))
           
           # 2. SEO compliance verification
           self._update_progress(25, "processing", "Verifying SEO compliance")
           seo_result = await self.call_tool("verify_seo_compliance", **input_data)
           quality_check_data["seo_compliance"] = seo_result
           all_reasoning.extend(seo_result.get("reasoning", []))
           
           # 3. Readability assessment
           self._update_progress(40, "processing", "Assessing readability")
           readability_result = await self.call_tool("assess_readability", **input_data)
           quality_check_data["readability_assessment"] = readability_result
           all_reasoning.extend(readability_result.get("reasoning", []))
           
           # 4. Error detection
           self._update_progress(55, "processing", "Detecting content errors")
           error_result = await self.call_tool("detect_content_errors", **input_data)
           quality_check_data["error_detection"] = error_result
           all_reasoning.extend(error_result.get("reasoning", []))
           
           # 5. Engagement evaluation
           self._update_progress(70, "processing", "Evaluating engagement factors")
           engagement_result = await self.call_tool("evaluate_engagement_factors", **input_data)
           quality_check_data["engagement_evaluation"] = engagement_result
           all_reasoning.extend(engagement_result.get("reasoning", []))
           
           # 6. Plagiarism risk check
           self._update_progress(85, "processing", "Checking plagiarism risk")
           plagiarism_result = await self.call_tool("check_plagiarism_risk", **input_data)
           quality_check_data["plagiarism_assessment"] = plagiarism_result
           all_reasoning.extend(plagiarism_result.get("reasoning", []))
           
           # 7. Generate optimization recommendations
           self._update_progress(95, "processing", "Generating optimization recommendations")
           optimization_result = await self.call_tool("generate_optimization_recommendations",
                                                    content_quality=quality_result,
                                                    seo_compliance=seo_result,
                                                    readability_assessment=readability_result,
                                                    error_detection=error_result,
                                                    engagement_evaluation=engagement_result,
                                                    plagiarism_assessment=plagiarism_result)
           quality_check_data["optimization_recommendations"] = optimization_result
           all_reasoning.extend(optimization_result.get("reasoning", []))
           
           # 8. Quality check summary
           self._update_progress(98, "processing", "Finalizing quality analysis")
           
           # Calculate average confidence
           confidences = [
               quality_result.get("confidence", 80),
               seo_result.get("confidence", 80),
               readability_result.get("confidence", 80),
               error_result.get("confidence", 80),
               engagement_result.get("confidence", 80),
               plagiarism_result.get("confidence", 80),
               optimization_result.get("confidence", 80)
           ]
           avg_confidence = sum(confidences) / len(confidences)
           
           # Extract final metrics
           optimization_data = optimization_result.get("optimization_recommendations", {})
           overall_score = optimization_data.get("overall_quality_score", 85)
           publication_ready = optimization_data.get("publication_ready", False)
           
           # Create comprehensive quality check summary
           quality_summary = {
               "quality_check_completed": True,
               "overall_quality_score": overall_score,
               "publication_ready": publication_ready,
               "avg_confidence": avg_confidence,
               "analysis_timestamp": datetime.now().isoformat(),
               "quality_areas_analyzed": [
                   "Content quality and depth",
                   "SEO compliance verification",
                   "Readability assessment",
                   "Error detection",
                   "Engagement evaluation",
                   "Plagiarism risk assessment",
                   "Optimization recommendations"
               ],
               "score_breakdown": optimization_data.get("score_breakdown", {}),
               "quality_grade": self._determine_quality_grade(overall_score),
               "recommendations_count": len(optimization_data.get("optimization_areas", [])),
               "critical_issues": error_result.get("error_detection", {}).get("error_summary", {}).get("critical_errors", 0)
           }
           
           quality_check_data["quality_summary"] = quality_summary
           
           return AgentResponse(
               success=True,
               data=quality_check_data,
               reasoning=all_reasoning,
               errors=[],
               processing_time=0.0,
               metadata={
                   "agent_name": self.config.name,
                   "confidence": avg_confidence,
                   "overall_quality_score": overall_score,
                   "publication_ready": publication_ready,
                   "quality_grade": quality_summary["quality_grade"],
                   "analysis_stages": 7
               }
           )
           
       except Exception as e:
           self.logger.error(f"Quality checking failed: {str(e)}")
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
   
   def _determine_quality_grade(self, score: int) -> str:
       """Determine quality grade based on score"""
       if score >= 95:
           return "A+"
       elif score >= 90:
           return "A"
       elif score >= 85:
           return "B+"
       elif score >= 80:
           return "B"
       elif score >= 75:
           return "C+"
       elif score >= 70:
           return "C"
       else:
           return "D"


# Test function
async def test_quality_checker():
   """Quality Checker Agent test function"""
   print("Testing Quality Checker Agent")
   print("=" * 50)
   
   # Services
   from services.gemini_service import GeminiService
   
   gemini = GeminiService()
   
   # Mock content writing data (simulating input from Content Writer)
   mock_content_writing = {
       "final_article": {
           "final_article": {
               "complete_article": """
# Best Wireless Gaming Headset Guide 2024

Are you tired of tangled wires ruining your epic gaming moments? In today's competitive gaming landscape, a top-tier wireless gaming headset is no longer a luxury—it's a necessity. Whether you're coordinating with teammates in intense multiplayer battles or immersing yourself in single-player adventures, the right wireless gaming headset can elevate your entire gaming experience.

## What Makes a Great Wireless Gaming Headset

A superior wireless gaming headset combines crystal-clear audio quality, comfortable design, and reliable connectivity. The best gaming headsets deliver immersive surround sound that lets you pinpoint enemy footsteps, hear subtle environmental cues, and experience games exactly as developers intended.

### Audio Quality and Performance

Premium wireless gaming headsets feature advanced drivers that reproduce both booming bass and crisp highs. Look for headsets with 50mm drivers or larger, as they typically provide fuller, more dynamic sound reproduction.

### Comfort and Build Quality

Extended gaming sessions demand exceptional comfort. The best wireless gaming headsets feature plush ear cushions, adjustable headbands, and lightweight designs that won't cause fatigue during marathon gaming sessions.

## Top Wireless Gaming Headsets Review

After extensive testing, these wireless gaming headsets stand out for their exceptional performance, comfort, and value.

### Premium Tier Options

High-end wireless gaming headsets offer professional-grade audio, premium materials, and advanced features like active noise cancellation and customizable EQ settings.

### Mid-Range Value Picks

These wireless gaming headsets provide excellent performance without breaking the bank, offering the perfect balance of features and affordability.

## How to Choose the Right Gaming Headset

Selecting the perfect wireless gaming headset depends on your specific needs, budget, and gaming preferences.

### Consider Your Gaming Platform

Different gaming platforms may have specific compatibility requirements. Ensure your chosen wireless gaming headset works seamlessly with your PC, PlayStation, Xbox, or Nintendo Switch.

### Battery Life and Charging

Look for wireless gaming headsets with at least 20+ hours of battery life to avoid interruptions during extended gaming sessions.

## Frequently Asked Questions

### What is the best wireless gaming headset for 2024?

The best wireless gaming headset depends on your specific needs and budget. Premium options offer superior audio quality and features, while mid-range models provide excellent value for most gamers.

### How long do wireless gaming headsets last?

High-quality wireless gaming headsets typically last 3-5 years with proper care. Battery performance may degrade over time, but most models offer replaceable batteries.

### Are wireless gaming headsets worth it?

Yes, wireless gaming headsets offer superior convenience and freedom of movement without sacrificing audio quality. Modern wireless technology provides reliable, low-latency connections perfect for gaming.

## Conclusion

Choosing the right wireless gaming headset can transform your gaming experience. Whether you prioritize premium audio quality, all-day comfort, or exceptional value, there's a perfect wireless gaming headset for every gamer and budget.

Ready to upgrade your gaming audio? Explore our recommended wireless gaming headsets and discover the difference premium audio can make in your gaming performance.
"""
           }
       },
       "writing_summary": {
           "total_word_count": 580,
           "content_sections": ["Introduction", "Main Content", "FAQ", "Conclusion"]
       },
       "introduction": {
           "introduction": {
               "content": "Are you tired of tangled wires ruining your epic gaming moments? In today's competitive gaming landscape, a top-tier wireless gaming headset is no longer a luxury—it's a necessity."
           }
       },
       "main_content": {
           "main_content": {
               "content": "A superior wireless gaming headset combines crystal-clear audio quality, comfortable design, and reliable connectivity..."
           }
       },
       "conclusion": {
           "conclusion": {
               "content": "Choosing the right wireless gaming headset can transform your gaming experience. Ready to upgrade your gaming audio?"
           }
       }
   }
   
   # Mock SEO optimization data
   mock_seo_optimization = {
       "meta_optimization": {
           "meta_optimization": {
               "meta_recommendations": {
                   "title_tags": ["Best Wireless Gaming Headset Guide 2024"],
                   "meta_descriptions": ["Discover the best wireless gaming headsets of 2024"]
               }
           }
       }
   }
   
   # Mock keyword analysis data
   mock_keyword_analysis = {
       "primary_selection": {
           "keyword_selection": {
               "primary_keywords": [
                   {"keyword": "wireless gaming headset", "search_volume": 8100},
                   {"keyword": "best gaming headset", "search_volume": 12000}
               ]
           }
       }
   }
   
   # Test input
   test_input = {
       "product_name": "Wireless Gaming Headset",
       "target_audience": "PC and console gamers aged 18-35",
       "content_writing": mock_content_writing,
       "seo_optimization": mock_seo_optimization,
       "keyword_analysis": mock_keyword_analysis
   }
   
   # Progress callback
   def progress_callback(agent_name, progress, status, current_step):
       print(f"[{agent_name}] {progress}% - {status}: {current_step}")
   
   # Test agent
   agent = QualityCheckerAgent(gemini)
   agent.set_progress_callback(progress_callback)
   
   result = await agent.execute(test_input)
   
   print("\nQuality Check Results:")
   print("-" * 30)
   print(f"Success: {result.success}")
   print(f"Data Keys: {list(result.data.keys())}")
   print(f"Overall Quality Score: {result.metadata.get('overall_quality_score', 'N/A')}")
   print(f"Quality Grade: {result.metadata.get('quality_grade', 'N/A')}")
   print(f"Publication Ready: {result.metadata.get('publication_ready', 'N/A')}")
   print(f"Confidence: {result.metadata.get('confidence', 'N/A'):.1f}%")
   print(f"Processing Time: {result.processing_time:.2f}s")
   
   if result.errors:
       print(f"Errors: {result.errors}")
   
   # Show sample results
   if result.success and result.data:
       summary = result.data.get("quality_summary", {})
       print(f"\nQuality Analysis Summary:")
       print(f"- Overall Score: {summary.get('overall_quality_score', 0)}/100")
       print(f"- Quality Grade: {summary.get('quality_grade', 'N/A')}")
       print(f"- Publication Ready: {summary.get('publication_ready', False)}")
       print(f"- Areas Analyzed: {len(summary.get('quality_areas_analyzed', []))}")
       print(f"- Critical Issues: {summary.get('critical_issues', 0)}")
       
       # Show score breakdown
       breakdown = summary.get("score_breakdown", {})
       if breakdown:
           print(f"\nScore Breakdown:")
           for area, score in breakdown.items():
               print(f"- {area.replace('_', ' ').title()}: {score}/100")
   
   return result


if __name__ == "__main__":
   # Test çalıştır
   result = asyncio.run(test_quality_checker())
   print(f"\nQuality Checker test completed!")
