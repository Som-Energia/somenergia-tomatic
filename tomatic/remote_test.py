# -*- coding: utf-8 -*-

from .remote import remotewrite, remoteread, remoterun, Remote
import unittest
import os

# In order to pass these tests you need to have your
# ssh public key copied as auhtorized key in you own
# computer.

config=None
try:
    import config
except ImportError:
    pass



class Remote_Test(unittest.TestCase):

    def setUp(self):
        if config and 'pbx' in config:
            self.user = config.pbx.scp.username
            self.host = config.pbx.scp.pbxhost
        else:
            self.user = os.getenv('USER')
            self.host = 'localhost'

    def test_remoterun(self):
        result = remoterun(self.user, self.host, "cat /etc/hosts")
        self.assertIn('localhost', result)

    def test_remoteread(self):
        content = remoteread(self.user, self.host, "/etc/hosts")
        self.assertIn("localhost", content)

    def test_remoteread_badPath(self):
        with self.assertRaises(IOError) as ctx:
            content = remoteread(
                self.user,
                self.host,
                "/etc/badfile")
        self.assertEqual(str(ctx.exception),
            "[Errno 2] No such file")

    def test_remotewrite(self):
        try:
            content = "Some content"
            remotewrite(
                self.user,
                self.host,
                "borrame.remotewritetest",
                content)
            result = remoteread(
                self.user,
                self.host,
                "borrame.remotewritetest")
            self.assertEqual(result, content)
        finally:
            remoterun(
                self.user,
                self.host,
                'rm borrame.remotewritetest'
                )

    def test_run(self):
        with Remote(self.user, self.host) as remote:
            result = remote.run("cat /etc/hosts")

        self.assertIn('localhost', result)

    def test_read(self):
        with Remote(self.user, self.host) as remote:
            content = remote.read("/etc/hosts")

        self.assertIn("localhost", content)

    def test_read_badPath(self):
        with Remote(self.user, self.host) as remote:
            with self.assertRaises(IOError) as ctx:
                content = remote.read("/etc/badfile")
        self.assertEqual(str(ctx.exception),
            "[Errno 2] No such file")

    def test_write(self):
        with Remote(self.user, self.host) as remote:
            try:
                content = "Some content"
                remote.write("borrame.remotewritetest", content)
                result = remote.read("borrame.remotewritetest")
                self.assertEqual(result, content)
            finally:
                remote.run('rm borrame.remotewritetest')


unittest.TestCase.__str__ = unittest.TestCase.id
 
if __name__ == "__main__":
    unittest.main()

# vim: ts=4 sw=4 et
