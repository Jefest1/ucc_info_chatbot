from qdrant_client import QdrantClient
from config.settings import settings

qdrant_client = QdrantClient(
    url="https://e310ee91-5952-4d0b-ae43-7f0487942aaa.eu-west-2-0.aws.cloud.qdrant.io:6333", 
    api_key=settings.QDRANT_API_KEY,
)

print(qdrant_client.get_collections())