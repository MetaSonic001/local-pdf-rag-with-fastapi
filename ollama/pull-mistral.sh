#!/bin/bash

# Start Ollama server in the background
ollama serve &

# Wait for Ollama server to start
sleep 5

# Pull Mistral model
ollama pull mistral

# Keep the container running
wait $!