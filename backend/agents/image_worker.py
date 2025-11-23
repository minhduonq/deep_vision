"""
Image Worker Agent - Executes actual image processing tasks
"""
from pathlib import Path
from loguru import logger

from backend.core.state import WorkflowState, TaskType, TaskStatus
from backend.agents.base_agent import ToolAgent
from backend.models.replicate_wrapper import replicate_client


class ImageWorkerAgent(ToolAgent):
    """
    Worker agent that calls appropriate image processing models
    based on the task type determined by TaskAnalyzer
    """
    
    def __init__(self):
        super().__init__(
            name="Image Worker",
            tool_name="Replicate API"
        )
        self.client = replicate_client
        logger.info("Image Worker Agent initialized")
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """
        Process image based on task type
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with output_path set
        """
        try:
            # Update status
            state.status = TaskStatus.PROCESSING
            state.progress = 40
            
            # Validate input
            if not state.input_path:
                raise ValueError("No input path provided")
            
            input_path = Path(state.input_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            logger.info(f"Processing {state.task_type.value} for {input_path.name}")
            
            # Route to appropriate model
            output_path = None
            
            if state.task_type == TaskType.DEBLUR:
                output_path = await self._process_deblur(state, input_path)
                
            elif state.task_type == TaskType.INPAINT:
                output_path = await self._process_inpaint(state, input_path)
                
            elif state.task_type == TaskType.BEAUTY_ENHANCE:
                output_path = await self._process_beauty(state, input_path)
                
            elif state.task_type == TaskType.GENERATE:
                output_path = await self._process_generate(state)
                
            else:
                raise ValueError(f"Unknown task type: {state.task_type}")
            
            # Update state
            if output_path and Path(output_path).exists():
                state.output_path = str(output_path)
                state.progress = 70
                logger.info(f"Processing complete: {output_path}")
            else:
                raise FileNotFoundError("Output file was not created")
            
            return state
            
        except Exception as e:
            logger.error(f"Worker processing failed: {e}")
            state.status = TaskStatus.FAILED
            if "errors" not in state.intermediate_results:
                state.intermediate_results["errors"] = []
            state.intermediate_results["errors"].append({
                "agent": self.name,
                "error": str(e)
            })
            raise
    
    async def _process_deblur(self, state: WorkflowState, input_path: Path) -> Path:
        """Process deblur task"""
        logger.info(f"Calling deblur model for {input_path.name}")
        
        # Store model info
        state.intermediate_results["model_used"] = "SwinIR"
        state.intermediate_results["task_params"] = {"scale": 2}
        
        output_path = await self.client.deblur_image(input_path)
        return output_path
    
    async def _process_inpaint(self, state: WorkflowState, input_path: Path) -> Path:
        """Process inpaint task"""
        logger.info(f"Calling inpaint model for {input_path.name}")
        
        # Get mask path if provided
        mask_path = state.intermediate_results.get("mask_path")
        
        # Store model info
        state.intermediate_results["model_used"] = "LaMa"
        state.intermediate_results["task_params"] = {
            "has_mask": mask_path is not None
        }
        
        output_path = await self.client.inpaint_image(
            input_path,
            mask_path=Path(mask_path) if mask_path else None
        )
        return output_path
    
    async def _process_beauty(self, state: WorkflowState, input_path: Path) -> Path:
        """Process beauty enhancement task"""
        logger.info(f"Calling beauty enhancement model for {input_path.name}")
        
        # Store model info
        state.intermediate_results["model_used"] = "GFPGAN"
        state.intermediate_results["task_params"] = {
            "version": "v1.4",
            "scale": 2
        }
        
        output_path = await self.client.enhance_beauty(input_path)
        return output_path
    
    async def _process_generate(self, state: WorkflowState) -> Path:
        """Process image generation task"""
        prompt = state.user_request
        logger.info(f"Calling generation model with prompt: {prompt[:50]}...")
        
        # Get generation params from analysis
        params = state.intermediate_results.get("analysis", {}).get("suggested_params", {})
        
        # Store model info
        state.intermediate_results["model_used"] = "Stable Diffusion XL"
        state.intermediate_results["task_params"] = {
            "prompt": prompt,
            **params
        }
        
        output_path = await self.client.generate_image(prompt, **params)
        return output_path
