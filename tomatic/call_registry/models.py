import pydantic
from pydantic_extra_types.color import Color
from typing import Literal, Annotated, Optional, Union
import stdnum.eu.vat

VatNumber = Annotated[
    str,
    pydantic.AfterValidator(stdnum.eu.vat.validate),
]   

RgbColor = pydantic.constr(
    pattern="^#([a-fA-F0-9]{3}){1,2}$",
    to_lower=True,
    strip_whitespace=True,
)


class Category(
    pydantic.BaseModel,
    # TODO: to allow description_ln, but we should got ride of them
    extra='allow',
):
    id: int
    name: str
    code: str
    keywords: list[str] = []
    color: Optional[RgbColor] = None
    enabled: bool = True

class Categories(pydantic.BaseModel):
    categories: list[Category]

class NewCall(pydantic.BaseModel):
    operator: str
    call_timestamp: pydantic.AwareDatetime

    # Optional: not informed when a manual call
    pbx_call_id: str = ''
    phone_number: str = ''

    # Caller: optional when caller not in database
    caller_erp_id: Optional[int] = None
    caller_vat: Union[VatNumber, Literal['']] = ''
    caller_name: str = ""

    # Contract: optional when no caller or caller has no contracts
    contract_erp_id: Optional[int] = None
    contract_number: str = ""
    contract_address: str = ""

    category_ids: list[int] = []
    comments: str = ""

class Call(NewCall):
    id: int

class CallLog(pydantic.BaseModel):
    operator_calls: list[Call] # TODO: rename as calls


class UpdatedCallLog(CallLog):
    odoo_id: int



def main():
    from yamlns import ns
    import datetime
    import dbconfig as configdb
    import erppeek
    erp = erppeek.Client(**configdb.tomatic.holidaysodoo)

    # TODO: odoo should return the categories key when not filtering
    # TODO: The optional parameter cannot be passed keyword
    include_disabled = True
    categories = Categories(**erp.CrmPhonecall.get_phonecall_categories(include_disabled))
    print(ns(categories.model_dump(mode='json')).dump())

    # TODO: null caller_erp_id shoulbe None, not False
    # TODO: null contract_erp_id shoulbe None, not ''

    response = ( #UpdatedCallLog(**
        erp.CrmPhonecall.create_call_and_get_operator_calls(
            NewCall(
                operator='operadora01',
                pbx_call_id='pbx_id',
                call_timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
            ).model_dump(mode='json'),
        )
    )
    print(ns(response).dump())

    response = ( #UpdatedCallLog(**
        erp.CrmPhonecall.update_call_and_get_operator_calls(
            Call(
                id=1, # TODO: odoo expects odoo_id, let's make them equal
                operator='operadora01',
                pbx_call_id='pbx_id',
                call_timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
            ).model_dump(mode='json')
        )
    )
    print(ns(response).dump())

"""
Detected issues

- Calls
    - Missing entry point for just obtaining the call list (no create, no update)
    - Not sure if we finnally can use the call list returned when updating or creating
        - Let's keep it, to see if we can still use it but if we don't it eventually, would be optimal to remove it
    - Missing caller_vat field in the returned call list
    - call.id vs call.odooo_id
        - create_call_and_get_operator_calls returns call.id
        - update_call_and_get_operator_calls expects call.odoo_id
        - we are using id but could change it
    - Los ids no seteados tendrian que ser None
        - caller_erp_id es False
        - contract_erp_id es ''
    - Response operator_calls -> calls for the type to be reusable in the future
- Categories
    - name_l1, name_l2...
        - not in the specs, we do not need or use it
        - the number layers could be subject to change, so building the attribute name
        - Because of that if we do not remove it, it is better an array
        - 'name' already taken so: levels, hierarchy... ??
        - Anyway no in the spec, forces us to add it or to allow any which is unsafe
    - category.enabled -> disabled
        - in the document, 'disabled', odoo dummy 'enabled'
        - We addapted to 'enabled' but 'disabled' could be more practical
        - 'disabled' as default is enabled, it could have more igual que en html, cuando no esta present es false
    - To discuss: is category.code required, already having category.id
        - One use left for category_code is being a short for display, but too cryptic "SC_FA_GE"
    - Pointless boolean parameter in get_phonecall_categories
        - We won't need a listing without disabled entries (disabled means taggable, but still displayable for old entries)
        - Without defaults and keywords is hard to document what the 'True' means (above we use a temp)
"""


if __name__ == '__main__':
    main()


