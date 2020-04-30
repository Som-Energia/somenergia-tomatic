import unittest
from execution import (
    Execution,
    executionRoot,
    PlannerExecution,
)
from pathlib2 import Path

def removeRecursive(f):
    if not f.exists():
        return
    if not f.is_dir():
        f.unlink()
        return
    for sub in f.iterdir():
        removeRecursive(sub)
    f.rmdir()

def cleanExecutionDir(self):
    removeRecursive(executionRoot)

def assertSandboxes(self, expected):
    result = [
        str(p)
        for p in sorted(executionRoot.glob('**/*'))
    ]
    self.assertEqual(result, expected)


class Execution_Test(unittest.TestCase):

    def setUp(self):
        self.cleanExecutionDir()
        executionRoot.mkdir()

    cleanExecutionDir = cleanExecutionDir
    assertSandboxes = assertSandboxes

    def test_simpleProperties(self):
        e = Execution(name="hola")
        self.assertEqual(e.name, 'hola')
        self.assertEqual(e.path, executionRoot/'hola')
        self.assertEqual(e.outputFile, executionRoot/'hola'/'output.txt')
        self.assertEqual(e.pidFile, executionRoot/'hola'/'pid')

    def test_createSandbox(self):
        e = Execution(name="hola")
        self.assertEqual(False, e.path.exists())
        e.createSandbox()
        self.assertEqual(True, e.path.exists())
        self.assertSandboxes([
            'executions/hola',
        ])

class PlannerExecution_Test(unittest.TestCase):

    def setUp(self):
        self.cleanExecutionDir()
        executionRoot.mkdir()
        self.configPath = Path('dummyconfig')
        removeRecursive(self.configPath)
        self.configPath.mkdir()
        (self.configPath/'config.yaml').write_text("""
            nTelefons: 7
        """)
        (self.configPath/'holidays.conf').write_text(
            "2020-12-25\tNadal"
        )
        (self.configPath/'drive-certificate.json').write_text(
            "{}"
        )

    cleanExecutionDir = cleanExecutionDir
    assertSandboxes = assertSandboxes

    def test_createSandbox_baseCase(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
        )

        e.createSandbox()
        self.assertSandboxes([
            'executions/2020-05-04',
            'executions/2020-05-04/config.yaml',
            'executions/2020-05-04/drive-certificate.json',
            'executions/2020-05-04/holidays.conf',
        ])

        #config = ns.load('executions/2020-05-04/config.yaml')
        #self.assertEqual(config.nTelefons, 7)


"""
    def _test_createSandbox(self):
        e = PlannerExecution(
            monday='2020-05-04',
            description='una descripción',
            nlines=2,
        )

        self.assertEqual(False, e.path.exists())
        e.createSandbox()
        self.assertEqual(True, e.path.exists())
        self.assertSandboxes([
            'executions',
            'executions/2020-05-04-una-descripcion',
            'executions/2020-05-04-una-descripcion/drive-certificate.json',
            'executions/2020-05-04-una-descripcion/config.yaml',
            'executions/2020-05-04-una-descripcion/holidays.conf',
        ])
"""







# vim: ts=4 sw=4 et
