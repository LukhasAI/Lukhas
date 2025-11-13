# QRG Keystore

The `QRGKeystore` is a hardened keystore with file-based ephemeral keys and GitHub secret integration.

## Usage

To use the `QRGKeystore`, first create an instance of the class:

```python
from lukhas.identity.qrg_keystore import QRGKeystore

keystore = QRGKeystore()
```

### Key Retrieval

The `get_key` method retrieves a key by searching in the following order:
1.  **Local File Cache:** Checks for a locally stored, ephemeral key in the directory specified by `key_dir` (defaults to `/tmp/qrg_keys`).
2.  **Environment Variables:** If not found locally, it checks for an environment variable named `QRG_SECRET_<KEY_ID_IN_UPPERCASE>`. This is designed to integrate with CI/CD systems like GitHub Actions, where secrets are exposed as environment variables.

If a key is found in an environment variable, it is automatically cached in the local file store for subsequent faster access.

Example:
```python
# This will first check for a file named "my_key" in the key_dir.
# If not found, it will check for an environment variable named QRG_SECRET_MY_KEY.
key = keystore.get_key("my_key")
```

### Key Storage

You can manually store a key in the local file cache using the `store_key` method. This is useful for pre-populating the cache.

Example:
```python
keystore.store_key("my_key", b"my_secret_key")
```
