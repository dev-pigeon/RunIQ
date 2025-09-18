import json
import argparse
import logging


class Chunker:
    def __init__(self, chunk_size=250, chunk_overlap_percent=30) -> None:
        self.logger = logging.getLogger(__name__)
        self.MAX_CHUNK_SIZE = chunk_size  # tokens
        self.CHUNK_OVERLAP = int(chunk_size * (chunk_overlap_percent / 100))

    def chunk_file(self, data):
        # data is json file containing a parsed document
        if self.has_key(data, "source"):
            self.logger.info(f"Starting chunking {data['source']}")
            paragraph_chunks = self.chunk_paragraphs(data)
            table_chunks = self.chunk_tables(data)

            chunks = []
            chunks += paragraph_chunks
            chunks += table_chunks

            self.logger.debug(
                f"Created {len(chunks)} chunks from {data['source']}")
            self.logger.info(f"Finished chunking {data['source']}")
            return chunks
        else:
            self.logger.warning("Data has no source, skipping file.")
            return []

    def has_key(self, data, key):
        return key in data

    def make_chunk(self, text, chunk_count, source):
        chunk = {
            "id": f"{source}-{chunk_count}",
            "metadata": {"source": source},
            "embedding": [],
            "document": text,
        }

        return chunk

    def chunk_paragraphs(self, data):
        if self.has_key(data, "paragraphs"):
            self.logger.debug(
                f"Chunking paragraphs from source {data['source']}")
            para_chunks = []
            curr_chunk = ""
            source = data['source']
            for para in data['paragraphs']:
                curr_chunk += para

                if len(curr_chunk) >= self.MAX_CHUNK_SIZE:
                    chunk = self.make_chunk(
                        curr_chunk, len(para_chunks), source)
                    para_chunks.append(chunk)
                    curr_chunk = curr_chunk[-self.CHUNK_OVERLAP:]

            chunk = self.make_chunk(
                curr_chunk, len(para_chunks), source)
            para_chunks.append(chunk)

            return para_chunks
        else:
            self.logger.debug(f"{data['source']} has no paragraphs.")
            return []

    def chunk_tables(self, data):
        if self.has_key(data, "tables"):
            self.logger.debug(f"Chunking tables from source {data['source']}")
            table_chunks = []
            for table in data['tables']:
                source = table['source_file']
                for week in table['weeks']:
                    chunk = self.make_chunk(week, len(table_chunks), source)
                    table_chunks.append(chunk)

            return table_chunks
        else:
            self.logger.debug(f"{data['source']} has no tables.")
            return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--data", help="Path to the json file containing the data to chunk.", required=True)
    args = parser.parse_args()
    data_path = args.data
    with open(data_path, 'r') as file:
        data = json.load(file)

    chunker = Chunker()
    chunks = chunker.chunk_file(data)
