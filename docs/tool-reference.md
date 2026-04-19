# Tool reference

88 tools across 19 modules. Full signatures live in the module docstrings
(`src/tools/*.py`); this page is a flat catalogue.

## Browser lifecycle (`browser.py`)

- `start_browser(headless, user_data_dir, proxy, browser_args, browser_executable_path)`
- `stop_browser()`
- `get_browser_status()`

## Navigation (`navigation.py`)

- `navigate(url, new_tab)`
- `go_back()`, `go_forward()`, `reload_page()`
- `get_page_info()`

## Tabs (`tabs.py`)

- `new_tab(url)`, `list_tabs()`, `switch_tab(tab_id)`, `close_tab(tab_id)`

## Elements (`elements.py`)

- `click(selector, text)`, `type_text(text, selector)`, `clear_input(selector)`
- `focus_element(selector)`, `select_option(selector, value)`
- `upload_file(selector, file_path)`

## Query (`query.py`)

- `find_element(selector)`, `find_all_elements(selector)`
- `get_element_text(selector)`, `get_element_attribute(selector, attr)`
- `find_buttons()`, `find_inputs()`

## Content (`content.py`)

- `get_content()`, `get_text_content()`
- `get_interaction_tree()` - the token-optimised DOM walker
- `scroll(direction, pixels)`, `scroll_to_element(selector)`

## Storage - legacy (`storage.py`)

`document.cookie` and `localStorage` only. For full-fidelity cookies use
the `cookies` module.

- `get_cookies()`, `set_cookie(name, value, domain)`
- `get_local_storage()`, `set_local_storage(key, value)`
- `clear_storage()`

## Logging (`logging.py`)

- `get_network_logs(limit)`, `get_console_logs(limit)`, `clear_logs()`
- `wait_for_network(url_pattern, timeout)`, `wait_for_request(url_pattern, timeout)`

## Forms (`forms.py`)

- `fill_form(fields)`, `submit_form(selector)`
- `press_key(key)`, `press_enter()`, `mouse_click(x, y)`

## Utils (`utils.py`)

- `screenshot(save_path)`, `execute_js(script)`, `wait(seconds)`
- `wait_for_element(selector, timeout)`, `run_security_audit()`

## Stealth (`stealth.py`)

- `bypass_cloudflare(timeout, click_delay)` - solve Turnstile
- `is_cloudflare_challenge_present(timeout)` - fast probe
- `set_user_agent(ua, accept_language, platform)`, `clear_user_agent()`
- `set_locale(locale)`, `set_timezone(tz)`
- `set_geolocation(lat, lon, accuracy)`

## Human-like input (`humanlike.py`)

- `human_click(selector, text, move_duration)` - bezier path + natural click
- `human_type(text, selector, wpm)` - gaussian inter-keystroke delays
- `estimated_typing_duration(char_count, wpm)`

## Emulation (`emulation.py`)

- `set_viewport(w, h, dpr, mobile)`, `restore_viewport()`
- `set_device(profile)`, `list_devices()`
  (`iphone-15-pro`, `pixel-8`, `ipad-pro`, `desktop-1080p`)
- `set_cpu_throttle(rate)`
- `set_network_conditions(profile)`, `list_network_profiles()`
  (`offline`, `slow-3g`, `fast-3g`, `4g`, `no-throttling`)
- `emulate_media(media, prefers_color_scheme)`

## DevTools (`devtools.py`)

- `start_trace(categories)`, `stop_trace(file_path)` - DevTools-loadable JSON
- `take_heap_snapshot(file_path)` - standard `.heapsnapshot`

## Lighthouse (`lighthouse.py`)

- `run_lighthouse(url, categories, form_factor, output_path)`
- `check_lighthouse_available()`

## Screencast (`screencast.py`)

- `start_screencast(output_dir, fmt, quality, max_width, every_nth_frame)`
- `stop_screencast()`

## Accessibility (`accessibility.py`)

- `get_accessibility_snapshot(max_nodes, interesting_only)`
- `click_by_uid(uid)`
- `describe_uid(uid)`

## Cookies - full fidelity (`cookies.py`)

CDP-level; sees HTTP-only cookies and all origins.

- `export_cookies(file_path)`, `import_cookies(file_path)`
- `list_all_cookies()`, `clear_all_cookies()`

## Network control (`network_control.py`)

- `block_urls(patterns)`, `unblock_all_urls()`
- `set_extra_headers(headers)`
- `bypass_service_worker(bypass)`

## Permissions (`permissions.py`)

- `grant_permissions(permissions, origin)`
- `reset_permissions()`
- `list_permission_names()`
