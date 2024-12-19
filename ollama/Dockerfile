FROM ollama/ollama

# Set working directory
WORKDIR /app
RUN echo "Step 1: Working directory set to /app"

# Copy the pull script
COPY pull-mistral.sh .

# Make the script executable
RUN echo "Step 2: Making pull script executable" && chmod +x pull-mistral.sh

# Set the entrypoint to the pull script
RUN echo "Step 3: Setting entrypoint to pull script"
ENTRYPOINT ["/bin/bash", "pull-mistral.sh"]
