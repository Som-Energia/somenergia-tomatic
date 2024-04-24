import pydantic
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
    calls: list[Call] # TODO: rename as calls


class UpdatedCallLog(CallLog):
    odoo_id: int


