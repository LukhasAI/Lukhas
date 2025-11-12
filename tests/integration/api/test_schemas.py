import pytest
from pydantic import ValidationError

# Import the models to be tested
from serve.schemas import (
    DreamRequest,
    DreamResponse,
    GlyphFeedbackRequest,
    GlyphFeedbackResponse,
    TierAuthRequest,
    TierAuthResponse,
    PluginLoadRequest,
    PluginLoadResponse,
    MemoryDumpResponse,
    ModulatedChatRequest,
    ModulatedChatResponse,
)
from serve.openai_schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    Usage,
    EmbeddingRequest,
    Embedding,
    EmbeddingResponse,
)


class TestServeSchemas:
    def test_dream_request_valid(self):
        data = {"symbols": ["symbol1", "symbol2"]}
        req = DreamRequest(**data)
        assert req.symbols == data["symbols"]

    def test_dream_request_invalid_symbols_type(self):
        with pytest.raises(ValidationError):
            DreamRequest(symbols="not_a_list")

    def test_dream_request_empty_symbols(self):
        req = DreamRequest(symbols=[])
        assert req.symbols == []

    def test_dream_response_valid(self):
        data = {"dream": "a beautiful dream"}
        res = DreamResponse(**data)
        assert res.dream == data["dream"]
        assert res.model_dump_json() == '{"dream":"a beautiful dream"}'

    def test_glyph_feedback_request_valid(self):
        data = {"driftScore": 0.85}
        req = GlyphFeedbackRequest(**data)
        assert req.driftScore == data["driftScore"]

    def test_glyph_feedback_request_invalid_type(self):
        with pytest.raises(ValidationError):
            GlyphFeedbackRequest(driftScore="not_a_float")

    def test_glyph_feedback_response_valid(self):
        data = {"suggestions": ["suggestion1", "suggestion2"]}
        res = GlyphFeedbackResponse(**data)
        assert res.suggestions == data["suggestions"]
        assert res.model_dump_json() == '{"suggestions":["suggestion1","suggestion2"]}'

    def test_tier_auth_request_valid(self):
        data = {"token": "some_token"}
        req = TierAuthRequest(**data)
        assert req.token == data["token"]

    def test_tier_auth_response_valid(self):
        data = {"access_rights": ["read", "write"]}
        res = TierAuthResponse(**data)
        assert res.access_rights == data["access_rights"]
        assert res.model_dump_json() == '{"access_rights":["read","write"]}'

    def test_plugin_load_request_valid(self):
        data = {"symbols": ["plugin1", "plugin2"]}
        req = PluginLoadRequest(**data)
        assert req.symbols == data["symbols"]

    def test_plugin_load_response_valid(self):
        data = {"status": "loaded"}
        res = PluginLoadResponse(**data)
        assert res.status == data["status"]
        assert res.model_dump_json() == '{"status":"loaded"}'

    def test_memory_dump_response_valid(self):
        data = {"folds": [{"key1": "value1"}, {"key2": "value2"}]}
        res = MemoryDumpResponse(**data)
        assert res.folds == data["folds"]

    def test_modulated_chat_request_valid(self):
        data = {"prompt": "Hello, world!"}
        req = ModulatedChatRequest(**data)
        assert req.prompt == data["prompt"]
        assert req.context is None
        assert req.task is None

    def test_modulated_chat_request_with_optional_fields(self):
        data = {
            "prompt": "Hello, world!",
            "context": {"user": "test"},
            "task": "testing",
        }
        req = ModulatedChatRequest(**data)
        assert req.prompt == data["prompt"]
        assert req.context == data["context"]
        assert req.task == data["task"]

    def test_modulated_chat_response_valid(self):
        data = {
            "content": "This is a response.",
            "raw": {"some": "data"},
            "modulation": {"sentiment": "positive"},
            "metadata": {"source": "test"},
        }
        res = ModulatedChatResponse(**data)
        assert res.content == data["content"]
        assert res.raw == data["raw"]
        assert res.modulation == data["modulation"]
        assert res.metadata == data["metadata"]


