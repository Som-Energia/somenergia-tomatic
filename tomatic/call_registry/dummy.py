from .models import CallLog, Call, NewCall
import datetime
import pathlib
from yamlns import ns

class CallRegistry():
    """
    Dummy implementation for call registry using local files.
    """

    def __init__(self, path: pathlib.Path):
        self.calls = []

        self.registry_path = path/"call_registry"
        self.registry_path.mkdir(exist_ok=True)

    def get_calls(self, operator: str):
        return CallLog(operator_calls=self.calls)
        
    def add_incoming_call(self, newcall: NewCall):
        self.calls.append(Call(id=1, **newcall.model_dump()))

        registry_file = self.registry_path / 'calls.yaml'
        updated_log = CallLog(operator_calls=[
            Call(id=1, **newcall.model_dump())
        ])
        ns(updated_log.model_dump()).dump(registry_file)
