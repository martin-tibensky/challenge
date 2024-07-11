import pytest
from ..common.test_chatbots import _TestChatbots
from playwright.sync_api import Page
from ...lib.chatbots import ChatbotInterface


@pytest.mark.copilot
class TestCopilot(_TestChatbots):
    def test_upload_picture(
        self, chat_page: Page, chatbot: ChatbotInterface, picture_path: str
    ):
        chatbot.upload_picture(chat_page, file_path=picture_path)
        query = "What is on the picture?"
        chatbot_response = chatbot.send_message(chat_page, query, timeout=90)
        response_check = "flag"
        assert response_check.lower() in chatbot_response.lower()
