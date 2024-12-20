from .models import CallLog, Call, NewCall, UpdatedCallLog, Categories
import erppeek
from ..config import secrets

"""
TODO:

- Pass limits and dates to call list
- Wait: Error handling is not implemented in odoo yet
- Blocked: When doing ui, decide whether we can get profit of the returned calls in create/update ops. If not remove them.
- create didn't save categories
- create does not takes caller_vat
- update accessed odoo_id instead of id
- dummy data vats are nifs (missing ES)
"""

class CallRegistry():

    def __init__(self):
        self.erp = erppeek.Client(**secrets('tomatic.holidaysodoo'))

    def _fix_categories(self, categories):
        # Turn empty colors into None
        for category in categories['categories']:
            category['color'] = category['color'] or None
        return categories

    def _fix_create_call(self, call):
        # XMLRpc rejects Nones, turn into False, 
        call['caller_erp_id'] = call['caller_erp_id'] or False
        call['contract_erp_id'] = call['contract_erp_id'] or False
        print(call)
        return call

    def _fix_calls(self, calls):
        # XMLRpc turns Nones in to False, recover them
        for call in calls['calls']:
            vat = call['caller_vat']
            if vat and len(vat)<=10:
                call['caller_vat'] = 'ES'+vat
            call['caller_erp_id'] = call['caller_erp_id'] or None
            call['contract_erp_id'] = call['contract_erp_id'] or None

        return calls

    def _process_server_errors(self, result) -> None:
        if 'error' not in result: return
        # TODO: proper handling
        raise Exception(str(result))

    def categories(self) -> Categories:
        # TODO: odoo should return the categories key when not filtering
        # TODO: The optional parameter cannot be passed keyword
        result = self.erp.CrmPhonecall.get_phonecall_categories()
        self._process_server_errors(result)
        # TODO: Remove this hack
        result = self._fix_categories(result)
        return Categories(**result)

    def get_calls(self, operator: str) -> CallLog:
        result = self.erp.CrmPhonecall.get_operator_calls(dict(
            operator=operator,
        ))
        self._process_server_errors(result)
        result = self._fix_calls(result)
        return CallLog(**result)

    def add_incoming_call(self, newcall: NewCall) -> UpdatedCallLog:
        newcall = newcall.model_dump(mode='json')
        newcall = self._fix_create_call(newcall)
        result = self.erp.CrmPhonecall.create_call_and_get_operator_calls(newcall)
        self._process_server_errors(result)
        result = self._fix_calls(result)
        return UpdatedCallLog(**result)

    def modify_existing_call(self, call: Call) -> UpdatedCallLog:
        call = call.model_dump(mode='json')
        call = self._fix_create_call(call)
        result = self.erp.CrmPhonecall.update_call_and_get_operator_calls(call)
        self._process_server_errors(result)
        result = self._fix_calls(result)
        return UpdatedCallLog(**result)


def main():
    # Run me with: python -m tomatic.call_registry.odoo
    import datetime
    from yamlns import ns
    from consolemsg import step, warn

    def dump(model):
        print(ns(model.model_dump(mode='json')).dump())

    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    print("Now:", now)
    registry = CallRegistry()

    step("Obtaining categories")
    dump(registry.categories())

    step("Obtaining operator call log")
    warn("not available yet")
    dump(registry.get_calls("operadora01"))

    step("Addiing incomming call")
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    result = registry.add_incoming_call(NewCall(
        operator='operadora01',
        pbx_call_id='trucada_creada',
        call_timestamp=now,
    ))

    created_call_id = result.updated_id
    dump(result)

    step("Editing existing call")
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    result = registry.modify_existing_call(Call(
        id=1,
        operator='operadora01',
        pbx_call_id='pbx_id',
        call_timestamp=now,
        category_ids=[1],
        caller_vat="ES12345678Z",
    ))
    edited_call_id = result.updated_id
    dump(result)

    step("Esborrant la annotació")
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    result = registry.delete_annotation(Call(
        id=1,
        operator='operadora01',
        pbx_call_id='pbx_id',
        call_timestamp=now,
        comments='holi',
        category_ids=[1],
        caller_vat="ES12345678Z",
    ))
    edited_call_id = result.updated_id
    dump(result)

if __name__ == '__main__':
    main()

