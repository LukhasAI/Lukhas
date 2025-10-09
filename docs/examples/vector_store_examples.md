# Vector Store Configuration Examples

**Part of BATCH-COPILOT-2025-10-08-01**  
**TaskID**: ASSIST-LOW-EXAMPLES-VECTOR-u3v4w5x6

## Overview

LUKHAS supports multiple vector store providers for RAG (Retrieval-Augmented Generation) and semantic search capabilities. This guide covers configuration for Pinecone, Weaviate, and local alternatives.

## Pinecone Configuration

### Basic Setup

```yaml
# config/vector_store_pinecone.yaml
vector_store:
  provider: "pinecone"
  api_key: "${PINECONE_API_KEY}"
  environment: "us-west1-gcp"  # or your environment
  index_name: "lukhas-embeddings"
  
  # Index configuration
  dimension: 1536  # OpenAI ada-002
  metric: "cosine"  # cosine, euclidean, dotproduct
  
  # Performance
  batch_size: 100
  timeout: 30
  max_retries: 3
```

### Python Configuration

```python
from candidate.consciousness.reflection.openai_modulated_service import OpenAIModulatedService

# Pinecone configuration
pinecone_config = {
    "provider": "pinecone",
    "api_key": os.getenv("PINECONE_API_KEY"),
    "environment": "us-west1-gcp",
    "index_name": "lukhas-embeddings",
    "dimension": 1536,
    "metric": "cosine"
}

service = OpenAIModulatedService(config=pinecone_config)
```

### Creating Index

```python
import pinecone

# Initialize Pinecone
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment="us-west1-gcp"
)

# Create index
pinecone.create_index(
    name="lukhas-embeddings",
    dimension=1536,
    metric="cosine",
    pods=1,
    pod_type="p1.x1"  # See Pinecone pricing
)

# Wait for index to be ready
index = pinecone.Index("lukhas-embeddings")
```

## Weaviate Configuration

### Basic Setup

```yaml
# config/vector_store_weaviate.yaml
vector_store:
  provider: "weaviate"
  url: "http://localhost:8080"  # or cloud URL
  auth_client_secret: "${WEAVIATE_API_KEY}"
  
  # Schema
  class_name: "LukhasDocuments"
  vectorizer: "text2vec-openai"
  
  # OpenAI integration
  openai_api_key: "${OPENAI_API_KEY}"
  openai_model: "text-embedding-ada-002"
  
  # Performance
  batch_size: 100
  consistency_level: "QUORUM"  # ONE, QUORUM, ALL
```

### Python Configuration

```python
import weaviate

# Weaviate configuration
weaviate_config = {
    "provider": "weaviate",
    "url": "http://localhost:8080",
    "auth_client_secret": os.getenv("WEAVIATE_API_KEY"),
    "class_name": "LukhasDocuments"
}

# Initialize client
client = weaviate.Client(
    url=weaviate_config["url"],
    auth_client_secret=weaviate.AuthApiKey(weaviate_config["auth_client_secret"])
)

service = OpenAIModulatedService(config=weaviate_config, client=client)
```

### Schema Definition

```python
# Define Weaviate schema
schema = {
    "class": "LukhasDocuments",
    "description": "LUKHAS document embeddings",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {
            "model": "ada",
            "type": "text"
        }
    },
    "properties": [
        {
            "name": "content",
            "dataType": ["text"],
            "description": "Document content"
        },
        {
            "name": "metadata",
            "dataType": ["object"],
            "description": "Document metadata"
        },
        {
            "name": "lambda_id",
            "dataType": ["string"],
            "description": "Lambda ID of owner"
        },
        {
            "name": "created_at",
            "dataType": ["date"],
            "description": "Creation timestamp"
        }
    ]
}

# Create schema
client.schema.create_class(schema)
```

## Embedding Pipeline Configuration

### OpenAI Embeddings

```python
from openai import AsyncOpenAI

# Configure OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using OpenAI."""
    
    response = await openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=texts
    )
    
    return [item.embedding for item in response.data]
```

### Batch Processing

```python
async def batch_embed_documents(documents: list[dict], batch_size: int = 100):
    """Embed documents in batches."""
    
    embeddings = []
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        texts = [doc["content"] for doc in batch]
        
        # Generate embeddings
        batch_embeddings = await generate_embeddings(texts)
        embeddings.extend(batch_embeddings)
        
        # Rate limiting
        await asyncio.sleep(0.1)
    
    return embeddings
```

## RAG (Retrieval-Augmented Generation) Setup

### Basic RAG Pipeline

```python
async def rag_search(
    query: str,
    top_k: int = 5,
    filter: dict = None
) -> list[dict]:
    """Perform RAG search."""
    
    # 1. Generate query embedding
    query_embedding = await generate_embeddings([query])
    
    # 2. Search vector store
    results = await service.similarity_search(
        query_embedding=query_embedding[0],
        top_k=top_k,
        filter=filter
    )
    
    # 3. Return ranked results
    return results
```

### Advanced RAG with Reranking

