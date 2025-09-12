import json
import argparse


class Chunker:
    def __init__(self) -> None:
        self.MAX_CHUNK_SIZE = 250  # tokens
        self.CHUNK_OVERLAP = 75
        pass

    def chunk_file(self, data):
        # data is json file containing a parsed document
        chunks = []
        # chunk the paragraphs then chunk the tables should they exist
        paragraph_chunks = self.chunk_paragraphs(data)
        table_chunks = []
        if self.has_tables(data):
            table_chunks = self.chunk_tables(data)

        chunks += paragraph_chunks
        chunks += table_chunks
        return chunks

    def has_tables(self, data):
        return "tables" in data

    def make_chunk(self, text, chunk_count, source):
        metadata = {
            "source": source,
            "text": text,
            "chunk_id": f"{source}-{chunk_count}"
        }

        chunk = {
            "metadata": metadata,
            "embedding": [],
        }

        return chunk

    def chunk_paragraphs(self, data):
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

        if len(curr_chunk) > self.CHUNK_OVERLAP:
            # have some remaining tokens, make a chunk
            chunk = self.make_chunk(
                curr_chunk, len(para_chunks), source)

        return para_chunks

    def chunk_tables(self, data):
        # for now blindly chunk each flattened week
        table_chunks = []
        for table in data['tables']:
            source = table['source_file']
            for week in table['weeks']:
                chunk = self.make_chunk(week, len(table_chunks), source)
                table_chunks.append(chunk)
        return table_chunks


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
    print(chunks)
