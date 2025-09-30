from multiprocessing import Queue, Process
from vectorize.chunker import Chunker
from vectorize.process_html import HTMLProcessor
from vectorize.vectorizer import Vectorizer
from sentence_transformers import SentenceTransformer  # type:ignore
import logging


class Worker(Process):
    def __init__(self, config, workload, output_queue: Queue, id: str):
        super().__init__()
        self.config = config
        self.workload = workload
        self.output_queue = output_queue
        self.id = id,
        self.logger = logging.getLogger(name=id)

    def process_workload(self, chunker: Chunker, vectorizer: Vectorizer, model):
        self.logger.info("Beginning workload")
        for task in self.workload['tasks']:
            self.process_task(task, chunker, vectorizer, model)
        self.logger.info("Finished with workload")

    def process_task(self, task, chunker: Chunker, vectorizer: Vectorizer, model):
        # process html file
        group_config_id = task['group_config_id']
        processing_config = self.workload['group_configs'][group_config_id]['processing_config']
        processor = HTMLProcessor(processing_config)
        intermediary_data = processor.process_html_file(
            task['processing_path'])

        # embed & forward data
        chunks_no_embeddings = chunker.chunk_file(intermediary_data)
        chunks_with_embeddings = vectorizer.embed_chunks(
            chunks_no_embeddings, model)
        self.output_queue.put(chunks_with_embeddings)

    def run(self):
        # initialize resources
        chunker_config = self.config['chunker']
        chunker = Chunker(
            chunker_config['chunk_size'], chunker_config['overlap_percent'], chunker_config['strategy'])
        vectorizer = Vectorizer()
        model = SentenceTransformer(self.config['model'])

        # complete tasks
        self.process_workload(chunker, vectorizer, model)
