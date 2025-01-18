from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Supabase and OpenAI
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize conversation memory
conversation_history = []
MAX_HISTORY = 5  # Maximum number of conversation pairs to remember

def generate_embeddings(texts):
    """
    Generate embeddings for a list of text strings.
    """
    embeddings = []
    for text in texts:
        response = openai_client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        embeddings.append(response.data[0].embedding)
    return embeddings

def query_supabase(query, top_k=5):
    """
    Query the Supabase database for the most relevant matches.
    """
    query_embedding = generate_embeddings([query])[0]
    
    response = supabase.rpc("match_embeddings", {
        "query_embedding": query_embedding,
        "match_count": top_k
    }).execute()
    
    if not response.data:
        return []
    
    return response.data

def get_conversation_context():
    """
    Format the conversation history into a string context.
    """
    if not conversation_history:
        return ""
    
    context = "\nPrevious conversation:\n"
    for i, (user_msg, assistant_msg) in enumerate(conversation_history, 1):
        context += f"User: {user_msg}\nAssistant: {assistant_msg}\n"
    return context

def generate_response(query):
    """
    Generate a response using retrieved content and GPT-4 Turbo with conversation memory.
    """
    results = query_supabase(query)
    if not results:
        return "I couldn't find any relevant information in the database to answer your question."

    # Combine the context from the retrieved results
    retrieved_context = " ".join([result["text"] for result in results])
    
    # Get conversation history context
    conversation_context = get_conversation_context()
    
    # Combine both contexts
    full_context = f"{retrieved_context}\n{conversation_context}"

    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant. Use the provided context and conversation history to answer the user's question. "
            "For follow-up questions, consider both the current context and the previous conversation. "
            "Respond in a structured and properly formatted way. Use the following guidelines for formatting:\n"
            "- Use headings for major sections, e.g., ## Heading\n"
            "- Use bullet points for lists, e.g., - Item\n"
            "- Highlight important points using **bold** or *italics*\n"
            "- Ensure clarity and maintain context from previous conversations when relevant."
        )},
        {"role": "user", "content": f"Context: {full_context}\n\nQuestion: {query}"}
    ]

    # Generate response using GPT
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1024
    )
    
    assistant_response = response.choices[0].message.content.strip()
    
    # Update conversation history
    conversation_history.append((query, assistant_response))
    
    # Keep only the last MAX_HISTORY conversations
    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)
    
    return assistant_response

if __name__ == "__main__":
    print("=== Supabase Query and GPT-4 Turbo Response Test ===")
    
    while True:
        query = input("Enter your query (or press 'q' to quit): ").strip()
        if query.lower() == 'q':
            print("Exiting... Goodbye!")
            break

        print("\nQuerying Supabase and generating response...\n")
        try:
            response = generate_response(query)
            print("Response:\n")
            print(response)
        except Exception as e:
            print("An error occurred:")
            print(e)
