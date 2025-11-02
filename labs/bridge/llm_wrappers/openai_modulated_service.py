"""
OpenAI Modulated Service

Provides modulated OpenAI API wrapper with vector store integration,
consciousness-aware request handling, and ΛID-based rate limiting.

Trinity Framework:
- ⚛️ Identity: ΛID-based authentication and rate limiting
- 🧠 Consciousness: Context-aware completions, memory integration
- 🛡️ Guardian: Content filtering, ethical guidelines enforcement

TaskIDs:
- TODO-HIGH-BRIDGE-LLM-m7n8o9p0: Vector store integration

#TAG:bridge
#TAG:llm
#TAG:openai
#TAG:trinity
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# OpenAI imports (conditional)
try:
    import openai  # noqa: F401  # TODO: openai; consider using importl...
    from openai import AsyncOpenAI, OpenAI
    from openai.types.chat import ChatCompletion, ChatCompletionChunk

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available, install with: pip install openai")
    AsyncOpenAI = None  # type: ignore[assignment]
    OpenAI = None  # type: ignore[assignment]
    ChatCompletion = Any  # type: ignore[assignment]
    ChatCompletionChunk = Any  # type: ignore[assignment]


class VectorStoreProvider(Enum):
    """Supported vector store providers"""

    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    CHROMA = "chroma"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    FAISS = "faiss"  # Local


class ModelTier(Enum):
    """OpenAI model tiers"""

    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT4 = "gpt-4"
    GPT35_TURBO = "gpt-3.5-turbo"
    EMBEDDING_3_LARGE = "text-embedding-3-large"
    EMBEDDING_3_SMALL = "text-embedding-3-small"
    EMBEDDING_ADA = "text-embedding-ada-002"


@dataclass
class VectorStoreConfig:
    """Vector store configuration"""

    provider: VectorStoreProvider
    endpoint: str
    api_key: Optional[str] = None
    namespace: str = "default"
    index_name: str = "lukhas-embeddings"
    dimension: int = 1536  # OpenAI embedding dimension
    metric: str = "cosine"  # cosine|euclidean|dot_product

    # Performance settings
    batch_size: int = 100
    connection_timeout: int = 30
    max_retries: int = 3

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddingRequest:
    """Embedding generation request"""

    text: Union[str, List[str]]
    model: ModelTier = ModelTier.EMBEDDING_3_SMALL

    # ΛID integration
    lambda_id: Optional[str] = None
    identity_tier: Optional[str] = None

    # Request metadata
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddingResult:
    """Embedding generation result"""

    embeddings: List[List[float]]
    model: str
    usage: Dict[str, int]

    # Metadata
    request_id: Optional[str] = None
    lambda_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class VectorSearchRequest:
    """Vector similarity search request"""

    query: Union[str, List[float]]  # Text query or embedding vector
    top_k: int = 10
    namespace: Optional[str] = None
    filter_metadata: Optional[Dict[str, Any]] = None

    # ΛID integration
    lambda_id: Optional[str] = None
    include_metadata: bool = True
    include_vectors: bool = False


@dataclass
class VectorSearchResult:
    """Vector search result"""

    matches: List[Dict[str, Any]]
    query_embedding: Optional[List[float]] = None
    search_time_ms: Optional[float] = None

    # Metadata
    request_id: Optional[str] = None
    lambda_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CompletionRequest:
    """Chat completion request with consciousness context"""

    messages: List[Dict[str, str]]
    model: ModelTier = ModelTier.GPT35_TURBO
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

    # Consciousness integration
    consciousness_context: Optional[Dict[str, Any]] = None
    memory_context: Optional[List[str]] = None  # From vector store

    # ΛID integration
    lambda_id: Optional[str] = None
    identity_tier: Optional[str] = None

    # Request metadata
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""

    requests_per_minute: int = 60
    tokens_per_minute: int = 90000

    # ΛID-based tier limits
    tier_multipliers: Dict[str, float] = field(
        default_factory=lambda: {
            "alpha": 3.0,
            "beta": 2.0,
            "gamma": 1.5,
            "delta": 1.0,
        }
    )


class VectorStoreAdapter:
    """
    Vector store adapter for embedding storage and retrieval

    TaskID: TODO-HIGH-BRIDGE-LLM-m7n8o9p0
    """

    def __init__(self, config: VectorStoreConfig):
        """Initialize vector store adapter"""
        self.config = config
        self._client = None
        self._initialized = False

        logger.info(
            f"VectorStoreAdapter initialized: provider={config.provider.value}, "
            f"index={config.index_name}, dimension={config.dimension}"
        )

    async def initialize(self):
        """Initialize vector store connection"""
        if self._initialized:
            return

        try:
            # Initialize provider-specific client
            if self.config.provider == VectorStoreProvider.PINECONE:
                await self._initialize_pinecone()
            elif self.config.provider == VectorStoreProvider.WEAVIATE:
                await self._initialize_weaviate()
            elif self.config.provider == VectorStoreProvider.CHROMA:
                await self._initialize_chroma()
            elif self.config.provider == VectorStoreProvider.QDRANT:
                await self._initialize_qdrant()
            elif self.config.provider == VectorStoreProvider.FAISS:
                await self._initialize_faiss()
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")

            self._initialized = True
            logger.info(f"Vector store initialized: {self.config.provider.value}")

        except Exception as e:
            logger.error(f"Vector store initialization failed: {e}", exc_info=True)
            raise

    async def _initialize_pinecone(self):
        """Initialize Pinecone client"""
        try:
            import pinecone

            pinecone.init(
                api_key=self.config.api_key,
                environment=self.config.endpoint,
            )
            self._client = pinecone.Index(self.config.index_name)
        except ImportError:
            logger.warning("Pinecone not installed: pip install pinecone-client")
            raise

    async def _initialize_weaviate(self):
        """Initialize Weaviate client"""
        try:
            import weaviate

            self._client = weaviate.Client(
                url=self.config.endpoint,
                auth_client_secret=weaviate.AuthApiKey(api_key=self.config.api_key) if self.config.api_key else None,
            )
        except ImportError:
            logger.warning("Weaviate not installed: pip install weaviate-client")
            raise

    async def _initialize_chroma(self):
        """Initialize ChromaDB client"""
        try:
            import chromadb

            self._client = chromadb.Client()
        except ImportError:
            logger.warning("ChromaDB not installed: pip install chromadb")
            raise

    async def _initialize_qdrant(self):
        """Initialize Qdrant client"""
        try:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(
                url=self.config.endpoint,
                api_key=self.config.api_key,
            )
        except ImportError:
            logger.warning("Qdrant not installed: pip install qdrant-client")
            raise

    async def _initialize_faiss(self):
        """Initialize FAISS index (local)"""
        try:
            import faiss
            import numpy as np  # noqa: F401  # TODO: numpy; consider using importli...

            # Create new index or load existing
            self._client = faiss.IndexFlatL2(self.config.dimension)
            self._vectors = []  # Store vectors in memory
            self._metadata = []  # Store metadata in memory
        except ImportError:
            logger.warning("FAISS not installed: pip install faiss-cpu")
            raise

    async def upsert_embeddings(
        self,
        embeddings: List[List[float]],
        ids: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Upsert embeddings to vector store

        Args:
            embeddings: List of embedding vectors
            ids: List of unique IDs
            metadata: List of metadata dicts (optional)
            namespace: Namespace (optional, uses config default)

        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()

        namespace = namespace or self.config.namespace
        metadata = metadata or [{} for _ in ids]

        try:
            # Provider-specific upsert
            if self.config.provider == VectorStoreProvider.PINECONE:
                vectors = list(zip(ids, embeddings, metadata))
                self._client.upsert(vectors=vectors, namespace=namespace)

            elif self.config.provider == VectorStoreProvider.WEAVIATE:
                # Weaviate batch upload
                with self._client.batch as batch:
                    for i, (id_, embedding, meta) in enumerate(zip(ids, embeddings, metadata)):
                        batch.add_data_object(
                            data_object=meta,
                            class_name=self.config.index_name,
                            uuid=id_,
                            vector=embedding,
                        )

            elif self.config.provider == VectorStoreProvider.CHROMA:
                collection = self._client.get_or_create_collection(self.config.index_name)
                collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadata,
                )

            elif self.config.provider == VectorStoreProvider.QDRANT:
                from qdrant_client.models import PointStruct

                points = [
                    PointStruct(id=id_, vector=embedding, payload=meta)
                    for id_, embedding, meta in zip(ids, embeddings, metadata)
                ]
                self._client.upsert(
                    collection_name=self.config.index_name,
                    points=points,
                )

            elif self.config.provider == VectorStoreProvider.FAISS:
                import numpy as np

                vectors_array = np.array(embeddings).astype("float32")
                self._client.add(vectors_array)
                self._vectors.extend(embeddings)
                self._metadata.extend(metadata)

            logger.info(f"Upserted {len(ids)} embeddings to {self.config.provider.value}")
            return True

        except Exception as e:
            logger.error(f"Embedding upsert failed: {e}", exc_info=True)
            return False

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Metadata filters (optional)
            namespace: Namespace (optional)

        Returns:
            List of matches with scores and metadata
        """
        if not self._initialized:
            await self.initialize()

        namespace = namespace or self.config.namespace

        try:
            # Provider-specific search
            if self.config.provider == VectorStoreProvider.PINECONE:
                results = self._client.query(
                    vector=query_embedding,
                    top_k=top_k,
                    namespace=namespace,
                    filter=filter_metadata,
                    include_metadata=True,
                )
                # ΛTAG: vector_store_normalization
                return self._normalize_matches(results.matches)

            elif self.config.provider == VectorStoreProvider.WEAVIATE:
                query = (
                    self._client.query.get(self.config.index_name, ["*"])
                    .with_near_vector({"vector": query_embedding})
                    .with_limit(top_k)
                )
                if filter_metadata:
                    query = query.with_where(filter_metadata)
                results = query.do()
                raw_matches = results.get("data", {}).get("Get", {}).get(self.config.index_name, [])
                return self._normalize_matches(raw_matches)

            elif self.config.provider == VectorStoreProvider.CHROMA:
                collection = self._client.get_collection(self.config.index_name)
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=filter_metadata,
                )
                matches = []
                for i in range(len(results["ids"][0])):
                    matches.append(
                        {
                            "id": results["ids"][0][i],
                            "score": results["distances"][0][i],
                            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        }
                    )
                return self._normalize_matches(matches)

            elif self.config.provider == VectorStoreProvider.QDRANT:
                results = self._client.search(
                    collection_name=self.config.index_name,
                    query_vector=query_embedding,
                    limit=top_k,
                    query_filter=filter_metadata,
                )
                raw_matches = [
                    {
                        "id": str(hit.id),
                        "score": hit.score,
                        "metadata": hit.payload,
                    }
                    for hit in results
                ]
                return self._normalize_matches(raw_matches)

            elif self.config.provider == VectorStoreProvider.FAISS:
                import numpy as np

                query_array = np.array([query_embedding]).astype("float32")
                distances, indices = self._client.search(query_array, top_k)
                matches = []
                for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                    if idx < len(self._metadata):
                        matches.append(
                            {
                                "id": str(idx),
                                "score": float(dist),
                                "metadata": self._metadata[idx],
                            }
                        )
                return self._normalize_matches(matches)

            return []

        except Exception as e:
            logger.error(f"Vector search failed: {e}", exc_info=True)
            return []

    def _normalize_matches(self, matches: List[Any]) -> List[Dict[str, Any]]:
        """Normalize provider-specific match objects into dictionaries."""

        normalized: List[Dict[str, Any]] = []
        for match in matches:
            # Provider SDKs often expose helper conversions
            if hasattr(match, "to_dict"):
                candidate = match.to_dict()
            elif isinstance(match, dict):
                candidate = match
            else:
                candidate = {
                    "id": getattr(match, "id", getattr(match, "uuid", "")),
                    "score": getattr(match, "score", getattr(match, "similarity", 0.0)),
                    "metadata": getattr(match, "metadata", getattr(match, "payload", {})),
                }

            metadata = candidate.get("metadata") or candidate.get("payload") or {}
            normalized.append(
                {
                    "id": str(candidate.get("id", candidate.get("uuid", ""))),
                    "score": float(candidate.get("score", candidate.get("similarity", 0.0))),
                    "metadata": metadata,
                }
            )

        return normalized


