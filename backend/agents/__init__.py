"""
Agent System for Deep Vision
Multi-agent coordination for image processing tasks
"""

from backend.agents.base_agent import BaseAgent, LLMAgent, ToolAgent
from backend.agents.task_analyzer import TaskAnalyzerAgent, SimpleTaskAnalyzer
from backend.agents.image_worker import ImageWorkerAgent
from backend.agents.quality_control import QualityControlAgent
from backend.agents.orchestrator import (
    SimpleOrchestrator,
    ConditionalOrchestrator,
    get_orchestrator
)

# Image generation & editing agents
from backend.agents.huggingface_generation_agent import (
    HuggingFaceGenerationAgent,
    generation_agent
)
from backend.agents.qwen_edit_agent import QwenEditAgent
from backend.agents.qwen_fast_edit_agent import (
    QwenFastEditAgent,
    qwen_fast_edit_agent
)
from backend.agents.qwen_lora_fusion_agent import (
    QwenLoRAFusionAgent,
    qwen_lora_fusion_agent
)

__all__ = [
    # Base classes
    "BaseAgent",
    "LLMAgent",
    "ToolAgent",
    
    # Concrete agents
    "TaskAnalyzerAgent",
    "SimpleTaskAnalyzer",
    "ImageWorkerAgent",
    "QualityControlAgent",
    
    # Orchestrators
    "SimpleOrchestrator",
    "ConditionalOrchestrator",
    "get_orchestrator",
    
    # Generation & Editing agents
    "HuggingFaceGenerationAgent",
    "generation_agent",
    "QwenEditAgent",
    "QwenFastEditAgent",
    "qwen_fast_edit_agent",
    "QwenLoRAFusionAgent",
    "qwen_lora_fusion_agent",
]

