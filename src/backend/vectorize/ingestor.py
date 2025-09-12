import os
import chromadb  # type: ignore


class Ingestor:
    def __init__(self) -> None:
        # get env vars here?
        self.MAX_BUFFER_SIZE = 100
        self.buffer = []

    def get_chroma_client(self):
        perisitent_chroma_path = os.environ['RUNBOT_CHROMA_PATH']
        client = chromadb.PersistentClient(path=perisitent_chroma_path)
        return client

    def get_chroma_collection(self, client):
        collection_name = os.environ['RUNBOT_CHROMA_COLLECTION']
        collection = client.get_or_create_collection(name=collection_name)
        return collection

    def process_chunk(self, chunk, collection):
        pass

    def flush_buffer(self, collection):
        pass
