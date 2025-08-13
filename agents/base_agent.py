"""
Base Agent Class for AI SEO Blog Generator

Bu sınıf tüm AI agent'ların temelini oluşturur ve şu özellikleri sağlar:
- Chain of thought reasoning
- Tool management ve API çağrıları
- Error handling ve retry logic
- Progress tracking
- Event emission için pipeline ile iletişim
"""

import logging
import asyncio
import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import traceback

# Python path fix for development
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.gemini_service import GeminiService
except ImportError:
    print("WARNING: GeminiService not found. Using mock for testing.")
    # Mock GeminiService for testing
    class GeminiService:
        async def generate_content(self, prompt, temperature=0.7, max_tokens=4000):
            return f"Mock response for: {prompt[:50]}..."


@dataclass
class AgentResponse:
    """Agent yanıt yapısı"""
    success: bool
    data: Dict[Any, Any]
    reasoning: List[str]  # Chain of thought adımları
    errors: List[str]
    processing_time: float
    metadata: Dict[str, Any]


@dataclass
class AgentConfig:
    """Agent konfigürasyon yapısı"""
    name: str
    description: str
    max_retries: int = 3
    timeout_seconds: int = 120
    temperature: float = 0.7
    max_tokens: int = 4000
    reasoning_enabled: bool = True


