from .models import CallLog, Call, NewCall, CreateCallResponse
import datetime
import pathlib
import random
from yamlns import ns

class CallRegistry():
    """
    Dummy implementation for call registry using local files.
    """

    def __init__(self, path: pathlib.Path):
        self.registry_path = path/"call_registry"
        self.registry_path.mkdir(exist_ok=True)

    def _load_calls(self, operator) -> CallLog:
        registry_file = self.registry_path / f'{operator}.yaml'
        if not registry_file.exists():
            return CallLog(operator_calls=[])
        return CallLog(**ns.load(registry_file))

    def _save_calls(self, operator, log: CallLog) -> None:
        registry_file = self.registry_path / f'{operator}.yaml'
        ns(log.model_dump()).dump(registry_file)

    def get_calls(self, operator: str) -> CallLog:
        return self._load_calls(operator)

    def add_incoming_call(self, newcall: NewCall) -> CreateCallResponse:
        log = self.get_calls(newcall.operator)
        odoo_id = random.getrandbits(128)
        log.operator_calls.append(
            Call(
                id=odoo_id,
                 **newcall.model_dump()
            )
        )
        self._save_calls(newcall.operator, log)
        return CreateCallResponse(
            odoo_id = odoo_id,
            **log.model_dump()
        )

