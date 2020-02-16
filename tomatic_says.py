#!/usr/bin/env python3
from __future__ import print_function
import asyncio

import hangups
import sys
import hangups.hangouts_pb2 as _
import appdirs
import os
import dbconfig

CONVERSATION_ID = 'UgwbNDnElaQHezX-qXN4AaABAQ' # it
CONVERSATION_ID = 'UgzYiKUaJZ1yCpn3R4J4AaABAQ' # petit dejuner
MESSAGE = ' '.join(sys.argv[1:])
if not MESSAGE:
    MESSAGE = sys.stdin.read()
dirs = appdirs.AppDirs('hangups', 'hangups')
REFRESH_TOKEN_PATH = os.path.join(dirs.user_cache_dir, 'refresh_token.txt')
print(MESSAGE)

@asyncio.coroutine
def send_message(client):
    request = _.SendChatMessageRequest(
        request_header = client.get_request_header(),
        event_request_header = _.EventRequestHeader(
            conversation_id = _.ConversationId(
                id=CONVERSATION_ID
            ),
            client_generated_id=client.get_client_generated_id(),
        ),
        message_content = _.MessageContent(
            segment=[hangups.ChatMessageSegment(MESSAGE).serialize()],
        ),
    )
    yield from client.send_chat_message(request)
    yield from client.disconnect()


def main():
    cookies = hangups.auth.get_auth_stdin(REFRESH_TOKEN_PATH)
    client = hangups.Client(cookies)
    client.on_connect.add_observer(lambda: asyncio.async(send_message(client)))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.connect())


if __name__ == '__main__':
	main()
