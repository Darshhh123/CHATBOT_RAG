from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
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
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY not found in secrets.yaml or environment variables")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0  # forces factual answers, reduces hallucination
)

class ChatState(TypedDict):
    messages: Annotated[List[dict], add_messages]

def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

