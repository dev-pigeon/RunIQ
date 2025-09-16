import ollama  # type: ignore


class Generator:
    def __init__(self) -> None:
        self.MODEL = "mistral"
        pass

    def generate(self, query_text, context, config_prompt):
        prompt = config_prompt.format(query_text, context)
        response = ollama.generate(model=self.MODEL, prompt=prompt)
        response_text = self.get_response_text(response)
        return response_text

    def get_response_text(self, response):
        text = ""
        for chunk in response:
            text += chunk['response']
        return text
