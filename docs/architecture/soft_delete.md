# Soft-Delete Functionality in Embedding Index

## Overview

This document describes the soft-delete functionality implemented in the `SoftDeleteEmbeddingIndex` class. This feature allows for marking items as "deleted" without permanently removing them from the index, providing a way to recover them later if needed.

## Implementation Details

The `SoftDeleteEmbeddingIndex` class inherits from the `EmbeddingIndex` class and extends its functionality with the following features:

- **`soft_delete(vector_id)`**: Marks a vector as deleted by setting an `is_deleted` flag to `True` in its metadata and recording the deletion time in a `deleted_at` field.

- **`restore(vector_id)`**: Reverses a soft-delete by setting the `is_deleted` flag back to `False` and clearing the `deleted_at` field.

- **`search(query_vector, top_k, include_deleted)`**: By default, this method now excludes soft-deleted items from search results. To include them, the `include_deleted` parameter can be set to `True`.

## Metadata Fields

The soft-delete functionality relies on two metadata fields:

- **`is_deleted` (bool)**: `True` if the item is soft-deleted, `False` otherwise.
- **`deleted_at` (str)**: An ISO 8601 formatted timestamp indicating when the item was soft-deleted.

These fields are automatically added to the metadata of each new item added to the index.
