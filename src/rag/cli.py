import os
import json
import argparse
from rag.retriever import Retriever
from rag.generator import Generator
from rag.conversation_buffer import ConversationBuffer
from rag.query_rephraser import QueryRephraser
from sentence_transformers import SentenceTransformer  # type: ignore
import logging


# set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename="rag/rag.log",
                    format="%(asctime)s [%(levelname)s] %(name)s %(message)s", level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def is_quit(query):
    return query.strip() == "quit"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-tp', '--template-path',
                        help="Path to prompt templates", required=True)
    logger.info("Initializing resources.")
    prompt_config_path = parser.parse_args().template_path
    with open(prompt_config_path, 'r') as file:
        prompt_templates = json.load(file)

    embedding_model_name = "BAAI/bge-base-en-v1.5"
    logger.debug(f"Loading embedding model {embedding_model_name}")
    embedding_model = SentenceTransformer(embedding_model_name)

    retriever = Retriever()
    generator = Generator()
    rephraser = QueryRephraser(
        prompt_template=prompt_templates['rephrasing_prompt'])
    conversation_buffer = ConversationBuffer(
        summerization_prompt_template=prompt_templates['summarization_prompt'])

    logger.info("Beginning query sequence.")

    try:
        while True:
            query_text = input("Enter a query: ")
            if is_quit(query_text):
                logger.info("Ending query sequence")
                print("Exiting...")
                break
            rephrased_query = rephraser.rephrase_query(
                query_text, conversation_buffer.get_context())
            print(rephrased_query)
            context = retriever.retrieve(
                rephrased_query, input_model=embedding_model)
            response = generator.generate(
                rephrased_query, context, prompt_templates['generation_prompt'])
            print(response)
            print(
                "********************************************************************************")
            conversation_buffer.add_turn(rephrased_query, response)
    except ConnectionError as e:
        logger.error(e)
