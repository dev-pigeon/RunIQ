import argparse
import json
import logging
from vectorize.worker import Worker
from multiprocessing import Queue
from util.timer import Timer
from vectorize.ingestor import Ingestor
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

    def start_workers(self, config, ingesting_queue: Queue):
        workload = self.initialize_workload(config['processing_groups'])
        process_workloads = self.divide_workload(workload)
        workers = []
        for i, process_workload in enumerate(process_workloads):
            worker = Worker(
                config['worker_config'], process_workload, ingesting_queue, f"Worker-{i}")
            workers.append(worker)
            worker.start()

        return workers

    def initialize_workload(self, processing_groups):
        workload = {
            "group_configs": {},
            "tasks": []
        }

        for group in processing_groups:
            group_tasks = self.create_tasks(group)
            workload['tasks'].extend(group_tasks)
            group_config_id = group['source']
            workload['group_configs'][group_config_id] = group

        return workload

    def divide_workload(self, workload, num_processes=4):
        # initialize each process workload object
        process_workloads = []
        for _ in range(num_processes):
            process_workload = {
                "group_configs": workload['group_configs'],
                "tasks": []
            }
            process_workloads.append(process_workload)

        # assign tasks to workers in round robin fashion
        workload_pointer = 0
        for task in workload['tasks']:
            process_workloads[workload_pointer]['tasks'].append(task)
            workload_pointer = (workload_pointer + 1) % num_processes

        return process_workloads

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
        ingesting_queue = Queue()
        # start them workers
        logger.debug("Starting workers")
        ingestor = Ingestor(ingesting_queue, config['chroma_collection_name'])
        ingestor.start()
        workers = self.start_workers(config, ingesting_queue)

        for w in workers:
            w.join()

        ingestor.input_queue.put(None)
        ingestor.join()

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
