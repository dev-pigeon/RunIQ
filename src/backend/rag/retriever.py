# takes raw query, embeds it, uses the chroma db collection to get relevant chunks
# returns relevant chunks
import os
import argparse
import chromadb  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
from vectorize.vectorizer import Vectorizer
import util.db as db


class Retriever:
    def __init__(self) -> None:
        self.vectorizer = Vectorizer()
        pass

    def retrieve(self, query_text):
        client = db.get_chroma_client()
        collection = db.get_chroma_collection(client)
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_embedding = self.vectorizer.embed_text(query_text, model)
        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
        )

        return result['documents']


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q", "--query", required=True)
    args = parser.parse_args()
    query = args.query
    retriever = Retriever()
    print(retriever.retrieve(query))
