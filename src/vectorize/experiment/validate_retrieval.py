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


def run_queries(collection_name, input_model, queries, k):
    running_p_at_k, running_map = 0, 0
    retriever = Retriever(collection_name=collection_name, k=k)
    vectorizer = Vectorizer(collection_name=collection_name)
    logger.debug(f"Calculating p@{k} for {collection_name}")
    for query in queries['queries']:
        results = retriever.retrieve_chunks(query['text'], input_model)
        precision_at_k, average_precision = calculate_precision_values(
            results, query, vectorizer, input_model)

        running_p_at_k += precision_at_k
        running_map += average_precision

    num_queries = len(queries['queries'])
    mean_precision_at_k = running_p_at_k / num_queries
    mean_average_precision = running_map / num_queries
    return mean_precision_at_k, mean_average_precision


def calculate_precision_values(results, query, vectorizer, input_model):
    result_embeddings = results['embeddings'][0]
    result_texts = results['documents'][0]

    query_response_embedding = numpy.array(vectorizer.embed_text(
        query['relevant_response'], input_model))
    query_response_text = query['relevant_response']

    num_relevant_chunks = 0
    precision_values = []
    k = len(result_embeddings)

    for i in range(0, k):
        result_embedding = result_embeddings[i]
        result_text = result_texts[i]
        cosine_similarity = calculate_cosine_similarity(
            result_embedding, query_response_embedding)
        if cosine_similarity > 0.75 or query_response_text in result_text:
            num_relevant_chunks += 1
            average_precision = num_relevant_chunks / \
                (i + 1)  # avoids divide by 0
            precision_values.append(average_precision)

    precision_at_k = num_relevant_chunks / k
    average_precision = calculate_average_precision(
        precision_values)
    return precision_at_k, average_precision


def calculate_average_precision(precision_values):
    map = 0
    if len(precision_values) > 0:
        for value in precision_values:
            map += value
        map /= len(precision_values)
    return map


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

    output = []

    for k_value in config['k_values']:
        for model_name in config['models']:
            input_model = SentenceTransformer(model_name)
            model_name = clean_model_name(model_name)
            for strategy in config['chunk_strategies']:
                for chunk_size in config['chunk_sizes']:
                    # if its not hybrid do the overlaps, else just call it with the sizes and move on
                    if strategy != "hybrid":
                        for overlap in config['chunk_overlaps']:
                            collection_name = f"MODEL{model_name}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAP{overlap}"
                            mean_precision_at_k, mean_average_precision = run_queries(
                                collection_name, input_model, queries, k_value)

                            record = {"chunk_scheme": collection_name, "MAP": mean_average_precision,
                                      "mean_p@k": mean_precision_at_k, "k": k_value}
                            output.append(record)

                    else:
                        collection_name = f"MODEL{model_name}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAPnone"
                        mean_precision_at_k, mean_average_precision = run_queries(
                            collection_name, input_model, queries, k_value)

                        record = {"chunk_scheme": collection_name, "MAP": mean_average_precision,
                                  "mean_p@k": mean_precision_at_k, "k": k_value}
                        output.append(record)

    # write output
    write_json("./dev/data/experiment/output.json", output)
