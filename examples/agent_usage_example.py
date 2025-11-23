"""
Example: How to use the Multi-Agent System
"""
import asyncio
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.state import WorkflowState, TaskType
from backend.agents.orchestrator import SimpleOrchestrator
from backend.core.utils import generate_task_id


async def example_1_simple_workflow():
    """
    Example 1: Simple workflow - deblur an image
    """
    print("\n" + "="*60)
    print("Example 1: Simple Deblur Workflow")
    print("="*60)
    
    # Create initial state
    state = WorkflowState(
        task_id=generate_task_id(),
        user_request="Làm rõ ảnh bị mờ",
        task_type=TaskType.DEBLUR,  # Can set manually or let analyzer decide
        input_path="path/to/blurry_image.jpg"  # Replace with actual path
    )
    
    print(f"\n📝 Initial State:")
    print(f"   Task ID: {state.task_id}")
    print(f"   Request: {state.user_request}")
    print(f"   Input: {state.input_path}")
    
    # Create orchestrator
    orchestrator = SimpleOrchestrator(use_llm_analyzer=False)  # No LLM for this example
    
    # Run workflow
    print(f"\n🚀 Starting workflow...")
    final_state = await orchestrator.run(state)
    
    # Check results
    print(f"\n✅ Final Status: {final_state.status.value}")
    print(f"   Progress: {final_state.progress}%")
    
    if final_state.output_path:
        print(f"   Output: {final_state.output_path}")
    
    if final_state.intermediate_results.get("errors"):
        print(f"   Errors: {final_state.intermediate_results['errors']}")


async def example_2_with_llm_analyzer():
    """
    Example 2: Use LLM to analyze user request
    """
    print("\n" + "="*60)
    print("Example 2: Workflow with LLM Task Analyzer")
    print("="*60)
    
    # Create state WITHOUT specifying task_type
    # Let the LLM figure it out!
    state = WorkflowState(
        task_id=generate_task_id(),
        user_request="Xóa người ở phía sau cho tôi",  # Ambiguous request
        input_path="path/to/photo.jpg"
    )
    
    print(f"\n📝 User Request: {state.user_request}")
    print(f"   (No task_type specified, let LLM decide)")
    
    # Create orchestrator with LLM analyzer
    orchestrator = SimpleOrchestrator(use_llm_analyzer=True)
    
    # Run workflow
    print(f"\n🤖 LLM analyzing request...")
    final_state = await orchestrator.run(state)
    
    # Show analysis results
    analysis = final_state.intermediate_results.get("analysis", {})
    print(f"\n🧠 LLM Analysis:")
    print(f"   Detected Task: {final_state.task_type.value}")
    print(f"   Confidence: {analysis.get('confidence', 0):.2%}")
    print(f"   Reasoning: {analysis.get('reasoning', 'N/A')}")
    
    print(f"\n✅ Final Status: {final_state.status.value}")


async def example_3_simple_rule_based():
    """
    Example 3: Use simple rule-based analyzer (no OpenAI needed)
    """
    print("\n" + "="*60)
    print("Example 3: Simple Rule-Based Analysis (No LLM)")
    print("="*60)
    
    from backend.agents.task_analyzer import SimpleTaskAnalyzer
    
    # Test different requests
    requests = [
        "Làm rõ ảnh mờ",
        "Remove background",
        "Beautify my face",
        "Generate a cat image"
    ]
    
    analyzer = SimpleTaskAnalyzer()
    
    for request in requests:
        result = await analyzer.analyze(request)
        print(f"\n📝 Request: '{request}'")
        print(f"   → Task: {result['task_type']}")
        print(f"   → Confidence: {result['confidence']:.2%}")
        print(f"   → Reasoning: {result['reasoning']}")


