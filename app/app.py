import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import rag module
sys.path.insert(0, str(Path(__file__).parent.parent))

from intent import detect_intent
from care_llm import get_care_response
from hospital_chain import get_hospital_response

st.set_page_config(
    page_title="AI", 
    page_icon="🐾",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "source_docs_history" not in st.session_state:
    st.session_state.source_docs_history = []

# Sidebar for additional info
with st.sidebar:
    st.header("🐾 Health Assistant")
    st.markdown("**Ask me about:**")
    st.markdown("- 🩺 Animal care and health guidance")
    st.markdown("-")
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.source_docs_history = []
        st.rerun()
    
    st.divider()
    st.caption("⚠️ This is educational guidance only. Consult a licensed veterinarian for medical advice.")

# Main chat interface

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show source documents for assistant messages with sources
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("📄 Source Documents"):
                for i, doc in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {i}:**")
                    st.text(doc.page_content)
                    st.divider()

# Chat input
if prompt := st.chat_input("Ask about animal care or nearby vet hospitals..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                intent = detect_intent(prompt)
                
                # Get conversation history (all messages except the current one we just added)
                conversation_history = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in st.session_state.messages[:-1]  # Exclude the just-added user message
                ]
                
                if intent == "CARE":
                    response = get_care_response(prompt, conversation_history)
                    st.markdown(response)
                    st.caption("⚠️ Educational guidance only. Consult a licensed veterinarian.")
                    
                    # Add assistant response to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": None
                    })
                else:
                    response = get_hospital_response(prompt, conversation_history)
                    if response and "result" in response:
                        st.markdown(response["result"])
                        
                        # Store source documents
                        source_docs = response.get("source_documents", [])
                        if source_docs:
                            with st.expander("📄 Source Documents"):
                                for i, doc in enumerate(source_docs, 1):
                                    st.markdown(f"**Source {i}:**")
                                    st.text(doc.page_content)
                                    st.divider()
                        
                        # Add assistant response to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response["result"],
                            "sources": source_docs
                        })
                    else:
                        error_msg = "No results found. Please try a different query."
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "sources": None
                        })
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.info("Please ensure the hospital database has been built by running: python ingest/build_hospital_db.py")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "sources": None
                })
