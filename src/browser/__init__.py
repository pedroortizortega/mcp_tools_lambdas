from .navigation import browser_navigate, browser_navigate_back, browser_close, browser_tabs
from .interaction import (
    browser_click,
    browser_type,
    browser_hover,
    browser_drag,
    browser_fill_form,
    browser_select_option,
    browser_press_key,
)
from .page import browser_snapshot, browser_take_screenshot, browser_evaluate, browser_run_code, browser_resize
from .utilities import (
    browser_console_messages,
    browser_network_requests,
    browser_wait_for,
    browser_handle_dialog,
    browser_file_upload,
)
from .install import browser_install

__all__ = [
    "browser_navigate",
    "browser_navigate_back",
    "browser_close",
    "browser_tabs",
    "browser_click",
    "browser_type",
    "browser_hover",
    "browser_drag",
    "browser_fill_form",
    "browser_select_option",
    "browser_press_key",
    "browser_snapshot",
    "browser_take_screenshot",
    "browser_evaluate",
    "browser_run_code",
    "browser_resize",
    "browser_console_messages",
    "browser_network_requests",
    "browser_wait_for",
    "browser_handle_dialog",
    "browser_file_upload",
    "browser_install",
]
