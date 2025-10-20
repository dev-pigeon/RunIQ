import logging
import ollama  # type:ignore
from util.timer import Timer


class ConversationBuffer:
    def __init__(self, summerization_prompt_template, max_turns=1) -> None:
        self.max_turns = max_turns
        self.history = []
        self.summary = ""
        self.model = "mistral"
        self.logger = logging.getLogger(__name__)
        self.prompt_template = summerization_prompt_template
        self.timer = Timer()

    def add_turn(self, query, response):
        entry = self.format_entry(query, response)
        self.history.append(entry)
        if len(self.history) > self.max_turns:
            self.logger.info("Evicting oldest turn")
            self.history.pop(0)
        self.summarize()

    def get_context(self):
        return self.summary

    def format_entry(self, query, response):
        entry = f"user:\n{query}\nresponse:{response}"
        return entry

    def summarize(self):
        context_to_summarize = self.summary + "\n" + "\n".join(self.history)
        self.logger.info(
            f"Calling summarizer with current context of {len(self.history)} turns")
        self.timer.start()
        prompt = self.prompt_template.format(
            context_to_summarize=context_to_summarize)
        new_summary = ollama.generate(model=self.model, prompt=prompt)
        self.timer.stop()
        self.summary = new_summary['response']
        self.logger.info(
            f"Finished summarizing conversation in {self.timer.get_time():.3f} seconds.")

    def to_string(self):
        history_string = ""
        for entry in self.history:
            history_string += entry
        return history_string
