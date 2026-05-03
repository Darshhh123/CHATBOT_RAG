import json
from langchain_core.documents import Document
from pathlib import Path

def load_hospital_docs():
    """
    Load hospital JSON and convert to Document objects
    """
    # Get path relative to project root
    json_path = Path(__file__).parent.parent / "data" / "hospitals" / "hospital.json"
    
    if not json_path.exists():
        raise FileNotFoundError(f"Hospital data file not found at {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        hospitals = json.load(f)

    docs = []
    for h in hospitals:
        text = f"""
Hospital Name: {h['name']}
Area: {h['area']}
City: {h['city']}
Animals Supported: {', '.join(h['animals_supported'])}
Services: {', '.join(h['services'])}
Emergency Available: {h['emergency']}
Type: {h['type']}
Contact: {h['contact']}
"""
        docs.append(
            Document(
                page_content=text.strip(),
                metadata={
                    "name": h["name"],
                    "area": h["area"],
                    "city": h["city"],
                    "emergency": h["emergency"],
                    "type": h["type"]
                }
            )
        )
    return docs
