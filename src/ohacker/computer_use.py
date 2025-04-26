import asyncio
import base64
from typing import Literal, Optional  # Added Optional

from agents import (
    AsyncComputer,
    Button,
    Environment,
)
from playwright.async_api import Browser, Page, Playwright, async_playwright

# CUA_KEY_TO_PLAYWRIGHT_KEY remains the same...
CUA_KEY_TO_PLAYWRIGHT_KEY = {
    "/": "Divide",
    "\\": "Backslash",
    "alt": "Alt",
    "arrowdown": "ArrowDown",
    "arrowleft": "ArrowLeft",
    "arrowright": "ArrowRight",
    "arrowup": "ArrowUp",
    "backspace": "Backspace",
    "capslock": "CapsLock",
    "cmd": "Meta",
    "ctrl": "Control",
    "delete": "Delete",
    "end": "End",
    "enter": "Enter",
    "esc": "Escape",
    "home": "Home",
    "insert": "Insert",
    "option": "Alt",
    "pagedown": "PageDown",
    "pageup": "PageUp",
    "shift": "Shift",
    "space": " ",
    "super": "Meta",
    "tab": "Tab",
    "win": "Meta",
    **{f"f{i}": f"F{i}" for i in range(1, 13)},
    **{str(i): str(i) for i in range(10)},
    **{chr(c): chr(c) for c in range(ord("a"), ord("z") + 1)},
}


