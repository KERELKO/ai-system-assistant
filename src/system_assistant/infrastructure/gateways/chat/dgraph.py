import httpx

from system_assistant.application.gateways.chat import ChatGateway  # noqa
from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import ID, Message


_GET_CHAT_DATA_QUERY = """
query {
    getChat(id: "1") {
        id,
        title,
        messages {
            sender,
            content
        }
    }
}
"""


class DgraphChatGateway:
    def __init__(self, dgraph_url: str):
        self.dgraph_url = dgraph_url
        self.client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self.client is None or self.client.is_closed:
            self.client = httpx.AsyncClient()
        return self.client

    async def get_by_id(self, id: ID) -> Chat | None:
        client = self._get_client()
        response = await client.post(
            url=self.dgraph_url,
            json={'query': _GET_CHAT_DATA_QUERY, 'variables': {'chatId': id}},
            headers={'Content-Type': 'application/json'},
        )
        print(response.json())
        return None

    async def save(self, chat: Chat) -> ID:
        raise NotImplementedError

    async def append_message(self, chat_id: ID, message: Message):
        raise NotImplementedError
