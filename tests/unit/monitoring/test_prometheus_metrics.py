import unittest
from unittest.mock import MagicMock, patch
import asyncio

from prometheus_client import REGISTRY

from matriz.monitoring.prometheus_exporter import (
    operation_latency,
    operation_total,
    memory_usage,
    execute_operation
)


class TestPrometheusMetrics(unittest.TestCase):

    def test_metrics_registration(self):
        self.assertIn('matriz_operation_latency_seconds', REGISTRY._names_to_collectors)
        self.assertIn('matriz_operations_total', REGISTRY._names_to_collectors)
        self.assertIn('matriz_memory_bytes', REGISTRY._names_to_collectors)

    @patch('matriz.monitoring.prometheus_exporter.operation_latency')
    @patch('matriz.monitoring.prometheus_exporter.operation_total')
    def test_execute_operation(self, mock_operation_total, mock_operation_latency):
        # Create a mock operation object
        mock_operation = MagicMock()
        mock_operation.type = 'test_operation'
        mock_operation.node.type = 'test_node'

        # Make the execute method an async function
        async def mock_execute():
            return 'test_result'
        mock_operation.execute = mock_execute

        # Run the execute_operation function
        # We need to create a new async function to be the entry point for asyncio.run
        async def run_test():
            return await execute_operation(mock_operation)

        result = asyncio.run(run_test())

        # Assert that the result is correct
        self.assertEqual(result, 'test_result')

        # Assert that the latency metric was called correctly
        mock_operation_latency.labels.assert_called_with(
            operation_type='test_operation',
            node_type='test_node'
        )
        mock_operation_latency.labels.return_value.time.assert_called_once()

        # Assert that the total metric was called correctly
        mock_operation_total.labels.assert_called_with(
            operation_type='test_operation',
            status='success'
        )
        mock_operation_total.labels.return_value.inc.assert_called_once()

    def test_gauge_updates(self):
        memory_usage.labels(component='test_component').set(1024)
        self.assertEqual(
            REGISTRY.get_sample_value('matriz_memory_bytes', {'component': 'test_component'}),
            1024
        )
        memory_usage.labels(component='test_component').set(2048)
        self.assertEqual(
            REGISTRY.get_sample_value('matriz_memory_bytes', {'component': 'test_component'}),
            2048
        )

    @patch('matriz.monitoring.prometheus_exporter.operation_latency')
    @patch('matriz.monitoring.prometheus_exporter.operation_total')
    def test_execute_operation_error(self, mock_operation_total, mock_operation_latency):
        # Create a mock operation object
        mock_operation = MagicMock()
        mock_operation.type = 'test_operation'
        mock_operation.node.type = 'test_node'

        # Make the execute method an async function that raises an exception
        async def mock_execute():
            raise ValueError("Test Exception")
        mock_operation.execute = mock_execute

        # Run the execute_operation function and assert that it raises the exception
        with self.assertRaises(ValueError):
            asyncio.run(execute_operation(mock_operation))

        # Assert that the latency metric was called correctly
        mock_operation_latency.labels.assert_called_with(
            operation_type='test_operation',
            node_type='test_node'
        )
        mock_operation_latency.labels.return_value.time.assert_called_once()

        # Assert that the total metric was called correctly
        mock_operation_total.labels.assert_called_with(
            operation_type='test_operation',
            status='error'
        )
        mock_operation_total.labels.return_value.inc.assert_called_once()


if __name__ == '__main__':
    unittest.main()
