"""
Loader Configuration

Configuration constants and settings for the data loading process.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class StageConfig:
    """Configuration for a single loading stage."""
    name: str
    description: str
    emoji: str
    required: bool = True
    depends_on: List[str] = None

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


class LoaderConfig:
    """Main configuration for the data loading process."""
    
    # Loading stages in order
    STAGES = [
        StageConfig(
            name="Database Setup",
            description="Database Setup and Verification", 
            emoji="📋",
            required=True
        ),
        StageConfig(
            name="Data Clearing",
            description="Clearing Existing Data",
            emoji="🗑️",
            required=True,
            depends_on=["Database Setup"]
        ),
        StageConfig(
            name="Core Data Loading", 
            description="Loading Core Mortgage Data",
            emoji="📊",
            required=True,
            depends_on=["Data Clearing"]
        ),
        StageConfig(
            name="Business Rules Loading",
            description="Loading Business Rules",
            emoji="⚖️",
            required=True,
            depends_on=["Core Data Loading"]
        ),
        StageConfig(
            name="Relationship Creation",
            description="Creating Graph Relationships", 
            emoji="🔗",
            required=True,
            depends_on=["Business Rules Loading"]
        ),
        StageConfig(
            name="Data Verification",
            description="Data Integrity Verification",
            emoji="",
            required=True,
            depends_on=["Relationship Creation"]
        )
    ]
    
    # Data integrity requirements
    MIN_NODE_COUNTS = {
        "loan_programs": 3,
        "business_rules": 1,
        "qm_rules": 5,
        "fannie_mae_rules": 5, 
        "property_risk_rules": 5
    }
    
    MIN_RELATIONSHIP_COUNT = 10
    
    # Performance settings
    BATCH_SIZE = 100
    TIMEOUT_SECONDS = 300
    
    # Logging settings
    LOG_LEVEL = "INFO"
    DETAILED_LOGGING = True
    
    @classmethod
    def get_stage_by_name(cls, name: str) -> StageConfig:
        """Get stage configuration by name."""
        for stage in cls.STAGES:
            if stage.name == name:
                return stage
        raise ValueError(f"Unknown stage: {name}")
    
    @classmethod
    def get_stage_names(cls) -> List[str]:
        """Get list of all stage names."""
        return [stage.name for stage in cls.STAGES]
