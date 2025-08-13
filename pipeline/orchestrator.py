# pipeline/orchestrator.py - FIXED VERSION

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
import uuid

# Event system
class PipelineEvent:
    def __init__(self, event_type: str, data: Dict[str, Any], timestamp: str = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def __str__(self):
        return f"Event: {self.event_type} - {self.data}"

class EventBus:
    def __init__(self):
        self.listeners = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def publish(self, event: PipelineEvent):
        print(event)  # For testing
        if event.event_type in self.listeners:
            for callback in self.listeners[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Event callback error: {e}")

# Pipeline status
class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PipelineOrchestrator:
    def __init__(self):
        self.event_bus = EventBus()
        self.status = PipelineStatus.PENDING
        self.agents_config = [
            {"name": "market_research", "class": "MarketResearchAgent", "timeout": 120},
            {"name": "keyword_analyzer", "class": "KeywordAnalyzer", "timeout": 90},
            {"name": "content_structure", "class": "ContentStructureAgent", "timeout": 60},
            {"name": "content_writer", "class": "ContentWriterAgent", "timeout": 300},
            {"name": "image_placement", "class": "ImagePlacementAgent", "timeout": 60},
            {"name": "seo_audit", "class": "SEOAuditAgent", "timeout": 90},
            {"name": "content_refresher", "class": "ContentRefresherAgent", "timeout": 60}
        ]
        self.results = {}
        self.errors = []
        self.start_time = None
        self.end_time = None
        
    def _load_agent(self, agent_config: Dict[str, Any]):
        """Load agent class dynamically"""
        agent_name = agent_config["name"]
        
        # Mock agents that don't exist yet
        mock_agents = [
            "market_research", "keyword_analyzer", "content_structure", 
            "content_writer", "image_placement", "seo_audit", "content_refresher"
        ]
        
        if agent_name in mock_agents:
            print(f"Agent {agent_config['class']} not implemented yet - using mock")
            
            # FIXED: Progress callback with correct signature
            def progress_callback(agent_name, current_step, total_steps, status, message, **kwargs):
                self.event_bus.publish(PipelineEvent(
                    "agent_progress", 
                    {
                        "agent_name": agent_name,
                        "current_step": current_step,
                        "total_steps": total_steps,
                        "status": status,
                        "message": message,
                        "progress_percent": (current_step / total_steps) * 100 if total_steps > 0 else 0
                    }
                ))
            
            # Mock agent class
            class MockAgent:
                def __init__(self, config, progress_callback=None):
                    self.config = type('Config', (), {
                        'name': agent_config['name'],
                        'timeout': agent_config.get('timeout', 60)
                    })()
                    self.progress_callback = progress_callback
                
                async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                    # Simulate progress
                    if self.progress_callback:
                        self.progress_callback(
                            agent_name=self.config.name,
                            current_step=1,
                            total_steps=3,
                            status="processing",
                            message=f"Mock {self.config.name} processing..."
                        )
                    
                    await asyncio.sleep(0.1)  # Simulate work
                    
                    # Return mock result
                    return {
                        f"{agent_name}_result": f"Mock result from {agent_name}",
                        "status": "completed",
                        "processing_time": 0.1
                    }
            
            return MockAgent(agent_config, progress_callback)
        
        # Real agent loading would go here
        try:
            module_name = f"agents.{agent_name}"
            class_name = agent_config["class"]
            # module = __import__(module_name, fromlist=[class_name])
            # agent_class = getattr(module, class_name)
            # return agent_class(agent_config, progress_callback)
            raise ImportError(f"Real agent {class_name} not implemented yet")
        except ImportError:
            raise Exception(f"Could not load agent {agent_config['class']}")

    async def execute_agent(self, agent_config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single agent with error handling"""
        agent_name = agent_config["name"]
        start_time = datetime.now()
        
        try:
            # Load agent
            agent = self._load_agent(agent_config)
            
            # Execute with timeout
            timeout = agent_config.get("timeout", 120)
            result = await asyncio.wait_for(
                agent.execute(input_data),
                timeout=timeout
            )
            
            # Success event
            processing_time = (datetime.now() - start_time).total_seconds()
            self.event_bus.publish(PipelineEvent(
                "agent_completed",
                {
                    "agent_name": agent_name,
                    "agent_data": {**result, "processing_time": processing_time},
                    "timestamp": datetime.now().isoformat()
                }
            ))
            
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Agent {agent_name} timed out after {agent_config.get('timeout', 120)}s"
            self.errors.append(error_msg)
            self.event_bus.publish(PipelineEvent(
                "agent_timeout",
                {"agent_name": agent_name, "timeout": agent_config.get('timeout', 120)}
            ))
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Agent {agent_name} failed: {str(e)}"
            self.errors.append(error_msg)
            
            import traceback
            self.event_bus.publish(PipelineEvent(
                "agent_agent_failed",  # Note: keeping original event name for consistency
                {
                    "agent_name": agent_name,
                    "agent_data": {
                        "error": error_msg,
                        "processing_time": (datetime.now() - start_time).total_seconds(),
                        "traceback": traceback.format_exc()
                    },
                    "timestamp": datetime.now().isoformat()
                }
            ))
            raise Exception(error_msg)

    async def run_pipeline(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete 7-agent pipeline"""
        self.start_time = datetime.now()
        self.status = PipelineStatus.RUNNING
        
        # Initialize output
        pipeline_output = {
            "pipeline_id": str(uuid.uuid4()),
            "generated_at": self.start_time.isoformat(),
            "language": "english",
            **input_data
        }
        
        # Pipeline started event
        self.event_bus.publish(PipelineEvent(
            "pipeline_started",
            {"input_keys": list(input_data.keys())}
        ))
        
        try:
            # Execute agents sequentially
            for i, agent_config in enumerate(self.agents_config):
                agent_name = agent_config["name"]
                
                # Agent started event
                self.event_bus.publish(PipelineEvent(
                    "agent_started",
                    {
                        "agent_name": agent_name,
                        "agent_index": i + 1,
                        "total_agents": len(self.agents_config)
                    }
                ))
                
                # Execute agent
                try:
                    agent_result = await self.execute_agent(agent_config, pipeline_output)
                    self.results[agent_name] = agent_result
                    
                    # Merge agent output into pipeline
                    pipeline_output.update(agent_result)
                    
                except Exception as e:
                    print(f"Agent {agent_name} failed with exception: {e}")
                    # Continue with next agent even if one fails
                    continue
            
            # Determine final status
            if len(self.errors) == 0:
                self.status = PipelineStatus.COMPLETED
            elif len(self.results) > 0:
                self.status = PipelineStatus.COMPLETED  # Partial success
            else:
                self.status = PipelineStatus.FAILED
                
        except Exception as e:
            self.status = PipelineStatus.FAILED
            self.errors.append(f"Pipeline failed: {str(e)}")
            
        finally:
            self.end_time = datetime.now()
            
            # Add processing summary
            pipeline_output["processing_summary"] = {
                "total_agents": len(self.agents_config),
                "successful_agents": len(self.results),
                "failed_agents": len(self.errors),
                "processing_time": (self.end_time - self.start_time).total_seconds(),
                "errors": self.errors
            }
            
            # Pipeline completed event
            self.event_bus.publish(PipelineEvent(
                "pipeline_completed",
                {
                    "status": self.status.value,
                    "duration": (self.end_time - self.start_time).total_seconds(),
                    "success_rate": len(self.results) / len(self.agents_config) * 100,
                    "total_agents": len(self.agents_config),
                    "successful_agents": len(self.results),
                    "errors": len(self.errors)
                }
            ))
            
        return pipeline_output

    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            "status": self.status.value,
            "agents_completed": len(self.results),
            "total_agents": len(self.agents_config),
            "errors": self.errors,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }

# Test the pipeline
async def test_pipeline():
    print("Pipeline Orchestrator Test")
    print("=" * 50)
    
    # Test input
    test_input = {
        "product_name": "Wireless Gaming Mouse",
        "niche": "gaming peripherals", 
        "target_keywords": ["gaming mouse", "wireless mouse", "gaming gear"],
        "target_audience": "gamers, pc enthusiasts",
        "budget": 1500,
        "competition_level": "high"
    }
    
    print(f"Starting pipeline with input: {test_input}")
    print("-" * 50)
    
    # Create and run pipeline
    orchestrator = PipelineOrchestrator()
    result = await orchestrator.run_pipeline(test_input)
    
    print(f"Pipeline completed with status: {orchestrator.status}")
    print(f"Final output keys: {list(result.keys())}")
    print("=" * 50)
    
    return result

if __name__ == "__main__":
    # Run test
    result = asyncio.run(test_pipeline())
    
    print("PIPELINE RESULTS:")
    print("=" * 50)
    print(f"Status: {result['processing_summary']['errors']}")
    print(f"Duration: {result['processing_summary']['processing_time']:.2f}s")
    print(f"Success Rate: {result['processing_summary']['successful_agents']}/{result['processing_summary']['total_agents']} agents")
    print(f"Errors: {result['processing_summary']['failed_agents']}")
    print(f"Final Output Keys: {list(result.keys())}")