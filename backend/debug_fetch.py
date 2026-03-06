import requests
from bs4 import BeautifulSoup
from app.scraper import fetch_module_page

html, error = fetch_module_page("CS1101S")

if error:
    print(f"Error fetching page: {error}")
else:
    print(html)
