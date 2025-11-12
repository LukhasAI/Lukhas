# Soft-Delete Pattern for Memory Entries

This document outlines the soft-delete pattern implemented in the `lukhas/memory` module.

## Overview

The soft-delete pattern allows memory entries to be marked as deleted without being permanently removed from the system. This provides a mechanism for data recovery and auditing.

## Implementation

The implementation consists of the following components:

- **`SoftDeletable` mixin**: A mixin class in `lukhas/memory/soft_delete.py` that provides the core soft-delete logic, including `is_deleted` and `deleted_at` attributes and `soft_delete()` and `restore()` methods.

- **`MemoryEntry` class**: A class in `lukhas/memory/index.py` that represents a single entry in the embedding index. It inherits from the `SoftDeletable` mixin to gain soft-delete capabilities.

### `EmbeddingIndex` Class

The `EmbeddingIndex` class in `lukhas/memory/index.py` manages `MemoryEntry` objects and has been updated to include the following methods for managing soft-deletes:

- `soft_delete(vector_id)`: Marks a vector as deleted by calling the `soft_delete()` method on the corresponding `MemoryEntry` object.
- `restore(vector_id)`: Restores a soft-deleted vector by calling the `restore()` method on the corresponding `MemoryEntry` object.
- `is_deleted(vector_id)`: Checks if a vector is soft-deleted.
- `get_deleted_at(vector_id)`: Returns the deletion timestamp for a vector.

The `search` method has also been updated to exclude soft-deleted entries from search results.
