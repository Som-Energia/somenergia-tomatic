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
)
import sys
import appdirs
import os
from yamlns import namespace as ns
from consolemsg import success, step, error, out

import click


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
    for user in user_list.get_all():
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

    for conversation in conversation_list.get_all(include_archived=True):
        if channel and channel == conversation.name:
            return channel.id_.gaia_id
        if channel and conversation.id_.gaia_id:
            return channel
    all_users = user_list.get_all()
    all_conversations = conversation_list.get_all(include_archived=True)
    error("No matching conversation target")
    out('{} known users'.format(len(all_users)))
    for user in all_users:
        out('    {}: {}'.format(user.full_name, user.id_.gaia_id))

    out('{} known conversations'.format(len(all_conversations)))
    for conversation in all_conversations:
        if conversation.name:
            name = conversation.name
        else:
            name = 'Unnamed conversation ({})'.format(conversation.id_)
        out('    {}'.format(name))

async def send_message(client, channel, message):
    step("Resolving channel: {}", channel)
    channel = await resolveChannel(client, channel)
    step("Channel selected: {}", channel)
    request = SendChatMessageRequest(
        request_header = client.get_request_header(),
        event_request_header = EventRequestHeader(
            conversation_id = ConversationId(
                id = channel,
            ),
            client_generated_id=client.get_client_generated_id(),
        ),
        message_content = MessageContent(
            segment=[hangups.ChatMessageSegment(message).serialize()],
        ),
    )
    await client.send_chat_message(request)
    await client.disconnect()


@click.command()
@click.argument('message', nargs=-1)
@click.option('-c', '--channel',
    help='message target: a hangout channel id, email or tomatic user',
    )
@click.option('-t', '--tokenfile',
    help='Token file instead the default one',
    )
def main(tokenfile, message, channel):
    if not message:
        message = sys.stdin.read()
    else:
        message=' '.join(message)
    step("Sending: '{}'", message)

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
    success('Sent')


if __name__ == '__main__':
    main()

# vim: et ts=4 sw=4
