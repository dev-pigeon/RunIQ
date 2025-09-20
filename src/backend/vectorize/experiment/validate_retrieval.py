import json
import logging
from rag.retriever import Retriever
from sentence_transformers import SentenceTransformer  # type: ignore


def open_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def get_collection_names(config):
    collection_names = []
    for model in config['models']:
        for strategy in config['chunk_strategies']:
            for chunk_size in config['chunk_sizes']:
                # if its not hybrid do the overlaps, else just call it with the sizes and move on
                if strategy != "hybrid":
                    for overlap in config['chunk_overlaps']:
                        collection_name = f"MODEL{model}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAP{overlap}"
                        collection_names.append(collection_name)
                else:
                    collection_name = f"MODEL{model}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAPnone"
                    collection_names.append(collection_name)
    return collection_names


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="vectorize/experiment/experiment.log",
                        level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    config_path = "./dev/config/experiment/config.json"
    config = open_json(config_path)

    collection_names = get_collection_names(config)
