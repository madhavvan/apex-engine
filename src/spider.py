import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import time
from collections import deque
from urllib.parse import urljoin, urlparse

# --- CONFIGURATION ---
START_URL = "https://en.wikipedia.org/wiki/Artificial_intelligence" # Where to start
MAX_PAGES = 50       # Stop after this many pages (Safety limit for your laptop)
RUST_API_URL = "http://127.0.0.1:8080"

print("1. Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# The Frontier: A queue of URLs to visit
queue = deque([START_URL])
# The Memory: A set of URLs we have already seen (to avoid infinite loops)
visited = set([START_URL])

def is_valid_url(url):
    """Ensure we only visit valid English Wikipedia pages (for this demo)"""
    parsed = urlparse(url)
    return (
        bool(parsed.netloc) and 
        bool(parsed.scheme) and 
        "en.wikipedia.org" in parsed.netloc and 
        ":" not in parsed.path # Avoid special wiki pages like Category: or Talk:
    )

def index_page(url):
    print(f"🕷️ Crawling: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'ApexBot/1.0'}, timeout=5)
        if response.status_code != 200: return []
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. CLEAN & INDEX CONTENT
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()
        
        paragraphs = [p.get_text().strip() for p in soup.find_all('p')]
        valid_chunks = [p for p in paragraphs if len(p) > 100] # Only meatier paragraphs

        # Send to Rust
        for i, text in enumerate(valid_chunks[:5]): # Limit to top 5 paragraphs per page to save space
            vector = model.encode(text).tolist()
            payload = {
                "id": f"{url}_{i}",
                "vector": vector,
                "content": text[:200] + "...", 
                "url": url
            }
            try:
                requests.post(f"{RUST_API_URL}/add", json=payload)
            except:
                pass

        # 2. HARVEST NEW LINKS
        new_links = []
        for link in soup.find_all('a', href=True):
            # Convert relative link (/wiki/Robot) to full link (https://en.wikipedia.org/wiki/Robot)
            full_url = urljoin(url, link['href'])
            
            # Remove hash fragments (e.g., #History)
            full_url = full_url.split('#')[0]

            if full_url not in visited and is_valid_url(full_url):
                new_links.append(full_url)
        
        return new_links

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

# --- MAIN LOOP ---
pages_crawled = 0

while queue and pages_crawled < MAX_PAGES:
    current_url = queue.popleft() # Get next URL
    
    # Process it
    found_links = index_page(current_url)
    pages_crawled += 1
    
    # Add new links to the queue
    for link in found_links:
        if link not in visited:
            visited.add(link)
            queue.append(link)
            
    print(f"   found {len(found_links)} new links. Queue size: {len(queue)}")
    print(f"   Progress: {pages_crawled}/{MAX_PAGES} pages.")
    
    # Be polite! Don't hammer the server.
    time.sleep(1) 

print("✅ Spider finished!")