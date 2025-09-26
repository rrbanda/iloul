"""
Stage Orchestrator

Coordinates the execution of all loading stages in the correct order
with proper error handling and progress tracking.
"""

import logging
from typing import Dict, Any, List
from database.setup import get_connection
from ..utils import StageLogger, LoadingTimer, LoaderConfig
from .database_setup_stage import DatabaseSetupStage
from .data_clearing_stage import DataClearingStage
from .core_data_stage import CoreDataStage
from .business_rules_stage import BusinessRulesStage
from .relationships_stage import RelationshipsStage
from .verification_stage import VerificationStage

logger = logging.getLogger(__name__)


class StageOrchestrator:
    """Orchestrates the execution of all loading stages."""
    
    def __init__(self):
        self.config = LoaderConfig()
        self.timer = LoadingTimer()
        self.stage_logger = StageLogger(self.timer)
        
        # Initialize all stages
        self.stages = {
            "Database Setup": DatabaseSetupStage(),
            "Data Clearing": DataClearingStage(),
            "Core Data Loading": CoreDataStage(),
            "Business Rules Loading": BusinessRulesStage(),
            "Relationship Creation": RelationshipsStage(),
            "Data Verification": VerificationStage()
        }
    
    def execute_all_stages(self) -> Dict[str, Any]:
        """
        Execute all loading stages in the correct order.
        
        Returns:
            dict: Comprehensive results from all stages
        """
        self.stage_logger.log_loading_start()
        
        results = {
            "success": False,
            "stages_completed": [],
            "stages_failed": [],
            "errors": [],
            "total_nodes_created": 0,
            "total_relationships_created": 0,
            "stage_results": {}
        }
        
        connection = None
        
        try:
            # Get database connection
            connection = get_connection()
            if not connection:
                raise Exception("Failed to establish database connection")
            
            # Execute each stage in order
            for stage_config in self.config.STAGES:
                stage_name = stage_config.name
                stage = self.stages[stage_name]
                
                logger.info(f"{stage_config.emoji} Stage {len(results['stages_completed']) + 1}: {stage_config.description}")
                
                try:
                    # Execute the stage
                    stage_result = stage.execute(connection)
                    
                    # Track results
                    results["stage_results"][stage_name] = stage_result
                    
                    if stage_result.get("success", False):
                        results["stages_completed"].append(stage_name)
                        
                        # Accumulate statistics
                        nodes_created = stage_result.get("nodes_created", 0)
                        relationships_created = stage_result.get("relationships_created", 0)
                        
                        results["total_nodes_created"] += nodes_created
                        results["total_relationships_created"] += relationships_created
                        
                        self.stage_logger.log_stage_success(
                            stage_name, 
                            {
                                "nodes_created": nodes_created,
                                "relationships_created": relationships_created
                            }
                        )
                    else:
                        # Stage failed
                        results["stages_failed"].append(stage_name)
                        stage_errors = stage_result.get("errors", [])
                        results["errors"].extend(stage_errors)
                        
                        self.stage_logger.log_stage_failure(stage_name, "; ".join(stage_errors))
                        
                        # Stop on critical stage failure
                        if stage_config.required:
                            break
                
                except Exception as e:
                    results["stages_failed"].append(stage_name)
                    error_msg = f"{stage_name} execution error: {str(e)}"
                    results["errors"].append(error_msg)
                    self.stage_logger.log_stage_failure(stage_name, str(e))
                    
                    # Stop on critical stage failure
                    if stage_config.required:
                        break
            
            # Determine overall success
            required_stages = [s.name for s in self.config.STAGES if s.required]
            completed_required = set(results["stages_completed"]) & set(required_stages)
            results["success"] = len(completed_required) == len(required_stages)
            
            # Log completion
            if results["success"]:
                self.stage_logger.log_completion_summary(results)
            else:
                self.stage_logger.log_failure_summary(results)
            
            return results
            
        except Exception as e:
            error_msg = f"Orchestrator error: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(f" {error_msg}")
            self.stage_logger.log_failure_summary(results)
            return results
    
    def get_stage_dependencies(self, stage_name: str) -> List[str]:
        """Get the dependencies for a specific stage."""
        stage_config = self.config.get_stage_by_name(stage_name)
        return stage_config.depends_on
    
    def validate_stage_order(self) -> bool:
        """Validate that stage dependencies are satisfied by the execution order."""
        completed = set()
        
        for stage_config in self.config.STAGES:
            # Check if all dependencies are already completed
            for dependency in stage_config.depends_on:
                if dependency not in completed:
                    logger.error(f"Stage '{stage_config.name}' depends on '{dependency}' which hasn't been completed yet")
                    return False
            
            completed.add(stage_config.name)
        
        return True
