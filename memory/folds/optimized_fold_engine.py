#!/usr/bin/env python3
"""
Optimized Memory Fold Engine
=============================
High-performance memory fold system with caching, compression,
parallel processing, and advanced indexing capabilities.

Performance Features:
- Lazy loading and caching
- Memory compression
- Parallel fold processing
- Bloom filter for fast existence checks
- LRU cache for frequently accessed folds
- Memory-mapped storage for large datasets
- Asynchronous I/O operations
"""

import asyncio
import hashlib
import mmap
import numpy as np
import pickle
import struct
import time
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import threading
from functools import partial

# Compression backend helpers
# Prefer lz4 for speed; if unavailable, fall back to zlib so tests run without optional deps.
try:  # Optional dependency
    import lz4.frame as _lz4frame  # type: ignore

    def _compress_bytes(data: bytes) -> bytes:
        return _lz4frame.compress(data)

    def _decompress_bytes(data: bytes) -> bytes:
        return _lz4frame.decompress(data)

except Exception:  # Fallback to stdlib
    import zlib as _zlib

    def _compress_bytes(data: bytes) -> bytes:
        return _zlib.compress(data, level=6)

    def _decompress_bytes(data: bytes) -> bytes:
        return _zlib.decompress(data)

# Import bloom filter for fast membership testing
try:
    from pybloom_live import BloomFilter
except ImportError:
    BloomFilter = None  # Fallback to set if not available


@dataclass
class OptimizedMemoryFold:
    """
    Optimized memory fold with compression and lazy loading
    """
    key: str
    content_hash: str  # Hash of content for deduplication
    compressed_content: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    compression_ratio: float = 1.0
    
    # Lazy loading
    _content: Any = None
    _is_loaded: bool = False
    
    @property
    def content(self) -> Any:
        """Lazy load and decompress content"""
        if not self._is_loaded and self.compressed_content:
            self._content = self._decompress(self.compressed_content)
            self._is_loaded = True
        self.access_count += 1
        self.last_accessed = time.time()
        return self._content
    
    @content.setter
    def content(self, value: Any):
        """Set and compress content"""
        self._content = value
        self._is_loaded = True
        compressed = self._compress(value)
        self.compression_ratio = len(compressed) / max(1, len(pickle.dumps(value)))
        self.compressed_content = compressed
        self.content_hash = hashlib.sha256(compressed).hexdigest()
    
    def _compress(self, data: Any) -> bytes:
        """Compress data using LZ4"""
        serialized = pickle.dumps(data)
        return _compress_bytes(serialized)
    
    def _decompress(self, data: bytes) -> Any:
        """Decompress LZ4 data"""
        decompressed = _decompress_bytes(data)
        return pickle.loads(decompressed)
    
    def evict(self):
        """Evict content from memory, keeping only compressed version"""
        if self._is_loaded:
            self._content = None
            self._is_loaded = False


