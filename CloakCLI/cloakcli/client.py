"""SDK client for CloakBrowser Manager REST API."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import httpx

from .config import Config
from .errors import _raise_for_status
from .models import (
    ClipboardRequest,
    LaunchResult,
    Profile,
    ProfileCreate,
    ProfileStatus,
    ProfileUpdate,
    SystemStatus,
)


class ProfileAPI:
    """Profile CRUD operations. Access via client.profiles."""
    def __init__(self, client: CloakBrowserManagerClient):
        self._client = client
        self._http = client._http

    def list(self) -> list[Profile]:
        r = self._http.get("/api/profiles")
        _raise_for_status(r.status_code, r.text)
        return [Profile(**item) for item in r.json()]

    def get(self, profile_id: str) -> Profile:
        r = self._http.get(f"/api/profiles/{profile_id}")
        _raise_for_status(r.status_code, r.text)
        return Profile(**r.json())

    def create(self, **kwargs: Any) -> Profile:
        body = ProfileCreate(**kwargs).model_dump(exclude_none=True)
        r = self._http.post("/api/profiles", json=body)
        _raise_for_status(r.status_code, r.text)
        return Profile(**r.json())

    def update(self, profile_id: str, **kwargs: Any) -> Profile:
        body = ProfileUpdate(**kwargs).model_dump(exclude_unset=True)
        r = self._http.put(f"/api/profiles/{profile_id}", json=body)
        _raise_for_status(r.status_code, r.text)
        return Profile(**r.json())

    def delete(self, profile_id: str) -> bool:
        r = self._http.delete(f"/api/profiles/{profile_id}")
        _raise_for_status(r.status_code, r.text)
        return True


class ClipboardAPI:
    """Clipboard read/write. Access via client.clipboard."""
    def __init__(self, client: CloakBrowserManagerClient):
        self._http = client._http

    def read(self, profile_id: str) -> str:
        r = self._http.get(f"/api/profiles/{profile_id}/clipboard")
        _raise_for_status(r.status_code, r.text)
        return r.json().get("text", "")

    def write(self, profile_id: str, text: str) -> None:
        body = ClipboardRequest(text=text).model_dump()
        r = self._http.post(f"/api/profiles/{profile_id}/clipboard", json=body)
        _raise_for_status(r.status_code, r.text)


class RunAPI:
    """Browser automation via CDP with humanize support.

    Each method opens a CDP connection, applies humanize (unless fast=True),
    executes the operation, and closes the connection.
    """

    def __init__(self, client: CloakBrowserManagerClient):
        self._client = client

    async def _with_page(self, profile_id: str, fast: bool = False):
        """Connect to profile via CDP, optionally apply humanize, return (browser, page)."""
        # Get profile config
        profile = self._client.profiles.get(profile_id)
        # Get CDP URL
        r = self._client._http.get(f"/api/profiles/{profile_id}/cdp")
        from .errors import _raise_for_status
        _raise_for_status(r.status_code, r.text)
        cdp_info = r.json()
        cdp_url = cdp_info.get("cdp_url", f"http://{self._client._http.base_url.host}:{self._client._http.base_url.port}/api/profiles/{profile_id}/cdp")

        from playwright.async_api import async_playwright
        pw = await async_playwright().start()
        browser = await pw.chromium.connect_over_cdp(cdp_url)

        if not fast:
            if profile.humanize:
                try:
                    from cloakbrowser import humanize_browser
                    humanize_browser(browser, human_preset=profile.human_preset)
                except ImportError:
                    # fallback: connect_and_humanize not yet available, use direct patch
                    pass

        # Get active page
        if browser.contexts:
            pages = browser.contexts[0].pages
            page = pages[-1] if pages else await browser.contexts[0].new_page()
        else:
            ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await ctx.new_page()

        return browser, page

    # --- Navigation ---
    async def open(self, profile_id: str, url: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.goto(url)
        finally:
            await browser.close()

    async def back(self, profile_id: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.go_back()
        finally:
            await browser.close()

    async def forward(self, profile_id: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.go_forward()
        finally:
            await browser.close()

    async def reload(self, profile_id: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.reload()
        finally:
            await browser.close()

    # --- Interactions ---
    async def click(self, profile_id: str, selector: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.click(selector)
        finally:
            await browser.close()

    async def dblclick(self, profile_id: str, selector: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.dblclick(selector)
        finally:
            await browser.close()

    async def type(self, profile_id: str, selector: str, text: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.type(selector, text)
        finally:
            await browser.close()

    async def fill(self, profile_id: str, selector: str, text: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.fill(selector, text)
        finally:
            await browser.close()

    async def press(self, profile_id: str, key: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.keyboard.press(key)
        finally:
            await browser.close()

    async def hover(self, profile_id: str, selector: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.hover(selector)
        finally:
            await browser.close()

    async def focus(self, profile_id: str, selector: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.focus(selector)
        finally:
            await browser.close()

    async def select(self, profile_id: str, selector: str, value: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.select_option(selector, value)
        finally:
            await browser.close()

    async def check(self, profile_id: str, selector: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.check(selector)
        finally:
            await browser.close()

    async def uncheck(self, profile_id: str, selector: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.uncheck(selector)
        finally:
            await browser.close()

    # --- Info ---
    async def get_text(self, profile_id: str, selector: str) -> str:
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            return await page.text_content(selector) or ""
        finally:
            await browser.close()

    async def get_html(self, profile_id: str, selector: str) -> str:
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            return await page.inner_html(selector)
        finally:
            await browser.close()

    async def get_value(self, profile_id: str, selector: str) -> str:
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            return await page.input_value(selector)
        finally:
            await browser.close()

    async def get_attr(self, profile_id: str, selector: str, name: str) -> str | None:
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            return await page.get_attribute(selector, name)
        finally:
            await browser.close()

    async def get_title(self, profile_id: str) -> str:
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            return await page.title()
        finally:
            await browser.close()

    async def get_url(self, profile_id: str) -> str:
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            return page.url
        finally:
            await browser.close()

    async def get_count(self, profile_id: str, selector: str) -> int:
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            return await page.locator(selector).count()
        finally:
            await browser.close()

    async def get_box(self, profile_id: str, selector: str) -> dict | None:
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            box = await page.locator(selector).first.bounding_box()
            return box
        finally:
            await browser.close()

    # --- Capture ---
    async def snapshot(
        self,
        profile_id: str,
        interactive_only: bool = False,
        compact: bool = False,
        max_depth: int | None = None,
        scope: str | None = None,
    ) -> str:
        """Generate accessibility tree snapshot compatible with agent-browser format."""
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            js = _SNAPSHOT_JS
            args = {
                "interactiveOnly": interactive_only,
                "compact": compact,
                "maxDepth": max_depth,
                "scope": scope,
            }
            return await page.evaluate(js, args)
        finally:
            await browser.close()

    async def screenshot(self, profile_id: str, path: str | None = None, full: bool = False, fast: bool = False) -> str:
        import time
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            dest = path or f"screenshot-{int(time.time() * 1000)}.png"
            await page.screenshot(path=dest, full_page=full)
            return dest
        finally:
            await browser.close()

    async def pdf(self, profile_id: str, path: str, fast: bool = False) -> str:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.pdf(path=path)
            return path
        finally:
            await browser.close()

    async def eval(self, profile_id: str, code: str, fast: bool = False) -> Any:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            return await page.evaluate(code)
        finally:
            await browser.close()

    # --- Tab ---
    async def tab_list(self, profile_id: str) -> list[dict]:
        browser, page = await self._with_page(profile_id, fast=True)
        try:
            tabs = []
            for i, ctx in enumerate(browser.contexts):
                for j, p in enumerate(ctx.pages):
                    tabs.append({
                        "index": f"t{i * len(ctx.pages) + j + 1}",
                        "title": await p.title(),
                        "url": p.url,
                        "active": p == page,
                    })
            return tabs
        finally:
            await browser.close()

    async def tab_new(self, profile_id: str, url: str | None = None, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            new_page = await browser.contexts[0].new_page()
            if url:
                await new_page.goto(url)
        finally:
            await browser.close()

    async def tab_switch(self, profile_id: str, tab_ref: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            pages = browser.contexts[0].pages
            idx = int(tab_ref.lstrip("t")) - 1
            if 0 <= idx < len(pages):
                await pages[idx].bring_to_front()
        finally:
            await browser.close()

    async def tab_close(self, profile_id: str, tab_ref: str | None = None, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            if tab_ref is None:
                await page.close()
            else:
                pages = browser.contexts[0].pages
                idx = int(tab_ref.lstrip("t")) - 1
                if 0 <= idx < len(pages):
                    await pages[idx].close()
        finally:
            await browser.close()

    async def window_new(self, profile_id: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await browser.new_context()
        finally:
            await browser.close()

    # --- Util ---
    async def wait(self, profile_id: str, target: str, fast: bool = False,
                   load_state: str | None = None, state: str = "visible") -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            if target.isdigit():
                await page.wait_for_timeout(int(target))
            elif load_state:
                await page.wait_for_load_state(load_state)
            else:
                await page.wait_for_selector(target, state=state)
        finally:
            await browser.close()

    async def scroll(self, profile_id: str, direction: str, px: int = 300, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            deltas = {"up": (0, -px), "down": (0, px), "left": (-px, 0), "right": (px, 0)}
            dx, dy = deltas.get(direction, (0, px))
            await page.mouse.wheel(dx, dy)
        finally:
            await browser.close()

    async def scrollintoview(self, profile_id: str, selector: str, fast: bool = False) -> None:
        browser, page = await self._with_page(profile_id, fast=fast)
        try:
            await page.locator(selector).first.scroll_into_view_if_needed()
        finally:
            await browser.close()

    # --- Batch ---
    async def batch(self, profile_id: str, commands: list[list], fast: bool = False) -> list[Any]:
        """Execute multiple commands in a single CDP connection."""
        browser, page = await self._with_page(profile_id, fast=fast)
        results = []
        try:
            for cmd in commands:
                action = cmd[0]
                args = cmd[1:]
                method = getattr(self, action, None)
                if method is None:
                    results.append({"error": f"Unknown action: {action}"})
                    continue
                try:
                    # Call with same browser/page context
                    if action in ("open",):
                        await page.goto(args[0])
                        results.append(None)
                    elif action in ("back",):
                        await page.go_back()
                        results.append(None)
                    elif action in ("click",):
                        await page.click(args[0])
                        results.append(None)
                    elif action in ("type",):
                        await page.type(args[0], args[1] if len(args) > 1 else "")
                        results.append(None)
                    elif action in ("fill",):
                        await page.fill(args[0], args[1] if len(args) > 1 else "")
                        results.append(None)
                    elif action in ("screenshot",):
                        path = args[0] if args else f"screenshot-{id(cmd)}.png"
                        await page.screenshot(path=path)
                        results.append(path)
                    elif action in ("snapshot",):
                        interactive_only = "-i" in args
                        result = await page.evaluate(_SNAPSHOT_JS, {"interactiveOnly": interactive_only})
                        results.append(result)
                    elif action in ("wait",):
                        if args and args[0].isdigit():
                            await page.wait_for_timeout(int(args[0]))
                        elif args:
                            await page.wait_for_selector(args[0])
                        results.append(None)
                    else:
                        results.append({"error": f"Batch action not implemented: {action}"})
                except Exception as e:
                    results.append({"error": str(e)})
        finally:
            await browser.close()
        return results


class CloakBrowserManagerClient:
    """Client for CloakBrowser Manager REST API.

    Usage:
        client = CloakBrowserManagerClient(host="http://localhost:8080", token="secret")
        profiles = client.profiles.list()
        client.launch("profile-id")
    """

    def __init__(
        self,
        host: str = "http://localhost:8080",
        token: str | None = None,
        timeout: float = 30.0,
    ):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._http = httpx.Client(
            base_url=host.rstrip("/"),
            headers=headers,
            timeout=timeout,
        )
        self.profiles = ProfileAPI(self)
        self.clipboard = ClipboardAPI(self)
        self.run = RunAPI(self)

    @classmethod
    def from_config(cls, config: Config, timeout: float = 30.0) -> CloakBrowserManagerClient:
        return cls(host=config.host, token=config.token, timeout=timeout)

    def launch(self, profile_id: str) -> LaunchResult:
        r = self._http.post(f"/api/profiles/{profile_id}/launch")
        _raise_for_status(r.status_code, r.text)
        return LaunchResult(**r.json())

    def stop(self, profile_id: str) -> bool:
        r = self._http.post(f"/api/profiles/{profile_id}/stop")
        _raise_for_status(r.status_code, r.text)
        return True

    def status(self, profile_id: str | None = None) -> SystemStatus | ProfileStatus:
        if profile_id is None:
            r = self._http.get("/api/status")
            _raise_for_status(r.status_code, r.text)
            return SystemStatus(**r.json())
        r = self._http.get(f"/api/profiles/{profile_id}/status")
        _raise_for_status(r.status_code, r.text)
        return ProfileStatus(**r.json())

    def close(self) -> None:
        self._http.close()

    async def connect(self, profile_id: str) -> Any:
        """Connect to a running profile via CDP and return a humanize-patched Browser."""
        from playwright.async_api import async_playwright

        profile = self.profiles.get(profile_id)
        r = self._http.get(f"/api/profiles/{profile_id}/cdp")
        _raise_for_status(r.status_code, r.text)
        cdp_url = r.json().get("cdp_url",
            f"http://{self._http.base_url.host}:{self._http.base_url.port}/api/profiles/{profile_id}/cdp")

        class _BrowserWrapper:
            def __init__(self, pw, browser, profile_data):
                self._pw = pw
                self.browser = browser
                self._profile = profile_data
            @property
            def contexts(self): return self.browser.contexts
            async def close(self): await self.browser.close(); await self._pw.stop()
            async def new_page(self):
                if self.browser.contexts:
                    return await self.browser.contexts[0].new_page()
                ctx = await self.browser.new_context()
                return await ctx.new_page()

        pw = await async_playwright().start()
        browser = await pw.chromium.connect_over_cdp(cdp_url)
        if profile.humanize:
            try:
                from cloakbrowser import humanize_browser
                humanize_browser(browser, human_preset=profile.human_preset)
            except ImportError:
                pass
        return _BrowserWrapper(pw, browser, profile)


# JavaScript for generating accessibility tree snapshots (agent-browser compatible)
_SNAPSHOT_JS = r"""
(args) => {
    const interactiveRoles = new Set([
        'button', 'link', 'textbox', 'searchbox', 'combobox', 'listbox',
        'menuitem', 'option', 'radio', 'switch', 'tab', 'menuitemcheckbox',
        'menuitemradio', 'treeitem', 'checkbox', 'option', 'spinbutton',
        'slider', 'gridcell', 'heading', 'img', 'listitem'
    ]);
    let refCounter = 0;
    function walk(node, depth, scopeSelector) {
        if (scopeSelector && depth === 0) {
            const match = document.querySelector(scopeSelector);
            if (match && match !== node) return null;
        }
        if (args.maxDepth != null && depth > args.maxDepth) return null;
        let role = (node.getAttribute('role') || node.tagName.toLowerCase() || '').trim();
        let name = (node.getAttribute('aria-label') || node.getAttribute('name') || node.title || '').trim();
        if (!name && (role === 'link' || role === 'button')) {
            name = node.textContent.trim().slice(0, 100);
        }
        if (!name && role === 'img') name = node.getAttribute('alt') || '';
        if (args.interactiveOnly && !interactiveRoles.has(role) && role !== 'document') return null;
        if (args.compact && !name && !interactiveRoles.has(role) && role !== 'document') {
            const kids = [];
            for (const child of node.children) {
                const result = walk(child, depth + 1, null);
                if (result) kids.push(...result);
            }
            return kids.length ? kids : null;
        }
        const r = [];
        const hasRef = interactiveRoles.has(role) || role === 'link' || role === 'button' || role === 'textbox' || role === 'img';
        if (hasRef) {
            refCounter++;
            node.setAttribute('data-snapshot-ref', 'e' + refCounter);
        }
        let line = '- ' + role;
        if (name) line += ' "' + name + '"';
        if (hasRef) line += ' [@e' + refCounter + ']';
        if (role === 'link' && node.href) line += ' -> ' + node.href;
        r.push(line);
        for (const child of node.children) {
            const kids = walk(child, depth + 1, null);
            if (kids) {
                for (const k of kids) r.push('  ' + k);
            }
        }
        return r;
    }
    const result = walk(document.body, 0, args.scope);
    return result ? result.join('\n') : '';
}
"""
