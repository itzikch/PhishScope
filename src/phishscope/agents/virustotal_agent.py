
import asyncio
import logging
import base64
import hashlib
from typing import Dict, Any, Optional, List
import httpx

class VirusTotalAgent:
    """
    Agent for interacting with the VirusTotal API v3.
    """
    def __init__(self, api_key: str, logger: Optional[logging.Logger] = None):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
        self.logger = logger or logging.getLogger(__name__)
        self.headers = {
            "x-apikey": self.api_key,
            "Accept": "application/json"
        }

    def _url_id(self, url: str) -> str:
        """
        Generate VirusTotal URL identifier (base64 encoded sha256 of url).
        """
        return base64.urlsafe_b64encode(url.encode()).decode().strip("=")

    async def scan_url(self, url: str) -> Dict[str, Any]:
        """
        Submit a URL for scanning.
        """
        async with httpx.AsyncClient() as client:
            try:
                # First, submit URL for scanning
                response = await client.post(
                    f"{self.base_url}/urls",
                    headers=self.headers,
                    data={"url": url}
                )
                response.raise_for_status()
                data = response.json()
                scan_id = data['data']['id']
                self.logger.info(f"Submitted URL to VirusTotal: {url} (ID: {scan_id})")
                return data
            except httpx.HTTPError as e:
                self.logger.error(f"VirusTotal scan submission failed: {str(e)}")
                if e.response:
                    self.logger.error(f"Response: {e.response.text}")
                raise

    async def get_url_analysis(self, url: str) -> Dict[str, Any]:
        """
        Get analysis results for a URL.
        """
        url_id = self._url_id(url)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/urls/{url_id}",
                    headers=self.headers
                )
                
                if response.status_code == 404:
                    # URL not found, scan it first
                    self.logger.info(f"URL not found in VirusTotal, submitting scan: {url}")
                    await self.scan_url(url)
                    # Poll for completion (simplified for now, might need better logic)
                    await asyncio.sleep(5) 
                    # Try getting it again
                    response = await client.get(
                        f"{self.base_url}/urls/{url_id}",
                        headers=self.headers
                    )

                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                self.logger.error(f"VirusTotal analysis retrieval failed: {str(e)}")
                raise

    async def get_domain_report(self, domain: str) -> Dict[str, Any]:
        """
        Get report for a domain.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/domains/{domain}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                self.logger.error(f"VirusTotal domain report failed: {str(e)}")
                raise

    async def get_ip_report(self, ip: str) -> Dict[str, Any]:
        """
        Get report for an IP address.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/ip_addresses/{ip}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                self.logger.error(f"VirusTotal IP report failed: {str(e)}")
                raise
