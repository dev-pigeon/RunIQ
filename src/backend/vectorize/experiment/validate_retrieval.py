import json
import logging
from rag.retriever import Retriever
from vectorize.vectorizer import Vectorizer
from sentence_transformers import SentenceTransformer  # type: ignore
import numpy


def open_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def run_queries(collection_name, model, queries):
    retriever = Retriever(collection_name=collection_name)
    vectorizer = Vectorizer(collection_name=collection_name)
    logger.debug(f"Running queries for {collection_name}")
    for query in queries['queries']:
        results = retriever.retrieve_chunks(query['text'], model)
        result_embeddings = results['embeddings'][0].tolist()
        query_response_embedding = vectorizer.embed_text(
            query['relevant_response'], model)
        # get the precision at k for that
        # add it to the mean


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="vectorize/experiment/experiment.log",
                        level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    config_path = "./dev/config/experiment/config.json"
    config = open_json(config_path)

    queries_path = "./dev/data/experiment/queries.json"
    queries = open_json(queries_path)

    for model_name in config['models']:
        model = SentenceTransformer(model_name)
        for strategy in config['chunk_strategies']:
            for chunk_size in config['chunk_sizes']:
                # if its not hybrid do the overlaps, else just call it with the sizes and move on
                if strategy != "hybrid":
                    for overlap in config['chunk_overlaps']:
                        collection_name = f"MODEL{model_name}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAP{overlap}"
                        # run_queries(collection_name, model, queries)
                else:
                    collection_name = f"MODEL{model_name}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAPnone"
                    run_queries(collection_name, model, queries)
