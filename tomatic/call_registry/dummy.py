from .models import CallLog, Call, NewCall, CreateCallResponse, Categories
import datetime
import pathlib
import random
from yamlns import ns

class CallRegistry():
    """
    Dummy implementation for call registry using local files.
    """

    def __init__(self, path: pathlib.Path = 'data'):
        self.registry_path = pathlib.Path(path) / "call_registry"
        self.registry_path.mkdir(exist_ok=True, parents=True)

    def _load_calls(self, operator) -> CallLog:
        registry_file = self.registry_path / f'calls-{operator}.yaml'
        if not registry_file.exists():
            return CallLog(operator_calls=[])
        return CallLog(**ns.load(registry_file))

    def _save_calls(self, operator, log: CallLog) -> None:
        registry_file = self.registry_path / f'calls-{operator}.yaml'
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

    # TODO: test this
    def get_call(self, operator: str, id: int):
        log = self._load_calls(operator)
        call = list(filter(lambda call: call.id == id, log.operator_calls))
        return call[0]

    def modify_existing_call(self, call, fields):
        calls = self.get_calls(call.operator)

        for index, operator_call in enumerate(calls.operator_calls):
            if operator_call.id == call.id:
                calls.operator_calls[index] = dict(operator_call, **fields)
                break

        self._save_calls(call.operator, calls)

    def categories(self) -> Categories:
        category_file = self.registry_path / f'categories.yaml'
        if not category_file.exists():
            return Categories(categories=[])
        return Categories(**ns.load(category_file))
