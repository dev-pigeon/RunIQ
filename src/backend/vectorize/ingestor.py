# get the chroma path and collection from env variables
class Ingestor:
    def __init__(self) -> None:
        # get env vars here?
        self.MAX_BUFFER_SIZE = 100
        self.buffer = []

    def get_chroma_client(self):
        # chroma path is env var
        pass

    def get_chroma_collection(self, client):
        # collection name is an env var
        pass

    def process_chunk(self, chunk, collection):
        pass

    def flush_buffer(self, collection):
        pass
