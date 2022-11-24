from json import dumps
from httplib2 import Http
from consolemsg import out


def send(channel, message):
    """Hangouts Chat incoming webhook quickstart."""
    bot_message = {'text' : message}
    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

    http_obj = Http()
    
    http_obj.request(
        uri=channel,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )
