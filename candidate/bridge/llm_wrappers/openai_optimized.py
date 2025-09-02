#!/usr/bin/env python3
"""
Optimized OpenAI API Wrapper for LUKHAS
========================================
Implements caching, rate limiting, and intelligent retries.
Based on GPT5 audit recommendations.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import openai
from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategies"""

    NONE = "none"  # No caching
    EXACT_MATCH = "exact_match"  # Cache exact prompt matches
    SEMANTIC = "semantic"  # Cache semantically similar prompts
    EMBEDDING = "embedding"  # Cache by embedding similarity


@dataclass
class CacheEntry:
    """Cache entry for API responses"""

    key: str
    prompt: str
    response: dict[str, Any]
    timestamp: float
    ttl: float  # Time to live in seconds
    hits: int = 0
    model: str = ""
    tokens_saved: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return time.time() - self.timestamp > self.ttl


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""

    requests_per_minute: int = 60
    requests_per_hour: int = 3000
    tokens_per_minute: int = 90000
    tokens_per_hour: int = 2000000

    # Burst allowance
    burst_multiplier: float = 1.5

    # Backoff strategy
    initial_backoff_ms: int = 1000
    max_backoff_ms: int = 60000
    backoff_multiplier: float = 2.0

    # Model-specific limits
    model_limits: dict[str, dict[str, int]] = field(
        default_factory=lambda: {
            "gpt-4": {"rpm": 40, "tpm": 40000},
            "gpt-3.5-turbo": {"rpm": 90, "tpm": 90000},
            "text-embedding-ada-002": {"rpm": 1000, "tpm": 1000000},
        }
    )


