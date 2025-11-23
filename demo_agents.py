"""
Quick Test - Demonstrate Multi-Agent System
Run this to see how agents work together
"""
import asyncio
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.state import WorkflowState, TaskType, TaskStatus
from backend.core.utils import generate_task_id


async def demo_simple_analyzer():
    """Demo: Simple rule-based task analyzer"""
    print("\n" + "="*70)
    print("🤖 DEMO: Simple Rule-Based Task Analyzer (No LLM)")
    print("="*70)
    
    from backend.agents.task_analyzer import SimpleTaskAnalyzer
    
    test_cases = [
        "Làm rõ ảnh bị mờ",
        "Xóa người ở phía sau",
        "Remove watermark",
        "Beautify my face please",
        "Make it sharper",
        "Delete object in corner",
    ]
    
    analyzer = SimpleTaskAnalyzer()
    
    print("\n📝 Testing various user requests:\n")
    
    for request in test_cases:
        result = await analyzer.analyze(request)
        
        # Visual indicator
        confidence = result['confidence']
        bars = "█" * int(confidence * 10)
        
        print(f"Request: '{request}'")
        print(f"  → Task Type: {result['task_type'].upper()}")
        print(f"  → Confidence: [{bars:<10}] {confidence:.0%}")
        print(f"  → Reasoning: {result['reasoning']}")
        print()


async def demo_state_flow():
    """Demo: How state flows through agents"""
    print("\n" + "="*70)
    print("📊 DEMO: State Flow Through Agents")
    print("="*70)
    
    # Create initial state
    state = WorkflowState(
        task_id=generate_task_id(),
        user_request="Xóa text ở góc dưới",
        input_path="test_image.jpg"
    )
    state.task_type = TaskType.INPAINT  # Set as enum
    
    print(f"\n📦 Initial State:")
    print(f"   Task ID: {state.task_id}")
    print(f"   Request: {state.user_request}")
    print(f"   Task Type: {state.task_type.value}")
    print(f"   Status: {state.status.value}")
    print(f"   Progress: {state.progress}%")
    
    print(f"\n🔄 Simulating Agent Processing...\n")
    
    # Simulate Task Analyzer
    print("1️⃣ Task Analyzer Agent")
    state.status = TaskStatus.ANALYZING
    state.progress = 20
    state.intermediate_results["analysis"] = {
        "confidence": 0.85,
        "reasoning": "Detected 'xóa text' keywords → inpaint task"
    }
    print(f"   → Status: {state.status.value}")
    print(f"   → Progress: {state.progress}%")
    print(f"   → Analysis: confidence={state.intermediate_results['analysis']['confidence']}")
    
    # Simulate Worker
    print(f"\n2️⃣ Image Worker Agent")
    state.status = TaskStatus.PROCESSING
    state.progress = 70
    state.output_path = "outputs/inpaint_test_image.jpg"
    state.intermediate_results["model_used"] = "LaMa"
    print(f"   → Status: {state.status.value}")
    print(f"   → Progress: {state.progress}%")
    print(f"   → Model: {state.intermediate_results['model_used']}")
    print(f"   → Output: {state.output_path}")
    
    # Simulate QC
    print(f"\n3️⃣ Quality Control Agent")
    state.status = TaskStatus.QUALITY_CHECK
    state.progress = 90
    state.intermediate_results["quality_checks"] = {
        "file_exists": {"passed": True},
        "valid_format": {"passed": True},
        "dimensions": {"passed": True}
    }
    print(f"   → Status: {state.status.value}")
    print(f"   → Progress: {state.progress}%")
    print(f"   → Checks: {len(state.intermediate_results['quality_checks'])} passed")
    
    # Final
    state.status = TaskStatus.COMPLETED
    state.progress = 100
    print(f"\n✅ Final State:")
    print(f"   Status: {state.status.value}")
    print(f"   Progress: {state.progress}%")
    print(f"   Output: {state.output_path}")