class LocalPlaywrightComputer(AsyncComputer):
    """A computer, implemented using a local Playwright browser."""

    # --- MODIFICATION: Accept target_url in __init__ ---
    def __init__(self, target_url: str):
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._page: Page | None = None
        self._target_url: str = target_url

    # _get_browser_and_page remains largely the same, uses self._target_url
    async def _get_browser_and_page(self) -> tuple[Browser, Page]:
        if not self._target_url:
            raise ValueError("Target URL was not set during initialization.")
        width, height = self.dimensions
        launch_args = [f"--window-size={width},{height}"]
        try:
            # Ensure playwright instance exists before launching browser
            if self._playwright is None:
                raise RuntimeError("Playwright instance not available in _get_browser_and_page.")
            browser = await self._playwright.chromium.launch(headless=False, args=launch_args)
        except Exception as e:
            print(f"Error launching Playwright browser: {e}")
            print("Ensure Playwright browsers are installed ('playwright install')")
            raise
        try:
            page = await browser.new_page()
            await page.set_viewport_size({"width": width, "height": height})
            print(f"Navigating to target URL: {self._target_url}")
            # Increased timeout slightly for potentially slower local setups
            await page.goto(self._target_url, wait_until="domcontentloaded", timeout=60000)

            print(f"Successfully navigated to {self._target_url}")
        except Exception as e:
            print(f"Error navigating to {self._target_url}: {e}")
            await browser.close()  # Clean up browser if navigation fails
            raise
        return browser, page

    # --- MODIFICATION: Move startup logic into __aenter__ ---
    async def __aenter__(self):
        """Starts Playwright, launches browser, and navigates upon entering context."""
        if self._playwright or self._browser:
            print("Computer context already entered.")
            return self  # Already initialized

        print("Starting Playwright...")
        try:
            # Important: Check if Playwright is already running (less likely here, but good practice)
            if self._playwright is None:
                self._playwright = await async_playwright().start()
            else:
                print("Playwright instance already exists.")

            print("Launching browser and navigating...")
            self._browser, self._page = await self._get_browser_and_page()
            print("Computer ready.")
        except Exception as e:
            print(f"Error during computer startup (__aenter__): {e}")
            # Attempt cleanup if startup failed
            await self.__aexit__(type(e), e, e.__traceback__)
            raise  # Re-raise the exception
        return self  # Required for 'async with'

    # __aexit__ remains the same
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Closing browser and stopping Playwright...")
        # Use Optional type hint now
        browser: Optional[Browser] = self._browser
        playwright: Optional[Playwright] = self._playwright

        self._page = None  # Clear page reference first
        self._browser = None
        self._playwright = None

        if browser:
            try:
                await browser.close()
            except Exception as e:
                print(f"Error closing browser: {e}")  # Log error but continue cleanup
        if playwright:
            try:
                await playwright.stop()
            except Exception as e:
                print(f"Error stopping playwright: {e}")
        print("Computer stopped.")

    # Properties remain the same...
    @property
    def playwright(self) -> Playwright:
        if self._playwright is None:
            raise RuntimeError("Playwright not started. Use 'async with computer:' context.")
        return self._playwright

    @property
    def browser(self) -> Browser:
        if self._browser is None:
            raise RuntimeError("Browser not available. Use 'async with computer:' context.")
        return self._browser

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Page not available. Use 'async with computer:' context.")
        return self._page

    @property
    def environment(self) -> Environment:
        return "browser"

    @property
    def dimensions(self) -> tuple[int, int]:
        # Standard viewport size
        return (1080, 1080)

    # screenshot, click, double_click, scroll, type, wait, move, keypress, drag methods remain the same...
    async def screenshot(self) -> str:
        # print("Taking screenshot...")
        try:
            png_bytes = await self.page.screenshot(full_page=False)
            with open("screen.png", "wb") as f:
                f.write(png_bytes)

            b64_string = base64.b64encode(png_bytes).decode("utf-8")
            # print("Screenshot taken.")
            return b64_string
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return ""

    async def click(self, x: int, y: int, button: Button = "left") -> None:
        print(f"Clicking at ({x}, {y}) with {button} button...")
        playwright_button: Literal["left", "middle", "right"] = "left"
        if button in ("left", "right", "middle"):
            playwright_button = button
        try:
            await self.page.mouse.click(x, y, button=playwright_button)
            print("Click successful.")
        except Exception as e:
            print(f"Error clicking at ({x}, {y}): {e}")

    async def double_click(self, x: int, y: int) -> None:
        print(f"Double clicking at ({x}, {y})...")
        try:
            await self.page.mouse.dblclick(x, y)
            print("Double click successful.")
        except Exception as e:
            print(f"Error double clicking at ({x}, {y}): {e}")

    async def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        print(f"Scrolling by ({scroll_x}, {scroll_y}) from ({x}, {y})...")
        try:
            await self.page.mouse.move(x, y)
            await self.page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")
            print("Scroll successful.")
        except Exception as e:
            print(f"Error scrolling: {e}")

    async def type(self, text: str) -> None:
        print(f"Typing text: '{text[:50]}{'...' if len(text) > 50 else ''}'...")
        try:
            await self.page.keyboard.type(text)
            print("Typing successful.")
        except Exception as e:
            print(f"Error typing text: {e}")

    async def wait(self) -> None:
        print("Waiting for 1 second...")
        await asyncio.sleep(1)
        print("Wait finished.")

    async def move(self, x: int, y: int) -> None:
        print(f"Moving mouse to ({x}, {y})...")
        try:
            await self.page.mouse.move(x, y)
            print("Mouse move successful.")
        except Exception as e:
            print(f"Error moving mouse to ({x}, {y}): {e}")

    async def keypress(self, keys: list[str]) -> None:
        if not keys:
            return
        mapped_keys = [CUA_KEY_TO_PLAYWRIGHT_KEY.get(key.lower(), key) for key in keys]
        combined_keys = "+".join(mapped_keys)
        print(f"Pressing key combination: {combined_keys}...")
        try:
            for key in mapped_keys:
                await self.page.keyboard.down(key)
            for key in reversed(mapped_keys):
                await self.page.keyboard.up(key)
            print("Keypress successful.")
        except Exception as e:
            print(f"Error pressing keys '{combined_keys}': {e}")

    async def drag(self, path: list[tuple[int, int]]) -> None:
        if not path or len(path) < 2:
            print("Drag path requires at least two points.")
            return
        start_x, start_y = path[0]
        print(f"Starting drag from ({start_x}, {start_y})...")
        try:
            await self.page.mouse.move(start_x, start_y)
            await self.page.mouse.down()
            print("Mouse down.")
            for i, (px, py) in enumerate(path[1:]):
                print(f"Dragging to point {i + 1}: ({px}, {py})")
                await self.page.mouse.move(px, py)
            await self.page.mouse.up()
            print("Mouse up. Drag complete.")
        except Exception as e:
            print(f"Error during drag operation: {e}")
            try:
                await self.page.mouse.up()
            except Exception:
                pass
