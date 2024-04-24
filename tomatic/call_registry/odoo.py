from .models import CallLog, Call, NewCall, UpdatedCallLog, Categories
import erppeek

"""
Detected issues


- Errors do not contain stacktrace yet
- Calls
    - Missing entry point for just obtaining the call list (no create, no update)
        - OK
    - Not sure if we finnally can use the call list returned when updating or creating
        - Let's keep it, to see if we can still use it but if we don't it eventually, would be optimal to remove it
        - OK, decission post-posed.
    - Missing caller_vat field in the returned call list
        - OK, ho revisen
    - call.id vs call.odoo_id
        - create_call_and_get_operator_calls returns call.id
        - update_call_and_get_operator_calls expects call.odoo_id
        - we are using id but could change it
        - OK -> id
    - Retorned id, odoo_id -> updated_id
        - Ok
    - All dates as tz informed iso strings (current dummy second call returns a dummy DateTime)
        - OK dates intercanviades totes en format string iso json amb T i Z
- Categories
    - category.enabled -> disabled
        - in the document, 'disabled', odoo dummy 'enabled'
        - We addapted to 'enabled' but 'disabled' could be more practical
        - 'disabled' as default is enabled, it could have more igual que en html, cuando no esta present es false
        - KO no cal adaptar-ho
    - To discuss: is category.code required, already having category.id
        - One use left for category_code is being a short for display, but too cryptic "SC_FA_GE"
        - PENDENT
    - Pointless boolean parameter in get_phonecall_categories
        - We won't need a listing without disabled entries (disabled means taggable, but still displayable for old entries)
        - Without defaults and keywords is hard to document what the 'True' means (above we use a temp)
        - OK el treiem
"""

class CallRegistry():

    def __init__(self):
        import dbconfig as configdb
        self.erp = erppeek.Client(**configdb.tomatic.holidaysodoo)

    def _fix_categories(self, categories):
        # Turn empty colors into None
        for category in categories['categories']:
            category['color'] = category['color'] or None
        return categories

    def _fix_modify_call(self, call):
        call['odoo_id'] = call.pop('id')
        return call

    def _fix_create_call(self, call):
        return call

    def _fix_calls(self, calls):
        # XMLRpc turns Nones in to False, recover them
        for call in calls['calls']:
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
        include_disabled = True
        result = self.erp.CrmPhonecall.get_phonecall_categories(include_disabled)
        self._process_server_errors(result)
        # TODO: Remove this hack
        result = self._fix_categories(result)
        return Categories(**result)

    def get_calls(self, operator: str) -> CallLog:
        # TODO: entrypoint missing
        #result = self.erp.CrmPhonecall.get_operator_phone_calls(operator)
        result = dict(calls=[])
        self._process_server_errors(result)
        # TODO: Remove this hack
        result = self._fix_calls(result)
        return CallLog(**result)

    def add_incoming_call(self, newcall: NewCall) -> UpdatedCallLog:
        newcall = newcall.model_dump(mode='json')
        # TODO: Remove this hack
        newcall = self._fix_create_call(newcall)
        result = self.erp.CrmPhonecall.create_call_and_get_operator_calls(newcall)
        self._process_server_errors(result)
        # TODO: Remove this hack
        result = self._fix_calls(result)
        return UpdatedCallLog(**result)

    def modify_existing_call(self, call: Call) -> UpdatedCallLog:
        call = call.model_dump(mode='json')
        # TODO: Remove this hack
        call = self._fix_modify_call(call)
        result = self.erp.CrmPhonecall.update_call_and_get_operator_calls(call)
        self._process_server_errors(result)
        # TODO: Remove this hack
        result = self._fix_calls(result)
        return UpdatedCallLog(**result)


def main():
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

    created_call_id = result.odoo_id
    dump(result)

    step("Editing existing call")
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    result = registry.modify_existing_call(Call(
        id=1, # TODO: odoo expects odoo_id, let's make them equal
        operator='operadora01',
        pbx_call_id='pbx_id',
        call_timestamp=now,
        category_ids=[1],
        caller_vat="ES12345678Z",
    ))

if __name__ == '__main__':
    main()

