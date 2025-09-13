import argparse
import json
from process_html import HTMLProcessor
from chunker import Chunker
from ingestor import Ingestor
from vectorizer import Vectorizer


def open_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


class Pipeline:
    def __init__(self) -> None:
        pass

    def run(self, config):
        # config = json with N processing groups / is a list of objects
        chunker = Chunker()
        ingestor = Ingestor()
        vectorizer = Vectorizer(ingestor)

        for group in config:
            # process files
            print(f"Processing files for {group['source']}")
            processing_config = open_json(group['processing_config_path'])
            processor = HTMLProcessor(processing_config)
            processor.process_files()

            # chunk & embed processed files
            chunking_config = open_json(group['chunking_config_path'])
            for path in chunking_config['paths']:
                data = open_json(path)
                print(f"Chunking file at {path}")
                chunks = chunker.chunk_file(data)
                print(f"Embedding chunks for {path}")
                vectorizer.embed_and_insert(chunks)

        pass


if __name__ == "__main__":
    # get the path to the config file
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config-path', help="Path to the config file for the vectorization pipeline")
    args = parser.parse_args()
    config_path = args.config_path

    config = open_json(config_path)
    print("Beginning vectorization pipeline.")
    pipeline = Pipeline()
    pipeline.run(config)
