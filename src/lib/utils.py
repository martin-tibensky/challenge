import os
import time

from playwright.sync_api import Page


def _wait_for_element_count(
    page: Page,
    selector: str,
    target_count: int,
    timeout: int = 10,
    backoff: float = 0.1,
):
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_count = len(page.query_selector_all(selector))
        if current_count >= target_count:
            return True
        time.sleep(backoff)
    raise TimeoutError(
        f"Timed out waiting for {target_count} elements with selector '{selector}'."
    )


def _get_credentials_from_env(username_variable_name, password_variable_name):
    username = os.getenv(username_variable_name)
    password = os.getenv(password_variable_name)
    assert (
        username
    ), f"{username_variable_name} environment variable is not set or empty."
    assert (
        password
    ), f"{password_variable_name} environment variable is not set or empty."
    return username, password


def _wait_for_all_detached(page, selector):
    elements = page.locator(selector)
    count = elements.count()
    for i in range(count):
        elements.nth(i).wait_for(state="hidden")
