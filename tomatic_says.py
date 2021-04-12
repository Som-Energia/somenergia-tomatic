#!/usr/bin/env python3

import sys
from tomatic.directmessage.hangouts import send
from consolemsg import step

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
