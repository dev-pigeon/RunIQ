from vectorize.chunker import Chunker


def test_has_tables_true():
    c = Chunker()
    data = {"tables": [{"fake": "table"}]}
    assert c.has_tables(data) is True


def test_has_tables_false():
    c = Chunker()
    data = {"other": [{"not a": "table"}]}
    assert c.has_tables(data) is False


def test_make_chunk_structure():
    c = Chunker()
    text = "Fake chunker"
    chunk = c.make_chunk(text, 0, "tests")
    assert chunk['id'] == "tests-0"
    assert chunk['metadata'] == {"source": "tests"}
    assert chunk['embedding'] is not None
    assert chunk['document'] == text


def test_multiple_chunks():
    c = Chunker()
    # each para here is 250 chars, should have 3 chunks
    data = {"paragraphs": ["a"*250, "b"*250, "c"*250], "source": "tests"}
    chunks = c.chunk_paragraphs(data)
    assert len(chunks) >= 3


def test_one_chunk():
    c = Chunker()
    # each para here is 250 chars, should have 3 chunks
    data = {"paragraphs": ["a"*100], "source": "tests"}
    chunks = c.chunk_paragraphs(data)
    assert len(chunks) == 1


def test_chunk_overlap():
    c = Chunker()
    data = {"paragraphs": ["a"*200, "b"*200], "source": "tests"}
    chunks = c.chunk_paragraphs(data)
    assert chunks[0]["document"][-c.CHUNK_OVERLAP:] == chunks[1]["document"][:c.CHUNK_OVERLAP]
