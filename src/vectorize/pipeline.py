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

    def initialize_workload(self, processing_groups):
        workload = {
            "group_configs": [],
            "tasks": []
        }

        for group in processing_groups:
            group_tasks = self.create_tasks(group)
            workload['tasks'].extend(group_tasks)
            workload['group_configs'].append(group)

        return workload

    def create_tasks(self, group):
        tasks = []
        group_directory = group['input_directory']
        for filename in os.listdir(group_directory):
            path = os.path.join(group_directory, filename)
            task = {
                "processing_path": path,
                "group_config_id": group['source']
            }
            tasks.append(task)
        return tasks

    def run(self, config):
        logger.info("Beginning vectorization pipeline.")
        timer = Timer()
        timer.start()
        workload = self.initialize_workload(config['processing_groups'])

        # timer.stop()
        # elapsed_time = timer.get_time()
        # logger.info(
        #     f"Finished with vectorization pipeline in {elapsed_time:.3f} seconds")


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
