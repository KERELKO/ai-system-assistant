from dataclasses import asdict
import json

import pydgraph  # type: ignore[import-untyped]
from loguru import logger

from system_assistant.application.gateways.chat import ChatGateway  # noqa
from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import ID, Message


_GET_CHAT_DATA_QUERY = """
query chat($id: string){
    chat(func: eq(id, $id)) {
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
        self.client = pydgraph.open(dgraph_url)

    async def get_by_id(self, id: ID) -> Chat | None:
        variables = {'$id': id}
        txn = self.client.txn(read_only=True)
        res = txn.query(query=_GET_CHAT_DATA_QUERY, variables=variables)
        chat_json = json.loads(res.json)
        if not chat_json['chat']:
            return None
        return Chat(**chat_json['chat'][0])

    async def save(self, chat: Chat) -> ID:
        txn = self.client.txn()
        try:
            response = txn.mutate(set_obj=asdict(chat), commit_now=True)
            logger.debug(response)
        except Exception as e:
            logger.error(str(e))
            txn.discard()
        return chat.id

    async def append_message(self, chat_id: ID, message: Message):
        raise NotImplementedError
