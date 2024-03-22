import pydantic
from pydantic_extra_types.color import Color
from typing import Literal, Annotated, Optional, Union
import stdnum.eu.vat

VatNumber = Annotated[
    str,
    pydantic.AfterValidator(stdnum.eu.vat.validate),
]   

class Category(
    pydantic.BaseModel,
    extra='allow', # to allow description_ln
):
    id: int
    name: str
    code: str
    keywords: list[str] = []
    color: Optional[Color] = None
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
    operator_calls: list[Call]


class CreateCallResponse(CallLog):
    odoo_id: int



def main():
    from yamlns import ns
    import datetime
    import dbconfig as configdb
    import erppeek
    erp = erppeek.Client(**configdb.tomatic.holidaysodoo)

    # TODO: odoo should return the categories key when not filtering
    # TODO: The optional parameter cannot be passed keyword
    categories = Categories(**erp.CrmPhonecall.get_phonecall_categories(True))
    print(ns(categories.model_dump(mode='json')).dump())

    # TODO: null caller_erp_id shoulbe None, not False
    # TODO: null contract_erp_id shoulbe None, not ''

    response = ( #CreateCallResponse(**
        erp.CrmPhonecall.create_call_and_get_operator_calls(
            NewCall(
                operator='operadora01',
                pbx_call_id='pbx_id',
                call_timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
            ).model_dump(mode='json'),
            True
        )
    )
    print(ns(response).dump())

    response = ( #CreateCallResponse(**
        erp.CrmPhonecall.update_call_and_get_operator_calls(
            Call(
                id=3, # TODO: odoo expects odoo_id, let's make them equal
                operator='operadora01',
                pbx_call_id='pbx_id',
                call_timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
            ).model_dump(mode='json')
        )
    )
    print(ns(response).dump())


if __name__ == '__main__':
    main()


