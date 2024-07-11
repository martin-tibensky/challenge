import pytest
from ...lib.chatbots import CopilotChatBot


@pytest.fixture(scope="module")
def chatbot() -> CopilotChatBot:
    return CopilotChatBot(load_credentials_from_env=True)
