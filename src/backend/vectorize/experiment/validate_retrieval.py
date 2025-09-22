import json
import logging
from rag.retriever import Retriever
from vectorize.vectorizer import Vectorizer
from vectorize.experiment.util import clean_model_name
from sentence_transformers import SentenceTransformer  # type: ignore
import numpy


def open_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def run_queries(collection_name, model, queries):
    running_sum = 0
    retriever = Retriever(collection_name=collection_name)
    vectorizer = Vectorizer(collection_name=collection_name)
    logger.debug(f"Calculating p@k for {collection_name}")
    for query in queries['queries']:
        results = retriever.retrieve_chunks(query['text'], model)
        precision_at_k = calculate_precision_at_k(
            results, query, vectorizer)
        running_sum += precision_at_k
    mean_precision_at_k = running_sum / len(queries['queries'])
    return mean_precision_at_k


def calculate_precision_at_k(results, query, vectorizer):
    result_embeddings = results['embeddings'][0]
    result_texts = results['documents'][0]

    query_response_embedding = numpy.array(vectorizer.embed_text(
        query['relevant_response'], model))
    query_response_text = query['relevant_response']

    num_relevant_chunks = 0
    k = len(result_embeddings)

    for i in range(0, k):
        result_embedding = result_embeddings[i]
        result_text = result_texts[i]
        cosine_similarity = calculate_cosine_similarity(
            result_embedding, query_response_embedding)
        if cosine_similarity > 0.75 or query_response_text in result_text:
            num_relevant_chunks += 1

    precision_at_k = num_relevant_chunks / k
    return precision_at_k


def calculate_cosine_similarity(result_embedding, query_response_embedding):
    dot_product = numpy.dot(result_embedding, query_response_embedding)

    result_embedding_norm = numpy.linalg.norm(result_embedding)
    response_embedding_norm = numpy.linalg.norm(query_response_embedding)
    if response_embedding_norm == 0 or result_embedding_norm == 0:
        return -1
    cosine_similarity = dot_product / \
        (result_embedding_norm * response_embedding_norm)
    return cosine_similarity


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="vectorize/experiment/scheme_validation.log",
                        level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    config_path = "./dev/config/experiment/config.json"
    config = open_json(config_path)

    queries_path = "./dev/data/experiment/queries.json"
    queries = open_json(queries_path)

    output = []  # list of json objects

    for model in config['models']:
        input_model = SentenceTransformer(model)
        model_name = clean_model_name(model)
        for strategy in config['chunk_strategies']:
            for chunk_size in config['chunk_sizes']:
                # if its not hybrid do the overlaps, else just call it with the sizes and move on
                if strategy != "hybrid":
                    for overlap in config['chunk_overlaps']:
                        collection_name = f"MODEL{model_name}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAP{overlap}"
                        mean_precision_at_k = run_queries(
                            collection_name, input_model, queries)
                        output.append({"chunk_scheme": collection_name,
                                       "mean_p@k": mean_precision_at_k})
                else:
                    collection_name = f"MODEL{model_name}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAPnone"
                    mean_precision_at_k = run_queries(
                        collection_name, input_model, queries)
                    output.append({"chunk_scheme": collection_name,
                                  "mean_p@k": mean_precision_at_k})
    # write output
    write_json("./dev/data/experiment/output.json", output)
