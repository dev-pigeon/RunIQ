import argparse
import json
import logging
from vectorize.process_html import HTMLProcessor
from vectorize.chunker import Chunker
from vectorize.ingestor import Ingestor
from vectorize.vectorizer import Vectorizer


# set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename="vectorize/vectorization.log",
                    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def open_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


class Pipeline:
    def __init__(self) -> None:
        pass

    def run(self, config):
        logger.info("Beginning vectorization pipeline.")
        chunker = Chunker()
        ingestor = Ingestor()
        vectorizer = Vectorizer()

        for group in config:
            # process files
            logger.info(f"Sending files from {group['source']} for processing")
            processing_config = open_json(group['processing_config_path'])
            processor = HTMLProcessor(processing_config)
            processor.process_files()

            # chunk & embed processed files
            chunking_config = open_json(group['chunking_config_path'])
            for path in chunking_config['paths']:
                data = open_json(path)
                chunks = chunker.chunk_file(data)
                vectorizer.embed_and_insert(chunks, ingestor)

        logger.info("Finished with vectorization pipeline.")


if __name__ == "__main__":
    # get the path to the config file
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config-path', help="Path to the config file for the vectorization pipeline")
    args = parser.parse_args()
    config_path = args.config_path

    config = open_json(config_path)
    pipeline = Pipeline()
    pipeline.run(config)
