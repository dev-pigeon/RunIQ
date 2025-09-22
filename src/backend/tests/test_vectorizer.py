from vectorize.vectorizer import Vectorizer
import pytest  # type: ignore
import numpy as np


@pytest.fixture
def sample_chunks():
    return [
        {
            "id": f"doc1-{x}",
            "document": f"test chunk {x}.",
            "metadata": {"source": "doc1.txt"},
            "embedding": [],
        }
        for x in range(101)
    ]


def test_vectorize_chunk_sets_embeddings(sample_chunks, mocker):
    fake_model = mocker.Mock()
    fake_model.encode.return_value = np.array([0.1, 0.2, 0.3])
    v = Vectorizer()

    chunk = sample_chunks[0].copy()
    result = v.vectorize_chunk(chunk, fake_model)
    assert "embedding" in result
    assert result['embedding'] == np.array(
        [0.1, 0.2, 0.3]).astype('float32').tolist()


def test_embed_and_insert_calls_ingestor(sample_chunks, mocker):
    mock_db = mocker.patch("vectorize.vectorizer.db")
    mock_collection = mock_db.get_chroma_collection.return_value

    fake_ingestor = mocker.Mock()
    mock_model = mocker.Mock()
    v = Vectorizer()
    v.embed_and_insert(sample_chunks, fake_ingestor, mock_model)

    # assert methods are called
    assert fake_ingestor.process_chunk.call_count == len(sample_chunks)
    fake_ingestor.flush_buffer.assert_called_once_with(mock_collection)
