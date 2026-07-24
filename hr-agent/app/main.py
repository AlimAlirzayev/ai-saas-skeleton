from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .rag_chain import hr_chain

app = FastAPI(
    title="HR Knowledge Agent",
    description="Şirkətin HR suallarını cavablayan AI agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    question: str


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "hr-knowledge-agent"}


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    answer = await hr_chain.ainvoke(request.question)
    return AnswerResponse(
        answer=answer,
        question=request.question
    )
