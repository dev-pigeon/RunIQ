from vectorize.ingestor import Ingestor
import pytest  # type: ignore
from util.db import get_chroma_client, get_chroma_collection


@pytest.fixture(scope='module', autouse=True)
def client():
    return get_chroma_client()


@pytest.fixture(scope='module', autouse=True)
def collection(client):
    return get_chroma_collection(client)


@pytest.fixture
def sample_buffer():
    return [
        {
            "id": f"doc1-{x}",
            "document": f"test chunk {x}.",
            "metadata": {"source": "doc1.txt"},
            "embedding": [float(i) for i in range(384)],
        }
        for x in range(90)
    ]


def test_get_parameters(sample_buffer):
    i = Ingestor()
    i.buffer = sample_buffer  # type: ignore
    parameters = i.get_parameters()
    assert parameters['ids'] == [f"doc1-{i}" for i in range(90)]
    assert len(parameters['docs']) == 90
    assert all("test chunk" in doc for doc in parameters['docs'])
    assert parameters['metas'][0]['source'] == "doc1.txt"


def test_flush_buffer_full(collection, sample_buffer):
    i = Ingestor()
    i.buffer = sample_buffer
    assert len(i.buffer) == 90
    i.flush_buffer(collection)
    assert len(i.buffer) == 0


def test_flush_buffer_empty(collection):
    i = Ingestor()
    try:
        i.flush_buffer(collection)
    except ValueError:
        pytest.fail("ValueError should not be thrown for an empty buffer.")
