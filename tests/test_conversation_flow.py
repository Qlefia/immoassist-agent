import pytest
from unittest.mock import MagicMock, patch

# from app.agent import ImmoAgent
from app.services.session_service import SessionService
from app.shared_libraries import conversation_constants as const
from app.shared_libraries.conversation_callbacks import combined_before_agent_callback
from app.tools.conversation_tools import analyze_conversation_context
from app.tools.memory_tools import memorize_conversation


# Mock for ADK's context objects
class MockContext:
    def __init__(self):
        self.state = {}


@pytest.fixture
def session_service():
    """Fixture for SessionService."""
    return SessionService()


@pytest.fixture
def mock_context():
    """Fixture for mocked ADK callback context."""
    return MockContext()


def test_session_initialization(session_service, mock_context):
    """
    Tests if a new session is initialized correctly in the state.
    """
    # Act
    result = session_service.initialize_session(mock_context)

    # Assert
    assert result["status"] == "created"
    assert const.CONVERSATION_INITIALIZED in mock_context.state
    assert mock_context.state[const.CONVERSATION_INITIALIZED] is True
    assert "session_id" in mock_context.state
    assert mock_context.state[const.CONVERSATION_PHASE] == const.PHASE_OPENING


def test_before_agent_callback_greeting(session_service, mock_context):
    """
    Tests if the before_agent_callback correctly identifies a greeting.
    """
    # Arrange
    session_service.initialize_session(mock_context)

    # Mock InvocationContext and user input
    invocation_context = MagicMock()
    invocation_context.state = mock_context.state

    with patch(
        "app.shared_libraries.conversation_callbacks._extract_user_input",
        return_value="hallo, wie geht's?",
    ):
        # Act
        combined_before_agent_callback(invocation_context)

    # Assert
    assert (
        mock_context.state[const.CURRENT_INTERACTION_TYPE] == const.INTERACTION_GREETING
    )
    assert mock_context.state[const.GREETING_COUNT] == 1
    assert mock_context.state[const.CONVERSATION_PHASE] == const.PHASE_OPENING


def test_before_agent_callback_question(session_service, mock_context):
    """
    Tests if the before_agent_callback correctly identifies a question
    after an initial greeting.
    """
    # Arrange
    session_service.initialize_session(mock_context)
    mock_context.state[const.GREETING_COUNT] = 1  # Simulate prior greeting
    mock_context.state[const.INTERACTION_COUNT] = 3  # Set to trigger phase change

    invocation_context = MagicMock()
    invocation_context.state = mock_context.state

    with patch(
        "app.shared_libraries.conversation_callbacks._extract_user_input",
        return_value="was kostet eine wohnung?",
    ):
        # Act
        combined_before_agent_callback(invocation_context)

    # Assert
    assert (
        mock_context.state[const.CURRENT_INTERACTION_TYPE] == const.INTERACTION_QUESTION
    )
    assert mock_context.state[const.GREETING_COUNT] == 1  # Should not increment
    assert mock_context.state[const.CONVERSATION_PHASE] == const.PHASE_EXPLORATION


@patch("app.tools.conversation_tools._analyze_user_input_with_llm")
def test_analyze_conversation_tool(mock_llm_analysis, mock_context):
    """
    Tests the analyze_conversation_context tool, ensuring it uses the
    LLM analysis function and returns a structured response.
    """
    # Arrange
    mock_response = {
        "interaction_type": "question",
        "emotional_tone": "curious",
        "topics": ["pricing", "apartment"],
        "style_recommendations": ["be direct", "provide details"],
    }
    mock_llm_analysis.return_value = mock_response

    # Act
    result = analyze_conversation_context.func(
        user_input="tell me about prices", session_context=mock_context.state
    )

    # Assert
    mock_llm_analysis.assert_called_once()
    assert result["status"] == "success"
    assert result["analysis"]["interaction_type"] == "question"
    assert result["analysis"]["emotional_tone"] == "curious"


def test_memorize_conversation_tool(mock_context):
    """
    Tests if the memorize_conversation tool correctly stores data
    in the callback_context.state.
    """
    # Arrange
    tool_context = MagicMock()
    tool_context.state = mock_context.state
    mock_context.state[const.USER_PREFERENCES] = {}  # Ensure it's initialized

    # Act
    result = memorize_conversation.func(
        key="budget", value="500000", category="financials", tool_context=tool_context
    )

    # Assert
    assert result["status"] == "success"
    assert "financials" in mock_context.state[const.USER_PREFERENCES]
    assert (
        mock_context.state[const.USER_PREFERENCES]["financials"]["budget"] == "500000"
    )
