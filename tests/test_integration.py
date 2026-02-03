"""
Integration tests for PhishScope full analysis pipeline
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from phishscope import PhishScope


@pytest.mark.integration
@pytest.mark.asyncio
class TestPhishScopeIntegration:
    """Integration tests for complete PhishScope analysis pipeline"""
    
    async def test_full_analysis_pipeline_mock(self, mock_logger, temp_output_dir):
        """Test complete analysis pipeline with mocked browser"""
        
        # Create PhishScope instance
        phishscope = PhishScope(
            url="https://phishing.example.com",
            output_dir=temp_output_dir,
            verbose=True,
            use_ai=False  # Disable AI for faster testing
        )
        
        # Mock the page loader to avoid actual browser launch
        with patch.object(phishscope.page_loader, 'load_page') as mock_load:
            with patch.object(phishscope.page_loader, 'cleanup') as mock_cleanup:
                
                # Mock page load response
                mock_page = AsyncMock()
                mock_page.url = "https://phishing.example.com"
                mock_page.title = AsyncMock(return_value="Fake Login")
                mock_page.content = AsyncMock(return_value="<html><body>Test</body></html>")
                mock_page.evaluate = AsyncMock(return_value=[])
                
                mock_load.return_value = {
                    "success": True,
                    "url": "https://phishing.example.com",
                    "final_url": "https://phishing.example.com",
                    "title": "Fake Login",
                    "status_code": 200,
                    "screenshot_path": str(temp_output_dir / "screenshot.png"),
                    "page_context": mock_page,
                    "network_log": []
                }
                
                # Run analysis
                results = await phishscope.analyze()
                
                # Verify results structure
                assert "url" in results
                assert "timestamp" in results
                assert "findings" in results
                assert "page_load" in results
                
                # Verify all agents ran
                assert "dom" in results["findings"]
                assert "javascript" in results["findings"]
                assert "network" in results["findings"]
                
                # Verify report was generated
                assert "report_path" in results
                
                # Verify cleanup was called
                mock_cleanup.assert_called_once()
    
    async def test_analysis_with_ai_enabled(self, mock_logger, temp_output_dir):
        """Test analysis pipeline with AI enabled"""
        
        phishscope = PhishScope(
            url="https://phishing.example.com",
            output_dir=temp_output_dir,
            verbose=True,
            use_ai=True
        )
        
        # Mock page loader
        with patch.object(phishscope.page_loader, 'load_page') as mock_load:
            with patch.object(phishscope.page_loader, 'cleanup') as mock_cleanup:
                with patch.object(phishscope.llm_agent, 'is_available', return_value=True):
                    with patch.object(phishscope.llm_agent, 'analyze') as mock_ai_analyze:
                        
                        # Mock responses
                        mock_page = AsyncMock()
                        mock_page.url = "https://phishing.example.com"
                        mock_page.title = AsyncMock(return_value="Fake Login")
                        mock_page.content = AsyncMock(return_value="<html><body>Test</body></html>")
                        mock_page.evaluate = AsyncMock(return_value=[])
                        
                        mock_load.return_value = {
                            "success": True,
                            "url": "https://phishing.example.com",
                            "final_url": "https://phishing.example.com",
                            "title": "Fake Login",
                            "status_code": 200,
                            "screenshot_path": str(temp_output_dir / "screenshot.png"),
                            "page_context": mock_page,
                            "network_log": []
                        }
                        
                        mock_ai_analyze.return_value = {
                            "verdict": "High Risk",
                            "confidence": 95
                        }
                        
                        # Run analysis
                        results = await phishscope.analyze()
                        
                        # Verify AI analysis was called
                        mock_ai_analyze.assert_called_once()
                        
                        # Verify AI findings in results
                        assert "ai_analysis" in results["findings"]
    
    async def test_analysis_handles_page_load_failure(self, mock_logger, temp_output_dir):
        """Test that analysis handles page load failures gracefully"""
        
        phishscope = PhishScope(
            url="https://invalid-url.example.com",
            output_dir=temp_output_dir,
            verbose=True,
            use_ai=False
        )
        
        # Mock page loader to fail
        with patch.object(phishscope.page_loader, 'load_page') as mock_load:
            with patch.object(phishscope.page_loader, 'cleanup') as mock_cleanup:
                
                mock_load.return_value = {
                    "success": False,
                    "url": "https://invalid-url.example.com",
                    "error": "Connection timeout",
                    "page_context": None,
                    "network_log": []
                }
                
                # Run analysis
                results = await phishscope.analyze()
                
                # Verify error is captured
                assert results["page_load"]["success"] is False
                assert "error" in results
                
                # Verify cleanup was still called
                mock_cleanup.assert_called_once()
    
    async def test_analysis_creates_output_directory(self, mock_logger, tmp_path):
        """Test that analysis creates output directory structure"""
        
        output_dir = tmp_path / "test_case_001"
        
        phishscope = PhishScope(
            url="https://phishing.example.com",
            output_dir=output_dir,
            verbose=True,
            use_ai=False
        )
        
        # Mock page loader
        with patch.object(phishscope.page_loader, 'load_page') as mock_load:
            with patch.object(phishscope.page_loader, 'cleanup'):
                
                mock_page = AsyncMock()
                mock_page.url = "https://phishing.example.com"
                mock_page.title = AsyncMock(return_value="Test")
                mock_page.content = AsyncMock(return_value="<html><body>Test</body></html>")
                mock_page.evaluate = AsyncMock(return_value=[])
                
                mock_load.return_value = {
                    "success": True,
                    "url": "https://phishing.example.com",
                    "final_url": "https://phishing.example.com",
                    "title": "Test",
                    "status_code": 200,
                    "screenshot_path": str(output_dir / "screenshot.png"),
                    "page_context": mock_page,
                    "network_log": []
                }
                
                # Run analysis
                results = await phishscope.analyze()
                
                # Verify output directory exists
                assert output_dir.exists()
                
                # Verify artifacts directory was created
                artifacts_dir = output_dir / "artifacts"
                assert artifacts_dir.exists()
    
    async def test_analysis_generates_all_artifacts(self, mock_logger, temp_output_dir):
        """Test that all expected artifacts are generated"""
        
        phishscope = PhishScope(
            url="https://phishing.example.com",
            output_dir=temp_output_dir,
            verbose=True,
            use_ai=False
        )
        
        # Mock page loader
        with patch.object(phishscope.page_loader, 'load_page') as mock_load:
            with patch.object(phishscope.page_loader, 'cleanup'):
                
                mock_page = AsyncMock()
                mock_page.url = "https://phishing.example.com"
                mock_page.title = AsyncMock(return_value="Test")
                mock_page.content = AsyncMock(return_value="<html><body>Test</body></html>")
                mock_page.evaluate = AsyncMock(return_value=[])
                
                # Create fake screenshot
                screenshot_path = temp_output_dir / "screenshot.png"
                screenshot_path.write_bytes(b"fake_image_data")
                
                mock_load.return_value = {
                    "success": True,
                    "url": "https://phishing.example.com",
                    "final_url": "https://phishing.example.com",
                    "title": "Test",
                    "status_code": 200,
                    "screenshot_path": str(screenshot_path),
                    "page_context": mock_page,
                    "network_log": []
                }
                
                # Run analysis
                results = await phishscope.analyze()
                
                # Verify artifacts
                assert (temp_output_dir / "report.md").exists()
                assert (temp_output_dir / "report.json").exists()
                assert (temp_output_dir / "artifacts" / "dom_snapshot.html").exists()
                assert (temp_output_dir / "artifacts" / "network_log.json").exists()
    
    async def test_concurrent_analyses(self, mock_logger, tmp_path):
        """Test that multiple analyses can run concurrently"""
        
        import asyncio
        
        async def run_analysis(url, output_dir):
            phishscope = PhishScope(
                url=url,
                output_dir=output_dir,
                verbose=False,
                use_ai=False
            )
            
            with patch.object(phishscope.page_loader, 'load_page') as mock_load:
                with patch.object(phishscope.page_loader, 'cleanup'):
                    
                    mock_page = AsyncMock()
                    mock_page.url = url
                    mock_page.title = AsyncMock(return_value="Test")
                    mock_page.content = AsyncMock(return_value="<html><body>Test</body></html>")
                    mock_page.evaluate = AsyncMock(return_value=[])
                    
                    mock_load.return_value = {
                        "success": True,
                        "url": url,
                        "final_url": url,
                        "title": "Test",
                        "status_code": 200,
                        "screenshot_path": str(output_dir / "screenshot.png"),
                        "page_context": mock_page,
                        "network_log": []
                    }
                    
                    return await phishscope.analyze()
        
        # Run multiple analyses concurrently
        urls = [
            "https://phishing1.example.com",
            "https://phishing2.example.com",
            "https://phishing3.example.com"
        ]
        
        tasks = []
        for i, url in enumerate(urls):
            output_dir = tmp_path / f"case_{i}"
            output_dir.mkdir()
            tasks.append(run_analysis(url, output_dir))
        
        results = await asyncio.gather(*tasks)
        
        # Verify all analyses completed
        assert len(results) == 3
        for result in results:
            assert result["page_load"]["success"] is True


@pytest.mark.integration
@pytest.mark.requires_browser
@pytest.mark.slow
@pytest.mark.asyncio
class TestPhishScopeRealBrowser:
    """Integration tests with real browser (slower, more comprehensive)"""
    
    async def test_analyze_example_com(self, mock_logger, temp_output_dir):
        """Test analysis of example.com (legitimate site)"""
        
        phishscope = PhishScope(
            url="https://example.com",
            output_dir=temp_output_dir,
            verbose=True,
            use_ai=False
        )
        
        # Run real analysis
        results = await phishscope.analyze()
        
        # Verify successful analysis
        assert results["page_load"]["success"] is True
        assert results["page_load"]["status_code"] == 200
        
        # Verify artifacts were created
        assert Path(results["page_load"]["screenshot_path"]).exists()
        assert (temp_output_dir / "report.md").exists()
        
        # Verify low risk (legitimate site)
        dom_findings = results["findings"]["dom"]
        js_findings = results["findings"]["javascript"]
        
        # Example.com should have minimal suspicious indicators
        assert len(js_findings.get("suspicious_patterns", [])) == 0
    
    async def test_analyze_phishing_html_file(self, mock_logger, temp_output_dir, sample_phishing_html, create_test_html_file):
        """Test analysis of local phishing HTML file"""
        
        # Create test HTML file
        html_file = create_test_html_file("phishing_test.html", sample_phishing_html)
        
        phishscope = PhishScope(
            url=f"file://{html_file}",
            output_dir=temp_output_dir,
            verbose=True,
            use_ai=False
        )
        
        # Run analysis
        results = await phishscope.analyze()
        
        # Verify analysis detected phishing indicators
        assert results["page_load"]["success"] is True
        
        dom_findings = results["findings"]["dom"]
        js_findings = results["findings"]["javascript"]
        network_findings = results["findings"]["network"]
        
        # Should detect forms and password fields
        assert dom_findings["forms_count"] > 0
        assert len(dom_findings["password_fields"]) > 0
        
        # Should detect suspicious JavaScript
        assert len(js_findings["suspicious_patterns"]) > 0
        
        # Report should be generated
        assert (temp_output_dir / "report.md").exists()