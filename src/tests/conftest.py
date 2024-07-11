import os
from pathlib import Path

import pytest
from playwright.sync_api import BrowserContext, Page

from ..lib.chatbots import ChatbotInterface, CohereChatBot, CopilotChatBot


@pytest.fixture(scope="module")
def browser_context(browser):
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="module")
def chatbot(request):
    # Get the directory name of the current test module
    test_dir = os.path.basename(os.path.dirname(request.module.__file__))

    if test_dir == "cohere":
        return CohereChatBot(load_credentials_from_env=True)
    elif test_dir == "copilot":
        return CopilotChatBot(load_credentials_from_env=True)
    else:
        raise ValueError(f"Unknown test directory: {test_dir}")


@pytest.fixture(scope="module")
def chat_page(authenticated_session: Page, chatbot: ChatbotInterface):
    page = chatbot.open_chat_page(authenticated_session)
    yield page
    page.close()


@pytest.fixture(scope="module")
def authenticated_session(browser_context: BrowserContext, chatbot: CohereChatBot):
    page = browser_context.new_page()
    page = chatbot.login(page)
    yield page
    page = chatbot.logout(page)
    page.close()


@pytest.fixture
def temp_file_with_numbers_sum(tmp_path: Path):
    temp_file_path = Path(tmp_path, "numbers.txt")
    numbers = [10, 8, 7, 9, 8]
    numbers_sum = sum(numbers)
    with temp_file_path.open("w") as temp_file:
        for number in numbers:
            temp_file.write(f"{number}\n")
    yield (temp_file_path, temp_file_path.name, numbers_sum)


@pytest.fixture
def data_path():
    return os.path.join(os.path.dirname(__file__), "test_data")


@pytest.fixture
def picture_path(data_path):
    return os.path.join(data_path, "secret_image.png")
