from .models import CallLog, Call, NewCall
import datetime
import pathlib

class CallRegistry():
    """
    Dummy implementation for call registry using local files.
    """

    def __init__(self, path: pathlib.Path):
        self.calls = []

    def get_calls(self, operator: str):
        return CallLog(operator_calls=self.calls)
        
        # Call(operator="caca", call_timestamp="2020-01-01T00:00:00.000Z", id=2)

    def add_incoming_call(self, newcall: NewCall):
        self.calls.append(Call(id=1, **newcall.model_dump()))
