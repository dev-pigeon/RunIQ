import logging


class Ingestor:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.MAX_BUFFER_SIZE = 100
        self.buffer = []

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
        collection.add(
            ids=parameters['ids'],
            documents=parameters['docs'],
            metadatas=parameters['metas'],
            embeddings=parameters['embeddings']
        )
