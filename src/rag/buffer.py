class Buffer:
    def __init__(self, max_turns=5) -> None:
        self.max_turns = max_turns
        self.history = []

    def add(self, query, response):
        entry = self.format_entry(query, response)
        if len(self.history) > self.max_turns:
            self.history.pop()
        self.history.append(entry)

    def format_entry(self, query, response):
        entry = f"[USER:]\n{query}\n[RESPONSE:]{response}"
        return entry

    def to_string(self):
        history_string = ""
        for entry in self.history:
            history_string += entry
        return history_string
