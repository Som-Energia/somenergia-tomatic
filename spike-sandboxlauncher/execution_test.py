import unittest
from execution import (
    Execution,
    executionRoot,
    PlannerExecution,
)
from pathlib2 import Path
from yamlns import namespace as ns

def removeRecursive(f):
    if not f.exists() and not f.is_symlink():
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

    cleanExecutionDir = cleanExecutionDir
    assertSandboxes = assertSandboxes
    from yamlns.testutils import assertNsEqual

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

    def assertContentEqual(self, path1, path2):
        self.assertMultiLineEqual(
            path1.read_text(encoding='utf8'),
            path2.read_text(encoding='utf8'),
        )


    def test_path_noDescription(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
        )
        self.assertEqual(e.path,
            executionRoot/'2020-05-04')

    def test_path_withDescription(self):
        e = PlannerExecution(
            monday='2020-05-04',
            description="description",
            configPath=self.configPath,
        )
        self.assertEqual(e.path,
            executionRoot/'2020-05-04-description')


    def test_path_withDescription_withSlug(self):
        e = PlannerExecution(
            monday='2020-05-04',
            description=u"Una Descripción", # Spaces, accent and uppercase
            configPath=self.configPath,
        )
        self.assertEqual(e.path,
            executionRoot/'2020-05-04-una-descripcion')

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

    def test_createSandbox_createsConfig(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
        )

        e.createSandbox()

        self.assertNsEqual(
            ns.load(self.configPath/'config.yaml'),
            ns.load(e.path/'config.yaml'))

    def test_createSandbox_createsHolidays(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
        )

        e.createSandbox()

        self.assertContentEqual(
            self.configPath/'holidays.conf',
            e.path/'holidays.conf')


    def test_createSandbox_linksCertificate(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
        )

        e.createSandbox()

        self.assertContentEqual(
            self.configPath/'drive-certificate.json',
            e.path/'drive-certificate.json')

        self.assertEqual(True,
            (e.path/'drive-certificate.json').is_symlink())
        self.assertEqual(
            (self.configPath/'drive-certificate.json').resolve(),
            (e.path/'drive-certificate.json').resolve())


    def test_createSandbox_changingLines(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            nlines=8,
        )
        e.createSandbox()
        config = ns.load(e.path/'config.yaml')
        self.assertEqual(config.nTelefons, 8)



# vim: ts=4 sw=4 et
