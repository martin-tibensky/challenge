import pytest
from ..common.test_chatbots import _TestChatbots
from playwright.sync_api import Page
from ...lib.chatbots import ChatbotInterface


@pytest.mark.cohere
class TestCohere(_TestChatbots):

    def test_upload_file(
        self, chat_page: Page, chatbot: ChatbotInterface, temp_file_with_numbers_sum
    ):
        query = "What is the sum of all numbers in this file?"
        temp_file_path, temp_file_name, total_sum = temp_file_with_numbers_sum
        chatbot.upload_file(
            chat_page, file_path=temp_file_path, file_name=temp_file_name
        )
        chatbot_response = chatbot.send_message(chat_page, query)
        assert str(total_sum) in chatbot_response
        chatbot.delete_file(chat_page, temp_file_name)
