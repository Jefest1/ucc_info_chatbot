from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Cookie
from fastapi.responses import JSONResponse, Response
from typing import Dict, Any, List
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Header
from typing import Optional
from app.retrieval_gen.rag import run_rag
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
import uuid

router = APIRouter()

SESSION_MEMORY: Dict[str, ConversationBufferMemory] = {}

async def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    if session_id is None:
        session_id = str(uuid.uuid4())
    return session_id


@router.get("/chat_ucc")
async def chat_ucc(query: str, response: Response, session_id: str = Depends(get_session_id)) -> JSONResponse:
    """
    Endpoint for chatting with the UCC RAG system.
    Args:
        query (str): The user's query.
        session_id (str, optional): The session ID. Defaults to Depends(get_session_id).

    Returns:
        JSONResponse: The response from the RAG system.
        
    """
    try:
        if session_id not in SESSION_MEMORY:
            SESSION_MEMORY[session_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        memory = SESSION_MEMORY[session_id]
        # Convert chat history to plain text
        chat_history = memory.load_memory_variables({})['chat_history']
        history = []
        for message in chat_history:
            if message.type == "human":
                history.append(f"Human: {message.content}")
            else:
                history.append(f"Assistant: {message.content}")
        rag_result = run_rag(query, history)
        response_text = rag_result["answer"]
        source_urls = [doc.metadata["url"] for doc in rag_result["context"]]
        memory.save_context({"input": query}, {"output": response_text})
        json_response = JSONResponse(content={"response": response_text, "source_urls": source_urls})
        json_response.set_cookie(key="session_id", value=session_id)
        return json_response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/chat_history")
async def chat_history(session_id: str = Depends(get_session_id)) -> JSONResponse:
    """
    Endpoint for retrieving chat history for a given session.
    Args:
        session_id (str, optional): The session ID. Defaults to Depends(get_session_id).

    Returns:
        JSONResponse: The chat history for the session.
    """
    if session_id not in SESSION_MEMORY:
        return JSONResponse(content={"history": []})
    memory = SESSION_MEMORY[session_id]
    history = memory.load_memory_variables({})['chat_history']
    # Convert chat history to plain text for display
    formatted_history = []
    for message in history:
        if message.type == "human":
            formatted_history.append(f"Human: {message.content}")
        else:
            formatted_history.append(f"Assistant: {message.content}")
    return JSONResponse(content={"history": formatted_history})
