import requests
import random
import time
import concurrent.futures

# --- CONFIGURATION ---
NUM_VECTORS = 50_000      # How many items to store
VECTOR_DIM = 384          # Same size as the AI model we used
BATCH_SIZE = 1_000        # Send data in chunks (faster)
RUST_API_URL = "http://127.0.0.1:8080"

def generate_vector():
    """Create a random list of 384 floats between -1.0 and 1.0"""
    return [random.uniform(-1.0, 1.0) for _ in range(VECTOR_DIM)]

print(f"--- STARTING BENCHMARK ---")
print(f"Goal: Index {NUM_VECTORS} vectors into Rust.")

# 1. GENERATE & INDEX DATA
start_index = time.time()

# We use a session for faster HTTP connections
session = requests.Session()

for i in range(0, NUM_VECTORS):
    vector = generate_vector()
    
    payload = {
        "id": f"bench_{i}",
        "vector": vector,
        "content": f"Random Data {i}"
    }
    
    # Send to Rust
    # Note: In a real production app, we would send batches. 
    # For now, we send 1-by-1 to test the API handler's speed too.
    resp = session.post(f"{RUST_API_URL}/add", json=payload)
    
    if i % 1000 == 0 and i > 0:
        print(f"Indexed {i} vectors...")

total_time_index = time.time() - start_index
print(f"\n✅ Indexing Complete!")
print(f"Time taken: {total_time_index:.2f} seconds")
print(f"Write Speed: {NUM_VECTORS / total_time_index:.0f} vectors/second")

# 2. SEARCH BENCHMARK
print(f"\n--- TESTING READ SPEED ---")
print("Running 100 concurrent searches...")

query_vector = generate_vector()

start_search = time.time()
num_searches = 100

# We'll hit the server 100 times as fast as possible
for _ in range(num_searches):
    resp = session.post(
        f"{RUST_API_URL}/search", 
        json={"vector": query_vector, "k": 5}
    )

total_time_search = time.time() - start_search
avg_latency = (total_time_search / num_searches) * 1000

print(f"✅ Search Complete!")
print(f"Total time for {num_searches} searches: {total_time_search:.2f}s")
print(f"Average Latency: {avg_latency:.2f} ms per search")
print(f"Throughput: {num_searches / total_time_search:.0f} Queries Per Second (QPS)")