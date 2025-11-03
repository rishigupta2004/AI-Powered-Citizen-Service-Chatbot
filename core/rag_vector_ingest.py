import os
import glob # We need this for a more robust path search
from langchain_community.document_loaders import PyPDFDirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS

# --- Configuration ---
DATA_PATH = "AI-Powered-Citizen-Service-Chatbot/data/docs" 
VECTOR_DB_PATH = "AI-Powered-Citizen-Service-Chatbot/faiss_index"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" 

def create_vector_store(data_path: str, db_path: str):
    """
    Loads, splits, and embeds documents, saving the FAISS index.
    Includes robust error handling to skip corrupted or non-PDF files.
    """
    print("Starting document loading and indexing...")
    
    # 1. Use glob to find all PDF paths recursively
    # This correctly finds all .pdf files in the data_path and its subdirectories
    search_path = os.path.join(data_path, "**", "*.pdf")
    try:
        pdf_paths = glob.glob(search_path, recursive=True)
    except Exception as e:
        raise RuntimeError(f"FATAL ERROR during path search: {e}")

    if not pdf_paths:
        raise RuntimeError(f"FATAL ERROR: No PDF documents found in '{data_path}'. Index creation failed.")

    documents = []
    print(f"Found {len(pdf_paths)} potential PDF files. Attempting to load individually...")
    
    # 2. Iterate through files and load individually (with error handling)
    for doc_path in pdf_paths:
        file_name = os.path.basename(doc_path)
        
        try:
            # Use the PyPDFLoader for a single file (more direct and less prone to errors)
            loader = PyPDFLoader(doc_path)
            docs = loader.load()
            
            if docs:
                documents.extend(docs)
                print(f"✅ Successfully loaded: {file_name}")
            else:
                print(f"⚠️ Skipped {file_name}: File was found but yielded no content (likely empty or protected).")
                
        except Exception as e:
            # Catch exceptions from failed PDF parsing (e.g., HTML files, corrupted data)
            print(f"❌ ERROR: Failed to load {file_name}. Skipping this file. Error details: {e}")


    # 3. Final check before proceeding
    if not documents:
        raise RuntimeError(f"FATAL ERROR: No valid documents could be loaded from {data_path}. Index creation failed.")

    print(f"\nTotal valid documents loaded: {len(documents)}")
    
    # 4. Splitting and Embedding
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # Create Embeddings
    embeddings = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    # Create the FAISS index and save it locally
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(db_path)
    print(f"FAISS index created and saved successfully at {db_path}.")

if __name__ == "__main__":
    # --- EXECUTION ---
    print(f"--- RAG INGESTION SCRIPT STARTING ---")
    
    # Check for existing index to prevent re-creation
    if os.path.exists(VECTOR_DB_PATH):
        print(f"Index found at '{VECTOR_DB_PATH}'. Delete the folder to rebuild the database.")
    else:
        try:
            create_vector_store(DATA_PATH, VECTOR_DB_PATH)
        except RuntimeError as e:
            print(f"FATAL ERROR: {e}")