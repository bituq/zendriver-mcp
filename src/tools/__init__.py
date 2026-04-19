# tools package - modular browser automation tools for Zendriver MCP server
from mcp.server.fastmcp import FastMCP

from src.tools.accessibility import AccessibilityTools
from src.tools.base import ToolBase
from src.tools.browser import BrowserTools
from src.tools.content import ContentTools
from src.tools.cookies import CookieTools
from src.tools.devtools import DevToolsTools
from src.tools.elements import ElementTools
from src.tools.emulation import EmulationTools
from src.tools.forms import FormTools
from src.tools.humanlike import HumanInputTools
from src.tools.lighthouse import LighthouseTools
from src.tools.logging import LoggingTools
from src.tools.navigation import NavigationTools
from src.tools.network_control import NetworkControlTools
from src.tools.permissions import PermissionsTools
from src.tools.query import QueryTools
from src.tools.screencast import ScreencastTools
from src.tools.stealth import StealthTools
from src.tools.storage import StorageTools
from src.tools.tabs import TabTools
from src.tools.utils import UtilityTools

# initialize the MCP server
mcp = FastMCP("Zendriver MCP")

# register all tool modules and keep instances for backwards compatibility
_browser_tools = BrowserTools(mcp)
_navigation_tools = NavigationTools(mcp)
_tab_tools = TabTools(mcp)
_element_tools = ElementTools(mcp)
_query_tools = QueryTools(mcp)
_content_tools = ContentTools(mcp)
_storage_tools = StorageTools(mcp)
_logging_tools = LoggingTools(mcp)
_form_tools = FormTools(mcp)
_utility_tools = UtilityTools(mcp)
_stealth_tools = StealthTools(mcp)
_human_input_tools = HumanInputTools(mcp)
_emulation_tools = EmulationTools(mcp)
_devtools_tools = DevToolsTools(mcp)
_lighthouse_tools = LighthouseTools(mcp)
_screencast_tools = ScreencastTools(mcp)
_accessibility_tools = AccessibilityTools(mcp)
_cookie_tools = CookieTools(mcp)
_network_control_tools = NetworkControlTools(mcp)
_permissions_tools = PermissionsTools(mcp)

# export individual tool functions for backwards compatibility
# browser lifecycle
start_browser = _browser_tools.start_browser
stop_browser = _browser_tools.stop_browser
get_browser_status = _browser_tools.get_browser_status

# navigation
navigate = _navigation_tools.navigate
go_back = _navigation_tools.go_back
go_forward = _navigation_tools.go_forward
reload_page = _navigation_tools.reload_page
get_page_info = _navigation_tools.get_page_info

# tabs
new_tab = _tab_tools.new_tab
list_tabs = _tab_tools.list_tabs
switch_tab = _tab_tools.switch_tab
close_tab = _tab_tools.close_tab

# elements
click = _element_tools.click
type_text = _element_tools.type_text
clear_input = _element_tools.clear_input
focus_element = _element_tools.focus_element
select_option = _element_tools.select_option
upload_file = _element_tools.upload_file

# query
find_element = _query_tools.find_element
find_all_elements = _query_tools.find_all_elements
get_element_text = _query_tools.get_element_text
get_element_attribute = _query_tools.get_element_attribute
find_buttons = _query_tools.find_buttons
find_inputs = _query_tools.find_inputs

# content
get_content = _content_tools.get_content
get_text_content = _content_tools.get_text_content
get_interaction_tree = _content_tools.get_interaction_tree
scroll = _content_tools.scroll
scroll_to_element = _content_tools.scroll_to_element

# storage
get_cookies = _storage_tools.get_cookies
set_cookie = _storage_tools.set_cookie
get_local_storage = _storage_tools.get_local_storage
set_local_storage = _storage_tools.set_local_storage
clear_storage = _storage_tools.clear_storage

# logging
get_network_logs = _logging_tools.get_network_logs
get_console_logs = _logging_tools.get_console_logs
clear_logs = _logging_tools.clear_logs
wait_for_network = _logging_tools.wait_for_network
wait_for_request = _logging_tools.wait_for_request

# forms
fill_form = _form_tools.fill_form
submit_form = _form_tools.submit_form
press_key = _form_tools.press_key
press_enter = _form_tools.press_enter
mouse_click = _form_tools.mouse_click

# utils
screenshot = _utility_tools.screenshot
execute_js = _utility_tools.execute_js
wait = _utility_tools.wait
wait_for_element = _utility_tools.wait_for_element
run_security_audit = _utility_tools.run_security_audit

# stealth
bypass_cloudflare = _stealth_tools.bypass_cloudflare
is_cloudflare_challenge_present = _stealth_tools.is_cloudflare_challenge_present
set_user_agent = _stealth_tools.set_user_agent
clear_user_agent = _stealth_tools.clear_user_agent
set_locale = _stealth_tools.set_locale
set_timezone = _stealth_tools.set_timezone
set_geolocation = _stealth_tools.set_geolocation