class FoldIndex:
    """
    High-performance index for memory folds
    """
    
    def __init__(self, use_bloom_filter: bool = True):
        # Primary indexes
        self.by_key: Dict[str, OptimizedMemoryFold] = {}
        self.by_hash: Dict[str, Set[str]] = defaultdict(set)  # Content deduplication
        self.by_tag: Dict[str, Set[str]] = defaultdict(set)
        self.by_time: OrderedDict[float, Set[str]] = OrderedDict()
        
        # Bloom filter for fast existence checks
        if use_bloom_filter and BloomFilter:
            self.bloom_filter = BloomFilter(capacity=100000, error_rate=0.001)
        else:
            self.bloom_filter = None
        
        # Statistics
        self.total_size = 0
        self.compressed_size = 0
        
        # Thread safety
        self._lock = threading.RLock()
    
    def add(self, fold: OptimizedMemoryFold):
        """Add fold to all indexes"""
        with self._lock:
            self.by_key[fold.key] = fold
            self.by_hash[fold.content_hash].add(fold.key)
            
            # Add to bloom filter
            if self.bloom_filter:
                self.bloom_filter.add(fold.key)
            
            # Update time index
            if fold.last_accessed not in self.by_time:
                self.by_time[fold.last_accessed] = set()
            self.by_time[fold.last_accessed].add(fold.key)
            
            # Update tags index
            tags = fold.metadata.get("tags", [])
            for tag in tags:
                self.by_tag[tag].add(fold.key)
            
            # Update statistics
            if fold.compressed_content:
                self.compressed_size += len(fold.compressed_content)
    
    def exists(self, key: str) -> bool:
        """Fast existence check using bloom filter"""
        if self.bloom_filter:
            if key not in self.bloom_filter:
                return False  # Definitely not present
        return key in self.by_key
    
    def get(self, key: str) -> Optional[OptimizedMemoryFold]:
        """Get fold by key"""
        with self._lock:
            return self.by_key.get(key)
    
    def find_duplicates(self, content_hash: str) -> Set[str]:
        """Find all folds with same content"""
        with self._lock:
            return self.by_hash.get(content_hash, set()).copy()
    
    def get_by_tags(self, tags: List[str]) -> Set[str]:
        """Get folds matching all tags"""
        with self._lock:
            if not tags:
                return set()
            
            result = self.by_tag.get(tags[0], set()).copy()
            for tag in tags[1:]:
                result &= self.by_tag.get(tag, set())
            
            return result
    
    def get_oldest(self, n: int = 10) -> List[str]:
        """Get n oldest accessed folds"""
        with self._lock:
            result = []
            for timestamp, keys in self.by_time.items():
                result.extend(keys)
                if len(result) >= n:
                    break
            return result[:n]
    
    def remove(self, key: str):
        """Remove fold from all indexes"""
        with self._lock:
            fold = self.by_key.get(key)
            if not fold:
                return
            
            # Remove from all indexes
            del self.by_key[key]
            self.by_hash[fold.content_hash].discard(key)
            
            # Remove from time index
            for timestamp, keys in self.by_time.items():
                if key in keys:
                    keys.discard(key)
                    if not keys:
                        del self.by_time[timestamp]
                    break
            
            # Remove from tags
            tags = fold.metadata.get("tags", [])
            for tag in tags:
                self.by_tag[tag].discard(key)
            
            # Update statistics
            if fold.compressed_content:
                self.compressed_size -= len(fold.compressed_content)


