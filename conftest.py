"""
Pytest configuration for ImmoAssist tests.

Sets up test environment with mock configuration to avoid requiring
actual Google Cloud credentials during testing.
"""

import os
import pytest
from typing import Generator
from unittest.mock import patch

# Set test environment variables before any imports
os.environ["ENVIRONMENT"] = "test"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["MODEL_NAME"] = "gemini-2.5-flash"
os.environ["SPECIALIST_MODEL"] = "gemini-2.5-flash"
os.environ["CHAT_MODEL"] = "gemini-2.5-flash"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
os.environ["GOOGLE_API_KEY"] = "test-key"


@pytest.fixture(autouse=True)
def mock_environment() -> Generator[None, None, None]:
    """Auto-use fixture to ensure test environment is properly mocked."""
    with patch.dict(
        os.environ,
        {
            "ENVIRONMENT": "test",
            "GOOGLE_CLOUD_PROJECT": "test-project",
            "MODEL_NAME": "gemini-2.5-flash",
            "SPECIALIST_MODEL": "gemini-2.5-flash",
            "CHAT_MODEL": "gemini-2.5-flash",
            "GOOGLE_GENAI_USE_VERTEXAI": "FALSE",
            "GOOGLE_API_KEY": "test-key",
        },
    ):
        yield
