import ollama  # type: ignore
import logging
from util.timer import Timer


class Generator:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.MODEL = "mistral"
        self.timer = Timer()
        pass

    def generate(self, query_text, context, config_prompt):
        try:
            self.logger.info("Generating response from user input and context")
            self.timer.start()
            prompt = config_prompt.format(
                query_text=query_text, context=context)
            response = ollama.generate(model=self.MODEL, prompt=prompt)
            self.timer.stop()
            self.logger.info(
                f"Finished generating response in {self.timer.get_time():3f} seconds.")
            return response['response']
        except ConnectionError as e:
            raise ConnectionError(e)

    def get_response_text(self, response):
        text = ""
        for chunk in response:
            text += chunk['response']
        return text + "\n\n"
