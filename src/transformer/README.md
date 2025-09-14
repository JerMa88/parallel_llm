# Local LLM Server

This is a local LLM implementation that mirrors the functionality of your Anthropic server with parallel processing capabilities.

## Features

- **Parallel Processing**: Handles concurrent requests using async/await
- **User Memory**: Persistent conversation history per user
- **Dynamic Prompting**: Role-based system messages
- **Thread-Safe**: Multiple requests can process simultaneously on single model instance

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the local server:
```bash
python local_server.py
```

3. Test with parallel clients:
```bash
python local_clients.py
```

## Architecture

- `local_llm.py`: Core LLM wrapper with thread-safe concurrent access
- `memory.py`: User conversation memory management
- `local_server.py`: HTTP server (port 8081)
- `local_clients.py`: Test client for parallel requests

## Model Options

The default model is `microsoft/DialoGPT-small` for faster loading. You can modify `local_llm.py` to use:
- `microsoft/DialoGPT-medium` (better quality, slower)
- `microsoft/DialoGPT-large` (best quality, slowest)
- Or any compatible HuggingFace model

## Performance

The server uses thread locks to ensure safe concurrent access to the single model instance, allowing multiple users to get responses in parallel while sharing GPU/CPU resources efficiently.