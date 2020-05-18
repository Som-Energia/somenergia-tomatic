#!/usr/bin/env python3
import asyncio

from hangups import (
    ChatMessageSegment,
)
import hangups
from hangups.hangouts_pb2 import (
    SendChatMessageRequest,
    EventRequestHeader,
    ConversationId,
    MessageContent,
)
import sys
import appdirs
import os
from yamlns import namespace as ns
from consolemsg import success, step

config = ns.load('config.yaml')

message = ' '.join(sys.argv[1:])
if not message:
    message = sys.stdin.read()
dirs = appdirs.AppDirs('hangups', 'hangups')
token_path = os.path.join(dirs.user_cache_dir, 'refresh_token.txt')
step(message)


async def send_message(client):
    request = SendChatMessageRequest(
        request_header = client.get_request_header(),
        event_request_header = EventRequestHeader(
            conversation_id = ConversationId(
                id = config.hangoutChannel,
            ),
            client_generated_id=client.get_client_generated_id(),
        ),
        message_content = MessageContent(
            segment=[hangups.ChatMessageSegment(message).serialize()],
        ),
    )
    await client.send_chat_message(request)
    await client.disconnect()


def main():
    cookies = hangups.auth.get_auth_stdin(token_path)
    client = hangups.Client(cookies)
    client.on_connect.add_observer(lambda: asyncio.ensure_future(send_message(client)))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.connect())
    success('Sent')


if __name__ == '__main__':
    main()

