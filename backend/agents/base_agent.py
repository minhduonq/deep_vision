"""
Base Agent Class - Foundation for all agents in the system
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from loguru import logger
from backend.core.state import WorkflowState, TaskStatus


class BaseAgent(ABC):
    """
    Abstract base class for all agents
    
    Each agent must implement the process() method which:
    - Takes a WorkflowState as input
    - Performs its specific task
    - Returns updated WorkflowState
    """
    
    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize agent
        
        Args:
            name: Agent name for logging
            description: Optional description of agent's purpose
        """
        self.name = name
        self.description = description or f"{name} Agent"
        logger.info(f"Initialized {self.name}")
    
    @abstractmethod
    async def process(self, state: WorkflowState) -> WorkflowState:
        """
        Process the workflow state
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        pass
    
    def log_start(self, state: WorkflowState):
        """Log when agent starts processing"""
        logger.info(f"[{self.name}] Starting - Task: {state.task_id}, Type: {state.task_type}")
    
    def log_complete(self, state: WorkflowState):
        """Log when agent completes"""
        logger.info(f"[{self.name}] Completed - Progress: {state.progress}%")
    
    def log_error(self, state: WorkflowState, error: Exception):
        """Log when agent encounters error"""
        logger.error(f"[{self.name}] Error - Task: {state.task_id}, Error: {str(error)}")
    
    async def safe_process(self, state: WorkflowState) -> WorkflowState:
        """
        Wrapper around process() with error handling
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state (with error status if failed)
        """
        try:
            self.log_start(state)
            result_state = await self.process(state)
            self.log_complete(result_state)
            return result_state
            
        except Exception as e:
            self.log_error(state, e)
            state.status = TaskStatus.FAILED
            if not state.intermediate_results.get("errors"):
                state.intermediate_results["errors"] = []
            state.intermediate_results["errors"].append({
                "agent": self.name,
                "error": str(e),
                "type": type(e).__name__
            })
            return state


class LLMAgent(BaseAgent):
    """
    Base class for agents that use Language Models
    """
    
    def __init__(self, name: str, model: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize LLM Agent
        
        Args:
            name: Agent name
            model: Model identifier (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Model temperature (0.0 = deterministic, 1.0 = creative)
        """
        super().__init__(name)
        self.model = model
        self.temperature = temperature
        self.client = None  # Will be initialized in subclass
    
    def create_prompt(self, state: WorkflowState, **kwargs) -> str:
        """
        Create prompt for LLM
        Override this in subclass
        
        Args:
            state: Current workflow state
            **kwargs: Additional parameters
            
        Returns:
            Formatted prompt string
        """
        raise NotImplementedError
    
    async def call_llm(self, prompt: str, **kwargs) -> str:
        """
        Call LLM with prompt
        Override this in subclass
        
        Args:
            prompt: Input prompt
            **kwargs: Additional LLM parameters
            
        Returns:
            LLM response
        """
        raise NotImplementedError


class ToolAgent(BaseAgent):
    """
    Base class for agents that use external tools/APIs
    """
    
    def __init__(self, name: str, tool_name: str):
        """
        Initialize Tool Agent
        
        Args:
            name: Agent name
            tool_name: Name of the tool/API being used
        """
        super().__init__(name)
        self.tool_name = tool_name
        self.client = None  # Tool client
    
    async def call_tool(self, **kwargs) -> Any:
        """
        Call external tool/API
        Override this in subclass
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool response
        """
        raise NotImplementedError
    
    def validate_tool_response(self, response: Any) -> bool:
        """
        Validate tool response
        Override this in subclass
        
        Args:
            response: Tool response
            
        Returns:
            True if valid, False otherwise
        """
        return response is not None
