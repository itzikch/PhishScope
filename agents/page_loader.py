"""
PageLoaderAgent - Safely loads and captures phishing pages
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class PageLoaderAgent:
    """
    Loads suspicious URLs using Playwright with anti-detection measures
    Captures screenshots and provides page context for other agents
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
    async def load_page(self, url: str, output_dir: Path, timeout: int = 30000) -> Dict[str, Any]:
        """
        Load a URL and capture initial state
        
        Args:
            url: Target URL to analyze
            output_dir: Directory to save artifacts
            timeout: Page load timeout in milliseconds
            
        Returns:
            Dictionary containing page load results and context
        """
        result = {
            "success": False,
            "url": url,
            "screenshot_path": None,
            "page_context": None,
            "network_log": [],
            "error": None
        }
        
        try:
            # Initialize Playwright
            self.playwright = await async_playwright().start()
            
            # Launch browser with anti-detection settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # New York
                color_scheme='light',
                accept_downloads=False
            )
            
            # Setup network logging
            network_log = []
            
            async def log_request(request):
                network_log.append({
                    "type": "request",
                    "url": request.url,
                    "method": request.method,
                    "resource_type": request.resource_type,
                    "headers": dict(request.headers)
                })
            
            async def log_response(response):
                network_log.append({
                    "type": "response",
                    "url": response.url,
                    "status": response.status,
                    "headers": dict(response.headers)
                })
            
            # Create page and attach listeners
            self.page = await self.context.new_page()
            self.page.on("request", log_request)
            self.page.on("response", log_response)
            
            # Navigate to URL
            self.logger.debug(f"Navigating to: {url}")
            response = await self.page.goto(url, timeout=timeout, wait_until='networkidle')
            
            # Wait a bit for dynamic content
            await asyncio.sleep(2)
            
            # Capture screenshot
            screenshot_path = output_dir / "screenshot.png"
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            self.logger.debug(f"Screenshot saved: {screenshot_path}")
            
            # Get page title and URL (may have redirected)
            final_url = self.page.url
            title = await self.page.title()
            
            # Success
            result["success"] = True
            result["screenshot_path"] = str(screenshot_path)
            result["final_url"] = final_url
            result["title"] = title
            result["status_code"] = response.status if response else None
            result["page_context"] = self.page  # Pass page object to other agents
            result["network_log"] = network_log
            
            self.logger.info(f"Page loaded successfully: {title}")
            
        except Exception as e:
            self.logger.error(f"Failed to load page: {str(e)}")
            result["error"] = str(e)
            
        return result
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.debug("Browser cleanup complete")
        except Exception as e:
            self.logger.warning(f"Cleanup error: {str(e)}")


# TODO: Add support for handling CAPTCHA detection
# TODO: Add support for detecting cloaking (different content for bots)
# TODO: Add cookie/localStorage capture
# TODO: Add support for multi-step phishing flows

# Made with Bob
