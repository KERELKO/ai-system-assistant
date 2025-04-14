from system_assistant.domain.vo import ID, AssistantModel, generate_id


class Assistant:
    def __init__(self, model: AssistantModel):
        self.id: ID = generate_id()
        self.model = model
