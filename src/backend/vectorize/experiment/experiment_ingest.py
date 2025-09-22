from vectorize.chunker import Chunker
from vectorize.vectorizer import Vectorizer
from vectorize.ingestor import Ingestor
from vectorize.experiment.util import clean_model_name
from sentence_transformers import SentenceTransformer  # type: ignore
import json
import logging


def open_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def run_experiment_ingest_pipeline(model):
    logger.info(
        f"Beginning test experiment ingestion sequence for {output_collection}")
    for path in chunker_paths:
        data = open_json(path)
        chunks = chunker.chunk_file(data)
        vectorizer.embed_and_insert(chunks, ingestor, input_model=model)
    logger.info(f"finished chunking and ingesting for {output_collection}")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="vectorize/experiment/experiment.log",
                        level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    config_path = "./dev/config/experiment/config.json"
    config = open_json(config_path)

    chunker_config = open_json(config['chunker_config_path'])
    chunker_paths = chunker_config['paths']

    ingestor = Ingestor()

    # everyhing below is in the loop
    for model in config['models']:
        model_name = clean_model_name()
        input_model = SentenceTransformer(model_name)
        for strategy in config['chunk_strategies']:
            for chunk_size in config['chunk_sizes']:
                # if its not hybrid do the overlaps, else just call it with the sizes and move on
                if strategy != "hybrid":
                    for overlap in config['chunk_overlaps']:
                        output_collection = f"MODEL{model_name}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAP{overlap}"
                        chunker = Chunker(
                            chunk_size=chunk_size, chunk_overlap_percent=overlap, chunking_strategy=strategy)
                        vectorizer = Vectorizer(
                            collection_name=output_collection)
                        run_experiment_ingest_pipeline(input_model)

                else:
                    output_collection = f"MODEL{model_name}-TYPE{strategy}-CHUNKS{chunk_size}-OVERLAPnone"
                    chunker = Chunker(
                        chunk_size=chunk_size, chunking_strategy=strategy)
                    vectorizer = Vectorizer(collection_name=output_collection)
                    run_experiment_ingest_pipeline(input_model)
