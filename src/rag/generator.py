import ollama  # type: ignore
import logging


class Generator:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.MODEL = "mistral"
        pass

    def generate(self, query_text, context, config_prompt):
        try:
            self.logger.info("Generating response from user input and context")
            prompt = config_prompt.format(
                query_text=query_text, context=context)
            response = ollama.generate(model=self.MODEL, prompt=prompt)

            return response['response']
        except ConnectionError as e:
            raise ConnectionError(e)

    def get_response_text(self, response):
        text = ""
        for chunk in response:
            text += chunk['response']
        return text + "\n\n"
