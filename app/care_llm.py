from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from prompts import CARE_PROMPT
import yaml
import os
from pathlib import Path
import base64

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

# Gemini LLM instance
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

def get_care_response(query, conversation_history=None, image_data=None):
    """
    Use Gemini LLM to provide general care guidance with conversation context and optional image
    
    Args:
        query: Current user question
        conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "..."}]
        image_data: Base64 encoded image data (optional)
    """
    try:
        # Build messages with system prompt and conversation history
        messages = [
            SystemMessage(content="""You are a friendly and helpful animal care assistant. 🐾

IMPORTANT RULES:
❌ NEVER diagnose diseases
❌ NEVER prescribe medicine or dosages
✅ Give simple, easy-to-understand care guidance
✅ Use emojis to make responses friendly and clear
✅ Format answers with bullet points (•) and sections
✅ Keep responses concise (2-4 short paragraphs max)
✅ Use simple words that anyone can understand
✅ Always advise consulting a licensed veterinarian

RESPONSE FORMAT:
• Use emojis relevant to the topic (🐾 🐱 🐶 🐄 🐐 etc.)
• Organize information with bullet points
• Use clear section headers with emojis (NO markdown headers like ###)
• Keep language simple - avoid complex medical terms
• Be friendly and conversational
• Keep it short and to the point
• DO NOT use markdown headers (#, ##, ###) - use bold text with emojis instead

Use conversation history to provide context-aware responses.""")
        ]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-20:]:  # Keep last 20 messages for context (increased from 6)
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add current query with image if provided
        if image_data:
            # Extract base64 data (remove data:image/...;base64, prefix if present)
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Add enhanced prompt for image analysis
            enhanced_query = f"""{query}

Please analyze the uploaded image carefully. Look for:
• Visible symptoms or issues
• Animal condition and behavior
• Any visible injuries, rashes, or abnormalities
• Overall health indicators

Provide general guidance based on what you observe, but remember:
❌ DO NOT diagnose specific diseases
❌ DO NOT prescribe medications
✅ Provide general observations and care suggestions
✅ Always recommend consulting a veterinarian for proper diagnosis"""
            
            # Create message with image and text using content blocks format
            # Gemini via LangChain accepts content blocks with type "image" and source_type "base64"
            messages.append(HumanMessage(content=[
                {
                    "type": "text",
                    "text": enhanced_query
                },
                {
                    "type": "image",
                    "source_type": "base64",
                    "data": image_data,
                    "mime_type": "image/jpeg"
                }
            ]))
        else:
            messages.append(HumanMessage(content=query))
        
        # Get response
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error generating response: {str(e)}"
