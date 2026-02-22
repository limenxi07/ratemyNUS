from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from typing import Optional, Tuple, List, Dict
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_module_page(module_code: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch NUSMods module page HTML.
    
    Returns:
        (html, None) if success
        (None, "not_found") if module doesn't exist
        (None, "scrape_failed") if scraping failed
    """
    url = f"https://nusmods.com/courses/{module_code}"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            response = page.goto(url, wait_until="networkidle", timeout=15000)
            
            # Check if module exists (404 page)
            if response.status == 404:
                logger.warning(f"Module {module_code} not found (404)")
                browser.close()
                return None, "not_found"
            
            # Wait for Disqus iframe to load
            try:
                page.wait_for_selector("div#disqus_thread", timeout=10000)
            except PlaywrightTimeout:
                logger.error(f"Disqus iframe didn't load for {module_code}")
                browser.close()
                return None, "scrape_failed"
            
            html = page.content()
            browser.close()
            
            logger.info(f"Successfully fetched {module_code}")
            return html, None
            
    except Exception as e:
        logger.error(f"Error fetching {module_code}: {e}")
        return None, "scrape_failed"


def extract_disqus_url(html: str, module_code: str) -> Optional[str]:
    """
    Extract Disqus embed URL from NUSMods page HTML.
    
    Returns:
        Disqus URL string or None if not found
    """
    soup = BeautifulSoup(html, "html.parser")
    iframe = soup.find("div", id="disqus_thread")
    if iframe and iframe.find("iframe"):
        return iframe.find("iframe")["src"]
    return None


def fetch_disqus_comments(disqus_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch Disqus embed page HTML.
    
    Returns:
        (html, None) if success
        (None, error_code) if failed
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            response = page.goto(disqus_url, wait_until="networkidle", timeout=15000)
            
            if not response.ok:
                logger.error(f"Failed to load Disqus URL: {disqus_url} with status {response.status}")
                browser.close()
                return None, "scrape_failed"
            
            html = page.content()
            browser.close()
            
            logger.info(f"Successfully fetched Disqus comments from {disqus_url}")
            return html, None
    except Exception as e:
        logger.error(f"Error fetching Disqus URL {disqus_url}: {e}")
        return None, "scrape_failed"


def parse_comments(html: str) -> List[Dict[str, any]]:
    """
    Parse comments from Disqus HTML. No data cleaning is done here, just raw extraction.
    
    Returns:
        List of dicts: [{"text": "...", "posted_date": "...", "upvotes": 0}, ...]
        Empty list if no comments found
    """
    soup = BeautifulSoup(html, "html.parser")
    comments = []
    post_list = soup.find("ul", id="post-list")
    if not post_list:
        logger.warning("Could not find post-list in Disqus HTML")
        return comments

    # Note: For now, children comments are ignored. Only top-level comments are scraped.
    for post in post_list.find_all("li", class_="post"):
        comment = {}

        # Extract text
        text_element = post.find("div", class_="post-message")
        if text_element:
            comment["text"] = text_element.get_text(strip=True)
        else:
            comment["text"] = ""

        # Extract date
        date_element = post.find("a", class_="time-ago")
        if date_element and date_element.get("title"):
            comment["posted_date"] = date_element["title"]
        else:
            comment["posted_date"] = None

        # Extract author
        author_element = post.find("span", class_="author")
        if author_element:
            comment["author"] = author_element.find("a").get_text(strip=True)
        else:
            comment["author"] = "Anonymous" # Disqus allows anonymous comments
        
        # Extract upvotes
        upvote_element = post.find("div", class_="post-votes")
        if upvote_element:
            comment["upvotes"] = upvote_element.find_all("span")[1].get_text(strip=True)
        else:
            comment["upvotes"] = 0

        comments.append(comment)

    return comments


def scrape_module_reviews(module_code: str, retry_count: int = 3) -> Tuple[List[Dict], Optional[str]]:
    """
    Complete scraping workflow for one module.
    Handles retries on failure.
    
    Returns:
        (list_of_comments, None) if success
        ([], "not_found") if module doesn't exist
        ([], "no_reviews") if module has 0 reviews
        ([], "scrape_failed") if scraping failed after retries
    """
    for attempt in range(retry_count):
        # Step 1: Fetch NUSMods page
        html, error = fetch_module_page(module_code)
        
        if error == "not_found":
            return [], "not_found"
        
        if error == "scrape_failed":
            if attempt < retry_count - 1:
                logger.info(f"Retry {attempt + 1}/{retry_count} for {module_code}")
                time.sleep(2)  # Wait before retry
                continue
            else:
                return [], "scrape_failed"
        
        # Step 2: Extract Disqus URL
        disqus_url = extract_disqus_url(html, module_code)
        if not disqus_url:
            logger.error(f"Could not find Disqus URL for {module_code}")
            return [], "scrape_failed"
        
        # Step 3: Fetch Disqus page
        disqus_html, error = fetch_disqus_comments(disqus_url)
        if error:
            if attempt < retry_count - 1:
                logger.info(f"Retry {attempt + 1}/{retry_count} for Disqus")
                time.sleep(2)
                continue
            else:
                return [], "scrape_failed"
        
        # Step 4: Parse comments
        comments = parse_comments(disqus_html)
        
        if len(comments) == 0:
            logger.info(f"No reviews found for {module_code}")
            return [], "no_reviews"
        
        logger.info(f"Scraped {len(comments)} reviews for {module_code}")
        return comments, None
    
    return [], "scrape_failed"