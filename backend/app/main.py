import hashlib
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import get_db, init_db
from .models import ChatMessage
from .redis_client import get_cached, set_cached
from .chain import chain, build_history

app = FastAPI(
    title="AI SaaS Skeleton",
    description="Production-ready AI backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


# --- Pydantic modellər ---
class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
    cached: bool = False


# --- Endpoints ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai-saas-skeleton"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):

    # 1. Redis keş yoxla
    cache_key = hashlib.md5(
        f"{request.session_id}:{request.message}".encode()
    ).hexdigest()

    cached = await get_cached(cache_key)
    if cached:
        return ChatResponse(
            response=cached,
            session_id=request.session_id,
            cached=True
        )

    # 2. Postgres-dən söhbət tarixini oxu
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == request.session_id)
        .order_by(ChatMessage.created_at)
        .limit(10)
    )
    history_rows = result.scalars().all()
    history = build_history([
        {"role": row.role, "content": row.content}
        for row in history_rows
    ])

    # 3. LCEL chain ilə cavab al
    response = await chain.ainvoke({
        "input": request.message,
        "history": history,
    })

    # 4. Postgres-ə yaz (human + assistant)
    db.add(ChatMessage(
        session_id=request.session_id,
        role="human",
        content=request.message
    ))
    db.add(ChatMessage(
        session_id=request.session_id,
        role="assistant",
        content=response,
        model_used="llama3.2"
    ))
    await db.commit()

    # 5. Redis-ə keşlə (1 saat)
    await set_cached(cache_key, response, ttl=3600)

    return ChatResponse(
        response=response,
        session_id=request.session_id,
        cached=False
    )


@app.get("/history/{session_id}")
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "model": m.model_used,
                "time": m.created_at
            }
            for m in messages
        ]
    }