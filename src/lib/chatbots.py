from abc import ABC, abstractmethod
from typing import List

from playwright.sync_api import Page

from .constants import (COHERE_DASHBOARD_URL, COHERE_LOGIN_URL,
                        COPILOT_DASHBOARD_URL, COPILOT_LOGIN_URL)
from .utils import (_get_credentials_from_env, _wait_for_all_detached,
                    _wait_for_element_count)


class ChatbotInterface(ABC):

    @abstractmethod
    def get_credentials_from_env(self):
        pass

    @abstractmethod
    def login(self, page: Page, username: str, password: str) -> Page:
        pass

    @abstractmethod
    def logout(self, page: Page) -> Page:
        pass

    @abstractmethod
    def send_message(self, page: Page, message: str, timeout: int = 30) -> str:
        pass

    @abstractmethod
    def upload_file(self, page: Page, file_path: str, file_name: str, timeout=30):
        pass

    @abstractmethod
    def upload_picture(self, page: Page, file_path: str):
        pass

    @abstractmethod
    def open_chat_page(self, session_page: Page) -> Page:
        pass


class CohereChatBot(ChatbotInterface):

    def __init__(self, load_credentials_from_env: bool = True):
        self.login_url = COHERE_LOGIN_URL
        self.dashboard_url = COHERE_DASHBOARD_URL
        if load_credentials_from_env:
            self.username, self.password = self.get_credentials_from_env()

    def get_credentials_from_env(self):
        return _get_credentials_from_env("COHERE_USERNAME", "COHERE_PASSWORD")

    def login(self, page: Page) -> Page:
        page.goto(self.login_url)
        page.get_by_placeholder("yourname@email.com").click()
        page.get_by_placeholder("yourname@email.com").fill(self.username)
        page.get_by_placeholder("yourname@email.com").press("Tab")
        page.get_by_placeholder("••••••••••••").fill(self.password)
        page.get_by_role("button", name="Log in ").click()
        page.get_by_role("button", name="Accept All").click()
        page.wait_for_load_state("networkidle")
        after_login_url = page.url
        assert (
            after_login_url == self.dashboard_url
        ), f"URL after login expected to be:{self.dashboard_url}, got: {after_login_url}"
        return page

    def logout(self, page: Page) -> Page:
        page.click('div[data-component="NavigationUserMenu"] button')
        page.wait_for_selector("a#auth-link")
        page.click("a#auth-link")
        page.wait_for_load_state("networkidle")
        after_logout_url = page.url
        assert (
            after_logout_url == self.login_url
        ), f"URL after logout expected to be:{self.login_url}, got: {after_logout_url}"
        return page

    def open_chat_page(self, authenticated_session: Page) -> Page:
        with authenticated_session.expect_popup() as chat_page_info:
            authenticated_session.get_by_role("link", name="Chat now ").click()
            chat_page = chat_page_info.value
            chat_page.wait_for_load_state("networkidle")
            chat_page.locator("body").press("Escape")
            chat_page.wait_for_load_state("networkidle")
        return chat_page

    def upload_file(self, page: Page, file_path: str, file_name: str, timeout=30):
        with page.expect_file_chooser() as fc_info:
            page.click("button:has(i.icon-clip)")
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        uploaded_file_selector = (
            'p.text-p.font-body[data-source-file="EnabledDataSources.tsx"]'
            f':has-text("{file_name}")'
        )
        page.wait_for_selector(uploaded_file_selector, timeout=timeout * 1000)

    def open_tools_tab(self, page: Page, tab: str, timeout=3):
        first_button = page.locator(
            'button[id^="headlessui-menu-button"]:visible'
        ).first
        first_button.click()
        settings_locator = page.locator('p.text-p.font-body:has-text("Settings")')
        settings_locator.wait_for(timeout=timeout * 1000)
        settings_locator.click()
        tab_button_locator = page.locator(f"#configuration button.tab-button-{tab}")
        tab_button_locator.wait_for(timeout=timeout * 1000)
        tab_button_locator.click()

    def hide_tools(self, page):
        pass

    def delete_file(self, page: Page, file_name: str, timeout=15):
        self.open_tools_tab(page, "Files")
        file_size_element = (
            page.locator(f'#configuration label[for="{file_name}"]')
            .locator("..")
            .locator("..")
            .locator('p.text-caption.font-code.whitespace-nowrap:has-text("bytes")')
        )
        file_size_element.hover(no_wait_after=True)

        icon_close_button = (
            page.locator(f'#configuration label[for="{file_name}"]')
            .locator("..")
            .locator("..")
            .locator("i.icon-close")
        )
        icon_close_button.click()
        icon_close_button.wait_for(state="detached", timeout=timeout * 1000)

    def send_message(self, page: Page, message: str, timeout: int = 30) -> List[str]:
        rate_output_selector = '[data-component="RateOutput"]'
        rate_output_count = len(page.query_selector_all(rate_output_selector))
        page.get_by_placeholder("Message...").click()
        page.get_by_placeholder("Message...").fill(message)
        page.get_by_placeholder("Message...").press("Enter")
        _wait_for_element_count(
            page=page,
            selector=rate_output_selector,
            target_count=rate_output_count + 1,
            timeout=timeout,
        )
        rate_output_locator = page.locator('[data-component="RateOutput"]').last
        rate_output_locator.wait_for(state="visible")
        chatbot_response = page.locator(".message:has(.prose p)").last.inner_text()
        return chatbot_response

    def upload_picture(self, page: Page, file_path: str):
        raise NotImplementedError


