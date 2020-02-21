# -*- coding: utf-8 -*-

from .remote import remotewrite, remoteread, remoterun, Remote
import unittest
import os
from io import open

# In order to pass these tests you need to have your
# ssh public key copied as auhtorized key in you own
# computer. And sshd installed and running!

@unittest.skipIf(os.environ.get("travis") == 'true',
    "Unable to set ssh self-connections in Travis")
class Remote_Test(unittest.TestCase):

    def read(self, filename):
        path = os.path.expanduser(filename)
        try:
            with open(path, encoding='utf8') as f:
                return f.read()
        except:
            return None

    def write(self, filename, content):
        path = os.path.expanduser(filename)
        with open(path, 'w', encoding='utf8') as f:
            return f.write(content)

    def append(self, filename, content):
        path = os.path.expanduser(filename)
        try:
            with open(path, encoding='utf8') as f:
                return f.write(content)
        except:
            return


    def setUp(self):
        self.previousAuthorized = self.read('~/.ssh/authorized_keys')
        self.publicKey = self.read('~/.ssh/id_rsa.pub')
        if self.previousAuthorized:
            content = self.previousAuthorized + '\n' + self.publicKey
        else:
            content = self.publicKey
        self.write('~/.ssh/authorized_keys',  content)
        self.conf = dict(
            username = os.getenv('USER'),
            host = 'localhost',
            port = os.getenv('REMOTEPORT',22),
        )

    def tearDown(self):
        if self.previousAuthorized:
            self.write('~/.ssh/authorized_keys', self.previousAuthorized)
        else:
            os.unlink(os.path.expanduser('~/.ssh/authorized_keys'))

    def test_remoterun(self):
        result = remoterun(command="cat /etc/hosts", **self.conf)
        self.assertIn('localhost', result)

    def test_remoteread(self):
        content = remoteread(filename="/etc/hosts", **self.conf)
        self.assertIn('localhost', content)

    def test_remoteread_badPath(self):
        with self.assertRaises(IOError) as ctx:
            remoteread(filename="/etc/badfile", **self.conf)
        self.assertEqual(format(ctx.exception),
            "[Errno 2] No such file")

    def test_remotewrite(self):
        try:
            content = "Some content"
            remotewrite(
                filename="borrame.remotewritetest",
                content=content,
                **self.conf)
            result = remoteread(
                filename="borrame.remotewritetest",
                **self.conf)
            self.assertEqual(result, content)
        finally:
            remoterun(
                command = 'rm borrame.remotewritetest',
                **self.conf)

    def test_run(self):
        with Remote(**self.conf) as remote:
            result = remote.run("cat /etc/hosts")

        self.assertIn('localhost', result)

    def test_read(self):
        with Remote(**self.conf) as remote:
            content = remote.read("/etc/hosts")

        self.assertIn("localhost", content)

    def test_read__binary(self):
        with Remote(**self.conf) as remote:
            content = remote.read("/etc/hosts", binary=True)

        self.assertIn(b"localhost", content)

    def test_read_badPath(self):
        with Remote(**self.conf) as remote:
            with self.assertRaises(IOError) as ctx:
                remote.read("/etc/badfile")
        self.assertEqual(format(ctx.exception),
            "[Errno 2] No such file")

    def test_write(self):
        with Remote(**self.conf) as remote:
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
