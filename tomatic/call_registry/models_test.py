import unittest
import pydantic
from .models import RgbColor, PhoneNumber, NewCall

class LeafTypes_Test(unittest.TestCase):

    def assertRefuses(self, atype, value, message):
        class AClass(pydantic.BaseModel):
            field: atype

        with self.assertRaises(pydantic.ValidationError) as ctx:
            AClass(field=value)

        self.assertIn(message, str(ctx.exception))

    def assertValidates(self, atype, value):
        class AClass(pydantic.BaseModel):
            field: atype
        AClass(field=value)

    def assertTransforms(self, atype, value, expected):
        class AClass(pydantic.BaseModel):
            field: atype
        o = AClass(field=value)
        self.assertEqual(o.field, expected)

    def test_RgbColor__refuses_2_hex_digits(self):
        self.assertRefuses(RgbColor, "#12", "String should match pattern '^#([a-fA-F0-9]{3}){1,2}$'")

    def test_RgbColor__validates_3_hex_digits(self):
        self.assertValidates(RgbColor, "#ff3")

    def test_RgbColor__refuses_4_hex_digits(self):
        self.assertRefuses(RgbColor, "#1234", "String should match pattern '^#([a-fA-F0-9]{3}){1,2}$'")

    def test_RgbColor__refuses_5_hex__digits(self):
        self.assertRefuses(RgbColor, "#12345", "String should match pattern '^#([a-fA-F0-9]{3}){1,2}$'")

    def test_RgbColor__validates_6_hex_digit(self):
        self.assertValidates(RgbColor, "#1aa11a")

    def test_RgbColor__refuses_7_hex_digits(self):
        self.assertRefuses(RgbColor, "#1234567", "String should match pattern '^#([a-fA-F0-9]{3}){1,2}$'")

    def test_RgbColor__refuses_missing_hash(self):
        self.assertRefuses(RgbColor, "123456", "String should match pattern '^#([a-fA-F0-9]{3}){1,2}$'")

    # This is a design choice to simplify, just hex
    def test_RgbColor__refuses_named_colors(self):
        self.assertRefuses(RgbColor, "green", "String should match pattern '^#([a-fA-F0-9]{3}){1,2}$'")

    def test_RgbColor__refuses_bad_hex_digits(self):
        self.assertRefuses(RgbColor, "#ggg", "String should match pattern '^#([a-fA-F0-9]{3}){1,2}$'")

    def test_PhoneNumber_removes_spaces(self):
        self.assertTransforms(PhoneNumber, "  1-234  :567 8 9 ", "123456789")

    def test_PhoneNumber_removes_spanish_prefix(self):
        self.assertTransforms(PhoneNumber, "+34123456789", "123456789")

    def test_PhoneNumber_removes_spanish_prefix_one_zero(self):
        self.assertTransforms(PhoneNumber, "034123456789", "123456789")

    def test_PhoneNumber_removes_spanish_prefix_two_zero(self):
        self.assertTransforms(PhoneNumber, "0034123456789", "123456789")

    def test_NewCall__completes_pbx_call_id(self):
        call = NewCall(
            operator="user",
            call_timestamp="2001-02-02T02:00:00+02:00",
            phone_number='123456789',
        )
        self.assertEqual(
            call.pbx_call_id,
            # zulu is 2h less
            "2001-02-02T00:00:00Z-123456789",
        )

    def test_NewCall__default__pbx_call_id__takes_clean_phone(self):
        call = NewCall(
            operator="user",
            call_timestamp="2001-02-02T02:00:00+02:00",
            phone_number='+++1234:56789', # THIS CHANGES
        )
        self.assertEqual(
            call.pbx_call_id,
            "2001-02-02T00:00:00Z-123456789",
        )



