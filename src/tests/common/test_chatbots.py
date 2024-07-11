import pytest
from playwright.sync_api import Page
from ...lib.chatbots import ChatbotInterface


@pytest.mark.usefixtures("chat_page", "chatbot")
class _TestChatbots:
    @pytest.mark.copilot
    @pytest.mark.cohere
    def test_bad_request(self, chat_page: Page, chatbot: ChatbotInterface):
        query = "dklwknddajdwmdnfwa"
        chatbot_response = chatbot.send_message(page=chat_page, message=query)
        response_checks = ["sorry", "apologize"]
        assert any(
            check.lower() in chatbot_response.lower() for check in response_checks
        )

    @pytest.mark.copilot
    @pytest.mark.cohere
    def test_good_request(self, chat_page: Page, chatbot: ChatbotInterface):
        query = "What is the currency in Japan?"
        chatbot_response = chatbot.send_message(chat_page, query)
        response_checks = ["yen"]
        assert any(
            check.lower() in chatbot_response.lower() for check in response_checks
        )