```python
from sentence_transformers import CrossEncoder

# Load reranker
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

async def rag_search_with_reranking(
    query: str,
    top_k: int = 5,
    rerank_top_n: int = 20
) -> list[dict]:
    """RAG search with reranking."""
    
    # 1. Initial retrieval (get more than needed)
    initial_results = await rag_search(query, top_k=rerank_top_n)
    
    # 2. Rerank with cross-encoder
    pairs = [[query, result["content"]] for result in initial_results]
    scores = reranker.predict(pairs)
    
    # 3. Sort by reranking scores
    for result, score in zip(initial_results, scores):
        result["rerank_score"] = float(score)
    
    reranked = sorted(initial_results, key=lambda x: x["rerank_score"], reverse=True)
    
    # 4. Return top-k after reranking
    return reranked[:top_k]
```

## Metadata Filtering

### Pinecone Metadata Filters

```python
# Search with metadata filter
results = await service.similarity_search(
    query_embedding=embedding,
    top_k=5,
    filter={
        "type": {"$eq": "research"},
        "tier": {"$in": ["pro", "enterprise"]},
        "created_at": {"$gte": "2025-01-01"}
    }
)
```

### Weaviate Metadata Filters

```python
# Search with where filter
results = client.query.get("LukhasDocuments", ["content", "metadata"]) \
    .with_near_vector({"vector": embedding}) \
    .with_where({
        "path": ["type"],
        "operator": "Equal",
        "valueString": "research"
    }) \
    .with_limit(5) \
    .do()
```

## Connection Examples

### With Error Handling

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def connect_vector_store(config: dict):
    """Connect to vector store with retry logic."""
    
    try:
        if config["provider"] == "pinecone":
            import pinecone
            pinecone.init(
                api_key=config["api_key"],
                environment=config["environment"]
            )
            index = pinecone.Index(config["index_name"])
            return index
            
        elif config["provider"] == "weaviate":
            import weaviate
            client = weaviate.Client(
                url=config["url"],
                auth_client_secret=weaviate.AuthApiKey(config["auth_client_secret"])
            )
            return client
            
    except Exception as e:
        logger.error(f"Failed to connect to vector store: {e}")
        raise
```

### Connection Pooling

```python
class VectorStorePool:
    """Connection pool for vector store clients."""
    
    def __init__(self, config: dict, pool_size: int = 5):
        self.config = config
        self.pool_size = pool_size
        self.connections = []
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool."""
        for _ in range(self.pool_size):
            conn = self._create_connection()
            self.connections.append(conn)
    
    def _create_connection(self):
        """Create new connection."""
        return connect_vector_store(self.config)
    
    async def get_connection(self):
        """Get connection from pool."""
        if self.connections:
            return self.connections.pop()
        return self._create_connection()
    
    async def return_connection(self, conn):
        """Return connection to pool."""
        self.connections.append(conn)
```

## Docker Compose Setup

### Weaviate with Docker

```yaml
# docker-compose.yml
version: '3.8'

services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
      ENABLE_MODULES: 'text2vec-openai'
      OPENAI_APIKEY: ${OPENAI_API_KEY}
    volumes:
      - weaviate_data:/var/lib/weaviate

volumes:
  weaviate_data:
```

Start with:
```bash
docker-compose up -d
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import hashlib

class EmbeddingCache:
    """Cache for embeddings."""
    
    def __init__(self, max_size: int = 10000):
        self.cache = {}
        self.max_size = max_size
    
    def _hash_text(self, text: str) -> str:
        """Hash text for cache key."""
        return hashlib.sha256(text.encode()).hexdigest()
    
    async def get_embedding(self, text: str) -> list[float]:
        """Get cached embedding or generate new."""
        cache_key = self._hash_text(text)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Generate new embedding
        embedding = await generate_embeddings([text])
        
        # Cache if not full
        if len(self.cache) < self.max_size:
            self.cache[cache_key] = embedding[0]
        
        return embedding[0]
```

### Batch Upsert

```python
async def batch_upsert_documents(
    documents: list[dict],
    embeddings: list[list[float]],
    batch_size: int = 100
):
    """Upsert documents in batches for performance."""
    
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_embs = embeddings[i:i + batch_size]
        
        await service.upsert_documents(batch_docs, batch_embs)
        
        logger.info(f"Upserted batch {i // batch_size + 1}")
```

## Monitoring and Metrics

```python
class VectorStoreMetrics:
    """Track vector store performance metrics."""
    
    def __init__(self):
        self.query_count = 0
        self.query_latencies = []
        self.upsert_count = 0
        self.errors = []
    
    async def track_query(self, query_func, *args, **kwargs):
        """Track query performance."""
        import time
        
        start = time.time()
        try:
            result = await query_func(*args, **kwargs)
            latency = time.time() - start
            
            self.query_count += 1
            self.query_latencies.append(latency)
            
            return result
        except Exception as e:
            self.errors.append(str(e))
            raise
    
    def get_stats(self) -> dict:
        """Get performance statistics."""
        return {
            "query_count": self.query_count,
            "avg_latency": sum(self.query_latencies) / len(self.query_latencies) if self.query_latencies else 0,
            "error_rate": len(self.errors) / max(self.query_count, 1),
            "errors": self.errors[-10:]  # Last 10 errors
        }
```

---

**⚛️🧠🛡️ LUKHAS AI Platform - High-Performance Vector Search**