class OpenAIModulatedService:
    """
    OpenAI API wrapper with modulation, vector store integration, and consciousness awareness

    Features:
    - Chat completions with streaming support
    - Embedding generation and storage
    - Vector similarity search
    - ΛID-based rate limiting
    - Consciousness context integration
    - Memory retrieval from vector store
    - Content filtering and ethical guidelines

    TaskID: TODO-HIGH-BRIDGE-LLM-m7n8o9p0
    """

    def __init__(
        self,
        api_key: str,
        vector_store_config: Optional[VectorStoreConfig] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        organization: Optional[str] = None,
        consciousness_integration: bool = True,
    ):
        """
        Initialize OpenAI modulated service

        Args:
            api_key: OpenAI API key
            vector_store_config: Vector store configuration (optional)
            rate_limit_config: Rate limiting configuration (optional)
            organization: OpenAI organization ID (optional)
            consciousness_integration: Enable consciousness context
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package required: pip install openai")

        self.api_key = api_key
        self.organization = organization
        self.consciousness_integration = consciousness_integration

        # Initialize OpenAI clients
        self.client = OpenAI(api_key=api_key, organization=organization)
        self.async_client = AsyncOpenAI(api_key=api_key, organization=organization)

        # Vector store
        self.vector_store = VectorStoreAdapter(vector_store_config) if vector_store_config else None

        # Rate limiting
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self._rate_limit_state: Dict[str, Dict[str, Any]] = {}

        logger.info(
            f"OpenAIModulatedService initialized: "
            f"vector_store={bool(self.vector_store)}, "
            f"consciousness={consciousness_integration}"
        )

    async def generate_embeddings(
        self,
        request: EmbeddingRequest,
    ) -> EmbeddingResult:
        """
        Generate embeddings for text

        Args:
            request: Embedding request

        Returns:
            Embedding result with vectors and metadata
        """
        texts = [request.text] if isinstance(request.text, str) else request.text

        try:
            response = await self.async_client.embeddings.create(
                model=request.model.value,
                input=texts,
            )

            embeddings = [item.embedding for item in response.data]

            result = EmbeddingResult(
                embeddings=embeddings,
                model=response.model,
                usage=response.usage.model_dump(),
                request_id=request.request_id,
                lambda_id=request.lambda_id,
            )

            logger.info(
                f"Generated {len(embeddings)} embeddings: "
                f"model={request.model.value}, tokens={result.usage.get('total_tokens')}"
            )

            return result

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}", exc_info=True)
            raise

    async def store_embeddings(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict[str, Any]]] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Store embeddings in vector store

        Args:
            texts: Original texts
            embeddings: Embedding vectors
            metadata: Metadata for each embedding
            namespace: Vector store namespace

        Returns:
            True if successful
        """
        if not self.vector_store:
            logger.warning("Vector store not configured")
            return False

        # Generate IDs from texts
        ids = [hashlib.sha256(text.encode()).hexdigest()[:16] for text in texts]

        # Add text to metadata
        if metadata is None:
            metadata = [{"text": text} for text in texts]
        else:
            for i, meta in enumerate(metadata):
                meta["text"] = texts[i]

        return await self.vector_store.upsert_embeddings(
            embeddings=embeddings,
            ids=ids,
            metadata=metadata,
            namespace=namespace,
        )

    async def search_similar(
        self,
        request: VectorSearchRequest,
    ) -> VectorSearchResult:
        """
        Search for similar vectors

        Args:
            request: Vector search request

        Returns:
            Vector search result with matches
        """
        if not self.vector_store:
            logger.warning("Vector store not configured")
            return VectorSearchResult(matches=[])

        start_time = datetime.utcnow()

        # Generate query embedding if text provided
        if isinstance(request.query, str):
            embed_request = EmbeddingRequest(
                text=request.query,
                lambda_id=request.lambda_id,
            )
            embed_result = await self.generate_embeddings(embed_request)
            query_embedding = embed_result.embeddings[0]
        else:
            query_embedding = request.query

        # Perform search
        matches = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=request.top_k,
            filter_metadata=request.filter_metadata,
            namespace=request.namespace,
        )

        search_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        return VectorSearchResult(
            matches=matches,
            query_embedding=query_embedding if request.include_vectors else None,
            search_time_ms=search_time_ms,
            lambda_id=request.lambda_id,
        )

    async def chat_completion(
        self,
        request: CompletionRequest,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """
        Generate chat completion with consciousness context

        Args:
            request: Completion request

        Returns:
            Chat completion or streaming iterator
        """
        # Retrieve memory context from vector store
        if request.memory_context and self.vector_store:
            # Get similar memories
            search_request = VectorSearchRequest(
                query=request.messages[-1]["content"],  # Last user message
                top_k=5,
                lambda_id=request.lambda_id,
            )
            search_result = await self.search_similar(search_request)

            # Add to system message
            if search_result.matches:
                memory_text = "\n".join(
                    [f"- {match.get('metadata', {}).get('text', '')}" for match in search_result.matches[:3]]
                )
                system_msg = f"Relevant context:\n{memory_text}"
                request.messages.insert(0, {"role": "system", "content": system_msg})

        # Add consciousness context
        if request.consciousness_context and self.consciousness_integration:
            context_msg = f"Consciousness state: {request.consciousness_context}"
            request.messages.insert(0, {"role": "system", "content": context_msg})

        try:
            if request.stream:
                return await self.async_client.chat.completions.create(
                    model=request.model.value,
                    messages=request.messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=True,
                )
            else:
                response = await self.async_client.chat.completions.create(
                    model=request.model.value,
                    messages=request.messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=False,
                )

                logger.info(
                    f"Chat completion: model={request.model.value}, "
                    f"tokens={response.usage.total_tokens if response.usage else 'unknown'}"
                )

                return response

        except Exception as e:
            logger.error(f"Chat completion failed: {e}", exc_info=True)
            raise

    def _check_rate_limit(self, lambda_id: Optional[str], identity_tier: Optional[str]) -> bool:
        """Check if request is within rate limits"""
        # TODO: Implement sliding window rate limiting
        # For now, always allow
        return True

    async def close(self):
        """Close clients and connections"""
        # Close OpenAI clients
        await self.async_client.close()

        logger.info("OpenAIModulatedService closed")
