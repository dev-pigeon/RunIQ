import logging
import ollama  # type: ignore


class QueryRephraser:
    def __init__(self, prompt_template, model='mistral') -> None:
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.prompt_template = prompt_template

    def rephrase_query(self, query, conversation_summary):
        self.logger.info("Rephrasing query based on conversation summary")
        prompt = self.prompt_template.format(
            conversation_summary=conversation_summary, query=query)
        reprhased_query = ollama.generate(
            model=self.model, prompt=prompt)['response']
        return reprhased_query
