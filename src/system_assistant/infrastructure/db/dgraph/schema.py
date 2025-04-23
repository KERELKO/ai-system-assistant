import pydgraph  # type: ignore[import-untyped]

CHAT_SCHEMA = """
id: string @index(exact) .
title: string .
content: string .
sender: string .
message: [uid] @reverse .

type Message {
    sender
    content
}

type Chat {
    id
    title
    message
}
"""


def set_schema(client: pydgraph.DgraphClient):
    client.alter(pydgraph.Operation(schema=CHAT_SCHEMA))