class BaseAgent(ABC):
    """
    Tüm AI Agent'ların temel sınıfı
    
    Her agent bu sınıftan türetilir ve process() metodunu implement eder.
    Chain of thought reasoning ve tool management otomatik olarak sağlanır.
    """
    
    def __init__(self, config: AgentConfig, gemini_service: GeminiService):
        self.config = config
        self.gemini_service = gemini_service
        self.logger = logging.getLogger(f"agent.{config.name}")
        
        # Progress tracking
        self._progress = 0
        self._status = "idle"
        self._current_step = ""
        
        # Event callbacks
        self._progress_callback: Optional[Callable] = None
        self._event_callback: Optional[Callable] = None
        
        self.logger.info(f"Agent {self.config.name} initialized")
    
    def set_progress_callback(self, callback: Callable):
        """Pipeline orchestrator tarafından progress callback set edilir"""
        self._progress_callback = callback
    
    def set_event_callback(self, callback: Callable):
        """Event emission için callback set edilir"""
        self._event_callback = callback
    
    def _update_progress(self, progress: int, status: str, current_step: str = ""):
        """Progress güncelleme ve callback tetikleme"""
        self._progress = progress
        self._status = status
        self._current_step = current_step
        
        if self._progress_callback:
            self._progress_callback(
                agent_name=self.config.name,
                progress=progress,
                status=status,
                current_step=current_step
            )
        
        self.logger.info(f"Progress: {progress}% - {status} - {current_step}")
    
    def _emit_event(self, event_type: str, data: Dict[Any, Any]):
        """Event emission - pipeline ile iletişim için"""
        if self._event_callback:
            self._event_callback(
                agent_name=self.config.name,
                event_type=event_type,
                data=data,
                timestamp=datetime.now().isoformat()
            )
    
    async def _call_gemini_with_reasoning(self, 
                                        system_prompt: str, 
                                        user_prompt: str, 
                                        reasoning_context: str = "") -> Dict[str, Any]:
        """
        Chain of thought ile Gemini API çağrısı
        
        Returns:
            {
                'response': str,
                'reasoning_steps': List[str],
                'confidence': float
            }
        """
        
        # Chain of thought için prompt engineering
        if self.config.reasoning_enabled:
            enhanced_prompt = f"""
{system_prompt}

IMPORTANT: Use chain of thought reasoning. Break down your thinking into clear steps.

Context from previous reasoning:
{reasoning_context}

Task: {user_prompt}

Please structure your response as follows:
REASONING:
1. [First step of your thinking]
2. [Second step of your thinking]
3. [Continue step by step]

RESPONSE:
[Your final response/output]

CONFIDENCE: [Your confidence level 0-100]
"""
        else:
            enhanced_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            response = await self.gemini_service.generate_content(
                prompt=enhanced_prompt,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            if self.config.reasoning_enabled:
                return self._parse_reasoning_response(response)
            else:
                return {
                    'response': response,
                    'reasoning_steps': [],
                    'confidence': 85.0  # Default confidence
                }
                
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {str(e)}")
            raise
    
    def _parse_reasoning_response(self, raw_response: str) -> Dict[str, Any]:
        """Chain of thought yanıtını parse eder"""
        try:
            parts = raw_response.split("REASONING:")
            if len(parts) > 1:
                reasoning_part = parts[1].split("RESPONSE:")[0].strip()
                response_part = parts[1].split("RESPONSE:")[1].split("CONFIDENCE:")[0].strip()
                confidence_part = parts[1].split("CONFIDENCE:")[1].strip() if "CONFIDENCE:" in parts[1] else "80"
                
                # Reasoning steps'leri parse et
                reasoning_steps = []
                for line in reasoning_part.split('\n'):
                    line = line.strip()
                    if line and (line.startswith(tuple('123456789')) or line.startswith('-')):
                        reasoning_steps.append(line)
                
                # Confidence parse et
                confidence = float(''.join(filter(str.isdigit, confidence_part))) if confidence_part else 80.0
                
                return {
                    'response': response_part,
                    'reasoning_steps': reasoning_steps,
                    'confidence': min(confidence, 100.0)
                }
            else:
                # Fallback: reasoning structure bulunamazsa
                return {
                    'response': raw_response,
                    'reasoning_steps': ["Direct response without structured reasoning"],
                    'confidence': 70.0
                }
                
        except Exception as e:
            self.logger.error(f"Failed to parse reasoning response: {str(e)}")
            return {
                'response': raw_response,
                'reasoning_steps': ["Parsing failed, using raw response"],
                'confidence': 60.0
            }
    
    async def _execute_with_retry(self, task_func: Callable, *args, **kwargs) -> Any:
        """Retry logic ile task execution"""
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.debug(f"Attempt {attempt + 1}/{self.config.max_retries}")
                result = await asyncio.wait_for(
                    task_func(*args, **kwargs),
                    timeout=self.config.timeout_seconds
                )
                return result
                
            except asyncio.TimeoutError:
                last_error = f"Task timed out after {self.config.timeout_seconds} seconds"
                self.logger.warning(f"Attempt {attempt + 1} timed out")
                
            except Exception as e:
                last_error = f"Task failed: {str(e)}"
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                # Kısa bekleme retry'lar arasında
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Task failed after {self.config.max_retries} attempts. Last error: {last_error}")
    
    @abstractmethod
    async def process(self, input_data: Dict[Any, Any]) -> AgentResponse:
        """
        Her agent bu metodu implement etmelidir
        
        Args:
            input_data: Pipeline'dan gelen input verisi
            
        Returns:
            AgentResponse: Standardize edilmiş agent yanıtı
        """
        pass
    
    async def execute(self, input_data: Dict[Any, Any]) -> AgentResponse:
        """
        Ana execution metodu - progress tracking ve error handling ile
        
        Bu metod pipeline orchestrator tarafından çağrılır
        """
        start_time = datetime.now()
        reasoning_chain = []
        errors = []
        
        try:
            self._update_progress(0, "starting", "Initializing agent")
            
            # Emit başlangıç eventi
            self._emit_event("agent_started", {
                "input_data_keys": list(input_data.keys()),
                "config": self.config.__dict__
            })
            
            self._update_progress(10, "processing", "Executing main task")
            
            # Ana işlemi retry logic ile çalıştır
            result = await self._execute_with_retry(self.process, input_data)
            
            self._update_progress(90, "finalizing", "Preparing response")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Başarılı completion eventi
            self._emit_event("agent_completed", {
                "processing_time": processing_time,
                "success": True
            })
            
            self._update_progress(100, "completed", "Task finished successfully")
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Agent {self.config.name} failed: {str(e)}"
            
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            # Hata eventi
            self._emit_event("agent_failed", {
                "error": error_msg,
                "processing_time": processing_time,
                "traceback": traceback.format_exc()
            })
            
            self._update_progress(100, "failed", f"Error: {str(e)}")
            
            return AgentResponse(
                success=False,
                data={},
                reasoning=reasoning_chain,
                errors=[error_msg],
                processing_time=processing_time,
                metadata={
                    "agent_name": self.config.name,
                    "failure_reason": str(e)
                }
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Mevcut agent durumunu döner"""
        return {
            "name": self.config.name,
            "progress": self._progress,
            "status": self._status,
            "current_step": self._current_step,
            "config": self.config.__dict__
        }


class ToolMixin:
    """Agent'lara tool functionality eklemek için mixin class"""
    
    def __init__(self):
        self.available_tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Varsayılan tool'ları kaydet"""
        self.available_tools.update({
            "search_web": self._search_web,
            "analyze_competitor": self._analyze_competitor,
            "get_keyword_metrics": self._get_keyword_metrics,
            "validate_content": self._validate_content
        })
    
    async def _search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Web search tool - bu daha sonra implement edilecek"""
        # Placeholder - gerçek web search API'si burada olacak
        return {
            "query": query,
            "results": [],
            "status": "not_implemented"
        }
    
    async def _analyze_competitor(self, domain: str) -> Dict[str, Any]:
        """Competitor analysis tool"""
        # Placeholder - SEO analysis burada olacak
        return {
            "domain": domain,
            "analysis": {},
            "status": "not_implemented"
        }
    
    async def _get_keyword_metrics(self, keywords: List[str]) -> Dict[str, Any]:
        """Keyword metrics tool"""
        # Placeholder - keyword research API'si burada olacak
        return {
            "keywords": keywords,
            "metrics": {},
            "status": "not_implemented"
        }
    
    async def _validate_content(self, content: str) -> Dict[str, Any]:
        """Content validation tool"""
        # Placeholder - content quality check burada olacak
        return {
            "content_length": len(content),
            "validation_results": {},
            "status": "not_implemented"
        }
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Tool çağırma metodu"""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self.available_tools.keys())}")
        
        try:
            return await self.available_tools[tool_name](**kwargs)
        except Exception as e:
            raise Exception(f"Tool '{tool_name}' failed: {str(e)}")


