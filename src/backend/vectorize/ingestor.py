import os
import chromadb  # type: ignore


class Ingestor:
    def __init__(self) -> None:
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
        self.buffer.append(chunk)
        if len(self.buffer) > self.MAX_BUFFER_SIZE:
            self.flush_buffer(collection)

    def get_parameters(self):
        ids = [chunk['id'] for chunk in self.buffer]
        docs = [chunk['document'] for chunk in self.buffer]
        metas = [chunk['metadata'] for chunk in self.buffer]
        embeddings = [chunk['embedding'] for chunk in self.buffer]

        parameters = {
            'ids': ids,
            'docs': docs,
            'metas': metas,
            'embeddings': embeddings
        }
        return parameters

    def flush_buffer(self, collection):
        parameters = self.get_parameters()
        self.batch_insert(collection, parameters)
        self.buffer = []

    def batch_insert(self, collection, parameters):
        collection.add(
            ids=parameters['ids'],
            documents=parameters['docs'],
            metadatas=parameters['metas'],
            embeddings=parameters['embeddings']
        )
