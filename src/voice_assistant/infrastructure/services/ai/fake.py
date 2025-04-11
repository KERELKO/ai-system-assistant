from voice_assistant.application.services.ai.base import AIAgent


class FakeAIAgent(AIAgent):
    async def make_request(self, text: str) -> str:
        return "I'm very intelligent AI of model RGT-34"
