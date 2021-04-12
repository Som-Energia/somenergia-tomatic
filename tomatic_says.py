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
    CreateConversationRequest,
    CONVERSATION_TYPE_ONE_TO_ONE,
    InviteeID,
    SEGMENT_TYPE_LINE_BREAK,
)
import sys
import appdirs
import os
from yamlns import namespace as ns
from consolemsg import success, step, error, out


config = ns.load('config.yaml')
persons = ns.load('persons.yaml')


async def open_conversation(client, conversation_name, *gaia_ids):
    request = CreateConversationRequest(
        request_header=client.get_request_header(),
        type=CONVERSATION_TYPE_ONE_TO_ONE,
        client_generated_id=client.get_client_generated_id(),
        invitee_id=[
            InviteeID(
                gaia_id=gaia_id
            ) for gaia_id in gaia_ids
        ],
        name=conversation_name
    )
    response = await client.create_conversation(request)
    return response.conversation.conversation_id.id

async def resolveChannel(client, channel):
    # If no channel provided take it from config or fail
    if not channel:
        channel = config.hangoutChannel

    # If the convesation is a tomatic person, get its email
    if channel in persons.emails:
        step("Tomatic person {} with email {}",
            channel, persons.emails[channel])
        channel = persons.emails[channel]

    user_list, conversation_list = (
        await hangups.build_user_conversation_list(client)
    )
    all_users = user_list.get_all()
    for user in all_users:
        if channel in user.emails:
            step("Sending message to {.full_name} <{}>", user, channel)
            return await open_conversation(client, "Tomatic", user.id_.gaia_id)
        if channel == user.full_name:
            step("Sending message to {.full_name} <{}>", user, channel)
            return await open_conversation(client, "Tomatic", user.id_.gaia_id)
        if channel == user.id_.gaia_id:
            step("Sending message to {.full_name} <{}>", user, channel)
            return await open_conversation(client, "Tomatic", user.id_.gaia_id)

    if channel.isdigit() and len(channel)==20: # gaia_id, not conversation id
        step("Sending message to unknown gaia_id {}", channel)
        return await open_conversation(client, "Tomatic", channel)

    all_conversations = conversation_list.get_all(include_archived=True)
    for conversation in all_conversations:
        if channel == conversation.name:
            step("Sending message to Group {0.name} ({0.id_})", conversation)
            return conversation.id_
        if channel == conversation.id_:
            step("Sending message to Group {0.name} ({0.id_})", conversation)
            return conversation.id_

    error("No matching conversation target")

    emails = dict((email, person) for person, email in persons.emails.items())
    out('{} known users'.format(len(all_users)))
    for user in all_users:
        email = user.emails[0] if user.emails else '???'
        out('    {} {} <{}> [{}]',
            user.full_name,
            '({})'.format(emails.get(email)) if email in emails else '',
            email,
            user.id_.gaia_id,
        )

    out('{} known conversations'.format(len(all_conversations)))
    for conversation in all_conversations:
        name = conversation.name or 'Unnamed Conversation'
        out('    {} ({})'.format(name, conversation.id_))

    return None

async def send_message(client, channel, message):
    try:
        step("Resolving channel: {}", channel)
        channel = await resolveChannel(client, channel)
        if not channel:
            error("Message couldn't be sent")
            return
        step("Channel selected: {}", channel)

        segments = sum([[
                hangups.ChatMessageSegment(m),
                hangups.ChatMessageSegment('',segment_type=SEGMENT_TYPE_LINE_BREAK),
                ]
            for m in message.splitlines()
            ],[])[:-1]

        request = SendChatMessageRequest(
            request_header = client.get_request_header(),
            event_request_header = EventRequestHeader(
                conversation_id = ConversationId(
                    id = channel,
                ),
                client_generated_id=client.get_client_generated_id(),
            ),
            message_content = MessageContent(
                segment=[segment.serialize()
                    for segment in segments
                ],
            ),
        )
        await client.send_chat_message(request)
        success("Message sent")
    finally:
        await client.disconnect()


def send(channel, message, tokenfile=None):
    if not tokenfile:
        dirs = appdirs.AppDirs('hangups', 'hangups')
        tokenfile = os.path.join(dirs.user_cache_dir, 'refresh_token.txt')

    cookies = hangups.auth.get_auth_stdin(tokenfile)
    client = hangups.Client(cookies)
    client.on_connect.add_observer(lambda:
        asyncio.ensure_future(
            send_message(client, channel, message )
        )
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.connect())


if __name__ == '__main__':
    import click

    @click.command()
    @click.argument('message', nargs=-1)
    @click.option('-c', '--channel',
        help='message target: a hangout channel id, email or tomatic user',
        )
    @click.option('-t', '--tokenfile',
        help='Token file instead the default one',
        )
    def main(channel, message, tokenfile):
        if not message:
            message = sys.stdin.read()
        else:
            message=' '.join(message)
        step("Sending: '{}'", message)

        send(channel, message, tokenfile)

    main()

# vim: et ts=4 sw=4
