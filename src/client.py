import requests
from sentence_transformers import SentenceTransformer
import time

# 1. Load the AI Model (Downloads automatically first time)
print("Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Define our dataset (Real sentences)
sentences = [
    "The quick brown fox jumps over the lazy dog.",
    "A king wears a golden crown and rules the kingdom.",
    "The space shuttle launched into orbit around Earth.",
    "A delicious pizza with pepperoni and extra cheese.",
    "A fast red animal running in the forest.",  # Similar to Fox
    "Modern royalty in Europe.",                 # Similar to King
]

# 3. Embed and Send to Rust
RUST_API_URL = "http://127.0.0.1:8080"

print(f"Sending {len(sentences)} documents to Apex Engine...")
for i, text in enumerate(sentences):
    # Convert text -> Vector (List of floats)
    vector = model.encode(text).tolist()
    
    # Payload for Rust
    payload = {
        "id": str(i),
        "vector": vector,
        "content": text
    }
    
    requests.post(f"{RUST_API_URL}/add", json=payload)

print("Indexing complete!\n")

# 4. Search Loop
while True:
    query_text = input("Enter a search query (or 'quit'): ")
    if query_text.lower() == 'quit':
        break
        
    # Convert query -> Vector
    query_vector = model.encode(query_text).tolist()
    
    # Send to Rust
    start_time = time.time()
    response = requests.post(
        f"{RUST_API_URL}/search", 
        json={"vector": query_vector, "k": 3} # Get top 3 matches
    )
    duration = (time.time() - start_time) * 1000
    
    # Print Results
    results = response.json()
    print(f"\nFound top 3 matches in {duration:.2f}ms:")
    for doc_content, score in results:
        print(f"  [{score:.4f}] {doc_content}")
    print("-" * 40)