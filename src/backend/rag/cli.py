import os
import json
from rag.retriever import Retriever
from rag.generator import Generator
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
    logger.info("Initializing resources.")
    prompt_config_path = os.environ['RUNBOT_PROMPT_PATH']
    with open(prompt_config_path, 'r') as file:
        config_prompt = json.load(file)['prompt']

    embedding_model_name = "BAAI/bge-base-en-v1.5"
    logger.debug(f"Loading embedding model {embedding_model_name}")
    embedding_model = SentenceTransformer(embedding_model_name)

    retriever = Retriever()
    generator = Generator()

    logger.info("Beginning query sequence.")

    try:
        while True:
            query_text = input("Enter a query: ")
            if is_quit(query_text):
                logger.info("Ending query sequence")
                print("Exiting...")
                break
            context = retriever.retrieve(
                query_text, input_model=embedding_model)
            response = generator.generate(query_text, context, config_prompt)
            print(response)
            print(
                "********************************************************************************")
    except ConnectionError as e:
        logger.error(e)
