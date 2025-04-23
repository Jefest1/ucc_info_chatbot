from unittest.mock import patch
import pytest
from qdrant_client import QdrantClient
from utils.vectorize import ingest_docs
from config.settings import settings


@pytest.fixture
def qdrant_client_fixture():
    client = QdrantClient(
        url="https://e310ee91-5952-4d0b-ae43-7f0487942aaa.eu-west-2-0.aws.cloud.qdrant.io:6333",
        api_key=settings.QDRANT_API_KEY,
    )
    return client


def test_qdrant_client_connection(qdrant_client_fixture):
    try:
        collections = qdrant_client_fixture.get_collections()
        assert collections is not None
    except Exception as e:
        pytest.fail(f"Qdrant client connection failed: {e}")


@patch("utils.vectorize.ingest_docs")
def test_ingest_docs(mock_ingest_docs):
    ingest_docs()
    mock_ingest_docs.assert_called_once()