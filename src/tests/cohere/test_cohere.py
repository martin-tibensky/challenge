import logging
import os
import time

import pytest
from playwright.sync_api import Page

from ...lib.chatbots import CohereChatBot

log = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def chat_page(authenticated_session):
    with authenticated_session.expect_popup() as chat_page_info:
        authenticated_session.get_by_role("link", name="Chat now ").click()
        chat_page = chat_page_info.value
        chat_page.wait_for_load_state("networkidle")
        chat_page.locator("body").press("Escape")
        chat_page.wait_for_load_state("networkidle")
        yield chat_page
        chat_page.close()


def test_cohere_bad_request(chat_page: Page, chatbot: CohereChatBot):
    query = "dklwknddajdwmdnfwa"
    chatbot_response = chatbot.send_message(page=chat_page, message=query)
    response_checks = ["sorry", "apologize"]
    assert any(check.lower() in chatbot_response.lower() for check in response_checks)


def test_cohere_good_request(chat_page: Page, chatbot: CohereChatBot):
    query = "What is the currency in Japan?"
    chatbot_response = chatbot.send_message(chat_page, query)
    response_checks = ["yen"]
    assert any(check.lower() in chatbot_response.lower() for check in response_checks)


def test_cohere_file_upload(
    chat_page: Page, chatbot: CohereChatBot, temp_file_with_numbers_sum: str
):
    query = "What is the sum of all numbers in this file?"
    temp_file_path, temp_file_name, total_sum = temp_file_with_numbers_sum
    chatbot.upload_file(chat_page, file_path=temp_file_path, file_name=temp_file_name)
    chatbot_response = chatbot.send_message(chat_page, query)
    assert str(total_sum) in chatbot_response
    chatbot.delete_file(chat_page, temp_file_name)
