
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")



VECTOR_DB_DIR = 'Vectordb'



# Step 4: Load existing Vector Store
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = FAISS.load_local(VECTOR_DB_DIR, embeddings, allow_dangerous_deserialization=True)
    return vectordb

from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template(
        """
You are a legal expert specializing in Nepal's Electronic Transactions Act (ETA) and associated cyber laws. Your primary responsibility is to assist users by providing clear, concise, and legally accurate information on topics related to:

1. Electronic records and digital signatures
2. Cybercrimes and their penalties
3. Legal recognition of electronic transactions
4. Roles and responsibilities of certifying authorities
5. Jurisdiction and enforcement of cyber laws in Nepal





Important Instructions:
- NO bullet points, NO special symbols like *, ~, # etc.
- Keep the formatting clean and formal.
- Do not hallucinate or add extra information.
- Answer length depends on the nature of the question and context.
- Maintain good grammar and professional tone.


Context:
{context}

User's Question:
{query}

Provide the answer following the exact format above.

Answer:
"""
    
)

def ask_chatbot(query):
    vector_store = load_vectorstore()

    context = vector_store.similarity_search(query)

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    prompt = prompt_template.invoke({"query": query, "context": context})

    response = llm.invoke(prompt).content

    return response

    # response = generate_answer(con)


if __name__ == "__main__":
    print(ask_chatbot("hi"))