# Example usage ve test helper'ları
class TestAgent(BaseAgent, ToolMixin):
    """Test agent for development - can be imported by test files"""
    
    def __init__(self, gemini_service: GeminiService):
        config = AgentConfig(
            name="test_agent",
            description="Test agent for development",
            reasoning_enabled=True
        )
        BaseAgent.__init__(self, config, gemini_service)
        ToolMixin.__init__(self)
    
    async def process(self, input_data: Dict[Any, Any]) -> AgentResponse:
        self._update_progress(20, "processing", "Analyzing input")
        
        # Chain of thought reasoning ile content üret
        gemini_response = await self._call_gemini_with_reasoning(
            system_prompt="You are a test AI agent. Analyze the given input and provide insights.",
            user_prompt=f"Analyze this data: {json.dumps(input_data)}"
        )
        
        self._update_progress(60, "processing", "Calling tools")
        
        # Tool kullanım örneği
        search_result = await self.call_tool("search_web", query="test query", max_results=3)
        
        self._update_progress(80, "processing", "Finalizing results")
        
        return AgentResponse(
            success=True,
            data={
                "analysis": gemini_response['response'],
                "tool_result": search_result,
                "input_summary": f"Processed {len(input_data)} input fields"
            },
            reasoning=gemini_response['reasoning_steps'],
            errors=[],
            processing_time=0.0,  # Will be calculated by execute()
            metadata={
                "confidence": gemini_response['confidence'],
                "agent_name": self.config.name
            }
        )


if __name__ == "__main__":
    print("BaseAgent class ready for implementation!")
    print("Next steps:")
    print("1. Test this base class with a sample agent")
    print("2. Create keyword_scorer.py")
    print("3. Create pipeline/orchestrator.py")
    print("4. Start implementing specific agents")