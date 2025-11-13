"""
Pydantic models for OpenAI API compatibility.
"""
from typing import Optional, Union

from pydantic import BaseModel, field_validator


class ChatCompletionRequest(BaseModel):
    messages: list[dict[str, str]]
    model: str
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 1024
    stream: Optional[bool] = False


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: dict[str, str]
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatCompletionResponseChoice]
    usage: Usage


class EmbeddingRequest(BaseModel):
    input: Union[str, list[str]]
    model: str

    @field_validator('input')
    @classmethod
    def validate_input_not_empty(cls, v):
        """Validate that input is not empty (string or list)."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError('Input string cannot be empty or whitespace-only')
        elif isinstance(v, list):
            if not v:
                raise ValueError('Input list cannot be empty')
            # Also validate that list items are not empty
            for item in v:
                if isinstance(item, str) and not item.strip():
                    raise ValueError('Input list cannot contain empty strings')
        return v


class Embedding(BaseModel):
    object: str
    embedding: list[float]
    index: int


class EmbeddingResponse(BaseModel):
    object: str
    data: list[Embedding]
    model: str
    usage: Usage
