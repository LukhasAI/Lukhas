"""
Pydantic models for OpenAI API compatibility.
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class ChatCompletionRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 1024
    stream: Optional[bool] = False


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: Dict[str, str]
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
    choices: List[ChatCompletionResponseChoice]
    usage: Usage


class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str


class Embedding(BaseModel):
    object: str
    embedding: List[float]
    index: int


class EmbeddingResponse(BaseModel):
    object: str
    data: List[Embedding]
    model: str
    usage: Usage
