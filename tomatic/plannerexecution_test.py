import unittest
import time
import datetime
import errno
import sys
from pathlib import Path
from yamlns import namespace as ns
from .plannerexecution import PlannerExecution
from .execution import (
    executionRoot,
    removeRecursive,
)

from .execution_test import (
    assertSandboxes,
    assertContentEqual,
    waitExist,
)

class PlannerExecution_Test(unittest.TestCase):

    assertSandboxes = assertSandboxes
    assertContentEqual = assertContentEqual
    waitExist = waitExist
    from yamlns.testutils import assertNsEqual

    def setUp(self):
        self.configPath = Path('dummyconfig')
        removeRecursive(self.configPath)
        removeRecursive(executionRoot)
        executionRoot.mkdir()
        self.configPath.mkdir()
        (self.configPath/'config.yaml').write_text("""
            nTelefons: 7
            maxOverload: 0
            diesCerca:
            - dv
            - dl
            - dm
            - dj
            - dx
        """)

    def addForcedTurnsFile(self):
        (self.configPath/'data').mkdir()
        (self.configPath/'data'/'forced-turns.yaml').write_text(
            "{}"
        )

    def tearDown(self):
        removeRecursive(self.configPath)
        removeRecursive(executionRoot)

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

    def test_attributes(self):
        e = PlannerExecution(
            monday='2020-05-04',
            description=u"Una Descripción",
            configPath=self.configPath,
        )
        self.assertEqual(e.monday, '2020-05-04')
        self.assertEqual(e.description, u'Una Descripción')
        self.assertEqual(e.nlines, 7)
        self.assertEqual(e.configPath, self.configPath)
        self.assertEqual(e.solutionYaml,
            e.path / 'graella-telefons-2020-05-04.yaml')
        self.assertEqual(e.solutionHtml,
            e.path / 'graella-telefons-2020-05-04.html')

    def test_construction_byName(self):
        original = PlannerExecution(
            monday='2020-05-04',
            description=u"Una Descripción",
            configPath=self.configPath,
            nlines=8,
        )
        original.createSandbox()

        e = PlannerExecution(name=original.name)

        self.assertEqual(e.monday, '2020-05-04')
        #self.assertEqual(e.description, u'Una Descripción')
        #self.assertEqual(e.nlines, 8)
        self.assertEqual(e.configPath, Path('.')) # Don't care, used to create sandbox
        self.assertEqual(e.solutionYaml,
            e.path / 'graella-telefons-2020-05-04.yaml')
        self.assertEqual(e.solutionHtml,
            e.path / 'graella-telefons-2020-05-04.html')

        # TODO configs not in name


    def test_createSandbox_baseCase(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
        )

        e.createSandbox()

        self.assertSandboxes([
            'executions/2020-05-04',
            'executions/2020-05-04/config.yaml',
        ])

    def test_createSandbox_createsConfig(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
        )

        e.createSandbox()

        self.assertNsEqual(
            ns.load(self.configPath/'config.yaml'),
            ns.load(e.path/'config.yaml'),
        )

    def test_createSandbox_linksForcedTurns(self):
        self.addForcedTurnsFile()
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
        )

        e.createSandbox()

        # A link to the original force-turns.yaml is created
        self.assertSandboxes([
            'executions/2020-05-04',
            'executions/2020-05-04/config.yaml',
            'executions/2020-05-04/forced-turns.yaml', # this
        ])
        self.assertEqual(True,
            (e.path/'forced-turns.yaml').is_symlink())
        self.assertEqual(
            (self.configPath/'data'/'forced-turns.yaml').resolve(),
            (e.path/'forced-turns.yaml').resolve(),
        )

        # Config adds the forcedTimeTable parameter
        self.assertNsEqual(
            ns(
                ns.load(self.configPath/'config.yaml'),
                forcedTimeTable ='forced-turns.yaml',
            ),
            ns.load(e.path/'config.yaml'),
        )

    def test_createSandbox_changingLines(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            nlines=8,
        )
        e.createSandbox()
        config = ns.load(e.path/'config.yaml')
        self.assertEqual(config.nTelefons, 8)

    def test_createSandbox_changingSearchDays(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            searchDays='dx',
        )
        e.createSandbox()
        config = ns.load(e.path/'config.yaml')
        self.assertEqual(config.diesCerca, ['dx', 'dv', 'dl', 'dm', 'dj'])

    def test_createSandbox_changingSearchDays(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            searchDays='dj,dx',
        )
        e.createSandbox()
        config = ns.load(e.path/'config.yaml')
        self.assertEqual(config.diesCerca, ['dj', 'dx', 'dv', 'dl', 'dm'])

    def test_createSandbox_badSearchDay_ignored(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            searchDays='dj,caca',
        )
        e.createSandbox()
        config = ns.load(e.path/'config.yaml')
        self.assertEqual(config.diesCerca, ['dj', 'dv', 'dl', 'dm', 'dx'])

    def test_createSandbox_searchDays_stripped(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            searchDays='dj , dx',
        )
        e.createSandbox()
        config = ns.load(e.path/'config.yaml')
        self.assertEqual(config.diesCerca, ['dj', 'dx', 'dv', 'dl', 'dm'])

    def test_listInfo_commonValues_noSandbox(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            nlines=8,
        )
        info = e.listInfo()
        self.assertEqual(info.state, "Launching")
        self.assertEqual(info.name, e.name)
        self.assertEqual(info.startTime, None)

    def test_listInfo_commonValues(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            nlines=8,
        )
        e.createSandbox()
        info = e.listInfo()
        self.assertEqual(info.state, "Launching")
        self.assertEqual(info.name, e.name)
        self.assertEqual(info.startTime, e.startTime)

    def test_listInfo_extendedValues(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            nlines=8,
        )
        e.createSandbox()
        (e.path/'status.yaml').write_text("""\
            totalCells: 120
            completedCells: 72
            solutionCost: 200
            timeOfLastSolution: '2020-12-25 20:45:29.123456'
        """)
        info = e.listInfo()
        self.assertEqual(info.totalCells, 120)
        self.assertEqual(info.completedCells, 72)
        self.assertEqual(info.solutionCost, 200)
        self.assertEqual(info.timeOfLastSolution, datetime.datetime(2020,12,25,20,45,29,123456))

    def test_listInfo_extendedValues_withNoStatus(self):
        e = PlannerExecution(
            monday='2020-05-04',
            configPath=self.configPath,
            nlines=8,
        )
        e.createSandbox()
        info = e.listInfo()
        self.assertEqual(info.totalCells, None)
        self.assertEqual(info.completedCells, None)
        self.assertEqual(info.solutionCost, None)
        self.assertEqual(info.timeOfLastSolution, None)




# vim: ts=4 sw=4 et
