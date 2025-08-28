import os
import yaml
from pydantic import BaseModel, Field, ValidationError, ConfigDict
from typing import Optional, List, Dict, Any


class AppMeta(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    session_name: str
    debug: bool = False


class LlamaConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    base_url: str
    model_id: str
    instructions: str


class VectorDBConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: str
    provider: str
    embedding: str
    embedding_dimension: int
    chunk_size: int
    provider_vector_db_id: Optional[str] = None


class DatabaseConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    host: str = "localhost"
    port: int = 5432
    database: str = "mortgage_db"
    username: str = "postgres"
    password: str = "password"


class DocumentRequirementConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    document_type: str
    quantity: int
    description: str


class ValidationRuleConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    max_days_until_expiry: Optional[int] = None
    max_age_months: Optional[int] = None
    max_age_years: Optional[int] = None
    acceptable_alternatives: Optional[List[str]] = None
    required_fields: Optional[List[str]] = None


class PromptsConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    system_prompt: str
    processing_instructions: str
    validation_prompt_template: str
    document_template: str
    completion_messages: Dict[str, str]
    next_steps: Dict[str, List[str]]


class MortgageConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    max_document_size_mb: int = 10
    allowed_document_types: List[str] = [".pdf", ".jpg", ".jpeg", ".png"]
    validation_timeout_seconds: int = 30
    required_documents: Dict[str, List[DocumentRequirementConfig]]
    validation_rules: Dict[str, ValidationRuleConfig]
    prompts: PromptsConfig


class ResponseFormatConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    include_confidence_scores: bool = True
    include_processing_steps: bool = True
    include_agent_reasoning: bool = True
    max_reasoning_length: int = 1000
    timestamp_format: str = "ISO"


class AppConfig(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    app: AppMeta
    llama: LlamaConfig
    vector_db: VectorDBConfig
    database: DatabaseConfig
    mortgage: MortgageConfig
    response_format: ResponseFormatConfig

    @staticmethod
    def _env_override(cfg: "AppConfig") -> "AppConfig":
        """Override config values with environment variables if present."""
        cfg.app.session_name = os.getenv("SESSION_NAME", cfg.app.session_name)
        cfg.app.debug = os.getenv("DEBUG", "false").lower() == "true"

        cfg.llama.base_url = os.getenv("LLAMA_BASE_URL", cfg.llama.base_url).rstrip("/")
        cfg.llama.model_id = os.getenv("MODEL_ID", cfg.llama.model_id)

        cfg.database.host = os.getenv("DB_HOST", cfg.database.host)
        cfg.database.port = int(os.getenv("DB_PORT", str(cfg.database.port)))
        cfg.database.database = os.getenv("DB_NAME", cfg.database.database)
        cfg.database.username = os.getenv("DB_USER", cfg.database.username)
        cfg.database.password = os.getenv("DB_PASSWORD", cfg.database.password)

        return cfg

    @classmethod
    def load(cls, path: Optional[str] = None) -> "AppConfig":
        """Load configuration from YAML file, then apply environment variable overrides."""
        if path is None:
            possible_paths = [
                os.getenv("CONFIG_PATH"),
                os.path.join(os.getcwd(), "config.yaml"),
                os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml"),
                "config.yaml"
            ]
            
            path = None
            for p in possible_paths:
                if p and os.path.exists(p):
                    path = p
                    break
        
        if not path or not os.path.exists(path):
            raise RuntimeError(f"Config file not found. Tried locations: {possible_paths}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if not data:
            raise RuntimeError(f"Config file is empty at {path}")
        
        try:
            cfg = cls(**data)
        except ValidationError as e:
            raise RuntimeError(f"Invalid config at {path}: {e}")
        
        return cls._env_override(cfg)

    def get_required_documents(self, loan_type: str) -> List[DocumentRequirementConfig]:
        """Get required documents for a specific loan type."""
        return self.mortgage.required_documents.get(loan_type, [])
    
    def get_validation_rules(self, document_type: str) -> Optional[ValidationRuleConfig]:
        """Get validation rules for a specific document type."""
        return self.mortgage.validation_rules.get(document_type)
    
    def format_processing_prompt(self, **kwargs) -> str:
        """Format the main processing prompt with provided variables."""
        return self.mortgage.prompts.validation_prompt_template.format(**kwargs)
    
    def format_document_info(self, index: int, **kwargs) -> str:
        """Format document information using the template."""
        return self.mortgage.prompts.document_template.format(index=index, **kwargs)