class OptimizedOpenAIClient:
    """
    Optimized OpenAI client with caching and rate limiting.
    Reduces costs and improves performance.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_strategy: CacheStrategy = CacheStrategy.EXACT_MATCH,
        cache_ttl: float = 3600,  # 1 hour default
        cache_size: int = 1000,
        rate_config: Optional[RateLimitConfig] = None,
        cache_dir: Optional[Path] = None,
    ):
        """
        Initialize optimized OpenAI client.

        Args:
            api_key: OpenAI API key
            cache_strategy: Caching strategy to use
            cache_ttl: Cache time-to-live in seconds
            cache_size: Maximum cache entries
            rate_config: Rate limiting configuration
            cache_dir: Directory for persistent cache
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

        # Caching
        self.cache_strategy = cache_strategy
        self.cache_ttl = cache_ttl
        self.cache_size = cache_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.cache_dir = cache_dir or Path("data/openai_cache")

        # Rate limiting
        self.rate_config = rate_config or RateLimitConfig()
        self.request_history: deque = deque(maxlen=10000)
        self.token_history: deque = deque(maxlen=10000)
        self.current_backoff = 0

        # Statistics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "tokens_used": 0,
            "tokens_saved": 0,
            "errors": 0,
            "rate_limited": 0,
        }

        # Load persistent cache if exists
        if self.cache_strategy != CacheStrategy.NONE:
            self._load_cache()

        logger.info(f"Optimized OpenAI client initialized with {cache_strategy.value} caching")

    def _generate_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate cache key for a request"""
        if self.cache_strategy == CacheStrategy.EXACT_MATCH:
            # Hash the exact prompt and parameters
            key_data = {
                "prompt": prompt,
                "model": model,
                **{k: v for k, v in kwargs.items() if k not in ["stream", "n"]},
            }
            key_str = json.dumps(key_data, sort_keys=True)
            return hashlib.sha256(key_str.encode()).hexdigest()

        elif self.cache_strategy == CacheStrategy.SEMANTIC:
            # Simplified semantic key (would need embeddings for real implementation)
            # For now, normalize and hash
            normalized = " ".join(prompt.lower().split())
            key_data = {"normalized": normalized, "model": model}
            key_str = json.dumps(key_data, sort_keys=True)
            return hashlib.sha256(key_str.encode()).hexdigest()

        else:
            # No caching
            return ""

    def _check_cache(self, key: str) -> Optional[CacheEntry]:
        """Check if response is cached"""
        if not key or self.cache_strategy == CacheStrategy.NONE:
            return None

        entry = self.cache.get(key)
        if entry and not entry.is_expired():
            # Move to end (LRU)
            self.cache.move_to_end(key)
            entry.hits += 1
            self.stats["cache_hits"] += 1
            self.stats["tokens_saved"] += entry.tokens_saved
            logger.debug(f"Cache hit: {key[:8]}... (hits: {entry.hits})")
            return entry

        # Remove expired entry
        if entry:
            del self.cache[key]

        self.stats["cache_misses"] += 1
        return None

    def _add_to_cache(
        self,
        key: str,
        prompt: str,
        response: dict[str, Any],
        model: str,
        tokens_used: int,
    ):
        """Add response to cache"""
        if not key or self.cache_strategy == CacheStrategy.NONE:
            return

        # Enforce cache size limit
        while len(self.cache) >= self.cache_size:
            # Remove oldest entry
            self.cache.popitem(last=False)

        entry = CacheEntry(
            key=key,
            prompt=prompt,
            response=response,
            timestamp=time.time(),
            ttl=self.cache_ttl,
            model=model,
            tokens_saved=tokens_used,
        )

        self.cache[key] = entry
        logger.debug(f"Added to cache: {key[:8]}... (size: {len(self.cache)})")

    async def _check_rate_limits(self, model: str, estimated_tokens: int) -> bool:
        """
        Check if request would exceed rate limits.

        Returns:
            True if request can proceed, False if should wait
        """
        current_time = time.time()

        # Get model-specific limits
        model_type = model.split("-")[0] + "-" + model.split("-")[1] if "-" in model else model
        limits = self.rate_config.model_limits.get(
            model_type,
            {
                "rpm": self.rate_config.requests_per_minute,
                "tpm": self.rate_config.tokens_per_minute,
            },
        )

        # Check requests per minute
        recent_requests = [t for t in self.request_history if current_time - t < 60]
        if len(recent_requests) >= limits["rpm"]:
            self.stats["rate_limited"] += 1
            wait_time = 60 - (current_time - recent_requests[0])
            logger.warning(f"Rate limit: {len(recent_requests)} requests in last minute, waiting {wait_time:.1f}s")
            return False

        # Check tokens per minute
        recent_tokens = [(t, tokens) for t, tokens in self.token_history if current_time - t < 60]
        total_recent_tokens = sum(tokens for _, tokens in recent_tokens)
        if total_recent_tokens + estimated_tokens > limits["tpm"]:
            self.stats["rate_limited"] += 1
            logger.warning(f"Token limit: {total_recent_tokens} tokens in last minute")
            return False

        return True

    async def _wait_for_rate_limit(self, model: str, estimated_tokens: int):
        """Wait until rate limits allow request"""
        while not await self._check_rate_limits(model, estimated_tokens):
            # Exponential backoff
            if self.current_backoff == 0:
                self.current_backoff = self.rate_config.initial_backoff_ms
            else:
                self.current_backoff = min(
                    self.current_backoff * self.rate_config.backoff_multiplier,
                    self.rate_config.max_backoff_ms,
                )

            wait_seconds = self.current_backoff / 1000
            logger.info(f"Rate limited, waiting {wait_seconds:.1f}s")
            await asyncio.sleep(wait_seconds)

        # Reset backoff on success
        self.current_backoff = 0

    def _estimate_tokens(self, prompt: str, max_tokens: Optional[int] = None) -> int:
        """Estimate token count for a prompt"""
        # Simple estimation: ~4 characters per token
        prompt_tokens = len(prompt) // 4
        response_tokens = max_tokens or 500  # Default estimate
        return prompt_tokens + response_tokens

    async def complete(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        use_cache: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Complete a prompt with caching and rate limiting.

        Args:
            prompt: Input prompt
            model: Model to use
            max_tokens: Maximum response tokens
            temperature: Response randomness
            use_cache: Whether to use cache
            **kwargs: Additional OpenAI parameters

        Returns:
            API response dictionary
        """
        self.stats["total_requests"] += 1

        # Check cache
        if use_cache:
            cache_key = self._generate_cache_key(prompt, model, temperature=temperature, **kwargs)
            cached = self._check_cache(cache_key)
            if cached:
                return cached.response
        else:
            cache_key = ""

        # Estimate tokens and check rate limits
        estimated_tokens = self._estimate_tokens(prompt, max_tokens)
        await self._wait_for_rate_limit(model, estimated_tokens)

        # Make API call
        try:
            messages = [{"role": "user", "content": prompt}]

            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

            # Convert to dict
            response_dict = response.model_dump()

            # Track usage
            tokens_used = response.usage.total_tokens if hasattr(response, "usage") else estimated_tokens
            self.request_history.append(time.time())
            self.token_history.append((time.time(), tokens_used))
            self.stats["tokens_used"] += tokens_used

            # Cache response
            if use_cache and cache_key:
                self._add_to_cache(cache_key, prompt, response_dict, model, tokens_used)

            return response_dict

        except openai.RateLimitError as e:
            self.stats["rate_limited"] += 1
            logger.error(f"Rate limit error: {e}")
            # Retry with backoff
            await asyncio.sleep(self.rate_config.initial_backoff_ms / 1000)
            return await self.complete(prompt, model, max_tokens, temperature, use_cache, **kwargs)

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"API error: {e}")
            raise

    async def embed(self, text: str, model: str = "text-embedding-ada-002", use_cache: bool = True) -> list[float]:
        """
        Generate embeddings with caching.

        Args:
            text: Text to embed
            model: Embedding model
            use_cache: Whether to use cache

        Returns:
            Embedding vector
        """
        # Check cache
        if use_cache:
            cache_key = self._generate_cache_key(text, model)
            cached = self._check_cache(cache_key)
            if cached:
                return cached.response["data"][0]["embedding"]
        else:
            cache_key = ""

        # Check rate limits
        estimated_tokens = len(text) // 4
        await self._wait_for_rate_limit(model, estimated_tokens)

        # Make API call
        try:
            response = await self.async_client.embeddings.create(model=model, input=text)

            response_dict = response.model_dump()
            embedding = response.data[0].embedding

            # Track usage
            self.request_history.append(time.time())
            self.token_history.append((time.time(), estimated_tokens))
            self.stats["tokens_used"] += estimated_tokens

            # Cache response
            if use_cache and cache_key:
                self._add_to_cache(cache_key, text, response_dict, model, estimated_tokens)

            return embedding

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Embedding error: {e}")
            raise

    def _save_cache(self):
        """Save cache to disk"""
        if self.cache_strategy == CacheStrategy.NONE:
            return

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = self.cache_dir / "cache.json"

        # Convert cache to serializable format
        cache_data = {
            key: {
                "prompt": entry.prompt,
                "response": entry.response,
                "timestamp": entry.timestamp,
                "ttl": entry.ttl,
                "hits": entry.hits,
                "model": entry.model,
                "tokens_saved": entry.tokens_saved,
            }
            for key, entry in self.cache.items()
        }

        with open(cache_file, "w") as f:
            json.dump(cache_data, f)

        logger.info(f"Saved {len(self.cache)} cache entries to disk")

    def _load_cache(self):
        """Load cache from disk"""
        cache_file = self.cache_dir / "cache.json"
        if not cache_file.exists():
            return

        try:
            with open(cache_file) as f:
                cache_data = json.load(f)

            # Rebuild cache
            for key, data in cache_data.items():
                entry = CacheEntry(
                    key=key,
                    prompt=data["prompt"],
                    response=data["response"],
                    timestamp=data["timestamp"],
                    ttl=data["ttl"],
                    hits=data.get("hits", 0),
                    model=data.get("model", ""),
                    tokens_saved=data.get("tokens_saved", 0),
                )

                # Only add non-expired entries
                if not entry.is_expired():
                    self.cache[key] = entry

            logger.info(f"Loaded {len(self.cache)} cache entries from disk")

        except Exception as e:
            logger.error(f"Failed to load cache: {e}")

    def get_statistics(self) -> dict[str, Any]:
        """Get client statistics"""
        cache_hit_rate = (
            self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"])
            if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
            else 0
        )

        return {
            "total_requests": self.stats["total_requests"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self.cache),
            "tokens_used": self.stats["tokens_used"],
            "tokens_saved": self.stats["tokens_saved"],
            "cost_saved": self.stats["tokens_saved"] * 0.002 / 1000,  # Rough estimate
            "errors": self.stats["errors"],
            "rate_limited": self.stats["rate_limited"],
        }

    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("Cache cleared")

    def __del__(self):
        """Save cache on cleanup"""
        if hasattr(self, "cache") and self.cache:
            self._save_cache()


