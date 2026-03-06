from bs4 import BeautifulSoup
from typing import Optional, Tuple, List, Dict
from datetime import datetime
import logging
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
BROWSERLESS_API_KEY = os.getenv("BROWSERLESS_API_KEY")
BROWSERLESS_URL = f"https://chrome.browserless.io/content?token={BROWSERLESS_API_KEY}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MAX_FAILURES = 3


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
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            logger.warning(f"Module {module_code} not found (404)")
            return None, "not_found"
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch {url}: {response.status_code}")
            return None, "scrape_failed"
        
        return response.text, None
        
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
    logger.warning(f"No Disqus iframe found for {module_code}")
    return None


def fetch_disqus_comments(disqus_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch Disqus embed page HTML.
    Clicks "Load more" button until all comments are visible.
    
    Returns:
        (html, None) if success
        (None, error_code) if failed
    """
    if not BROWSERLESS_API_KEY:
        logger.error("BROWSERLESS_API_KEY not set")
        return None, "scrape_failed"
    
    try:
        # JavaScript to click "Load more" button repeatedly
        load_more_script = """
        async function loadAllComments() {
            let clicks = 0;
            const maxClicks = 200;
            
            while (clicks < maxClicks) {
                const loadMoreButton = document.querySelector('a[data-action="more-posts"]');
                
                if (!loadMoreButton || !loadMoreButton.offsetParent) {
                    // Button not visible, we're done
                    break;
                }
                
                const beforeCount = document.querySelectorAll('li.post').length;
                loadMoreButton.click();
                clicks++;
                
                // Wait for new comments to load
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                const afterCount = document.querySelectorAll('li.post').length;
                
                // If no new comments loaded after 3 attempts, stop
                if (afterCount === beforeCount) {
                    break;
                }
            }
            
            return document.documentElement.outerHTML;
        }
        
        loadAllComments();
        """

        # Browserless request payload
        payload = {
            "url": disqus_url,
            "gotoOptions": {
                "waitUntil": "networkidle",
                "timeout": 30000
            },
            "waitFor": 5000,  # Wait 5 seconds for initial load
            "addScriptTag": [{
                "content": load_more_script
            }]
        }

        logger.info(f"Fetching Disqus comments via Browserless...")
        response = requests.post(
            BROWSERLESS_URL,
            json=payload,
            timeout=120  # 2 minute timeout
        )
        
        if response.status_code != 200:
            logger.error(f"Browserless failed with status {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
            return None, "scrape_failed"
        
        html = response.text
        
        # Count comments
        soup = BeautifulSoup(html, 'html.parser')
        comment_count = len(soup.find_all('li', class_='post'))
        logger.info(f"Loaded {comment_count} comments from Disqus")
        
        return html, None
    except requests.exceptions.Timeout:
        logger.error("Browserless request timed out")
        return None, "scrape_failed"
    except Exception as e:
        logger.error(f"Error with Browserless: {e}")
        return None, "scrape_failed"


def parse_comments(html: str) -> List[Dict[str, any]]:
    """
    Parse comments from Disqus HTML. 
    
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
            date_string = date_element["title"]
            try: 
                comment["posted_date"] = datetime.strptime(date_string, "%A, %B %d, %Y %I:%M %p")
            except ValueError:
                comment["posted_date"] = None
        else:
            comment["posted_date"] = None

        # Extract author
        author_element = post.find("span", class_="author").find("a")
        if author_element:
            comment["author"] = author_element.get_text(strip=True)
        else:
            comment["author"] = "Anonymous" # Disqus allows anonymous comments
        
        # Extract upvotes
        upvote_element = post.find("div", class_="post-votes")
        if upvote_element:
            try: 
                comment["upvotes"] = upvote_element.find_all("span")[1].get_text(strip=True)
            except (IndexError, ValueError, AttributeError):
                comment["upvotes"] = 0
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
        
        logger.info(f"Fetched NUSMods page for {module_code}, retrieved HTML of length {len(html)}")
        
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

def get_comment_count(module_code: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Get total number of comments for a module without scraping them all.
    
    Returns:
        (count, None) if success
        (None, error_code) if failed
    """
    try:
        comments, error = scrape_module_reviews(module_code)  
        if error == "no_reviews":
            return 0, None
        
        if error:
            return None, error
        
        return len(comments), None
        
    except Exception as e:
        logger.error(f"Error getting comment count for {module_code}: {e}")
        return None, "scrape_failed"