from vectorize.ingestor import Ingestor
import util.db as db
from sentence_transformers import SentenceTransformer  # type: ignore
import logging


class Vectorizer:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def embed_and_insert(self, chunks, ingestor: Ingestor):
        self.logger.info("Starting embed / insert process.")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        client = db.get_chroma_client()
        collection = db.get_chroma_collection(client)

        for chunk in chunks:
            embedded_chunk = self.vectorize_chunk(chunk, model)
            ingestor.process_chunk(embedded_chunk, collection)

        # flush anything that might still be in the buffer
        ingestor.flush_buffer(collection)
        self.logger.info("Finished with embed / insert process.")

    def vectorize_chunk(self, chunk, model):
        embedding = self.embed_text(chunk['document'], model)
        chunk['embedding'] = embedding
        return chunk

    def embed_text(self, text, model):
        embedding_raw = model.encode(text, show_progress_bar=False)
        embedding_raw = embedding_raw.astype('float32')
        embedding = embedding_raw.tolist()
        return embedding
