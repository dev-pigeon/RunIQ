import json
import argparse
import logging
import re


class Chunker:
    def __init__(self, chunk_size=256, chunk_overlap_percent=.20, chunking_strategy="naive") -> None:
        self.logger = logging.getLogger(__name__)
        self.MAX_CHUNK_SIZE = chunk_size  # tokens
        self.CHUNK_OVERLAP = int(chunk_size * chunk_overlap_percent)
        self.strategy = chunking_strategy
        self.ABBREVIATIONS = {"Mr.", "Mrs.", "Dr.",
                              "Prof.", "Sr.", "Jr.", "e.g.", "i.e."}

    def chunk_file(self, data):
        # data is json file containing a parsed document
        if self.has_key(data, "source"):
            self.logger.info(
                f"Starting chunking {data['source']} with STRATEGY: {self.strategy} SIZE: {self.MAX_CHUNK_SIZE} OVERLAP: {self.CHUNK_OVERLAP}")
            paragraph_chunks = self.chunk_paragraphs(data)
            table_chunks = self.chunk_tables(data)

            chunks = []
            chunks += paragraph_chunks
            chunks += table_chunks

            self.logger.debug(
                f"Created {len(chunks)} chunks from {data['source']}")
            self.logger.info(
                f"Finished chunking {data['source']} with STRATEGY: {self.strategy} SIZE: {self.MAX_CHUNK_SIZE} OVERLAP: {self.CHUNK_OVERLAP}")
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

    def tokenize(self, text):
        return text.split()

    def get_sentences(self, paragraph):
        sentences = []
        left, right = 0, 0
        while right < len(paragraph):
            if self.is_sentence_boundary(right, paragraph):
                sentence = paragraph[left: right + 1].strip()
                sentences.append(sentence)
                left = right + 1

            right += 1
        return sentences

    def is_sentence_boundary(self, index, paragraph):
        if paragraph[index] in ".!?":
            start = paragraph.rfind(" ", 0, index) + 1
            prev_word = paragraph[start:index+1]
            if prev_word in self.ABBREVIATIONS:
                return False
            else:
                return True
        return False

    def emit_chunks(self, chunks, curr_chunk, source):
        chunk_text = " ".join(curr_chunk)
        chunk = self.make_chunk(
            chunk_text, len(chunks), source)
        chunks.append(chunk)

    def chunk_strategy_naive(self, data):
        # builds each chunk at the token level
        # overlap is token wise
        chunks = []
        curr_chunk = []
        source = data['source']
        for para in data['paragraphs']:
            tokens = self.tokenize(para)
            for token in tokens:
                if len(curr_chunk) < self.MAX_CHUNK_SIZE:
                    curr_chunk.append(token)
                else:
                    self.emit_chunks(chunks, curr_chunk, source)
                    curr_chunk = curr_chunk[-self.CHUNK_OVERLAP:]

        self.emit_chunks(chunks, curr_chunk, source)
        return chunks

    def chunk_strategy_paragraph(self, data):
        # builds each chunk at the paragraph level
        # overlap is token wise
        chunks = []
        curr_chunk = []
        source = data['source']
        for para in data['paragraphs']:
            tokens = self.tokenize(para)
            # decide on token
            if len(curr_chunk) + len(tokens) > self.MAX_CHUNK_SIZE:
                self.emit_chunks(chunks, curr_chunk, source)
                curr_chunk = curr_chunk[-self.CHUNK_OVERLAP:]
            else:
                curr_chunk.extend(tokens)
        self.emit_chunks(chunks, curr_chunk, source)
        return chunks

    def chunk_strategy_hybrid(self, data):
        # builds a sentence level
        # overlap is prev sentence, not token wise
        chunks = []
        curr_chunk = []
        source = data['source']
        for para in data['paragraphs']:
            sentences = self.get_sentences(para)
            for sentence in sentences:
                sentence_tokens = self.tokenize(sentence)
                if len(curr_chunk) + len(sentence_tokens) > self.MAX_CHUNK_SIZE:
                    self.emit_chunks(chunks, curr_chunk, source)
                    curr_chunk = sentence_tokens.copy()
                else:
                    curr_chunk.extend(sentence_tokens)
        self.emit_chunks(chunks, curr_chunk, source)
        return chunks

    def chunk_paragraphs(self, data):
        if self.has_key(data, "paragraphs"):
            self.logger.debug(
                f"Chunking paragraphs from source: {data['source']}")
            chunks = []
            match self.strategy:
                case "naive":
                    chunks = self.chunk_strategy_naive(data)
                case "paragraph":
                    chunks = self.chunk_strategy_paragraph(data)
                case "hybrid":
                    chunks = self.chunk_strategy_hybrid(data)

            return chunks
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

    chunker = Chunker(chunking_strategy="hybrid")
    chunks = chunker.chunk_file(data)
