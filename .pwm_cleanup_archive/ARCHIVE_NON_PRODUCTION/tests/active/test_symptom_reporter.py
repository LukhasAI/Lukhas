import asyncio
import logging

from core.interaction.symptom_reporter import SymptomReporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_symptom_reporting():
    """Test the symptom reporting flow"""
    logger.info("Starting symptom reporting test")

    # Initialize the reporter
    reporter = SymptomReporter()

    # Test with a simulated user ID
    user_id = "test_user_123"

    # Start a session
    result = await reporter.start_symptom_reporting(user_id, mode="text")

    logger.info(f"Session completed with result: {result}")
    return result


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_symptom_reporting())