class TestOpenAISchemas:
    def test_chat_completion_request_valid(self):
        data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-3.5-turbo",
        }
        req = ChatCompletionRequest(**data)
        assert req.model == data["model"]
        assert req.messages == data["messages"]
        assert req.temperature == 1.0
        assert req.max_tokens == 1024
        assert not req.stream

    def test_chat_completion_request_invalid_messages(self):
        with pytest.raises(ValidationError):
            ChatCompletionRequest(messages="invalid", model="gpt-3.5-turbo")

    def test_chat_completion_request_with_optional_fields(self):
        data = {
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-3.5-turbo",
            "temperature": 0.5,
            "max_tokens": 500,
            "stream": True,
        }
        req = ChatCompletionRequest(**data)
        assert req.temperature == data["temperature"]
        assert req.max_tokens == data["max_tokens"]
        assert req.stream

    def test_chat_completion_response_valid(self):
        data = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-3.5-turbo-0613",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Hello there!"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 9, "completion_tokens": 12, "total_tokens": 21},
        }
        res = ChatCompletionResponse(**data)
        assert res.id == data["id"]
        assert res.choices[0].message["content"] == "Hello there!"
        assert res.usage.total_tokens == 21

    def test_embedding_request_valid_string(self):
        data = {"input": "The quick brown fox jumped over the lazy dog", "model": "text-embedding-ada-002"}
        req = EmbeddingRequest(**data)
        assert req.input == data["input"]
        assert req.model == data["model"]

    def test_embedding_request_valid_list(self):
        data = {
            "input": ["The quick brown fox", "jumped over the lazy dog"],
            "model": "text-embedding-ada-002",
        }
        req = EmbeddingRequest(**data)
        assert req.input == data["input"]

    def test_embedding_request_invalid_input(self):
        with pytest.raises(ValidationError):
            EmbeddingRequest(input=123, model="text-embedding-ada-002")

    def test_embedding_response_valid(self):
        data = {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [
                        0.0023064255,
                        -0.009327292,
                        -0.0028842222,
                    ],
                    "index": 0,
                }
            ],
            "model": "text-embedding-ada-002-v2",
            "usage": {"prompt_tokens": 8, "completion_tokens": 0, "total_tokens": 8},
        }
        res = EmbeddingResponse(**data)
        assert res.object == data["object"]
        assert len(res.data) == 1
        assert res.data[0].index == 0
        assert len(res.data[0].embedding) == 3
        assert res.usage.total_tokens == 8

    def test_nested_model_validation(self):
        with pytest.raises(ValidationError):
            # Invalid choice structure in ChatCompletionResponse
            ChatCompletionResponse(
                id="123",
                object="chat.completion",
                created=123,
                model="gpt-4",
                choices=[{"index": "zero"}],
                usage={"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            )

    def test_dream_request_invalid_symbol_content(self):
        with pytest.raises(ValidationError):
            DreamRequest(symbols=[123])

    def test_glyph_feedback_response_empty(self):
        res = GlyphFeedbackResponse(suggestions=[])
        assert res.suggestions == []

    def test_tier_auth_response_empty(self):
        res = TierAuthResponse(access_rights=[])
        assert res.access_rights == []

    def test_memory_dump_response_empty(self):
        res = MemoryDumpResponse(folds=[])
        assert res.folds == []

    def test_modulated_chat_request_empty_prompt(self):
        req = ModulatedChatRequest(prompt="")
        assert req.prompt == ""

    def test_chat_completion_request_empty_messages(self):
        req = ChatCompletionRequest(messages=[], model="gpt-3.5-turbo")
        assert req.messages == []

    def test_embedding_request_invalid_list_content(self):
        with pytest.raises(ValidationError):
            EmbeddingRequest(input=[1, 2], model="text-embedding-ada-002")

    def test_embedding_response_empty_data(self):
        data = {
            "object": "list",
            "data": [],
            "model": "text-embedding-ada-002-v2",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
        res = EmbeddingResponse(**data)
        assert res.data == []

    def test_chat_completion_response_multiple_choices(self):
        data = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677652288,
            "model": "gpt-3.5-turbo-0613",
            "choices": [
                {"index": 0, "message": {"role": "assistant", "content": "Choice 1"}, "finish_reason": "stop"},
                {"index": 1, "message": {"role": "assistant", "content": "Choice 2"}, "finish_reason": "length"},
            ],
            "usage": {"prompt_tokens": 9, "completion_tokens": 24, "total_tokens": 33},
        }
        res = ChatCompletionResponse(**data)
        assert len(res.choices) == 2
        assert res.choices[1].message["content"] == "Choice 2"

    def test_usage_model_validation(self):
        with pytest.raises(ValidationError):
            Usage(prompt_tokens="a", completion_tokens=1, total_tokens=2)

    def test_chat_completion_choice_model_validation(self):
        with pytest.raises(ValidationError):
            ChatCompletionResponseChoice(index=0, message="invalid", finish_reason="stop")

    def test_embedding_model_validation(self):
        with pytest.raises(ValidationError):
            Embedding(object="embedding", embedding=[0.1, "b"], index=0)
