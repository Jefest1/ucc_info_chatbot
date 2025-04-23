import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from scraper import run_crawl
from config.settings import settings
import logging
from logger import setup_logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_openai import OpenAIEmbeddings

# Initialize root logger
setup_logging()
logger = logging.getLogger(__name__)

# create collection if it doesn't exist
collection_name = settings.QDRANT_COLLECTION_NAME
client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
try:
    client.get_collection(collection_name)
except Exception as e:
    if "Not found" in str(e):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
    else:
        raise e

# 50 static pages: top‑level UCC URLs (excluding news pagination)
STATIC_URLS = [
    "https://ucc.edu.gh/",                      # 1. Homepage
    "https://ucc.edu.gh/main/about/history",    # 2. History
    "https://ucc.edu.gh/main/about/vision-mission",  # 3. Vision & Mission
    "https://ucc.edu.gh/main/about/administration",  # 4. Administration
    "https://ucc.edu.gh/main/about/leadership",      # 5. Leadership
    "https://ucc.edu.gh/contacts",               # 6. Contacts
    "https://ucc.edu.gh/announcements",          # 7. Announcements
    "https://ucc.edu.gh/press-releases",         # 8. Press Releases
    "https://ucc.edu.gh/main/academic-programmes/all",  # 9. All Programmes
    # 10. UG Programmes
    "https://ucc.edu.gh/main/applicants-and-students/undergraduate-programmes",
    # 11. PG Programmes
    "https://ucc.edu.gh/main/applicants-and-students/postgraduate-programmes",
    "https://ucc.edu.gh/academics/faculties-schools",    # 12. Faculties & Schools
    "https://ucc.edu.gh/academics/departments",          # 13. Departments
    "https://ucc.edu.gh/academics/affiliate-institutions",  # 14. Affiliations
    "https://ucc.edu.gh/main/applicants-and-students/credit-weightings",
    # 17. Grading System
    "https://ucc.edu.gh/main/applicants-and-students/registration",  # 18. Registration
    "https://ucc.edu.gh/admission-notices",            # 19. Admission Notices
    "https://ucc.edu.gh/admission-notices/undergraduate-admissions",  # 20. UG Admissions
    "https://ucc.edu.gh/admission-notices/regular-postgraduate-admissions",  # 21. PG Admissions
    "https://ucc.edu.gh/admission-notices/distance-postgraduate-admissions",  # 22. Distance PG
    "https://apply.ucc.edu.gh/",                       # 23. Apply Portal
    "https://admissionlist.ucc.edu.gh/",               # 24. Admissions List
    "https://ucc.edu.gh/main/explore-ucc/our-campus",          # 25. Our Campus
    "https://ucc.edu.gh/main/explore-ucc/accommodation",       # 26. Accommodation
    "https://ucc.edu.gh/main/explore-ucc/restaurants-and-eateries",  # 27. Eateries
    "https://ucc.edu.gh/main/explore-ucc/recreational-and-social-activities",  # 28. Recreation
    # 29. Library
    # 30. Transport   # 31. Health Services
    "https://ucc.edu.gh/main/explore-ucc/transportation",
    "https://www.ucc.edu.gh/events",                        # 32. Events
    "https://dric.ucc.edu.gh/",
    # 33. DRIC Home
    "https://ucc.edu.gh/main/about/vision-mission-and-core-values",
    "https://dric.ucc.edu.gh/policy-guidelines",            # 34. DRIC Policies
    "https://dric.ucc.edu.gh/annual-research-report",       # 35. DRIC Reports
    "https://dric.ucc.edu.gh/research-lectures",            # 36. DRIC Lectures
    "https://dric.ucc.edu.gh/research-lectures/inaugural-lectures",  # 37. Inaugurals
    "https://ucc.edu.gh/quick-links/portal",                # 38. Portal
    "https://ucc.edu.gh/quick-links/sitemap",               # 39. Sitemap
    "https://library.ucc.edu.gh/",                          # 40. Library Subdomain
    "https://ucc.edu.gh/quick-links/e-learning",            # 41. E‑Learning
    "https://ucc.edu.gh/main/about/policies-and-guidelines",  # 42. Policies & Guidelines
    "https://ucc.edu.gh/main/about/corporate-strategic-plan",  # 43. Strategic Plan
    "https://ucc.edu.gh/main/about/quality-assurance",      # 44. Quality Assurance
    "https://ucc.edu.gh/main/about/awards-and-achievements",  # 45. Awards & Achievements
    "https://ucc.edu.gh/main/about/statutes-of-ucc",        # 46. Statutes
    "https://ucc.edu.gh/main/about/governance-and-administration",  # 47. Governance
    "https://ucc.edu.gh/main/about/compliance",             # 48. Compliance
    # 49.                 # 50. Data Hub
    "https://ucc.edu.gh/main/about/fast-facts",
]

NEWS_PAGES = [f"https://ucc.edu.gh/news?page={i}" for i in range(50)]
ACADEMIC_PROGRAMMES = [
    f"https://ucc.edu.gh/main/academic-programmes/all?page={i}" for i in range(14)]
ALL_URLS = STATIC_URLS + NEWS_PAGES + ACADEMIC_PROGRAMMES

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  

def ingest_docs():
    logger.info("Starting full crawl of %d URLs", len(ALL_URLS))

    raw_documents = run_crawl(ALL_URLS)
    if not raw_documents:
        logger.error("No documents were retrieved from crawling")
        return

    logger.info("Retrieved %d documents from crawling", len(raw_documents))

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1300,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    documents = text_splitter.split_documents(raw_documents)
    logger.info("Split into %d chunks", len(documents))

    logger.info("Adding %d chunks to Qdrant", len(documents))
    try:
        vector_store = QdrantVectorStore.from_documents(
            documents,
            embeddings,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=240,
            batch_size=100,
            prefer_grpc=True
        )
        logger.info("Successfully loaded documents to Qdrant")
        return vector_store
    except Exception as e:
        logger.error("Error loading documents to Qdrant: %s", str(e))
        raise

if __name__ == "__main__":
    ingest_docs()