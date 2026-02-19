FROM ubuntu:24.04

# Match WSL default environment
RUN apt-get update && apt-get install -y \
    curl git build-essential python3 python3-pip python3-venv \
    ca-certificates gnupg sudo \
    && rm -rf /var/lib/apt/lists/*

# Node.js 22 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Claude Code CLI (Agent SDK spawns this as a subprocess)
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user (mimics WSL default user)
RUN useradd -m -s /bin/bash testuser
USER testuser

# uv (Python package manager) — installed as testuser
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/testuser/.local/bin:$PATH"

# Pre-create workspace directory so VS Code can open it immediately
RUN mkdir -p /tmp/work

WORKDIR /home/testuser
