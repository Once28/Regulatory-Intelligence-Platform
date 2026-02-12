from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def initialize_rag(raw_law_text: str):
    # Split the long law text into digestible chunks for the AI
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    chunks = splitter.split_text(raw_law_text)
    docs = [Document(page_content=c) for c in chunks]
    
    # Use a medical/legal-friendly embedding model (we can update this to be more medical friendly)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Create persistent local database
    vector_db = Chroma.from_documents(
        docs, embeddings, persist_directory="./data/chroma_db"
    )
    return vector_db.as_retriever(search_kwargs={"k": 5})