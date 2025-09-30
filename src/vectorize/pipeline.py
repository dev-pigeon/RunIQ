import argparse
import json
import logging
from vectorize.process_html import HTMLProcessor
from vectorize.chunker import Chunker
from vectorize.ingestor import Ingestor
from vectorize.vectorizer import Vectorizer
from util.timer import Timer
from sentence_transformers import SentenceTransformer  # type: ignore
import os


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
        chunker_config = config['worker_parameters']['chunker']
        chunker = Chunker(chunk_size=chunker_config['chunk_size'],
                          chunk_overlap_percent=chunker_config['overlap_percent'], chunking_strategy=chunker_config['strategy'])
        ingestor = Ingestor()
        vectorizer = Vectorizer()
        timer = Timer()
        model_name = config['model']
        logger.debug(f"Loading model {model_name}")
        model = SentenceTransformer(config['model'])

        timer.start()
        for group in config['processing_groups']:
            # process files
            logger.info(f"Sending files from {group['source']} for processing")
            processing_config = group['processing_config']
            processor = HTMLProcessor(processing_config)
            processor.process_files()

            # chunk & embed processed files
            chunking_config = group['chunking_config']
            # should be directory based now
            dir_path = chunking_config['input_directory']
            for filename in os.listdir(dir_path):
                path = os.path.join(dir_path, filename)
                data = open_json(path)
                chunks = chunker.chunk_file(data)
                vectorizer.embed_and_insert(chunks, ingestor, model)

        timer.stop()
        elapsed_time = timer.get_time()
        logger.info(
            f"Finished with vectorization pipeline in {elapsed_time:.3f} seconds")


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
