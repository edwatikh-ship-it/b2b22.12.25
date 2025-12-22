"""
Schemas for parsing run logs.
SSoT: api-contracts.yaml
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ParsingRunEventLevel(str, Enum):
    """Log event level."""
    info = "info"
    warn = "warn"
    error = "error"


class ParsingRunEventDTO(BaseModel):
    """Single log event for a parsing run."""
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    level: ParsingRunEventLevel
    message: str
    context: dict | None = None


class ParsingRunLogResponseDTO(BaseModel):
    """Response with parsing run logs."""
    model_config = ConfigDict(from_attributes=True)

    runId: str
    events: list[ParsingRunEventDTO]
