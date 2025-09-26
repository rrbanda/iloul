"""
Stage Logging Utilities

Specialized logging for database loading stages with progress tracking,
timing, and formatted output.
"""

import logging
import time
from typing import Dict, Any, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class LoadingTimer:
    """Timer for tracking loading performance."""
    
    def __init__(self):
        self.start_time = None
        self.stage_times = {}
        self.current_stage = None
    
    def start(self):
        """Start the overall timer."""
        self.start_time = time.time()
    
    def start_stage(self, stage_name: str):
        """Start timing a specific stage."""
        self.current_stage = stage_name
        self.stage_times[stage_name] = {"start": time.time()}
    
    def end_stage(self, stage_name: str):
        """End timing a specific stage."""
        if stage_name in self.stage_times:
            self.stage_times[stage_name]["end"] = time.time()
            self.stage_times[stage_name]["duration"] = (
                self.stage_times[stage_name]["end"] - 
                self.stage_times[stage_name]["start"]
            )
    
    def get_total_time(self) -> float:
        """Get total elapsed time."""
        if self.start_time:
            return time.time() - self.start_time
        return 0.0
    
    def get_stage_time(self, stage_name: str) -> float:
        """Get time for a specific stage."""
        return self.stage_times.get(stage_name, {}).get("duration", 0.0)


class StageLogger:
    """Specialized logger for database loading stages."""
    
    def __init__(self, timer: LoadingTimer = None):
        self.timer = timer or LoadingTimer()
        self.logger = logging.getLogger(__name__)
    
    def log_loading_start(self):
        """Log the start of the loading process."""
        self.timer.start()
        self.logger.info("🏦 Starting mortgage knowledge graph data loading...")
    
    def log_stage_start(self, stage_name: str, description: str, emoji: str):
        """Log the start of a specific stage."""
        self.timer.start_stage(stage_name)
        self.logger.info(f"{emoji} Stage: {description}")
    
    def log_stage_success(self, stage_name: str, details: Dict[str, Any] = None):
        """Log successful completion of a stage."""
        self.timer.end_stage(stage_name)
        stage_time = self.timer.get_stage_time(stage_name)
        
        message = f" {stage_name} completed"
        if details:
            if "nodes_created" in details:
                message += f": {details['nodes_created']} nodes created"
            if "relationships_created" in details:
                message += f", {details['relationships_created']} relationships created"
        
        message += f" ({stage_time:.2f}s)"
        self.logger.info(message)
    
    def log_stage_failure(self, stage_name: str, error: str):
        """Log failure of a stage."""
        self.timer.end_stage(stage_name)
        self.logger.error(f" {stage_name} failed: {error}")
    
    def log_completion_summary(self, results: Dict[str, Any]):
        """Log comprehensive completion summary."""
        total_time = self.timer.get_total_time()
        
        self.logger.info("🎉 Mortgage knowledge graph loading completed successfully!")
        self.logger.info("=" * 50)
        self.logger.info("MORTGAGE KNOWLEDGE GRAPH LOADING COMPLETED")
        self.logger.info("=" * 50)
        self.logger.info(f" Stages Completed: {len(results.get('stages_completed', []))}")
        
        if results.get("total_nodes_created"):
            self.logger.info(f"📊 Total Nodes Created: {results['total_nodes_created']}")
        
        if results.get("total_relationships_created"):
            self.logger.info(f"🔗 Total Relationships Created: {results['total_relationships_created']}")
        
        self.logger.info(f"⏱️ Total Loading Time: {total_time:.2f} seconds")
        self.logger.info("=" * 50)
        self.logger.info("Knowledge graph is ready for mortgage processing agents!")
    
    def log_failure_summary(self, results: Dict[str, Any]):
        """Log failure summary with troubleshooting info."""
        total_time = self.timer.get_total_time()
        
        self.logger.error(" LOADING FAILED")
        self.logger.error("=" * 40)
        
        completed = results.get("stages_completed", [])
        failed = results.get("stages_failed", [])
        
        if completed:
            self.logger.info(f"⏹️ Stages Completed: {len(completed)}")
            for stage in completed:
                self.logger.info(f"    {stage}")
        
        if failed:
            self.logger.error(f" Stages Failed: {len(failed)}")
            for stage in failed:
                self.logger.error(f"    {stage}")
        
        errors = results.get("errors", [])
        if errors:
            self.logger.error("\n🔧 Errors:")
            for error in errors:
                self.logger.error(f"   • {error}")
        
        self.logger.error("\n💡 Troubleshooting:")
        self.logger.error("   • Check Neo4j connection")
        self.logger.error("   • Verify database permissions") 
        self.logger.error("   • Review error logs above")
        self.logger.error("   • Try running with --verbose flag")
    
    @contextmanager
    def stage_context(self, stage_name: str, description: str, emoji: str):
        """Context manager for stage logging."""
        try:
            self.log_stage_start(stage_name, description, emoji)
            yield
            self.log_stage_success(stage_name)
        except Exception as e:
            self.log_stage_failure(stage_name, str(e))
            raise
