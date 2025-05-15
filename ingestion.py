from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os



VECTOR_DB_DIR = 'Vectordb'
pdf_path = "Electronic_Act_Law.pdf"

def load_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    return pages

def split_text(pages):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(pages)
    return chunks



def create_vectorstore(chunks, embeddings):
    vectordb = FAISS.from_documents(chunks, embedding=embeddings)
    vectordb.save_local(VECTOR_DB_DIR)
    return vectordb

# Step 4: Load existing Vector Store
def load_vectorstore(embeddings):
    vectordb = FAISS.load_local(VECTOR_DB_DIR, embeddings, allow_dangerous_deserialization=True)
    return vectordb


def main():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    

    print('Creating new vector database...')
    pages = load_pdf(pdf_path)
    chunks = split_text(pages)
    create_vectorstore(chunks, embeddings)


main()






