from typing import Any, Dict, List

from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.config.settings import settings


def run_rag(query: str, chat_history: List[Dict[str, Any]] = []):
    """
    Run a retrieval-augmented generation (RAG) pipeline:
    1. Embed the query and retrieve context from Qdrant.
    2. Optionally rephrase the query in context of chat history.
    3. Combine retrieved docs into a final answer.

    Args:
        query: The user’s question.
        chat_history: List of {"input": str, "output": str} dicts for context.

    Returns:
        A dict containing:
          - "result": the generated answer string
          - "source_documents": list of Documents used in the answer
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY)
    vector_store = QdrantVectorStore(
        embedding = embeddings,
        collection_name=settings.QDRANT_COLLECTION_NAME,
        client=QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    )

    chat = ChatGroq(model_name="meta-llama/llama-4-scout-17b-16e-instruct", api_key=settings.GROQ_API_KEY, temperature=0.0, verbose=True)

    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    qa_prompt       = hub.pull("langchain-ai/retrieval-qa-chat")

    stuff_chain = create_stuff_documents_chain(chat, qa_prompt)
    history_aware_retriever = create_history_aware_retriever(
        llm=chat,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        prompt=rephrase_prompt,
    )
    qa_chain = create_retrieval_chain(
        retriever=history_aware_retriever,
        combine_docs_chain=stuff_chain,
    )

    response = qa_chain.invoke(
        input={"input": query, "chat_history": chat_history}
    )
    return response
