"""
Unit tests for the orchestrator error recovery module.
"""

import asyncio
import time
import unittest
from unittest.mock import AsyncMock, MagicMock

from lukhas.orchestration.error_recovery import CircuitBreaker, fallback, retry


class TestErrorRecovery(unittest.TestCase):
    def test_retry_decorator_success(self):
        """
        Test that the retry decorator returns the result of the wrapped function
        when it succeeds on the first attempt.
        """
        mock_func = AsyncMock(return_value="success")

        @retry(retries=3)
        async def decorated_func():
            return await mock_func()

        result = asyncio.run(decorated_func())
        self.assertEqual(result, "success")
        mock_func.assert_called_once()

    def test_retry_decorator_failure_then_success(self):
        """
        Test that the retry decorator successfully returns a result after
        a few failed attempts.
        """
        mock_func = AsyncMock(
            side_effect=[ValueError("failed"), ValueError("failed"), "success"]
        )

        @retry(retries=3)
        async def decorated_func():
            return await mock_func()

        result = asyncio.run(decorated_func())
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 3)

    def test_retry_decorator_persistent_failure(self):
        """
        Test that the retry decorator raises the last exception after the
        configured number of retries.
        """
        mock_func = AsyncMock(side_effect=ValueError("persistent failure"))

        @retry(retries=3, backoff=0.01)
        async def decorated_func():
            return await mock_func()

        with self.assertRaises(ValueError):
            asyncio.run(decorated_func())
        self.assertEqual(mock_func.call_count, 3)

    def test_circuit_breaker_closed_state(self):
        """
        Test that the circuit breaker allows calls to pass through when it is
        in the closed state.
        """
        breaker = CircuitBreaker()
        mock_func = MagicMock()

        async def run():
            async with breaker:
                mock_func()

        asyncio.run(run())
        mock_func.assert_called_once()

    def test_circuit_breaker_opens_on_failures(self):
        """
        Test that the circuit breaker opens after the configured number of
        failures.
        """
        breaker = CircuitBreaker(failure_threshold=2)

        async def run_failure():
            async with breaker:
                raise ValueError("failure")

        with self.assertRaises(ValueError):
            asyncio.run(run_failure())
        with self.assertRaises(ValueError):
            asyncio.run(run_failure())

        with self.assertRaises(RuntimeError):
            asyncio.run(run_failure())
        self.assertEqual(breaker.state, "open")

    def test_circuit_breaker_half_open_state(self):
        """
        Test that the circuit breaker transitions to the half-open state after
        the recovery timeout and then closes on success.
        """
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01)

        async def run_failure():
            async with breaker:
                raise ValueError("failure")

        async def run_success():
            async with breaker:
                pass

        with self.assertRaises(ValueError):
            asyncio.run(run_failure())
        with self.assertRaises(ValueError):
            asyncio.run(run_failure())

        time.sleep(0.02)
        asyncio.run(run_success())
        self.assertEqual(breaker.state, "closed")

    def test_fallback_handler(self):
        """
        Test that the fallback handler is called when the primary function
        raises an exception.
        """
        mock_primary = AsyncMock(side_effect=ValueError("primary failed"))
        mock_fallback = AsyncMock(return_value="fallback success")

        @fallback(fallback_handler=mock_fallback)
        async def decorated_func():
            return await mock_primary()

        result = asyncio.run(decorated_func())
        self.assertEqual(result, "fallback success")
        mock_primary.assert_called_once()
        mock_fallback.assert_called_once()

    def test_fallback_handler_no_failure(self):
        """
        Test that the fallback handler is not called when the primary function
        succeeds.
        """
        mock_primary = AsyncMock(return_value="primary success")
        mock_fallback = AsyncMock()

        @fallback(fallback_handler=mock_fallback)
        async def decorated_func():
            return await mock_primary()

        result = asyncio.run(decorated_func())
        self.assertEqual(result, "primary success")
        mock_primary.assert_called_once()
        mock_fallback.assert_not_called()

    def test_retry_decorator_ignores_cancellation(self):
        """
        Test that the retry decorator does not catch asyncio.CancelledError.
        """
        mock_func = AsyncMock(side_effect=asyncio.CancelledError)

        @retry(retries=3)
        async def decorated_func():
            return await mock_func()

        with self.assertRaises(asyncio.CancelledError):
            asyncio.run(decorated_func())
        mock_func.assert_called_once()

    def test_circuit_breaker_resets_on_success(self):
        """
        Test that the circuit breaker resets its failure count after a successful
        call in the closed state.
        """
        breaker = CircuitBreaker(failure_threshold=3)

        async def run_failure():
            async with breaker:
                raise ValueError("failure")

        async def run_success():
            async with breaker:
                pass

        with self.assertRaises(ValueError):
            asyncio.run(run_failure())
        self.assertEqual(breaker.failure_count, 1)

        asyncio.run(run_success())
        self.assertEqual(breaker.failure_count, 0)

    def test_circuit_breaker_ignores_cancellation(self):
        """
        Test that the circuit breaker does not count asyncio.CancelledError as a failure.
        """
        breaker = CircuitBreaker(failure_threshold=2)

        async def run_cancellation():
            async with breaker:
                raise asyncio.CancelledError

        with self.assertRaises(asyncio.CancelledError):
            asyncio.run(run_cancellation())
        self.assertEqual(breaker.failure_count, 0)
        self.assertEqual(breaker.state, "closed")

    def test_fallback_handler_ignores_cancellation(self):
        """
        Test that the fallback handler does not catch asyncio.CancelledError.
        """
        mock_primary = AsyncMock(side_effect=asyncio.CancelledError)
        mock_fallback = AsyncMock()

        @fallback(fallback_handler=mock_fallback)
        async def decorated_func():
            return await mock_primary()

        with self.assertRaises(asyncio.CancelledError):
            asyncio.run(decorated_func())
        mock_fallback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
