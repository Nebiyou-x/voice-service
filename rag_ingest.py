import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

def ingest_knowledge_base():
    print("⏳ Loading embedding model (BGE-M3)...")
    encoder = SentenceTransformer("BAAI/bge-m3")

    client = QdrantClient(path="./qdrant_db")
    COLLECTION_NAME = "lersha_agronomy"

    if not client.collection_exists(collection_name=COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=encoder.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            )
        )
        print(f"✅ Created Qdrant collection: {COLLECTION_NAME}")

    documents = [
        {
            "id": 1,
            "text": "በበቆሎ እርሻ ላይ የሚከሰት የእንቁንጣጥ ተባይ (Fall Armyworm) ለመቆጣጠር በቅድመ-ዕድገት ወቅት ተስማሚ ኬሚካሎችን መጠቀም ያስፈልጋል። ምልክቶቹም በቅጠሎች ላይ የሚታዩ ቀዳዳዎች ናቸው።",
            "source": "Lersha Pest Management Guide v2"
        },
        {
            "id": 2,
            "text": "ለስንዴ እህል ምርት መጨመር የዩሪያ እና የዳፕ (DAP) ማዳበሪያ በወቅቱ መጠቀም ወሳኝ ነው። በአንድ ሄክታር መሬት ላይ መደበኛ አጠቃቀም 100 ኪሎ ግራም ዳፕ ይመከራል።",
            "source": "Ethiopian Ministry of Agriculture Fertilizer Manual"
        }
    ]

    points = []
    for doc in documents:
        vector = encoder.encode(doc["text"]).tolist()
        points.append(
            models.PointStruct(
                id=doc["id"],
                vector=vector,
                payload={"text": doc["text"], "source": doc["source"]}
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Successfully ingested {len(documents)} documents into Qdrant!")

if __name__ == "__main__":
    ingest_knowledge_base()