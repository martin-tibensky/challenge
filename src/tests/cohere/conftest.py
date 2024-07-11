import pytest
from ...lib.chatbots import CohereChatBot


@pytest.fixture(scope="module")
def chatbot() -> CohereChatBot:
    return CohereChatBot(load_credentials_from_env=True)