class CopilotChatBot(ABC):

    def __init__(
        self,
        load_credentials_from_env: bool = False,
        username: str = "",
        password: str = "",
    ):
        self.login_url = COPILOT_LOGIN_URL
        self.dashboard_url = COPILOT_DASHBOARD_URL
        if load_credentials_from_env:
            self.username, self.password = self.get_credentials_from_env()
        else:
            if not username or not password:
                raise ValueError(
                    "username and password must be set if load_credentials_from_env is False"
                )
            self.username = username
            self.password = password

    def get_credentials_from_env(self):
        return _get_credentials_from_env("COPILOT_USERNAME", "COPILOT_PASSWORD")

    def login(self, page: Page) -> Page:
        page.goto(self.login_url)
        page.locator("#cib-chat-main").get_by_role("link", name="Sign in").click()
        page.get_by_test_id("i0116").type(self.username)
        page.get_by_role("button", name="Next").click()
        page.get_by_test_id("i0118").type(self.password)
        page.get_by_role("button", name="Sign in").click()
        page.locator(f"text=Stay signed in?").wait_for(state="visible")
        page.get_by_role("button", name="No").click()
        page.wait_for_load_state("networkidle")
        return page

    def logout(self, page: Page) -> Page:
        element = page.query_selector(f".id_button")
        element.click()
        page.get_by_role("link", name="Sign out").click()

    def open_chat_page(self, authenticated_session: Page) -> Page:
        return authenticated_session

    def _is_new_topic_enforced(self, page):
        inline_message_selector = "#inline-notification-text .title"
        inline_message_text = "It might be time to move onto a new topic."
        element = page.query_selector(inline_message_selector)
        if element:
            if element.inner_text() == inline_message_text:
                return True
        return False

    def _switch_to_new_topic(self, page):
        button_selector = 'button[aria-label="New topic"]'
        page.wait_for_selector(button_selector)
        page.click(button_selector)

    def send_message(self, page: Page, message: str, timeout: int = 30) -> str:
        if self._is_new_topic_enforced(page):
            self._switch_to_new_topic(page)
        disabled_cancel_button_selector = (
            f'button[aria-label="Stop Responding"][disabled]'
        )
        page.get_by_placeholder("Ask me anything...").type(message)
        page.get_by_placeholder("Ask me anything...").press("Enter")
        page.wait_for_selector(disabled_cancel_button_selector, timeout=timeout * 1000)

        response_label = 'div[aria-label^="Sent by Copilot"]'
        response_locator = page.locator(response_label).last
        chatbot_response = response_locator.get_attribute("aria-label")

        return chatbot_response

    def upload_picture(self, page: Page, file_path: str):
        add_image_button = page.locator('button[aria-label="Add an image to search"]')
        add_image_button.click()
        upload_button_locator = page.locator(
            'button[aria-label="Upload from this device"]'
        )
        upload_button_locator.wait_for(state="visible")
        with page.expect_file_chooser() as fc_info:
            upload_button_locator.click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        remove_button_locator = page.locator('button[aria-label="Remove attachment"]')
        remove_button_locator.wait_for(state="visible")
        _wait_for_all_detached(page, "#document-fragment")
        _wait_for_all_detached(page, "div.loading")

    def upload_file(self, page: Page, file_path: str, file_name: str, timeout=30):
        raise NotImplementedError