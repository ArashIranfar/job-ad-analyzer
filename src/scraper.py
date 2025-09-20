"""
Web scraping module for Job Ad Analyzer
"""

import logging
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional
import html2text
import config
from src.utils import save_text_file, clean_text, truncate_text, load_text_file


class WebScraper:
    """Web scraper for job advertisements"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.get_headers())
        self.h = html2text.HTML2Text()
        self.h.ignore_links = True
        self.h.ignore_images = True
        self.h.body_width = 0  # Don't wrap lines
        
        logging.debug("WebScraper initialized")
    
    # def scrape_url(self, url: str, url_id: str) -> Optional[str]:
    #     """
    #     Scrape content from a URL and return cleaned text
        
    #     Args:
    #         url: URL to scrape
    #         url_id: Unique identifier for this URL
        
    #     Returns:
    #         Cleaned text content or None if failed
    #     """
    
    def _check_cached_content(self, url_id: str) -> Optional[str]:
        """Check if we have cached scraped content"""
        
        # Check for cleaned text file
        text_file = config.RAW_DATA_DIR / f"{url_id}_cleaned.txt"
        if text_file.exists():
            try:
                content = load_text_file(text_file)
                if content and len(content.strip()) > 100:  # Ensure it's substantial content
                    logging.debug(f"Found cached cleaned content for {url_id}")
                    return content
            except Exception as e:
                logging.warning(f"Error reading cached content for {url_id}: {e}")
        
        return None

    def scrape_url(self, url: str, url_id: str, force: bool = False) -> Optional[str]:
        """
        Scrape content from URL with caching support
        
        Args:
            url: URL to scrape
            url_id: Unique identifier for this URL
            force: If True, ignore cached content and scrape fresh
        
        Returns:
            Cleaned text content or None if failed
        """
        
        # Check cache first (unless force=True)
        if not force:
            cached_content = self._check_cached_content(url_id)
            if cached_content:
                logging.info(f"Using cached content for {url_id}")
                return cached_content
        try:
            logging.debug(f"Scraping {url}")
            
            # Make request
            response = self.session.get(
                url,
                timeout=config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Save raw HTML if configured
            if config.SAVE_RAW_HTML:
                raw_file = config.RAW_DATA_DIR / f"{url_id}.html"
                save_text_file(response.text, raw_file)
            
            # Extract content
            content = self._extract_content(response.text, url)
            
            if not content:
                logging.warning(f"No content extracted from {url}")
                return None
            
            # Clean and truncate content
            content = clean_text(content)
            content = truncate_text(content, config.MAX_CONTENT_LENGTH)
            
            # Save cleaned text if configured
            if config.SAVE_CLEANED_TEXT:
                clean_file = config.RAW_DATA_DIR / f"{url_id}_cleaned.txt"
                save_text_file(content, clean_file)
            
            logging.debug(f"Extracted {len(content)} characters from {url}")
            return content
            
        except requests.RequestException as e:
            logging.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            logging.error(f"Scraping failed for {url}: {e}")
            return None
    
    def _extract_content(self, html: str, url: str) -> Optional[str]:
        """Extract main content from HTML"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Try different content extraction strategies
            content = self._try_content_extraction_strategies(soup, url)
            
            if not content:
                # Fallback: convert entire body
                content = self.h.handle(str(soup.body or soup))
            
            return content
            
        except Exception as e:
            logging.error(f"Content extraction failed: {e}")
            return None
    
    def _try_content_extraction_strategies(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Try multiple strategies to extract main content"""
        
        # Strategy 1: Look for common job ad containers
        job_selectors = [
            '[class*="job-description"]',
            '[class*="job-detail"]',
            '[class*="job-content"]',
            '[id*="job-description"]',
            '[id*="job-detail"]',
            '.job-description',
            '.job-details',
            '.job-content',
            '.description',
            'article',
            '[role="main"]',
            'main'
        ]
        
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                content = self.h.handle(str(elements[0]))
                if len(content.strip()) > 100:  # Minimum content length
                    logging.debug(f"Used selector: {selector}")
                    return content
        
        # Strategy 2: Look for largest text block
        text_elements = soup.find_all(['div', 'section', 'article'], 
                                     string=lambda text: text and len(text.strip()) > 50)
        
        if text_elements:
            # Find element with most text
            best_element = max(text_elements, 
                             key=lambda el: len(el.get_text(strip=True)))
            
            # Get parent element for more context
            parent = best_element.parent
            if parent:
                content = self.h.handle(str(parent))
                if len(content.strip()) > 100:
                    logging.debug("Used largest text block strategy")
                    return content
        
        # Strategy 3: Site-specific extraction
        content = self._site_specific_extraction(soup, url)
        if content:
            return content
        
        return None
    
    def _site_specific_extraction(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Site-specific content extraction rules"""
        
        domain = url.lower()
        
        # LinkedIn
        if 'linkedin.com' in domain:
            job_desc = soup.find('div', {'class': lambda x: x and 'jobs-description' in x})
            if job_desc:
                return self.h.handle(str(job_desc))
        
        # Indeed
        elif 'indeed.com' in domain:
            job_desc = soup.find('div', {'id': 'jobDescriptionText'})
            if not job_desc:
                job_desc = soup.find('div', {'class': lambda x: x and 'jobsearch-jobDescriptionText' in x})
            if job_desc:
                return self.h.handle(str(job_desc))
        
        # Glassdoor
        elif 'glassdoor.com' in domain:
            job_desc = soup.find('div', {'class': lambda x: x and 'jobDescriptionContent' in x})
            if job_desc:
                return self.h.handle(str(job_desc))
        
        # Monster
        elif 'monster.com' in domain:
            job_desc = soup.find('div', {'class': lambda x: x and 'job-description' in x})
            if job_desc:
                return self.h.handle(str(job_desc))
        
        # AngelList/Wellfound
        elif 'angel.co' in domain or 'wellfound.com' in domain:
            job_desc = soup.find('div', {'class': lambda x: x and 'job-description' in x})
            if job_desc:
                return self.h.handle(str(job_desc))
        
        return None
    
    def test_scraping(self, url: str) -> dict:
        """Test scraping on a single URL and return debug info"""
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Remove scripts/styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get basic info
            title = soup.title.string if soup.title else "No title"
            
            # Try different extraction methods
            strategies = {}
            
            # Method 1: Job-specific selectors
            job_selectors = [
                '[class*="job-description"]', '[class*="job-detail"]', 
                '.job-description', '.description', 'article', 'main'
            ]
            
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    content = self.h.handle(str(elements[0]))
                    strategies[f"selector_{selector}"] = {
                        "length": len(content),
                        "preview": content[:200] + "..." if len(content) > 200 else content
                    }
            
            # Method 2: Full body
            body_content = self.h.handle(str(soup.body or soup))
            strategies["full_body"] = {
                "length": len(body_content),
                "preview": body_content[:200] + "..." if len(body_content) > 200 else body_content
            }
            
            return {
                "url": url,
                "status_code": response.status_code,
                "title": title,
                "content_length": len(response.text),
                "strategies": strategies,
                "success": True
            }
            
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "success": False
            }
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()
            logging.debug("WebScraper session closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()