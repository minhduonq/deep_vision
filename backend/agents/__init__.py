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
]

