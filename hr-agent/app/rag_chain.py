from langchain_groq import ChatGroq
from langchain_qdrant import QdrantVectorStore
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from qdrant_client import QdrantClient
from .config import settings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

vectorstore = QdrantVectorStore(
    client=client,
    collection_name=settings.collection_name,
    embedding=embeddings,
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.groq_model,
    temperature=0.1,
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """Sən şirkətin HR assistentisən. 
Yalnız aşağıdakı kontekstdəki məlumata əsasən cavab ver.
Kontekstdə məlumat yoxdursa, 'Bu barədə sənədlərdə məlumat tapılmadı' de.

Kontekst:
{context}"""
    ),
    ("human", "{question}"),
])


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


hr_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
