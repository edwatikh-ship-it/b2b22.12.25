"""Parsing runs schemas. SSoT: api-contracts.yaml."""

from enum import Enum

from pydantic import BaseModel, Field


class ParsingRunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ParsingRunDTO(BaseModel):
    id: str = Field(..., description="Run UUID")
    requestId: int = Field(..., description="Source request ID")
    status: ParsingRunStatus
    keysCount: int = Field(..., description="Number of keys processed")
    createdAt: str  # ISO string для MVP


class ParsingRunListResponseDTO(BaseModel):
    items: list[ParsingRunDTO]
    limit: int
    offset: int
    total: int
