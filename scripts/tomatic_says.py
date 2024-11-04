#!/usr/bin/env python3

import sys
from tomatic.config import secrets
from tomatic.directmessage import send
from consolemsg import step

if __name__ == '__main__':
    import click

    @click.command()
    @click.argument('message', nargs=-1)
    def main(message):
        if not message:
            message = sys.stdin.read()
        else:
            message=' '.join(message)
        step("Sending: '{}'", message)

        send(
            secrets('tomatic.monitorChatChannel'),
            message
        )

    main()

# vim: et ts=4 sw=4
