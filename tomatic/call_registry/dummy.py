from .models import CallLog, Call, NewCall, UpdatedCallLog, Categories
import pathlib
import random
from yamlns import ns

class CallRegistry():
    """
    Dummy implementation for call registry using local files.
    """

    def __init__(self, path: pathlib.Path):
        self.registry_path = pathlib.Path(path) / "call_registry"
        self.registry_path.mkdir(exist_ok=True, parents=True)

    def categories(self) -> Categories:
        category_file = self.registry_path / f'categories.yaml'
        if not category_file.exists():
            return Categories(categories=[])
        return Categories(**ns.load(category_file))

    def _load_calls(self, operator) -> CallLog:
        registry_file = self.registry_path / f'calls-{operator}.yaml'
        if not registry_file.exists():
            return CallLog(calls=[])
        return CallLog(**ns.load(registry_file))

    def _save_calls(self, operator, log: CallLog) -> None:
        registry_file = self.registry_path / f'calls-{operator}.yaml'
        ns(log.model_dump()).dump(registry_file)

    def get_calls(self, operator: str) -> CallLog:
        return self._load_calls(operator)

    def add_incoming_call(self, newcall: NewCall) -> UpdatedCallLog:
        log = self._load_calls(newcall.operator)
        updated_id = random.getrandbits(32)
        log.calls.append(
            Call(
                id=updated_id,
                 **newcall.model_dump()
            )
        )
        self._save_calls(newcall.operator, log)
        return UpdatedCallLog(
            updated_id = updated_id,
            **log.model_dump()
        )

    # TODO: test this
    def _find_call(self, operator: str, id: int):
        log = self._load_calls(operator)
        for call in log.calls:
            if call.id == id: return call

    def modify_existing_call(self, call: Call) -> UpdatedCallLog:
        calls = self._load_calls(call.operator)

        for index, candidate in enumerate(calls.calls):
            if candidate.id == call.id:
                calls.calls[index] = call
                break

        self._save_calls(call.operator, calls)
        return UpdatedCallLog(
            updated_id = call.id,
            **calls.model_dump()
        )


