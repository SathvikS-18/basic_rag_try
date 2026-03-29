# 1. Download the Brain and the Embedder
ollama pull llama3.2
ollama pull nomic-embed-text

# 2. Tell Ollama to use your Intel Arc GPU (Run this before starting your app)
set OLLAMA_NUM_GPU=999
set ZES_ENABLE_SYSMAN=1