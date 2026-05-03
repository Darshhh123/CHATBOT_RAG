from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import yaml
import os
from pathlib import Path

# Load API key from secrets.yaml
secrets_path = Path(__file__).parent / "secrets.yaml"
if secrets_path.exists():
    with open(secrets_path) as f:
        secrets = yaml.safe_load(f)
    os.environ["GOOGLE_API_KEY"] = secrets.get("api_key", "")
else:
    # Try environment variable as fallback
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY not found in secrets.yaml or environment variables")

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Vector DB path (relative to app directory)
db_path = Path(__file__).parent / "hospital_db"

if not db_path.exists():
    raise FileNotFoundError(
        f"Hospital database not found at {db_path}. "
        "Please run: python app/build_hospital_db.py"
    )

# Vector DB (make sure build_hospital_db.py ran)
vectordb = Chroma(
    persist_directory=str(db_path),
    embedding_function=embeddings
)

# LLM for RAG summarization
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

# Create retriever
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that provides information about veterinary hospitals in Nashik, India. 🏥

RESPONSE GUIDELINES:
✅ Use simple, easy-to-understand language
✅ Use emojis to make responses friendly (🏥 🐾 📍 📞 ⚕️)
✅ Format with bullet points (•) and clear sections
✅ Keep responses concise (2-3 short paragraphs max)
✅ Highlight important info (location, contact, services)
✅ Use simple words - avoid complex terms
✅ DO NOT use markdown headers (#, ##, ###) - use bold text with emojis instead

FORMAT EXAMPLE:
🏥 **Hospital Name**
📍 Location: [area]
📞 Contact: [phone]
⚕️ Services: [list services]
🐾 Animals: [list animals]

If you don't know the answer, say so simply."""),
    ("human", "Context:\n{context}\n\nQuestion: {question}")
])

# Create RAG chain using LCEL (LangChain Expression Language)
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

hospital_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def get_hospital_response(query, conversation_history=None):
    """
    Returns hospital info from RAG DB with conversation context
    
    Args:
        query: Current user question
        conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
    """
    try:
        # Get source documents
        source_docs = retriever.invoke(query)
        
        # Build context with conversation history if available
        context_with_history = ""
        if conversation_history:
            # Include relevant previous questions about hospitals
            recent_hospital_queries = [
                msg["content"] for msg in conversation_history[-10:]  # Increased from 4 to 10
                if msg["role"] == "user" and any(kw in msg["content"].lower() 
                for kw in ["hospital", "clinic", "vet", "emergency", "near"])
            ]
            if recent_hospital_queries:
                context_with_history = f"\n\nPrevious related questions: {', '.join(recent_hospital_queries)}"
        
        # Enhance query with context if needed
        enhanced_query = query + context_with_history if context_with_history else query
        
        # Get response from chain
        result = hospital_chain.invoke(enhanced_query)
        
        return {
            "result": result,
            "source_documents": source_docs
        }
    except Exception as e:
        return {"result": f"Error retrieving hospital information: {str(e)}", "source_documents": []}
