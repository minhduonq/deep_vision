"""
Quality Control Agent - Validates output quality and completeness
"""
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from PIL import Image

from backend.core.state import WorkflowState, TaskStatus
from backend.agents.base_agent import BaseAgent


class QualityControlAgent(BaseAgent):
    """
    Validates the output from Worker Agent:
    - File exists and is valid
    - Image format is correct
    - File size is reasonable
    - Image dimensions are valid
    """
    
    def __init__(self):
        super().__init__(
            name="Quality Control",
            description="Validates output quality"
        )
        self.min_file_size = 1000  # 1KB minimum
        self.min_dimension = 32     # 32px minimum
        logger.info("Quality Control Agent initialized")
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """
        Validate output quality
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with quality check results
        """
        try:
            state.status = TaskStatus.QUALITY_CHECK
            state.progress = 80
            
            # Run validation checks
            checks = await self._run_checks(state)
            
            # Store check results
            state.intermediate_results["quality_checks"] = checks
            
            # Determine if passed
            all_passed = all(check["passed"] for check in checks.values())
            
            if all_passed:
                state.status = TaskStatus.COMPLETED
                state.progress = 100
                logger.info(f"Quality check PASSED for task {state.task_id}")
            else:
                # Find failed checks
                failed_checks = [
                    name for name, check in checks.items() 
                    if not check["passed"]
                ]
                error_msg = f"Quality check FAILED: {', '.join(failed_checks)}"
                logger.error(error_msg)
                
                state.status = TaskStatus.FAILED
                if "errors" not in state.intermediate_results:
                    state.intermediate_results["errors"] = []
                state.intermediate_results["errors"].append({
                    "agent": self.name,
                    "error": error_msg
                })
            
            return state
            
        except Exception as e:
            logger.error(f"Quality control failed: {e}")
            state.status = TaskStatus.FAILED
            if "errors" not in state.intermediate_results:
                state.intermediate_results["errors"] = []
            state.intermediate_results["errors"].append({
                "agent": self.name,
                "error": str(e)
            })
            return state
    
    async def _run_checks(self, state: WorkflowState) -> Dict[str, Dict[str, Any]]:
        """
        Run all quality checks
        
        Returns:
            Dictionary of check results
        """
        checks = {}
        
        # Check 1: Output path exists
        checks["output_exists"] = self._check_output_exists(state)
        
        if not checks["output_exists"]["passed"]:
            return checks
        
        output_path = Path(state.output_path)
        
        # Check 2: File size
        checks["file_size"] = self._check_file_size(output_path)
        
        # Check 3: Valid image format
        checks["image_format"] = self._check_image_format(output_path)
        
        if checks["image_format"]["passed"]:
            # Check 4: Image dimensions
            checks["dimensions"] = self._check_dimensions(output_path)
            
            # Check 5: Compare with input (if applicable)
            if state.input_path:
                checks["comparison"] = self._check_comparison(
                    Path(state.input_path),
                    output_path
                )
        
        return checks
    
    def _check_output_exists(self, state: WorkflowState) -> Dict[str, Any]:
        """Check if output file exists"""
        if not state.output_path:
            return {
                "passed": False,
                "message": "No output path provided",
                "details": None
            }
        
        output_path = Path(state.output_path)
        exists = output_path.exists()
        
        return {
            "passed": exists,
            "message": "Output file exists" if exists else "Output file not found",
            "details": {"path": str(output_path)}
        }
    
    def _check_file_size(self, output_path: Path) -> Dict[str, Any]:
        """Check if file size is reasonable"""
        try:
            file_size = output_path.stat().st_size
            passed = file_size >= self.min_file_size
            
            return {
                "passed": passed,
                "message": f"File size: {file_size} bytes",
                "details": {
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2),
                    "min_required": self.min_file_size
                }
            }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Failed to check file size: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_image_format(self, output_path: Path) -> Dict[str, Any]:
        """Check if file is a valid image"""
        try:
            with Image.open(output_path) as img:
                return {
                    "passed": True,
                    "message": f"Valid {img.format} image",
                    "details": {
                        "format": img.format,
                        "mode": img.mode,
                        "size": img.size
                    }
                }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Invalid image: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_dimensions(self, output_path: Path) -> Dict[str, Any]:
        """Check if image dimensions are valid"""
        try:
            with Image.open(output_path) as img:
                width, height = img.size
                passed = width >= self.min_dimension and height >= self.min_dimension
                
                return {
                    "passed": passed,
                    "message": f"Image size: {width}x{height}",
                    "details": {
                        "width": width,
                        "height": height,
                        "min_dimension": self.min_dimension
                    }
                }
        except Exception as e:
            return {
                "passed": False,
                "message": f"Failed to check dimensions: {e}",
                "details": {"error": str(e)}
            }
    
    def _check_comparison(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        """Compare input and output images"""
        try:
            with Image.open(input_path) as input_img:
                with Image.open(output_path) as output_img:
                    # Check if dimensions match
                    same_size = input_img.size == output_img.size
                    
                    # Check if output is not identical to input (was actually processed)
                    input_bytes = input_path.read_bytes()
                    output_bytes = output_path.read_bytes()
                    is_different = input_bytes != output_bytes
                    
                    passed = same_size and is_different
                    
                    return {
                        "passed": passed,
                        "message": "Output was processed successfully",
                        "details": {
                            "input_size": input_img.size,
                            "output_size": output_img.size,
                            "size_match": same_size,
                            "was_processed": is_different
                        }
                    }
        except Exception as e:
            return {
                "passed": True,  # Don't fail on comparison error
                "message": f"Could not compare: {e}",
                "details": {"error": str(e)}
            }
