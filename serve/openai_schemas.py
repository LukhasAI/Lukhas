"""
Pydantic models for OpenAI API compatibility.
"""
from typing import Optional, Union

from pydantic import BaseModel


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


class Embedding(BaseModel):
    object: str
    embedding: list[float]
    index: int


class EmbeddingResponse(BaseModel):
    object: str
    data: list[Embedding]
    model: str
    usage: Usage
