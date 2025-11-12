import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock the 'identity.webauthn' module to avoid ImportError, since it's a conditional dependency
mock_webauthn_manager_instance = MagicMock()
mock_webauthn_manager_class = MagicMock(return_value=mock_webauthn_manager_instance)
mock_webauthn_module = MagicMock()
mock_webauthn_module.WebAuthnManager = mock_webauthn_manager_class
sys.modules['identity.webauthn'] = mock_webauthn_module

# Mock the 'observability.matriz_decorators' module
mock_instrument = lambda *args, **kwargs: lambda func: func
mock_observability_module = MagicMock()
mock_observability_module.instrument = mock_instrument
sys.modules['observability.matriz_decorators'] = mock_observability_module

# Mock the 'lukhas_website.lukhas.identity.auth_service' module to avoid NameError
sys.modules['lukhas_website.lukhas.identity.auth_service'] = MagicMock()


# Ensure the module under test can be imported
# The file path is `lukhas_website/lukhas/identity/lambda_id.py`.
# Assuming `lukhas_website` is in the python path or the CWD.
from labs.governance.identity.core.namespace_manager import NamespaceManager, NamespaceType
from lukhas_website.lukhas.identity.lambda_id import LambdaIDService


class TestLambdaIDService(unittest.TestCase):

    def setUp(self):
        # Reset the mock before each test to ensure isolation
        mock_webauthn_manager_instance.reset_mock()
        # Reload the module under test to re-evaluate top-level conditionals
        # This allows tests to patch environment variables and control WEBAUTHN_ACTIVE
        self.lambda_id_module = self.reload_module()

    def reload_module(self):
        """Helper to reload the lambda_id module for clean test state."""
        module_name = 'lukhas_website.lukhas.identity.lambda_id'
        if module_name in sys.modules:
            del sys.modules[module_name]
        return __import__(module_name, fromlist=['*'])

    def get_service(self):
        """Helper to get a fresh service instance."""
        return self.lambda_id_module.LambdaIDService()

    # --- Authenticate Tests ---

    def test_authenticate_dry_run_mode(self):
        """Test authenticate in 'dry_run' mode."""
        service = self.get_service()
        result = service.authenticate("user-123", mode="dry_run")
        self.assertTrue(result["ok"])
        self.assertEqual(result["method"], "dry_run")
        self.assertEqual(result["user"]["lid"], "user-123")

    def test_authenticate_invalid_lid_returns_error(self):
        """Test authenticate with an invalid (too short) Lambda ID."""
        service = self.get_service()
        result = service.authenticate("id")
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "invalid_lid")

    @patch('lukhas_website.lukhas.identity.lambda_id.os.environ.get', return_value="true")
    def test_authenticate_webauthn_success(self, mock_env_get):
        """Test successful WebAuthn authentication when active."""
        lambda_id_module = self.reload_module()
        service = lambda_id_module.LambdaIDService()

        credential = {"type": "webauthn", "authentication_id": "auth1", "response": {"data": "..."}}
        mock_webauthn_manager_instance.verify_authentication_response.return_value = {
            "success": True, "user_id": "user-123", "tier_level": 3
        }

        result = service.authenticate("user-123", credential=credential, mode="live")

        self.assertTrue(result["ok"])
        self.assertEqual(result["method"], "webauthn")
        self.assertEqual(result["user"]["lid"], "user-123")
        self.assertEqual(result["tier_level"], 3)
        mock_webauthn_manager_instance.verify_authentication_response.assert_called_once_with(
            authentication_id="auth1", response={"data": "..."}
        )

    @patch('lukhas_website.lukhas.identity.lambda_id.os.environ.get', return_value="true")
    def test_authenticate_webauthn_failure(self, mock_env_get):
        """Test failed WebAuthn authentication."""
        lambda_id_module = self.reload_module()
        service = lambda_id_module.LambdaIDService()

        credential = {"type": "webauthn", "authentication_id": "auth1", "response": {}}
        mock_webauthn_manager_instance.verify_authentication_response.return_value = {"success": False}

        result = service.authenticate("user-123", credential=credential, mode="live")

        self.assertFalse(result["ok"])
        mock_webauthn_manager_instance.verify_authentication_response.assert_called_once()

    @patch('lukhas_website.lukhas.identity.lambda_id.os.environ.get', return_value="true")
    def test_authenticate_webauthn_active_but_no_credential(self, mock_env_get):
        """Test WebAuthn flow falls back when no credential is provided."""
        lambda_id_module = self.reload_module()
        service = lambda_id_module.LambdaIDService()
        result = service.authenticate("user-123", credential=None, mode="live")

        self.assertTrue(result["ok"])
        self.assertEqual(result["method"], "dry_run") # Falls back
        mock_webauthn_manager_instance.verify_authentication_response.assert_not_called()

    # --- Register Passkey Tests ---

    def test_register_passkey_dry_run(self):
        """Test register_passkey in 'dry_run' mode."""
        service = self.get_service()
        result = service.register_passkey("u1", "uname", "User Name", mode="dry_run")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "registration_initiated(dry_run)")

    @patch('lukhas_website.lukhas.identity.lambda_id.os.environ.get', return_value="true")
    def test_register_passkey_live_success(self, mock_env_get):
        """Test successful passkey registration when WebAuthn is active."""
        lambda_id_module = self.reload_module()
        service = lambda_id_module.LambdaIDService()

        mock_webauthn_manager_instance.generate_registration_options.return_value = {
            "success": True, "registration_id": "reg123", "options": {"challenge": "abc"}
        }

        result = service.register_passkey("u1", "uname", "User Name", mode="live", tier=2)

        self.assertTrue(result["ok"])
        self.assertEqual(result["registration_id"], "reg123")
        mock_webauthn_manager_instance.generate_registration_options.assert_called_once_with(
            user_id="u1", user_name="uname", user_display_name="User Name", user_tier=2
        )

    # --- Verify Passkey Tests ---

    def test_verify_passkey_dry_run(self):
        """Test verify_passkey in 'dry_run' mode."""
        service = self.get_service()
        result = service.verify_passkey("reg123", {}, mode="dry_run")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "verified(dry_run)")

    @patch('lukhas_website.lukhas.identity.lambda_id.os.environ.get', return_value="true")
    def test_verify_passkey_live_success(self, mock_env_get):
        """Test successful passkey verification when WebAuthn is active."""
        lambda_id_module = self.reload_module()
        service = lambda_id_module.LambdaIDService()

        mock_webauthn_manager_instance.verify_registration_response.return_value = {
            "success": True, "credential_id": "cred1", "user_id": "u1", "tier_level": 2
        }

        result = service.verify_passkey("reg123", {"response": "data"}, mode="live")

        self.assertTrue(result["ok"])
        self.assertEqual(result["credential_id"], "cred1")
        self.assertEqual(result["user_id"], "u1")
        mock_webauthn_manager_instance.verify_registration_response.assert_called_once_with(
            registration_id="reg123", response={"response": "data"}
        )

    # --- List Credentials Tests ---

    def test_list_credentials_dry_run(self):
        """Test list_credentials in 'dry_run' mode."""
        service = self.get_service()
        result = service.list_credentials("u1", mode="dry_run")
        self.assertTrue(result["ok"])
        self.assertEqual(result["credentials"], [])
        self.assertEqual(result["total"], 0)

    @patch('lukhas_website.lukhas.identity.lambda_id.os.environ.get', return_value="true")
    def test_list_credentials_live_success(self, mock_env_get):
        """Test successfully listing credentials when WebAuthn is active."""
        lambda_id_module = self.reload_module()
        service = lambda_id_module.LambdaIDService()

        creds = [{"id": "cred1"}]
        mock_webauthn_manager_instance.get_user_credentials.return_value = {
            "success": True, "credentials": creds, "total_credentials": 1
        }

        result = service.list_credentials("u1", mode="live")

        self.assertTrue(result["ok"])
        self.assertEqual(result["credentials"], creds)
        self.assertEqual(result["total"], 1)
        mock_webauthn_manager_instance.get_user_credentials.assert_called_once_with("u1")

    # --- Revoke Credential Tests ---

    def test_revoke_credential_dry_run(self):
        """Test revoke_credential in 'dry_run' mode."""
        service = self.get_service()
        result = service.revoke_credential("u1", "cred1", mode="dry_run")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "revoked(dry_run)")

    @patch('lukhas_website.lukhas.identity.lambda_id.os.environ.get', return_value="true")
    def test_revoke_credential_live_success(self, mock_env_get):
        """Test successfully revoking a credential when WebAuthn is active."""
        lambda_id_module = self.reload_module()
        service = lambda_id_module.LambdaIDService()

        mock_webauthn_manager_instance.revoke_credential.return_value = {
            "success": True, "revoked_at": "timestamp"
        }

        result = service.revoke_credential("u1", "cred1", mode="live")

        self.assertTrue(result["ok"])
        self.assertEqual(result["revoked_at"], "timestamp")
        mock_webauthn_manager_instance.revoke_credential.assert_called_once_with("u1", "cred1")

