from .models import CallLog, Call, NewCall
import datetime
import pathlib
from yamlns import ns

class CallRegistry():
    """
    Dummy implementation for call registry using local files.
    """

    def __init__(self, path: pathlib.Path):
        self.registry_path = path/"call_registry"
        self.registry_path.mkdir(exist_ok=True)

    def get_calls(self, operator: str):
        registry_file = self.registry_path / 'calls.yaml'
        if not registry_file.exists():
            return CallLog(operator_calls=[])
        return CallLog(**ns.load(registry_file))
        
    def add_incoming_call(self, newcall: NewCall):
        log = self.get_calls(newcall.operator)
        log.operator_calls.append(
            Call(
                id=len(log.operator_calls)+1,
                 **newcall.model_dump()
            )
        )
        registry_file = self.registry_path / 'calls.yaml'
        ns(log.model_dump()).dump(registry_file)