# human input
human_click = _human_input_tools.human_click
human_type = _human_input_tools.human_type
estimated_typing_duration = _human_input_tools.estimated_typing_duration

# emulation
set_viewport = _emulation_tools.set_viewport
restore_viewport = _emulation_tools.restore_viewport
set_device = _emulation_tools.set_device
list_devices = _emulation_tools.list_devices
set_cpu_throttle = _emulation_tools.set_cpu_throttle
set_network_conditions = _emulation_tools.set_network_conditions
list_network_profiles = _emulation_tools.list_network_profiles
emulate_media = _emulation_tools.emulate_media

# devtools
start_trace = _devtools_tools.start_trace
stop_trace = _devtools_tools.stop_trace
take_heap_snapshot = _devtools_tools.take_heap_snapshot

# lighthouse
run_lighthouse = _lighthouse_tools.run_lighthouse
check_lighthouse_available = _lighthouse_tools.check_lighthouse_available

# screencast
start_screencast = _screencast_tools.start_screencast
stop_screencast = _screencast_tools.stop_screencast

# accessibility uids
get_accessibility_snapshot = _accessibility_tools.get_accessibility_snapshot
click_by_uid = _accessibility_tools.click_by_uid
describe_uid = _accessibility_tools.describe_uid

# cookies (full fidelity, including HTTP-only)
export_cookies = _cookie_tools.export_cookies
import_cookies = _cookie_tools.import_cookies
list_all_cookies = _cookie_tools.list_all_cookies
clear_all_cookies = _cookie_tools.clear_all_cookies

# network controls
block_urls = _network_control_tools.block_urls
unblock_all_urls = _network_control_tools.unblock_all_urls
set_extra_headers = _network_control_tools.set_extra_headers
bypass_service_worker = _network_control_tools.bypass_service_worker

# permissions
grant_permissions = _permissions_tools.grant_permissions
reset_permissions = _permissions_tools.reset_permissions
list_permission_names = _permissions_tools.list_permission_names

__all__ = [
    # mcp server
    "mcp",
    # base class
    "ToolBase",
    # tool classes
    "BrowserTools",
    "NavigationTools",
    "TabTools",
    "ElementTools",
    "QueryTools",
    "ContentTools",
    "StorageTools",
    "LoggingTools",
    "FormTools",
    "UtilityTools",
    "StealthTools",
    "HumanInputTools",
    "EmulationTools",
    "DevToolsTools",
    "LighthouseTools",
    "ScreencastTools",
    "AccessibilityTools",
    "CookieTools",
    "NetworkControlTools",
    "PermissionsTools",
    # individual tool functions
    "start_browser",
    "stop_browser",
    "get_browser_status",
    "navigate",
    "go_back",
    "go_forward",
    "reload_page",
    "get_page_info",
    "new_tab",
    "list_tabs",
    "switch_tab",
    "close_tab",
    "click",
    "type_text",
    "clear_input",
    "focus_element",
    "select_option",
    "upload_file",
    "find_element",
    "find_all_elements",
    "get_element_text",
    "get_element_attribute",
    "find_buttons",
    "find_inputs",
    "get_content",
    "get_text_content",
    "get_interaction_tree",
    "scroll",
    "scroll_to_element",
    "get_cookies",
    "set_cookie",
    "get_local_storage",
    "set_local_storage",
    "clear_storage",
    "get_network_logs",
    "get_console_logs",
    "clear_logs",
    "wait_for_network",
    "wait_for_request",
    "fill_form",
    "submit_form",
    "press_key",
    "press_enter",
    "mouse_click",
    "screenshot",
    "execute_js",
    "wait",
    "wait_for_element",
    "run_security_audit",
    "bypass_cloudflare",
    "is_cloudflare_challenge_present",
    "set_user_agent",
    "clear_user_agent",
    "set_locale",
    "set_timezone",
    "set_geolocation",
    "human_click",
    "human_type",
    "estimated_typing_duration",
    "set_viewport",
    "restore_viewport",
    "set_device",
    "list_devices",
    "set_cpu_throttle",
    "set_network_conditions",
    "list_network_profiles",
    "emulate_media",
    "start_trace",
    "stop_trace",
    "take_heap_snapshot",
    "run_lighthouse",
    "check_lighthouse_available",
    "start_screencast",
    "stop_screencast",
    "get_accessibility_snapshot",
    "click_by_uid",
    "describe_uid",
    "export_cookies",
    "import_cookies",
    "list_all_cookies",
    "clear_all_cookies",
    "block_urls",
    "unblock_all_urls",
    "set_extra_headers",
    "bypass_service_worker",
    "grant_permissions",
    "reset_permissions",
    "list_permission_names",
]
