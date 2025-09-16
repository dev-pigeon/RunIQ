import os
import json
from rag.retriever import Retriever
from rag.generator import Generator


def is_quit(query):
    return query.strip() == "quit"


if __name__ == "__main__":
    prompt_config_path = os.environ['RUNBOT_PROMPT_PATH']
    with open(prompt_config_path, 'r') as file:
        config_prompt = json.load(file)['prompt']

    retriever = Retriever()
    generator = Generator()

    while True:
        query_text = input("Enter a query: ")
        if is_quit(query_text):
            print("Exiting...")
            break
        context = retriever.retrieve(query_text)
        response = generator.generate(query_text, context, config_prompt)
        print(response)
