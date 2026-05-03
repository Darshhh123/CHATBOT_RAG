from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from load_hospitals import load_hospital_docs
from pathlib import Path

def main():
    # Load hospital documents
    docs = load_hospital_docs()
    
    if not docs:
        print("❌ No hospital documents loaded!")
        return

    # Create embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    # Create Chroma vector DB (path relative to project root)
    db_path = Path(__file__).parent / "hospital_db"
    db_path.mkdir(exist_ok=True)

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(db_path)
    )

    # Persist the database (newer ChromaDB versions handle this automatically)
    # vectordb.persist()  # May be deprecated, but keeping for compatibility
    print("✅ Hospital vector DB created successfully!")
    print(f"   Database location: {db_path}")

if __name__ == "__main__":
    main()
