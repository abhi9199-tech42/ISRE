"""Configuration system for ISRE pipeline.

Supports JSON, YAML, and environment variable configuration sources.
All configs use Pydantic BaseSettings for validation.
"""

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class CompressionConfig(BaseModel):
    """Configuration for semantic compression layer."""
    semantic_map_path: str | None = None
    fuzzy_match_threshold: int = 3
    enable_emoji: bool = True


class ConflictConfig(BaseModel):
    """Configuration for conflict detection."""
    custom_opposites: dict[str, str] = Field(default_factory=dict)
    enable_heuristic_detection: bool = True


class ReasoningConfig(BaseModel):
    """Configuration for reasoning engine."""
    oscillator_frequency: float = 1.0
    oscillator_bifurcation: float = 1.0
    max_oscillation_steps: int = 50
    oscillation_tolerance: float = 0.01
    intent_satisfaction_weight: float = 0.4
    constraint_compliance_weight: float = 0.4
    semantic_coherence_weight: float = 0.2


class KnowledgeConfig(BaseModel):
    """Configuration for knowledge integration."""
    backend: str = "memory"  # memory, sqlite, json
    sqlite_path: str = "knowledge.db"
    json_path: str = "knowledge.json"
    cache_size: int = 1000


class ReconstructionConfig(BaseModel):
    """Configuration for output reconstruction."""
    default_formats: list = Field(default_factory=lambda: ["text", "code", "action"])
    enable_markdown: bool = True


class PipelineConfig(BaseModel):
    """Main pipeline configuration."""
    memory_threshold_mb: float = 500.0
    compression: CompressionConfig = Field(default_factory=CompressionConfig)
    conflict: ConflictConfig = Field(default_factory=ConflictConfig)
    reasoning: ReasoningConfig = Field(default_factory=ReasoningConfig)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    reconstruction: ReconstructionConfig = Field(default_factory=ReconstructionConfig)


def load_config(config_path: str | None = None) -> PipelineConfig:
    """
    Load configuration from file or environment variables.

    Priority:
    1. config_path argument
    2. ISRE_CONFIG environment variable
    3. ./config.json in current directory
    4. Default configuration
    """
    config_data: dict[str, Any] = {}

    # Try loading from file
    paths_to_try = []
    if config_path:
        paths_to_try.append(Path(config_path))

    env_config = os.environ.get("ISRE_CONFIG")
    if env_config:
        paths_to_try.append(Path(env_config))

    paths_to_try.append(Path("config.json"))
    paths_to_try.append(Path("config.yaml"))

    for path in paths_to_try:
        if path.exists():
            if path.suffix == ".json":
                import json
                with open(path) as f:
                    config_data = json.load(f)
                break
            elif path.suffix in (".yaml", ".yml"):
                try:
                    import yaml
                    with open(path) as f:
                        config_data = yaml.safe_load(f)
                    break
                except ImportError:
                    pass

    # Override with environment variables
    env_prefix = "ISRE_"
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            parts = key[len(env_prefix):].lower().split("_")
            # Set nested config values
            current = config_data
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            # Try to parse as appropriate type
            if value.lower() in ("true", "false"):
                current[parts[-1]] = value.lower() == "true"
            elif value.replace(".", "").isdigit():
                current[parts[-1]] = float(value) if "." in value else int(value)
            else:
                current[parts[-1]] = value

    return PipelineConfig(**config_data) if config_data else PipelineConfig()


# Global config instance
_config: PipelineConfig | None = None


def get_config() -> PipelineConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: PipelineConfig):
    """Set the global configuration instance."""
    global _config
    _config = config
