from vectorize.ingestor import Ingestor
import util.db as db
import logging
import os


class Vectorizer:
    def __init__(self, id, collection_name="") -> None:
        self.collection_name = os.environ['RUNBOT_CHROMA_COLLECTION'] if collection_name == "" else collection_name
        self.logger = logging.getLogger(id)

    def embed_and_insert(self, chunks, ingestor: Ingestor, input_model):
        self.logger.info("Starting embed / insert process.")
        client = db.get_chroma_client()
        collection = db.get_chroma_collection(client, self.collection_name)

        for chunk in chunks:
            embedded_chunk = self.vectorize_chunk(chunk, input_model)
            ingestor.process_chunk(embedded_chunk, collection)

        # flush anything that might still be in the buffer
        ingestor.flush_buffer(collection)
        self.logger.info("Finished with embed / insert process.")

    def embed_chunks(self, chunks, model):
        embedded_chunks = []
        for chunk in chunks:
            embedded_chunk = self.vectorize_chunk(chunk, model)
            embedded_chunks.append(embedded_chunk)
        return embedded_chunks

    def vectorize_chunk(self, chunk, model):
        embedding = self.embed_text(chunk['document'], model)
        chunk['embedding'] = embedding
        return chunk

    def embed_text(self, text, model):
        embedding_raw = model.encode(text, show_progress_bar=False)
        embedding_raw = embedding_raw.astype('float32')
        embedding = embedding_raw.tolist()
        return embedding
