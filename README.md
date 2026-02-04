# Apex High-Performance Vector Engine

Apex is a high-performance semantic search engine built from scratch in **Rust**. It utilizes HNSW (Hierarchical Navigable Small World) graphs for sub-millisecond vector lookups and provides a full-stack AI experience.

##  Architecture
* **Core Engine:** Rust + Rayon (Parallel Computing).
* **Algorithm:** HNSW Graph (O(log N) search complexity).
* **Persistence:** SQLite (Embedded ACID-compliant storage).
* **Frontend:** HTML5 + Vanilla JS (Edge-side embeddings via ONNX/WASM).
* **Client:** Python Script for batch ingestion.

##  Performance
* **Throughput:** ~300+ Queries Per Second (QPS) on local hardware.
* **Latency:** < 4ms per search (p99).
* **Capacity:** Tested with 50,000+ vector embeddings.

##  Setup & Usage

### 1. Prerequisites
* Rust (Cargo)
* Python 3.10+ (for ingestion script)

### 2. Run the Engine
```bash
cargo run --release