class OptimizedFoldEngine:
    """
    High-performance memory fold engine with advanced optimizations
    """
    
    def __init__(
        self,
        max_memory_mb: int = 1024,
        cache_size: int = 1000,
        enable_mmap: bool = False,
        storage_path: Optional[Path] = None
    ):
        # Configuration
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache_size = cache_size
        self.enable_mmap = enable_mmap
        self.storage_path = storage_path or Path("./memory_folds")
        
        # Core components
        self.index = FoldIndex()
        self.lru_cache = OrderedDict()  # LRU cache for hot folds
        
        # Memory-mapped file for large storage
        self.mmap_file = None
        self.mmap_index = {}  # key -> (offset, size)
        if enable_mmap:
            self._init_mmap()
        
        # Thread pools for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        
        # Performance monitoring
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "compressions": 0,
            "decompressions": 0
        }
        
        # Background tasks
        self._background_tasks = []
        self._shutdown = False
    
    def _init_mmap(self):
        """Initialize memory-mapped file"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        mmap_path = self.storage_path / "folds.mmap"
        
        # Create or open mmap file
        if mmap_path.exists():
            self.mmap_file = open(mmap_path, "r+b")
        else:
            # Create 100MB file
            self.mmap_file = open(mmap_path, "w+b")
            self.mmap_file.write(b'\0' * (100 * 1024 * 1024))
            self.mmap_file.flush()
        
        self.mmap = mmap.mmap(self.mmap_file.fileno(), 0)
        self.mmap_offset = 0
    
    def create_fold(
        self,
        key: str,
        content: Any,
        tags: Optional[List[str]] = None,
        **metadata
    ) -> OptimizedMemoryFold:
        """
        Create optimized memory fold
        """
        fold = OptimizedMemoryFold(
            key=key,
            content_hash="",
            metadata={"tags": tags or [], **metadata}
        )
        
        # Set and compress content
        fold.content = content
        
        # Add to index
        self.index.add(fold)
        
        # Add to LRU cache
        self._update_lru(key, fold)
        
        # Check for memory pressure
        if self.index.compressed_size > self.max_memory_bytes:
            self._evict_cold_folds()
        
        self.stats["compressions"] += 1
        
        return fold
    
    def get_fold(self, key: str) -> Optional[OptimizedMemoryFold]:
        """
        Get fold with caching
        """
        # Check LRU cache first
        if key in self.lru_cache:
            self.stats["hits"] += 1
            fold = self.lru_cache[key]
            self._update_lru(key, fold)
            return fold
        
        # Check main index
        fold = self.index.get(key)
        if fold:
            self.stats["hits"] += 1
            self._update_lru(key, fold)
            return fold
        
        # Check mmap storage
        if self.enable_mmap and key in self.mmap_index:
            fold = self._load_from_mmap(key)
            if fold:
                self.stats["hits"] += 1
                self._update_lru(key, fold)
                return fold
        
        self.stats["misses"] += 1
        return None
    
    def _update_lru(self, key: str, fold: OptimizedMemoryFold):
        """Update LRU cache"""
        # Remove if exists
        if key in self.lru_cache:
            del self.lru_cache[key]
        
        # Add to end (most recent)
        self.lru_cache[key] = fold
        
        # Evict if over capacity
        while len(self.lru_cache) > self.cache_size:
            oldest_key = next(iter(self.lru_cache))
            del self.lru_cache[oldest_key]
            self.stats["evictions"] += 1
    
    def _evict_cold_folds(self):
        """Evict cold folds to reduce memory usage"""
        # Get oldest folds
        oldest_keys = self.index.get_oldest(100)
        
        for key in oldest_keys:
            fold = self.index.get(key)
            if fold and fold._is_loaded:
                # Evict content from memory
                fold.evict()
                self.stats["evictions"] += 1
                
                # Optionally move to mmap
                if self.enable_mmap:
                    self._save_to_mmap(key, fold)
            
            # Check if under memory limit
            if self.index.compressed_size < self.max_memory_bytes * 0.8:
                break
    
    def _save_to_mmap(self, key: str, fold: OptimizedMemoryFold):
        """Save fold to memory-mapped file"""
        if not self.mmap or not fold.compressed_content:
            return
        
        data = fold.compressed_content
        size = len(data)
        
        # Write to mmap
        if self.mmap_offset + size + 8 < len(self.mmap):
            # Write size and data
            self.mmap[self.mmap_offset:self.mmap_offset+8] = struct.pack('Q', size)
            self.mmap[self.mmap_offset+8:self.mmap_offset+8+size] = data
            
            # Update index
            self.mmap_index[key] = (self.mmap_offset, size)
            self.mmap_offset += size + 8
    
    def _load_from_mmap(self, key: str) -> Optional[OptimizedMemoryFold]:
        """Load fold from memory-mapped file"""
        if key not in self.mmap_index:
            return None
        
        offset, size = self.mmap_index[key]
        
        # Read from mmap
        data = bytes(self.mmap[offset+8:offset+8+size])
        
        # Recreate fold
        fold = OptimizedMemoryFold(
            key=key,
            content_hash=hashlib.sha256(data).hexdigest(),
            compressed_content=data
        )
        
        return fold
    
    async def batch_create(
        self,
        items: List[Tuple[str, Any, Dict[str, Any]]]
    ) -> List[OptimizedMemoryFold]:
        """
        Create multiple folds in parallel
        """
        loop = asyncio.get_running_loop()
        futures = []
        for key, content, metadata in items:
            func = partial(
                self.create_fold,
                key,
                content,
                metadata.get("tags"),
                **{k: v for k, v in metadata.items() if k != "tags"},
            )
            futures.append(loop.run_in_executor(self.thread_pool, func))
        return await asyncio.gather(*futures)
    
    async def parallel_search(
        self,
        predicate: Callable[[OptimizedMemoryFold], bool],
        max_results: int = 100
    ) -> List[OptimizedMemoryFold]:
        """
        Search folds in parallel
        """
        results = []
        
        # Split folds into chunks
        all_keys = list(self.index.by_key.keys())
        chunk_size = max(1, len(all_keys) // 4)
        chunks = [
            all_keys[i:i+chunk_size]
            for i in range(0, len(all_keys), chunk_size)
        ]
        
        async def search_chunk(keys: List[str]) -> List[OptimizedMemoryFold]:
            chunk_results = []
            for key in keys:
                fold = self.get_fold(key)
                if fold and predicate(fold):
                    chunk_results.append(fold)
                    if len(chunk_results) >= max_results:
                        break
            return chunk_results
        
        # Search chunks in parallel using threads invoking sync function
        loop = asyncio.get_running_loop()

        def _search_chunk_sync(keys: List[str]) -> List[OptimizedMemoryFold]:
            # Synchronous wrapper around the async search to run in executor
            return asyncio.run(search_chunk(keys))

        tasks = [loop.run_in_executor(self.thread_pool, _search_chunk_sync, chunk) for chunk in chunks]

        chunk_results = await asyncio.gather(*tasks)
        
        # Combine results
        for chunk in chunk_results:
            results.extend(chunk)
            if len(results) >= max_results:
                break
        
        return results[:max_results]
    
    def deduplicate(self) -> int:
        """
        Remove duplicate folds based on content hash
        """
        duplicates_removed = 0
        
        for content_hash, keys in self.index.by_hash.items():
            if len(keys) > 1:
                # Keep first, remove rest
                keys_list = list(keys)
                for key in keys_list[1:]:
                    self.index.remove(key)
                    if key in self.lru_cache:
                        del self.lru_cache[key]
                    duplicates_removed += 1
        
        return duplicates_removed
    
    def optimize_storage(self):
        """
        Optimize storage by recompressing and reorganizing
        """
        optimized_count = 0
        
        for key, fold in self.index.by_key.items():
            # Skip if recently accessed
            if time.time() - fold.last_accessed < 3600:  # 1 hour
                continue
            
            # Recompress if ratio is poor
            if fold.compression_ratio > 0.8:
                # Try higher compression
                original_content = fold.content
                fold.content = original_content  # Recompress
                
                if fold.compression_ratio < 0.8:
                    optimized_count += 1
        
        # Defragment mmap if enabled
        if self.enable_mmap:
            self._defragment_mmap()
        
        return optimized_count
    
    def _defragment_mmap(self):
        """Defragment memory-mapped storage"""
        if not self.mmap:
            return
        
        # Create new mmap file
        new_path = self.storage_path / "folds_new.mmap"
        with open(new_path, "w+b") as new_file:
            new_file.write(b'\0' * (100 * 1024 * 1024))
            new_mmap = mmap.mmap(new_file.fileno(), 0)
            
            # Copy data to new file
            new_offset = 0
            new_index = {}
            
            for key, (offset, size) in self.mmap_index.items():
                data = bytes(self.mmap[offset+8:offset+8+size])
                
                # Write to new location
                new_mmap[new_offset:new_offset+8] = struct.pack('Q', size)
                new_mmap[new_offset+8:new_offset+8+size] = data
                
                new_index[key] = (new_offset, size)
                new_offset += size + 8
            
            # Replace old with new
            self.mmap.close()
            self.mmap_file.close()
            
            old_path = self.storage_path / "folds.mmap"
            old_path.unlink()
            new_path.rename(old_path)
            
            self.mmap_file = open(old_path, "r+b")
            self.mmap = mmap.mmap(self.mmap_file.fileno(), 0)
            self.mmap_index = new_index
            self.mmap_offset = new_offset
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total_folds = len(self.index.by_key)
        
        return {
            **self.stats,
            "total_folds": total_folds,
            "cache_size": len(self.lru_cache),
            "total_size_mb": self.index.compressed_size / (1024 * 1024),
            "avg_compression_ratio": np.mean([
                fold.compression_ratio 
                for fold in self.index.by_key.values()
            ]) if total_folds > 0 else 0,
            "cache_hit_rate": self.stats["hits"] / max(1, self.stats["hits"] + self.stats["misses"]),
            "unique_content": len(self.index.by_hash),
            "deduplication_ratio": total_folds / max(1, len(self.index.by_hash))
        }
    
    def shutdown(self):
        """Clean shutdown"""
        self._shutdown = True
        
        # Wait for background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Shutdown thread pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        # Close mmap
        if self.mmap:
            self.mmap.close()
            self.mmap_file.close()


# Demo functionality
async def demo_optimized_folds():
    """Demonstrate optimized memory fold performance"""
    
    print("⚡ Optimized Memory Fold Engine Demo")
    print("=" * 60)
    
    engine = OptimizedFoldEngine(
        max_memory_mb=100,
        cache_size=50,
        enable_mmap=False  # Disable for demo
    )
    
    # 1. Create folds with compression
    print("\n1️⃣ Creating Compressed Folds:")
    
    start_time = time.time()
    
    folds = []
    for i in range(100):
        # Create varying content sizes
        content = {
            "id": i,
            "data": "x" * (100 + i * 10),  # Increasing size
            "metadata": {"index": i, "type": "test"},
            "vector": np.random.randn(100).tolist()  # High compression potential
        }
        
        fold = engine.create_fold(
            key=f"fold_{i}",
            content=content,
            tags=["test", f"batch_{i//10}"]
        )
        folds.append(fold)
    
    create_time = time.time() - start_time
    
    stats = engine.get_statistics()
    print(f"   Created 100 folds in {create_time:.3f}s")
    print(f"   Total size: {stats['total_size_mb']:.2f} MB")
    print(f"   Avg compression: {stats['avg_compression_ratio']:.3f}")
    
    # 2. Test cache performance
    print("\n2️⃣ Cache Performance:")
    
    start_time = time.time()
    
    # Access pattern: 80/20 rule
    hot_keys = [f"fold_{i}" for i in range(20)]
    
    for _ in range(1000):
        if np.random.random() < 0.8:
            key = np.random.choice(hot_keys)
        else:
            key = f"fold_{np.random.randint(0, 100)}"
        
        fold = engine.get_fold(key)
    
    access_time = time.time() - start_time
    
    stats = engine.get_statistics()
    print(f"   1000 accesses in {access_time:.3f}s")
    print(f"   Cache hit rate: {stats['cache_hit_rate']:.3%}")
    print(f"   Evictions: {stats['evictions']}")
    
    # 3. Deduplication
    print("\n3️⃣ Deduplication:")
    
    # Create duplicate content
    duplicate_content = {"duplicate": True, "data": "same"}
    
    for i in range(10):
        engine.create_fold(
            key=f"dup_{i}",
            content=duplicate_content,
            tags=["duplicate"]
        )
    
    before_dedup = len(engine.index.by_key)
    removed = engine.deduplicate()
    after_dedup = len(engine.index.by_key)
    
    print(f"   Before: {before_dedup} folds")
    print(f"   Removed: {removed} duplicates")
    print(f"   After: {after_dedup} folds")
    
    # 4. Parallel batch creation
    print("\n4️⃣ Parallel Batch Creation:")
    
    items = [
        (f"batch_{i}", {"batch_id": i}, {"tags": ["batch"]})
        for i in range(50)
    ]
    
    start_time = time.time()
    batch_folds = await engine.batch_create(items)
    batch_time = time.time() - start_time
    
    print(f"   Created {len(batch_folds)} folds in parallel")
    print(f"   Time: {batch_time:.3f}s")
    print(f"   Rate: {len(batch_folds)/batch_time:.1f} folds/sec")
    
    # 5. Parallel search
    print("\n5️⃣ Parallel Search:")
    
    def search_predicate(fold: OptimizedMemoryFold) -> bool:
        """Find folds with specific pattern"""
        return "batch" in fold.metadata.get("tags", [])
    
    start_time = time.time()
    search_results = await engine.parallel_search(search_predicate, max_results=20)
    search_time = time.time() - start_time
    
    print(f"   Found {len(search_results)} matching folds")
    print(f"   Search time: {search_time:.3f}s")
    
    # 6. Memory optimization
    print("\n6️⃣ Memory Optimization:")
    
    # Force eviction
    engine._evict_cold_folds()
    
    # Optimize storage
    optimized = engine.optimize_storage()
    
    final_stats = engine.get_statistics()
    print(f"   Optimized {optimized} folds")
    print(f"   Final size: {final_stats['total_size_mb']:.2f} MB")
    print(f"   Deduplication ratio: {final_stats['deduplication_ratio']:.2f}x")
    
    # 7. Tag-based retrieval
    print("\n7️⃣ Tag-Based Retrieval:")
    
    tag_results = engine.index.get_by_tags(["test", "batch_5"])
    print(f"   Found {len(tag_results)} folds with tags [test, batch_5]")
    
    # Cleanup
    engine.shutdown()
    
    print("\n✅ Optimized memory fold demonstration complete!")
    print("\nFinal Statistics:")
    for key, value in final_stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")


if __name__ == "__main__":
    asyncio.run(demo_optimized_folds())
