import logging
import ollama  # type: ignore
from util.timer import Timer


class QueryRephraser:
    def __init__(self, prompt_template, model='mistral') -> None:
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.prompt_template = prompt_template
        self.timer = Timer()

    def rephrase_query(self, query, conversation_summary):
        self.timer.start()
        self.logger.info("Rephrasing query based on conversation summary")
        prompt = self.prompt_template.format(
            conversation_summary=conversation_summary, query=query)
        reprhased_query = ollama.generate(
            model=self.model, prompt=prompt)['response']
        self.timer.stop()
        self.logger.info(
            f"Finished rephrashing query in {self.timer.get_time():.3f} seconds.")
        self.timer.reset()
        return reprhased_query
