import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from app.services import ai_service

logger = logging.getLogger(__name__)


async def scrape_url(url: str) -> Optional[str]:
    """Fetch URL content and return cleaned text."""
    if not url:
        return None
    try:
        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; GrantsBot/1.0)"},
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove scripts and styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            # Collapse whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(lines)
    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return None


async def scrape_with_playwright(url: str) -> Optional[str]:
    """Fallback scraping with Playwright for JS-heavy sites."""
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_timeout(2000)
            content = await page.content()
            await browser.close()
            soup = BeautifulSoup(content, "html.parser")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return "\n".join(lines)
    except Exception as e:
        logger.warning(f"Playwright failed for {url}: {e}")
        return None


async def scrape_grant(grant_id: int, url: str, grant_name: str) -> Dict[str, Any]:
    """Full scraping pipeline: httpx -> playwright -> Claude extraction."""
    text = await scrape_url(url)
    if not text or len(text) < 100:
        text = await scrape_with_playwright(url)

    if not text:
        return {"success": False, "error": "Could not fetch page content"}

    extracted = await ai_service.extract_grant_data(text, grant_name)
    return {
        "success": True,
        "raw_text_length": len(text),
        "extracted": extracted,
        "raw_text_preview": text[:500],
    }
