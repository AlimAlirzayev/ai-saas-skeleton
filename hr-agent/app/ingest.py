import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from .config import settings

DOCUMENTS_DIR = "documents"


def ingest_documents():
    client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    # Collection yarat
    try:
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print(f"Collection yaradildi: {settings.collection_name}")
    except Exception:
        print(f"Collection artiq movcuddur: {settings.collection_name}")

    # Sənədləri yüklə
    documents = []
    for filename in os.listdir(DOCUMENTS_DIR):
        filepath = os.path.join(DOCUMENTS_DIR, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
        elif filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding="utf-8")
        else:
            continue
        documents.extend(loader.load())
        print(f"Yuklendi: {filename}")

    # Chunk-la
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_documents(documents)
    print(f"Chunk sayi: {len(chunks)}")

    # Qdrant-a yaz
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=f"http://{settings.qdrant_host}:{settings.qdrant_port}",
        collection_name=settings.collection_name,
    )
    print("Ingestion tamamlandi!")


if __name__ == "__main__":
    ingest_documents()