async def demo_agent_classes():
    """Demo: Understanding agent class hierarchy"""
    print("\n" + "="*70)
    print("🏗️  DEMO: Agent Class Architecture")
    print("="*70)
    
    from backend.agents.base_agent import BaseAgent, LLMAgent, ToolAgent
    from backend.agents.task_analyzer import TaskAnalyzerAgent
    from backend.agents.image_worker import ImageWorkerAgent
    
    print("""
📚 Agent Hierarchy:

BaseAgent (Abstract)
├── process(state) → state          # Must implement
├── safe_process(state) → state     # With error handling
├── log_start(), log_complete()     # Built-in logging
│
├─→ LLMAgent (for AI reasoning)
│   ├── create_prompt(state)
│   ├── call_llm(prompt)
│   └── Example: TaskAnalyzerAgent
│
└─→ ToolAgent (for external APIs)
    ├── call_tool(**kwargs)
    ├── validate_tool_response()
    └── Example: ImageWorkerAgent

📋 Key Concepts:

1. **State**: Shared data structure passed between agents
   - Contains: task_id, user_request, status, progress, paths
   - Each agent reads and updates state

2. **Agents**: Independent units with single responsibility
   - Task Analyzer: Determines what to do
   - Worker: Actually does it
   - Quality Control: Validates result

3. **Orchestrator**: Coordinates agent execution
   - Runs agents in sequence
   - Handles errors and failures
   - Ensures proper state flow

4. **Base Classes**: Provide common functionality
   - Error handling (safe_process)
   - Logging (log_start, log_complete, log_error)
   - Structure (abstract process method)
    """)


async def demo_error_handling():
    """Demo: How errors are handled"""
    print("\n" + "="*70)
    print("⚠️  DEMO: Error Handling in Agents")
    print("="*70)
    
    from backend.agents.base_agent import BaseAgent
    from backend.core.state import WorkflowState
    
    # Create a mock failing agent
    class FailingAgent(BaseAgent):
        async def process(self, state: WorkflowState) -> WorkflowState:
            raise ValueError("Simulated error!")
    
    state = WorkflowState(
        task_id="test_error",
        user_request="Test error handling"
    )
    
    print(f"\n📦 Initial state:")
    print(f"   Status: {state.status.value}")
    print(f"   Errors: {state.intermediate_results.get('errors', [])}")
    
    print(f"\n💥 Running failing agent...")
    
    agent = FailingAgent("Test Agent")
    result_state = await agent.safe_process(state)
    
    print(f"\n❌ After error:")
    print(f"   Status: {result_state.status.value}")
    print(f"   Errors: {result_state.intermediate_results.get('errors', [])}")
    
    print(f"\n✅ Key Points:")
    print(f"   • Error was caught by safe_process()")
    print(f"   • State was updated with error info")
    print(f"   • Agent name and error type recorded")
    print(f"   • Workflow can continue or stop based on status")


def print_summary():
    """Print summary of agent system"""
    print("\n" + "="*70)
    print("📚 SUMMARY: Multi-Agent System")
    print("="*70)
    
    print("""
🎯 Key Components Created:

1. **Base Agent Classes** (backend/agents/base_agent.py)
   - BaseAgent: Abstract base for all agents
   - LLMAgent: For agents using language models
   - ToolAgent: For agents using external tools/APIs

2. **Concrete Agents**:
   - TaskAnalyzerAgent: LLM-based request analysis
   - SimpleTaskAnalyzer: Rule-based analysis (no LLM)
   - ImageWorkerAgent: Image processing via Replicate
   - QualityControlAgent: Output validation

3. **Orchestrator** (backend/agents/orchestrator.py)
   - SimpleOrchestrator: Linear agent execution
   - ConditionalOrchestrator: Advanced routing logic
   - get_orchestrator(): Singleton pattern

4. **State Management** (backend/core/state.py)
   - WorkflowState: Shared data structure
   - TaskType, TaskStatus: Enums for consistency

📖 Documentation:
   - AGENT_TUTORIAL.md: Complete guide
   - examples/README.md: Usage examples
   - examples/agent_usage_example.py: Code samples

🚀 Next Steps:

1. Read AGENT_TUTORIAL.md for detailed explanation
2. Run examples: python examples/agent_usage_example.py
3. Integrate into FastAPI: Use orchestrator in background tasks
4. Test with real images and Replicate API
5. Add custom agents for specific needs

💡 Pro Tips:

• Start with SimpleTaskAnalyzer (no API costs)
• Use safe_process() for automatic error handling
• Check state.status after each agent
• Log everything for debugging
• Test agents individually before full workflow
    """)


async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("🤖 MULTI-AGENT SYSTEM - QUICK DEMO")
    print("="*70)
    
    # Run demos
    await demo_simple_analyzer()
    await demo_state_flow()
    await demo_agent_classes()
    await demo_error_handling()
    
    # Print summary
    print_summary()
    
    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70)
    print("\n📖 Next: Read AGENT_TUTORIAL.md for detailed explanation")
    print("🎮 Try: python examples/agent_usage_example.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