class TestNamespaceManager(unittest.TestCase):

    def setUp(self):
        self.manager = NamespaceManager()

    def test_initialization(self):
        """Test that the manager initializes with default namespaces."""
        self.assertIn("ai", self.manager.namespaces)
        self.assertIn("enterprise.ai", self.manager.namespaces)
        self.assertIn("dev.ai", self.manager.namespaces)
        self.assertEqual(len(self.manager.namespaces), 3)

    def test_create_namespace_success(self):
        """Test successful creation of a new tenant namespace."""
        result = self.manager.create_namespace(
            "my-tenant.ai", NamespaceType.TENANT, "My Tenant", "owner-123"
        )
        self.assertTrue(result["success"])
        self.assertIn("my-tenant.ai", self.manager.namespaces)
        self.assertEqual(self.manager.namespaces["my-tenant.ai"].owner_id, "owner-123")

    def test_create_namespace_duplicate_fails(self):
        """Test that creating a namespace that already exists fails."""
        self.manager.create_namespace(
            "my-tenant.ai", NamespaceType.TENANT, "My Tenant", "owner-123"
        )
        result = self.manager.create_namespace(
            "my-tenant.ai", NamespaceType.TENANT, "My Tenant", "owner-123"
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Namespace already exists")

    def test_create_namespace_invalid_id_fails(self):
        """Test that creating a namespace with an invalid ID fails."""
        result = self.manager.create_namespace(
            "invalid/", NamespaceType.TENANT, "Invalid", "owner-123"
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Invalid namespace ID format")

    def test_resolve_namespace_direct_hit(self):
        """Test resolving an existing namespace by its exact ID."""
        namespace = self.manager.resolve_namespace("enterprise.ai")
        self.assertIsNotNone(namespace)
        self.assertEqual(namespace.namespace_id, "enterprise.ai")

    def test_resolve_namespace_with_normalization(self):
        """Test that resolution works with http prefixes and trailing slashes."""
        namespace = self.manager.resolve_namespace("https://dev.ai/")
        self.assertIsNotNone(namespace)
        self.assertEqual(namespace.namespace_id, "dev.ai")

    def test_resolve_namespace_pattern_match(self):
        """Test resolving a namespace by a subdomain pattern."""
        self.manager.create_namespace("sub.dev.ai", NamespaceType.SERVICE, "Sub Service", "owner-456", parent_namespace="dev.ai")
        namespace = self.manager.resolve_namespace("test.sub.dev.ai")
        self.assertIsNotNone(namespace)
        self.assertEqual(namespace.namespace_id, "sub.dev.ai")

    def test_resolve_namespace_not_found(self):
        """Test that resolving a non-existent namespace returns None."""
        namespace = self.manager.resolve_namespace("nonexistent.com")
        self.assertIsNone(namespace)

    def test_get_namespace_policy(self):
        """Test retrieving the policy for a namespace."""
        policy = self.manager.get_namespace_policy("dev.ai")
        self.assertIsNotNone(policy)
        self.assertEqual(policy.namespace_id, "dev.ai")
        self.assertEqual(policy.access_control, "relaxed")

    def test_update_namespace_policy_success(self):
        """Test successfully updating a namespace policy."""
        update = {"access_control": "strict", "data_retention_days": 90}
        result = self.manager.update_namespace_policy("dev.ai", update, "admin-001")
        self.assertTrue(result["success"])

        policy = self.manager.get_namespace_policy("dev.ai")
        self.assertEqual(policy.access_control, "strict")
        self.assertEqual(policy.data_retention_days, 90)

    def test_create_cross_namespace_mapping_success(self):
        """Test creating a valid cross-namespace identity mapping."""
        # By default, only 'ai' root allows cross-namespace mapping
        self.manager.policies['enterprise.ai'].cross_namespace_allowed = True

        result = self.manager.create_cross_namespace_mapping(
            "enterprise.ai", "dev.ai", {"user1": "dev-user1"}, "admin-001"
        )
        self.assertTrue(result["success"])
        self.assertIn("enterprise.ai", self.manager.cross_namespace_mappings)
        self.assertIn("dev.ai", self.manager.cross_namespace_mappings["enterprise.ai"])

    def test_create_cross_namespace_mapping_disallowed(self):
        """Test that mapping fails if the source namespace policy disallows it."""
        result = self.manager.create_cross_namespace_mapping(
            "dev.ai", "enterprise.ai", {}, "admin-001"
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Cross-namespace mapping not allowed for source namespace")

    def test_map_identity_across_namespaces(self):
        """Test mapping an identity from a source to a target namespace."""
        self.manager.policies['enterprise.ai'].cross_namespace_allowed = True
        self.manager.create_cross_namespace_mapping(
            "enterprise.ai", "dev.ai", {"user-a": "user-b"}, "admin-001"
        )

        mapped_id = self.manager.map_identity_across_namespaces(
            "user-a", "enterprise.ai", "dev.ai"
        )
        self.assertEqual(mapped_id, "user-b")

    def test_list_namespaces_no_filter(self):
        """Test listing all namespaces."""
        self.manager.create_namespace("t1.ai", NamespaceType.TENANT, "T1", "o1")
        namespaces = self.manager.list_namespaces()
        self.assertEqual(len(namespaces), 4)

    def test_list_namespaces_with_type_filter(self):
        """Test filtering namespaces by type."""
        self.manager.create_namespace("t1.ai", NamespaceType.TENANT, "T1", "o1")
        namespaces = self.manager.list_namespaces(namespace_type=NamespaceType.TENANT)
        self.assertEqual(len(namespaces), 1)
        self.assertEqual(namespaces[0]["namespace_id"], "t1.ai")

    def test_get_system_status(self):
        """Test the system status report."""
        status = self.manager.get_system_status()
        self.assertEqual(status["statistics"]["total_namespaces"], 3)
        self.assertIn("performance_metrics", status)


if __name__ == '__main__':
    unittest.main()
