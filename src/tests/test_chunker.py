from vectorize.chunker import Chunker
import pytest  # type: ignore


@pytest.fixture(scope='module', autouse=True)
def sentences_paragraph_no_abbrev():
    return "This is sentence one. What is a sentence? I love sentences!"


@pytest.fixture(scope='module', autouse=True)
def sentences_paragraph_with_abbrev():
    return "This is sentence one. Dr. Young is my wife's title."


def test_get_sentences_no_abbrev(sentences_paragraph_no_abbrev):
    c = Chunker()
    sentences = c.get_sentences(sentences_paragraph_no_abbrev)
    assert sentences[0] == "This is sentence one."
    assert sentences[1] == "What is a sentence?"
    assert sentences[2] == "I love sentences!"


def test_get_sentences_with_abbrev(sentences_paragraph_with_abbrev):
    c = Chunker()
    sentences = c.get_sentences(sentences_paragraph_with_abbrev)
    assert sentences[0] == "This is sentence one."
    assert sentences[1] == "Dr. Young is my wife's title."


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
    data = {"paragraphs": ["aaa "*250, "bbb " *
                           250, "ccc "*250], "source": "tests"}
    chunks = c.chunk_paragraphs(data)
    assert len(chunks) >= 3


def test_one_chunk():
    c = Chunker()
    # each para here is 250 chars, should have 3 chunks
    data = {"paragraphs": ["aaa "*100], "source": "tests"}
    chunks = c.chunk_paragraphs(data)
    assert len(chunks) == 1


def test_chunk_overlap():
    c = Chunker()
    data = {"paragraphs": ["a "*200, "b "*200], "source": "tests"}
    chunks = c.chunk_paragraphs(data)
    assert chunks[0]["document"][-c.CHUNK_OVERLAP:] == chunks[1]["document"][:c.CHUNK_OVERLAP]


def test_has_key_true():
    c = Chunker()
    data = {"tables": ["t1"], "source": "tests"}
    key = "tables"
    assert c.has_key(data, key) is True


def test_has_key_false():
    c = Chunker()
    data = {"other": [{"not a": "table"}]}
    assert c.has_key(data, "tables") is False


def test_no_paragraphs():
    c = Chunker()
    data = {"tables": ["t1"], "source": "tests"}
    try:
        chunks = c.chunk_paragraphs(data)
        assert len(chunks) == 0
    except KeyError:
        pytest.fail("KeyError was unexpectedly raised.")


def test_chunk_tables_no_tables():
    try:
        c = Chunker()
        data = {"other": [{"not a": "table"}], "source": "tests"}
        c.chunk_tables(data)
    except KeyError as e:
        pytest.fail(f"KeyError was unexpectedly raised: {e}")
