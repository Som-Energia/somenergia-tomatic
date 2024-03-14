import unittest
import os
from unittest.mock import patch
from yamlns import namespace as ns
from .auth import (
    create_access_token,
    validatedUser,
)
import datetime
from fastapi import HTTPException

@patch.dict('os.environ', TOMATIC_JWT_SECRET_KEY='NOTSOSECRET')
@patch.dict('os.environ', TOMATIC_AUTH_DUMMY='') # Use the real auth
class Auth_Test(unittest.TestCase):
    from yamlns.testutils import assertNsEqual

    def test_token_validates(self):
        payload = ns.loads("""
            username: alice
        """)
        token = create_access_token(payload)
        user = validatedUser(token)
        self.assertNsEqual(user, f"""
            username: alice
            exp: {user.get('exp', 'MISSING')} # self referring
        """)

    def test_token_ignoresExtra(self):
        payload = ns.loads("""
            field1: content1
            field2: content2
            username: alice
        """)
        token = create_access_token(payload)
        user = validatedUser(token)
        self.assertNsEqual(user, f"""
            username: alice
            exp: {user.get('exp', 'MISSING')} # self referring
        """)

    def test_token_passesThruAccepted(self):
        payload = ns.loads("""
            email: me@here.coop
            name: Alice Wonderlander
            picture: https://lh3.googleusercontent.com/a-/jiverjiverjiverjiverjiverjiverjiverjiver
            given_name: Alice
            family_name: Wonderlander
            locale: ca
            username: alice
        """)
        token = create_access_token(payload)
        user = validatedUser(token)
        self.assertNsEqual(user, f"""
            email: me@here.coop
            name: Alice Wonderlander
            picture: https://lh3.googleusercontent.com/a-/jiverjiverjiverjiverjiverjiverjiverjiver
            given_name: Alice
            family_name: Wonderlander
            locale: ca
            username: alice
            exp: {user.get('exp', 'MISSING')} # self referring
        """)

    def test_token_expired(self):
        payload = ns.loads("""
            username: alice
        """)
        token = create_access_token(
            payload,
            datetime.timedelta(minutes=-10)
        )
        with self.assertRaises(HTTPException) as ctx:
            user = validatedUser(token)

        self.assertEqual(format(ctx.exception.detail),
            "Token decoding failed: Signature has expired.")

    def test_token_noUsername(self):
        payload = ns.loads("""
            name: alice
        """)
        token = create_access_token(payload)
        with self.assertRaises(HTTPException) as ctx:
            user = validatedUser(token)

        self.assertEqual(format(ctx.exception.detail),
            "Payload failed")

        # TODO: assert logged: Payload failed

    @patch.dict('os.environ', TOMATIC_AUTH_DUMMY='bob')
    def test_token_dummy_auth(self):
        payload = ns.loads("""
            username: alice
        """)
        token = create_access_token(payload)
        user = validatedUser(token)
        self.assertNsEqual(user, f"""
            username: bob
            email: bob@somenergia.coop
            exp: {user.get('exp', 'MISSING')} # self referring
        """)

    @patch.dict('os.environ', TOMATIC_AUTH_DUMMY='1')
    def test_token_default_dummy_auth(self):
        payload = ns.loads("""
            username: bob
        """)
        token = create_access_token(payload)
        user = validatedUser(token)
        self.assertNsEqual(user, f"""
            username: alice
            email: me@here.coop
            exp: {user.get('exp', 'MISSING')} # self referring
        """)


