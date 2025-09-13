import chromadb  # type: ignore
import os


def get_chroma_client():
    perisitent_chroma_path = os.environ['RUNBOT_CHROMA_PATH']
    client = chromadb.PersistentClient(path=perisitent_chroma_path)
    return client


def get_chroma_collection(client):
    collection_name = os.environ['RUNBOT_CHROMA_COLLECTION']
    collection = client.get_or_create_collection(name=collection_name)
    return collection
