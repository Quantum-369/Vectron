from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set API keys and URLs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Preprocess the Markdown File
def preprocess_markdown(file_path, chunk_size=500):
    """
    Preprocess the Markdown file into smaller chunks.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    return chunks

# 2. Generate Embeddings with Batching
def generate_embeddings_with_batching(chunks, batch_size=10):
    """
    Generate embeddings for text chunks in batches.
    """
    embeddings = []
    for i in range(0, len(chunks), batch_size):
        # Create a batch of chunks
        batch = chunks[i:i + batch_size]
        
        # Generate embeddings for the batch
        response = openai_client.embeddings.create(
            input=batch,
            model="text-embedding-3-small"
        )
        
        # Store embeddings from the batch
        for text, embedding in zip(batch, response.data):
            embeddings.append({
                "text": text,
                "embedding": embedding.embedding
            })
    return embeddings

# 3. Store Embeddings in Supabase with Batching
def store_embeddings_in_supabase(embeddings):
    """
    Store text and embeddings in the Supabase database.
    """
    for item in embeddings:
        data, count = supabase.table("embeddings").insert({
            "text": item["text"],
            "embedding": item["embedding"]
        }).execute()

if __name__ == "__main__":
    # File path for the Markdown file
    file_path = r"C:\Users\harsh\Downloads\MS projects\Deepgram\RAG\scraped_content.md"

    # Step 1: Preprocess Markdown File
    print("Preprocessing Markdown file...")
    chunks = preprocess_markdown(file_path)
    print(f"Total Chunks: {len(chunks)}")

    # Step 2: Generate Embeddings
    print("Generating embeddings for chunks...")
    embeddings = generate_embeddings_with_batching(chunks, batch_size=10)
    print(f"Generated {len(embeddings)} embeddings.")

    # Step 3: Store Embeddings in Supabase
    print("Storing embeddings in Supabase...")
    store_embeddings_in_supabase(embeddings)
    print("Embeddings stored successfully.")
