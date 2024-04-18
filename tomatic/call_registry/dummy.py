from .models import CallLog, Call
import datetime

class CallRegistry():
    """
    Dummy implementation for call registry using local files.
    """

    def __init__(self, path):
        pass

    def get_calls(self, operator):
        return CallLog(operator_calls=[])
        
        # Call(operator="caca", call_timestamp="2020-01-01T00:00:00.000Z", id=2)