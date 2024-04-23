from json import dumps
from consolemsg import out
import requests

def send(channel, message):
    """Hangouts Chat incoming webhook quickstart."""
    response = requests.post(
        channel,
        json = {
            'text' : message,
        },
    )
    print(response.text)
    response.raise_for_status()
