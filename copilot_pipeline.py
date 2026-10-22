import httpx
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("BAAI/bge-m3")
client = QdrantClient(path="./qdrant_db")
COLLECTION_NAME = "lersha_agronomy"

TTS_API_URL = "http://localhost:8000/v1/synthesize"
LLAMA_API_URL = "http://localhost:11434/api/generate" 

def retrieve_context(query: str, top_k: int = 2) -> str:
    query_vector = encoder.encode(query).tolist()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    contexts = [hit.payload["text"] for hit in results]
    return "\n".join(contexts)

def query_llama3(prompt: str) -> str:
    system_prompt = (
        "አንተ የለርሻ የግብርና ባለሙያ ረዳት ነህ። "
        "እባክህ የቀረበውን መረጃ ብቻ በመጠቀም ለአርሶ አደሩ አጭር፣ ግልጽ እና ትክክለኛ ምላሽ በአማርኛ ስጥ። "
        "ከመረጃው ውጭ አታስብ።"
    )
    
    full_prompt = f"{system_prompt}\n\nአውድ (Context):\n{prompt}\n\nጥያቄ: የግብርና ባለሙያ ምክር ይስጡኝ።"

    payload = {
        "model": "llama3",
        "prompt": full_prompt,
        "stream": False
    }
    
    with httpx.Client(timeout=30.0) as client_http:
        response = client_http.post(LLAMA_API_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            raise Exception(f"LLM Error: {response.text}")

def generate_voice_response(user_query: str, output_filename: str = "copilot_output.wav"):
    print(f"🔍 Searching knowledge base for: '{user_query}'")
    context = retrieve_context(user_query)
    
    print("🤖 Generating grounded answer using Llama 3...")
    llm_answer = query_llama3(f"ጥያቄ: {user_query}\nማጣቀሻ መረጃ: {context}")
    print(f"📝 Generated Text: {llm_answer}")

    print("🎙️ Sending text to OmniVoice TTS microservice...")
    tts_payload = {
        "text": llm_answer,
        "language": "Amharic",
        "format": "wav"
    }
    
    with httpx.Client(timeout=60.0) as client_http:
        response = client_http.post(TTS_API_URL, json=tts_payload)
        if response.status_code == 200:
            with open(output_filename, "wb") as f:
                f.write(response.content)
            print(f"✅ Success! Voice response saved to {output_filename}")
        else:
            print(f"❌ TTS Error: {response.text}")

if __name__ == "__main__":
    sample_query = "በቆሎ እርሻ ላይ የእንቁንጣጥ ተባይ ስጋት ሲኖር ምን ማድረግ አለበት?"
    generate_voice_response(sample_query)