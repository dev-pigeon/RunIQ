# takes raw query, embeds it, uses the chroma db collection to get relevant chunks
# returns relevant chunks
import os
import chromadb  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
from vectorize.vectorizer import Vectorizer


class Retriever:
    def __init__(self) -> None:
        self.vectorizer = Vectorizer()
        pass

    def get_chroma_client(self):
        perisitent_chroma_path = os.environ['RUNBOT_CHROMA_PATH']
        client = chromadb.PersistentClient(path=perisitent_chroma_path)
        return client

    def get_chroma_collection(self, client):
        collection_name = os.environ['RUNBOT_CHROMA_COLLECTION']
        collection = client.get_or_create_collection(name=collection_name)
        return collection

    def retrieve(self, text):
        pass
