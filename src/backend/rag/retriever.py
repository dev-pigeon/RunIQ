# takes raw query, embeds it, uses the chroma db collection to get relevant chunks
# returns relevant chunks
import argparse
from sentence_transformers import SentenceTransformer  # type: ignore
from vectorize.vectorizer import Vectorizer
import os
import util.db as db
import logging


class Retriever:
    def __init__(self, collection_name="", model_type="all-MiniLM-L6-v2") -> None:
        self.logger = logging.getLogger(__name__)
        self.vectorizer = Vectorizer()
        self.model_type = model_type
        self.collection_name = os.environ['RUNBOT_CHROMA_COLLECTION'] if collection_name == "" else collection_name

    def retrieve_chunks(self, query_text, input_model=None):
        self.logger.info("Retrieving context based on user query.")
        client = db.get_chroma_client()
        collection = db.get_chroma_collection(client, self.collection_name)
        model = input_model if input_model is not None else SentenceTransformer(
            self.model_type)
        query_embedding = self.vectorizer.embed_text(query_text, model)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=['documents', 'metadatas', 'embeddings']
        )
        return results

    def retrieve(self, query_text, input_model=None):
        results = self.retrieve_chunks(query_text, input_model)
        # log the results
        result_ids = self.get_result_chunk_ids(results)
        self.logger.debug(f"Retrieved chunks {result_ids}")

        result_text = self.get_result_text(results)
        return result_text

    def get_result_chunk_ids(self, results):
        return [result_id for result_id in results['ids']]

    def get_result_text(self, results):
        text = ""
        documents = results['documents']
        for doc in documents:
            text = "\n".join(doc)

        return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q", "--query", required=True)
    args = parser.parse_args()
    query = args.query
    retriever = Retriever()
    retriever.retrieve(query)
