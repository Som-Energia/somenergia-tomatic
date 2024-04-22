import unittest
import pydantic
from .models import RgbColor

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



