import pydantic
from typing_extensions import Self
from typing import Literal, Annotated, Optional, Union
import stdnum.eu.vat
import re
import datetime

VatNumber = Annotated[
    str,
    pydantic.AfterValidator(stdnum.eu.vat.validate),
]   

RgbColor = Annotated[str, pydantic.StringConstraints(
    pattern="^#([a-fA-F0-9]{3}){1,2}$",
    to_lower=True,
    strip_whitespace=True,
)]

def _cleanupPhone(phone):
    phone = re.sub('[^0-9]', '', phone) # remove non digits
    phone = re.sub(r'^0?0?34','', phone) # remove prefixes
    return phone

PhoneNumber = Annotated[str,
    pydantic.BeforeValidator(_cleanupPhone),
]

class Category(
    pydantic.BaseModel,
):
    id: int
    name: str
    code: str
    levels: list[str]
    keywords: list[str] = []
    color: Optional[RgbColor] = None
    enabled: bool = True

class Categories(pydantic.BaseModel):
    categories: list[Category]

class NewCall(pydantic.BaseModel):
    operator: str
    call_timestamp: pydantic.AwareDatetime

    # Optional: not informed when a manual call
    phone_number: PhoneNumber = ''
    pbx_call_id: str = ''

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

    @pydantic.model_validator(mode='after')
    def _default_pbx_call_id(self) -> Self:
        "If empty, sets a default pbx id based on other attributes"
        if not self.pbx_call_id:
            timestamp = self.call_timestamp
            utctime = timestamp.astimezone(datetime.timezone.utc)
            self.pbx_call_id = f"{utctime:%Y-%m-%dT%H:%M:%SZ}-{self.phone_number}"
        return self

class Call(NewCall):
    id: int

class CallLog(pydantic.BaseModel):
    calls: list[Call] # TODO: rename as calls


class UpdatedCallLog(CallLog):
    updated_id: int


