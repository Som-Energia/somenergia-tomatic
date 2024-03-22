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
    extra=pydantic.Extra.allow, # to allow description_ln
):
    id: int
    description: str
    code: str
    keywords: str
    color: Color

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

class LoggedCall(NewCall):
    id: int

class CallLog(pydantic.BaseModel):
    calls: list[LoggedCall]


class CreateCallResponse(CallLog):
    created_id: int


