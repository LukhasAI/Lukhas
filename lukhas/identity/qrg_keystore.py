import os

class QRGKeystore:
    def __init__(self, key_dir: str = "/tmp/qrg_keys"):
        self.key_dir = key_dir
        if not os.path.exists(self.key_dir):
            os.makedirs(self.key_dir)

    def get_key(self, key_id: str) -> bytes:
        """
        Retrieves a key from the keystore.
        It first checks the local file-based cache, and if not found,
        it checks for an environment variable, simulating a GitHub secret.
        """
        # 1. Check local file cache first
        key_path = os.path.join(self.key_dir, key_id)
        try:
            with open(key_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            pass  # Continue to next method

        # 2. Check environment variables (simulating GitHub secrets)
        # Secrets are typically exposed as ENV_VARS in CI/CD
        env_var_name = f"QRG_SECRET_{key_id.upper()}"
        secret_value = os.environ.get(env_var_name)
        if secret_value:
            key_bytes = secret_value.encode('utf-8')
            # Cache the secret locally for ephemeral access
            self.store_key(key_id, key_bytes)
            return key_bytes

        return None

    def store_key(self, key_id: str, key: bytes):
        """Stores a key in the keystore."""
        key_path = os.path.join(self.key_dir, key_id)
        with open(key_path, "wb") as f:
            f.write(key)
