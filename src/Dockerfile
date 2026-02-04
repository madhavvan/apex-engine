# 1. Base Image: Start with a lightweight Linux (Debian) that has Rust pre-installed
FROM rust:1.80-slim-bookworm

# 2. System Setup: Install Python, Pip, and build tools (needed for some Python libs)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Work Directory: All commands run inside this folder in the container
WORKDIR /app

# 4. Copy specific dependency files first (Caching Strategy)
# This makes re-building faster if you didn't change dependencies
COPY Cargo.toml Cargo.lock ./

# 5. Create a dummy build to cache Rust dependencies
# (This is a pro trick to stop Docker from re-downloading crates every time you change 1 line of code)
RUN mkdir src && \
    echo "fn main() {println!(\"if you see this, the build broke\")}" > src/main.rs && \
    cargo build --release && \
    rm -rf src target/release/deps/apex_engine*

# 6. Install Python Dependencies
# We install them globally in the container because it's isolated anyway
RUN pip3 install requests beautifulsoup4 sentence-transformers --break-system-packages

# 7. Copy the actual source code
COPY src ./src
COPY static ./static

# 8. Build the Real Application
RUN cargo build --release

# 9. Expose the Port (Open port 8080 to the world)
EXPOSE 8080

# 10. The Start Command
CMD ["./target/release/apex_engine"]