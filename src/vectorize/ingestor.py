import logging
from multiprocessing import Process, Queue
import util.db as db


class Ingestor(Process):
    def __init__(self, input_queue: Queue, collection_name) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.MAX_BUFFER_SIZE = 250
        self.buffer = []
        self.input_queue = input_queue
        self.collection_name = collection_name

    def process_chunk(self, chunk, collection):
        self.buffer.append(chunk)
        if len(self.buffer) > self.MAX_BUFFER_SIZE:
            self.flush_buffer(collection)

    def get_parameters(self):
        self.logger.debug("Collecting parameters for batch insert.")
        ids = [chunk['id'] for chunk in self.buffer]
        docs = [chunk['document'] for chunk in self.buffer]
        metas = [chunk['metadata'] for chunk in self.buffer]
        embeddings = [chunk['embedding'] for chunk in self.buffer]

        parameters = {
            'ids': ids,
            'docs': docs,
            'metas': metas,
            'embeddings': embeddings
        }
        return parameters

    def flush_buffer(self, collection):
        if len(self.buffer) > 0:
            parameters = self.get_parameters()
            self.batch_insert(collection, parameters)
            self.buffer = []

    def batch_insert(self, collection, parameters):
        self.logger.debug(
            f"Performing batch insert for {len(parameters['ids'])} chunks.")
        collection.upsert(
            ids=parameters['ids'],
            documents=parameters['docs'],
            metadatas=parameters['metas'],
            embeddings=parameters['embeddings']
        )

    def run(self):
        client = db.get_chroma_client()
        collection = db.get_chroma_collection(client, self.collection_name)
        run = True
        while run:
            while not self.input_queue.empty():
                chunks = self.input_queue.get()
                if chunks is None:
                    self.flush_buffer(collection)
                    run = False
                    break
                self.buffer.extend(chunks)
                if len(self.buffer) >= self.MAX_BUFFER_SIZE:
                    self.flush_buffer(collection)
