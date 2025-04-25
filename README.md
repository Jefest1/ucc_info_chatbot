# UCC Info Chatbot

## Description

This project implements a chatbot that provides information about the University of Cape Coast (UCC). It leverages Retrieval-Augmented Generation (RAG) to answer user queries based on a knowledge base of UCC-related documents. The chatbot is built using FastAPI, Langchain, and Qdrant for efficient information retrieval and response generation.


## Setup

1.  Clone the repository.
    ```
    git clone [https://github.com/Jefest1/ucc_info_chatbot](https://github.com/Jefest1/ucc_info_chatbot)
    ```
3.  Install uv:

    ```bash
    pip install uv
    ```

4.  Create a virtual environment using uv:

    ```bash
    uv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```
5.  Install the dependencies:

    ```bash
    uv sync
    ```
6.  Create a `.env` file with the following variables:

    ```
    GROQ_API_KEY=<your_groq_api_key>
    OPENAI_API_KEY=<your_openai_api_key>
    QDRANT_API_KEY=<your_qdrant_api_key>
    QDRANT_URL=<your_qdrant_url>
    QDRANT_COLLECTION_NAME=<your_qdrant_collection_name>
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=<your_langsmith_api_key>
    LANGCHAIN_PROJECT=ucc-info-chatbot
    ```

## Running the application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Deployment

1.  Build the Docker image:

    ```bash
    docker build -t ucc-info-chatbot .
    ```
2.  Run the Docker container:

    ```bash
    docker run -p 8000:8000 ucc-info-chatbot
    ```