async def example_4_individual_agents():
    """
    Example 4: Use individual agents separately
    """
    print("\n" + "="*60)
    print("Example 4: Using Individual Agents")
    print("="*60)
    
    from backend.agents.task_analyzer import TaskAnalyzerAgent
    from backend.agents.quality_control import QualityControlAgent
    
    # Test Task Analyzer only
    print("\n🔍 Testing Task Analyzer Agent...")
    
    state = WorkflowState(
        task_id=generate_task_id(),
        user_request="Xóa text watermark"
    )
    
    analyzer = TaskAnalyzerAgent()
    state = await analyzer.process(state)
    
    print(f"   Detected: {state.task_type.value}")
    print(f"   Analysis: {state.intermediate_results.get('analysis', {})}")
    
    # Test Quality Control
    print("\n✅ Testing Quality Control Agent...")
    
    state.output_path = "path/to/output.jpg"  # Set output path
    
    qc = QualityControlAgent()
    state = await qc.process(state)
    
    checks = state.intermediate_results.get("quality_checks", {})
    print(f"   Quality Checks: {len(checks)} checks performed")
    for check_name, result in checks.items():
        status = "✅" if result["passed"] else "❌"
        print(f"   {status} {check_name}: {result['message']}")


async def example_5_error_handling():
    """
    Example 5: Error handling in workflow
    """
    print("\n" + "="*60)
    print("Example 5: Error Handling")
    print("="*60)
    
    # Create state with invalid input
    state = WorkflowState(
        task_id=generate_task_id(),
        user_request="Process image",
        task_type=TaskType.DEBLUR,
        input_path="nonexistent_file.jpg"  # Invalid path!
    )
    
    print(f"\n📝 Input: {state.input_path} (doesn't exist)")
    
    orchestrator = SimpleOrchestrator(use_llm_analyzer=False)
    
    print(f"\n🚀 Running workflow...")
    final_state = await orchestrator.run(state)
    
    # Check error handling
    print(f"\n❌ Status: {final_state.status.value}")
    
    errors = final_state.intermediate_results.get("errors", [])
    if errors:
        print(f"\n🔴 Errors captured:")
        for error in errors:
            print(f"   Agent: {error.get('agent', 'Unknown')}")
            print(f"   Error: {error.get('error', 'Unknown error')}")


async def example_6_full_workflow():
    """
    Example 6: Complete workflow from upload to result
    """
    print("\n" + "="*60)
    print("Example 6: Complete Workflow Simulation")
    print("="*60)
    
    # Simulate user uploading image with request
    print("\n👤 User uploads image with request:")
    print("   Request: 'Xóa object ở góc trái'")
    print("   File: photo.jpg")
    
    # Step 1: Create workflow state
    state = WorkflowState(
        task_id=generate_task_id(),
        user_request="Xóa object ở góc trái",
        input_path="uploads/photo.jpg"  # Simulated path
    )
    
    print(f"\n📦 Created task: {state.task_id}")
    
    # Step 2: Run through agents
    orchestrator = SimpleOrchestrator(use_llm_analyzer=True)
    
    print(f"\n🔄 Processing through agents:")
    print(f"   1️⃣ Task Analyzer - analyzing request...")
    print(f"   2️⃣ Image Worker - processing image...")
    print(f"   3️⃣ Quality Control - validating output...")
    
    # This would normally be async in background
    final_state = await orchestrator.run(state)
    
    # Step 3: Return result
    print(f"\n✨ Result:")
    print(f"   Status: {final_state.status.value}")
    print(f"   Progress: {final_state.progress}%")
    
    if final_state.status.value == "completed":
        print(f"   Output: {final_state.output_path}")
        print(f"   Model used: {final_state.intermediate_results.get('model_used', 'N/A')}")
    
    # Step 4: Show metadata
    print(f"\n📊 Metadata:")
    for key, value in final_state.intermediate_results.items():
        if key not in ["errors", "quality_checks"]:
            print(f"   {key}: {value}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("🤖 MULTI-AGENT SYSTEM EXAMPLES")
    print("="*60)
    print("\nThese examples demonstrate how to use the agent system.")
    print("Each example shows a different use case.\n")
    
    # Run examples
    # Note: Some examples require actual files and API keys
    # Uncomment the ones you want to run
    
    # asyncio.run(example_1_simple_workflow())
    # asyncio.run(example_2_with_llm_analyzer())
    asyncio.run(example_3_simple_rule_based())
    # asyncio.run(example_4_individual_agents())
    asyncio.run(example_5_error_handling())
    # asyncio.run(example_6_full_workflow())
    
    print("\n" + "="*60)
    print("✅ Examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
