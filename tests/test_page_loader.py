"""
Unit tests for PageLoaderAgent
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from agents.page_loader import PageLoaderAgent


@pytest.mark.unit
@pytest.mark.asyncio
class TestPageLoaderAgent:
    """Test suite for PageLoaderAgent"""
    
    async def test_init(self, mock_logger):
        """Test PageLoaderAgent initialization"""
        agent = PageLoaderAgent(mock_logger)
        
        assert agent.logger == mock_logger
        assert agent.browser is None
        assert agent.context is None
        assert agent.page is None
        assert agent.playwright is None
    
    async def test_load_page_success(self, mock_logger, temp_output_dir):
        """Test successful page loading"""
        agent = PageLoaderAgent(mock_logger)
        
        # Mock Playwright components
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_response = AsyncMock()
        
        # Setup mock chain
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.screenshot = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.url = "https://example.com"
        mock_response.status = 200
        
        # Patch async_playwright
        with patch('agents.page_loader.async_playwright') as mock_ap:
            mock_ap.return_value.start = AsyncMock(return_value=mock_playwright)
            
            # Execute
            result = await agent.load_page("https://example.com", temp_output_dir)
            
            # Verify
            assert result["success"] is True
            assert result["url"] == "https://example.com"
            assert result["final_url"] == "https://example.com"
            assert result["title"] == "Test Page"
            assert result["status_code"] == 200
            assert result["error"] is None
            assert "screenshot.png" in result["screenshot_path"]
            
            # Verify browser was launched with correct settings
            mock_playwright.chromium.launch.assert_called_once()
            launch_args = mock_playwright.chromium.launch.call_args
            assert launch_args.kwargs["headless"] is True
            
            # Verify page navigation
            mock_page.goto.assert_called_once()
            goto_args = mock_page.goto.call_args
            assert goto_args.args[0] == "https://example.com"
            
            # Verify screenshot was taken
            mock_page.screenshot.assert_called_once()
            
            # Cleanup
            await agent.cleanup()
    
    async def test_load_page_timeout(self, mock_logger, temp_output_dir):
        """Test page loading with timeout"""
        agent = PageLoaderAgent(mock_logger)
        
        # Mock Playwright to raise timeout
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.goto = AsyncMock(side_effect=TimeoutError("Navigation timeout"))
        
        with patch('agents.page_loader.async_playwright') as mock_ap:
            mock_ap.return_value.start = AsyncMock(return_value=mock_playwright)
            
            # Execute
            result = await agent.load_page("https://slow-site.com", temp_output_dir)
            
            # Verify
            assert result["success"] is False
            assert result["error"] is not None
            assert "timeout" in result["error"].lower()
            
            # Cleanup
            await agent.cleanup()
    
    async def test_load_page_invalid_url(self, mock_logger, temp_output_dir):
        """Test page loading with invalid URL"""
        agent = PageLoaderAgent(mock_logger)
        
        # Mock Playwright to raise error
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.goto = AsyncMock(side_effect=Exception("Invalid URL"))
        
        with patch('agents.page_loader.async_playwright') as mock_ap:
            mock_ap.return_value.start = AsyncMock(return_value=mock_playwright)
            
            # Execute
            result = await agent.load_page("not-a-valid-url", temp_output_dir)
            
            # Verify
            assert result["success"] is False
            assert result["error"] is not None
            
            # Cleanup
            await agent.cleanup()
    
    async def test_network_logging(self, mock_logger, temp_output_dir):
        """Test that network requests are logged"""
        agent = PageLoaderAgent(mock_logger)
        
        # Mock Playwright components
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_response = AsyncMock()
        
        # Setup mock chain
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.screenshot = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.url = "https://example.com"
        mock_response.status = 200
        
        # Track event listeners
        event_listeners = {}
        
        def mock_on(event_name, callback):
            event_listeners[event_name] = callback
        
        mock_page.on = mock_on
        
        with patch('agents.page_loader.async_playwright') as mock_ap:
            mock_ap.return_value.start = AsyncMock(return_value=mock_playwright)
            
            # Execute
            result = await agent.load_page("https://example.com", temp_output_dir)
            
            # Verify network logging was set up
            assert "request" in event_listeners
            assert "response" in event_listeners
            assert result["network_log"] is not None
            assert isinstance(result["network_log"], list)
            
            # Cleanup
            await agent.cleanup()
    
    async def test_cleanup(self, mock_logger):
        """Test cleanup of browser resources"""
        agent = PageLoaderAgent(mock_logger)
        
        # Mock browser components
        agent.page = AsyncMock()
        agent.context = AsyncMock()
        agent.browser = AsyncMock()
        agent.playwright = AsyncMock()
        
        # Execute cleanup
        await agent.cleanup()
        
        # Verify all components were closed
        agent.page.close.assert_called_once()
        agent.context.close.assert_called_once()
        agent.browser.close.assert_called_once()
        agent.playwright.stop.assert_called_once()
    
    async def test_cleanup_with_errors(self, mock_logger):
        """Test cleanup handles errors gracefully"""
        agent = PageLoaderAgent(mock_logger)
        
        # Mock browser components with errors
        agent.page = AsyncMock()
        agent.page.close = AsyncMock(side_effect=Exception("Close failed"))
        agent.context = AsyncMock()
        agent.browser = AsyncMock()
        agent.playwright = AsyncMock()
        
        # Execute cleanup - should not raise exception
        await agent.cleanup()
        
        # Verify warning was logged
        mock_logger.warning.assert_called()
    
    async def test_screenshot_saved_to_correct_path(self, mock_logger, temp_output_dir):
        """Test that screenshot is saved to the specified output directory"""
        agent = PageLoaderAgent(mock_logger)
        
        # Mock Playwright components
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_response = AsyncMock()
        
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.screenshot = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.url = "https://example.com"
        mock_response.status = 200
        
        with patch('agents.page_loader.async_playwright') as mock_ap:
            mock_ap.return_value.start = AsyncMock(return_value=mock_playwright)
            
            # Execute
            result = await agent.load_page("https://example.com", temp_output_dir)
            
            # Verify screenshot path
            expected_path = str(temp_output_dir / "screenshot.png")
            assert result["screenshot_path"] == expected_path
            
            # Verify screenshot was called with correct path
            mock_page.screenshot.assert_called_once()
            screenshot_call = mock_page.screenshot.call_args
            assert screenshot_call.kwargs["path"] == expected_path
            assert screenshot_call.kwargs["full_page"] is True
            
            # Cleanup
            await agent.cleanup()
    
    async def test_custom_timeout(self, mock_logger, temp_output_dir):
        """Test page loading with custom timeout"""
        agent = PageLoaderAgent(mock_logger)
        
        # Mock Playwright components
        mock_playwright = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_response = AsyncMock()
        
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.screenshot = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test")
        mock_page.url = "https://example.com"
        mock_response.status = 200
        
        with patch('agents.page_loader.async_playwright') as mock_ap:
            mock_ap.return_value.start = AsyncMock(return_value=mock_playwright)
            
            # Execute with custom timeout
            custom_timeout = 60000
            result = await agent.load_page(
                "https://example.com",
                temp_output_dir,
                timeout=custom_timeout
            )
            
            # Verify timeout was passed to goto
            goto_call = mock_page.goto.call_args
            assert goto_call.kwargs["timeout"] == custom_timeout
            
            # Cleanup
            await agent.cleanup()


@pytest.mark.integration
@pytest.mark.requires_browser
@pytest.mark.slow
@pytest.mark.asyncio
class TestPageLoaderIntegration:
    """Integration tests for PageLoaderAgent with real browser"""
    
    async def test_load_real_page(self, mock_logger, temp_output_dir):
        """Test loading a real webpage (example.com)"""
        agent = PageLoaderAgent(mock_logger)
        
        # Execute
        result = await agent.load_page("https://example.com", temp_output_dir)
        
        # Verify
        assert result["success"] is True
        assert result["title"] is not None
        assert result["status_code"] == 200
        assert Path(result["screenshot_path"]).exists()
        assert len(result["network_log"]) > 0
        
        # Cleanup
        await agent.cleanup()