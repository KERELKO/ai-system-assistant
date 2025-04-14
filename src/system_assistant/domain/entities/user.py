from system_assistant.domain.vo import ID, generate_id


class User:
    def __init__(self):
        self.id: ID = generate_id()
