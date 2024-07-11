import pytest
from playwright.sync_api import Page

from ...lib.chatbots import CopilotChatBot


@pytest.fixture(scope="module")
def chat_page(authenticated_session: Page):
    yield authenticated_session


def test_copilot_bad_request(chat_page: Page, chatbot: CopilotChatBot) -> None:
    query = "dklwknddawmdnfwa"
    chatbot_response = chatbot.send_message(page=chat_page, message=query, timeout=90)
    response_checks = ["sorry", "apologize"]
    assert any(check.lower() in chatbot_response.lower() for check in response_checks)


def test_copilot_good_request(chat_page: Page, chatbot: CopilotChatBot):
    query = "What is the currency in Japan?"
    chatbot_response = chatbot.send_message(chat_page, query, timeout=90)
    response_check = "yen"
    assert response_check.lower() in chatbot_response.lower()


def test_copilot_picture(chat_page: Page, chatbot: CopilotChatBot, picture_path: str):
    chatbot.upload_picture(chat_page, file_path=picture_path)
    query = "What is on the picture?"
    chatbot_response = chatbot.send_message(chat_page, query, timeout=90)
    response_check = "flag"
    assert response_check.lower() in chatbot_response.lower()