class BatchProcessor:
    """Process multiple requests efficiently"""

    def __init__(self, client: OptimizedOpenAIClient):
        self.client = client

    async def process_batch(
        self,
        prompts: list[str],
        model: str = "gpt-3.5-turbo",
        max_concurrent: int = 5,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        Process multiple prompts concurrently with rate limiting.

        Args:
            prompts: List of prompts to process
            model: Model to use
            max_concurrent: Maximum concurrent requests
            **kwargs: Additional parameters

        Returns:
            List of responses
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_one(prompt: str) -> dict[str, Any]:
            async with semaphore:
                return await self.client.complete(prompt, model, **kwargs)

        tasks = [process_one(prompt) for prompt in prompts]
        responses = await asyncio.gather(*tasks)

        return responses


# Example usage
if __name__ == "__main__":
    import asyncio
    import os

    async def demo():
        # Create optimized client
        client = OptimizedOpenAIClient(
            cache_strategy=CacheStrategy.EXACT_MATCH,
            cache_ttl=3600,
            rate_config=RateLimitConfig(requests_per_minute=20),
        )

        print("🚀 Optimized OpenAI Client Demo")
        print("=" * 40)

        # First request (cache miss)
        response1 = await client.complete("What is machine learning?", model="gpt-3.5-turbo", max_tokens=100)
        print(f"Response 1: {response1['choices'][0]['message']['content'][:100]}...")

        # Same request (cache hit)
        response2 = await client.complete("What is machine learning?", model="gpt-3.5-turbo", max_tokens=100)
        print(f"Response 2 (cached): {response2['choices'][0]['message']['content'][:100]}...")

        # Get statistics
        stats = client.get_statistics()
        print("\n📊 Statistics:")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Cache hits: {stats['cache_hits']}")
        print(f"  Cache hit rate: {stats['cache_hit_rate']:.1%}")
        print(f"  Tokens saved: {stats['tokens_saved']}")
        print(f"  Cost saved: ${stats['cost_saved']:.4f}")

        # Batch processing
        batch_processor = BatchProcessor(client)
        prompts = ["What is Python?", "What is JavaScript?", "What is Rust?"]

        print("\n🔄 Processing batch...")
        responses = await batch_processor.process_batch(prompts, max_concurrent=2, max_tokens=50)

        for i, response in enumerate(responses):
            content = response["choices"][0]["message"]["content"]
            print(f"  {i + 1}. {content[:50]}...")

        # Final stats
        final_stats = client.get_statistics()
        print("\n📊 Final Statistics:")
        print(f"  Total requests: {final_stats['total_requests']}")
        print(f"  Cache size: {final_stats['cache_size']}")
        print(f"  Tokens used: {final_stats['tokens_used']}")

    # Run demo
    asyncio.run(demo())
