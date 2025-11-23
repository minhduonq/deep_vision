"""
Orchestrator - Coordinates multiple agents in a workflow
"""
from typing import List, Optional
from loguru import logger

from backend.core.state import WorkflowState, TaskStatus
from backend.agents.base_agent import BaseAgent
from backend.agents.task_analyzer import TaskAnalyzerAgent
from backend.agents.image_worker import ImageWorkerAgent
from backend.agents.quality_control import QualityControlAgent


class SimpleOrchestrator:
    """
    Simple linear orchestrator - runs agents in sequence
    
    Flow: Task Analyzer → Image Worker → Quality Control
    """
    
    def __init__(self, use_llm_analyzer: bool = True):
        """
        Initialize orchestrator
        
        Args:
            use_llm_analyzer: If True, use LLM-based analyzer. 
                            If False, use simple rule-based analyzer
        """
        self.agents: List[BaseAgent] = []
        
        # Add agents in order
        if use_llm_analyzer:
            self.agents.append(TaskAnalyzerAgent())
        # Note: If not using LLM, task_type should be set before orchestration
        
        self.agents.append(ImageWorkerAgent())
        self.agents.append(QualityControlAgent())
        
        logger.info(f"Orchestrator initialized with {len(self.agents)} agents")
    
    async def run(self, state: WorkflowState) -> WorkflowState:
        """
        Run the workflow through all agents
        
        Args:
            state: Initial workflow state
            
        Returns:
            Final workflow state after all agents
        """
        logger.info(f"Starting workflow for task {state.task_id}")
        logger.info(f"Initial state: {state.task_type.value if state.task_type else 'unspecified'}")
        
        current_state = state
        
        # Run each agent in sequence
        for i, agent in enumerate(self.agents, 1):
            logger.info(f"Step {i}/{len(self.agents)}: {agent.name}")
            
            try:
                # Process with agent
                current_state = await agent.safe_process(current_state)
                
                # Check if failed
                if current_state.status == TaskStatus.FAILED:
                    logger.error(f"Workflow failed at {agent.name}")
                    break
                    
            except Exception as e:
                logger.error(f"Agent {agent.name} raised exception: {e}")
                current_state.status = TaskStatus.FAILED
                if "errors" not in current_state.intermediate_results:
                    current_state.intermediate_results["errors"] = []
                current_state.intermediate_results["errors"].append({
                    "agent": agent.name,
                    "error": str(e)
                })
                break
        
        # Log final status
        if current_state.status == TaskStatus.COMPLETED:
            logger.info(f"Workflow completed successfully: {state.task_id}")
        else:
            logger.error(f"Workflow ended with status: {current_state.status.value}")
        
        return current_state


class ConditionalOrchestrator:
    """
    Advanced orchestrator with conditional logic
    
    Can route to different agents based on state
    """
    
    def __init__(self):
        self.agents = {
            "analyzer": TaskAnalyzerAgent(),
            "worker": ImageWorkerAgent(),
            "quality": QualityControlAgent()
        }
        logger.info("Conditional Orchestrator initialized")
    
    async def run(self, state: WorkflowState) -> WorkflowState:
        """
        Run workflow with conditional logic
        
        Args:
            state: Initial workflow state
            
        Returns:
            Final workflow state
        """
        logger.info(f"Starting conditional workflow for task {state.task_id}")
        
        # Step 1: Analyze task
        state = await self.agents["analyzer"].safe_process(state)
        
        if state.status == TaskStatus.FAILED:
            return state
        
        # Step 2: Process based on confidence
        confidence = state.intermediate_results.get("analysis", {}).get("confidence", 0)
        
        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}), may need manual review")
            state.intermediate_results["needs_review"] = True
        
        # Step 3: Process image
        state = await self.agents["worker"].safe_process(state)
        
        if state.status == TaskStatus.FAILED:
            # Could implement retry logic here
            retry_count = state.intermediate_results.get("retry_count", 0)
            if retry_count < 3:
                logger.info(f"Retrying worker (attempt {retry_count + 1})")
                state.intermediate_results["retry_count"] = retry_count + 1
                state.status = TaskStatus.PROCESSING
                state = await self.agents["worker"].safe_process(state)
        
        if state.status == TaskStatus.FAILED:
            return state
        
        # Step 4: Quality check
        state = await self.agents["quality"].safe_process(state)
        
        return state


# Global orchestrator instance
_orchestrator_instance: Optional[SimpleOrchestrator] = None


def get_orchestrator(use_llm_analyzer: bool = True) -> SimpleOrchestrator:
    """
    Get or create orchestrator instance (singleton pattern)
    
    Args:
        use_llm_analyzer: Whether to use LLM-based task analyzer
        
    Returns:
        Orchestrator instance
    """
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = SimpleOrchestrator(use_llm_analyzer=use_llm_analyzer)
    
    return _orchestrator_instance
