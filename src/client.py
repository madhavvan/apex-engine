import requests
from sentence_transformers import SentenceTransformer
import time

print("Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define dataset with URLs
data = [
    {"text": "The quick brown fox jumps over the lazy dog.", "url": "https://en.wikipedia.org/wiki/Fox"},
    {"text": "A king wears a golden crown and rules the kingdom.", "url": "https://en.wikipedia.org/wiki/Monarchy"},
    {"text": "The space shuttle launched into orbit around Earth.", "url": "https://www.nasa.gov/shuttle"},
    {"text": "A delicious pizza with pepperoni and extra cheese.", "url": "https://www.dominos.com"},
    {"text": "Modern royalty in Europe.", "url": "https://www.royal.uk"}, 
]

RUST_API_URL = "http://127.0.0.1:8080"

print(f"Sending {len(data)} documents to Apex Engine...")

# FIX: We use 'item' here so we can use 'item' inside the loop
for i, item in enumerate(data):
    # Convert text -> Vector
    vector = model.encode(item["text"]).tolist()
    
    payload = {
        "id": str(i),
        "vector": vector,
        "content": item["text"],
        "url": item["url"]
    }
    
    # Send to Rust
    requests.post(f"{RUST_API_URL}/add", json=payload)

print("Indexing complete!\n")

# Search Loop
while True:
    query_text = input("Enter a search query (or 'quit'): ")
    if query_text.lower() == 'quit':
        break
        
    query_vector = model.encode(query_text).tolist()
    
    start_time = time.time()
    response = requests.post(
        f"{RUST_API_URL}/search", 
        json={"vector": query_vector, "k": 3}
    )
    duration = (time.time() - start_time) * 1000
    
    results = response.json()
    print(f"\nFound top 3 matches in {duration:.2f}ms:")
    
    # The API returns [ [doc_object, score], ... ]
    for doc, score in results:
        print(f"  [{score:.4f}] {doc['content']} -> {doc['url']}")
    print("-" * 40)