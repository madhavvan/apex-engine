import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import time

# --- CONFIGURATION ---
TARGET_URL = "https://en.wikipedia.org/wiki/Artificial_intelligence" 
RUST_API_URL = "http://127.0.0.1:8080"

print("1. Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def scrape_and_index(url):
    print(f"2. Fetching {url}...")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(f"Failed to load page: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')

        # Cleanup: Remove Javascript and CSS
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        # Extract all paragraphs (chunks)
        paragraphs = [p.get_text().strip() for p in soup.find_all('p')]
        
        # Filter out empty or short paragraphs
        valid_chunks = [p for p in paragraphs if len(p) > 50]

        print(f"3. Found {len(valid_chunks)} valid paragraphs. Indexing...")

        for i, text in enumerate(valid_chunks):
            # Create a unique ID
            doc_id = f"wiki_{i}_{int(time.time())}"
            
            # Embed
            vector = model.encode(text).tolist()

            payload = {
                "id": doc_id,
                "vector": vector,
                "content": text[:200] + "...", # Store preview text
                "url": url # Link back to the source
            }

            # Send to Rust
            requests.post(f"{RUST_API_URL}/add", json=payload)
            
            if i % 5 == 0:
                print(f"   Indexed chunk {i}/{len(valid_chunks)}")

        print("✅ Done! This page is now searchable.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        print("\n--- APEX WEB CRAWLER ---")
        url = input("Enter a URL to index (or 'q' to quit): ").strip()
        
        if url.lower() == 'q':
            break
            
        if not url.startswith("http"):
            print("❌ Please enter a full URL starting with http:// or https://")
            continue
            
        scrape_and_index(url)
