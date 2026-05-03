def detect_intent(query: str) -> str:
    """
    Simple keyword-based intent detection:
    Returns "HOSPITAL" or "CARE"
    """
    hospital_keywords = ["hospital", "clinic", "vet", "emergency", "near", "ngo"]
    if any(k in query.lower() for k in hospital_keywords):
        return "HOSPITAL"
    return "CARE"
