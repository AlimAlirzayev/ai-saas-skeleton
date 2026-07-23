from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from .config import settings


@tool
def get_current_time() -> str:
    """Cari tarixi və saatı qaytarır."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """Sadə riyazi hesablamalar aparmaq üçün."""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Hesablama xətası: {str(e)}"


TOOLS = [get_current_time, calculate]

llm = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.groq_model,
    temperature=0.7,
)

llm_with_tools = llm.bind_tools(TOOLS)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Sən köməkçi bir AI assistantsan. "
        "Lazım olduqda alətlərdən istifadə et. "
        "Cavablarını qısa və aydın ver."
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = (
    RunnablePassthrough.assign(
        history=lambda x: x.get("history", [])
    )
    | prompt
    | llm_with_tools
    | StrOutputParser()
)


def build_history(messages: list[dict]) -> list:
    history = []
    for msg in messages:
        if msg["role"] == "human":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=msg["content"]))
    return history