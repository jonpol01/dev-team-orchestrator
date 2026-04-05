FROM python:3.12-slim

# System tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential jq \
    && rm -rf /var/lib/apt/lists/*

# Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Go 1.22
RUN curl -fsSL https://go.dev/dl/go1.22.5.linux-arm64.tar.gz | tar -C /usr/local -xz
ENV PATH="/usr/local/go/bin:${PATH}"

# Rust (minimal)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile minimal
ENV PATH="/root/.cargo/bin:${PATH}"

# Python tools
RUN pip install --no-cache-dir --break-system-packages pytest mypy ruff black

WORKDIR /workspace
