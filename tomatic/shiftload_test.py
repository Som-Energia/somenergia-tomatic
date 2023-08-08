#!/usr/bin/env python

import unittest
from pathlib import Path
from yamlns import namespace as ns
from . import shiftload
from . import busy

class ShiftLoadTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff=None

    from yamlns.testutils import assertNsEqual

    def test_workingDays_allWorkingDays(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=[],
        )
        self.assertEqual(workingDays,5)

    def test_workingDays_withLeave(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=['alice'],
        )
        self.assertEqual(workingDays,0)

    def test_workingDays_withOthersLeave(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=['bob'],
        )
        self.assertEqual(workingDays,5)

    def test_workingDays_withOneDayoff(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[ns(
                optional = False,
                person = 'alice',
                reason = 'a reason',
                turns = '1111',
                weekday = 'dl',
                )],
            leaves=[],
        )
        self.assertEqual(workingDays,4)

    def test_workingDays_withOneDayoffFromSomeOneElse(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'bob',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dl',
                )],
            leaves=[],
        )
        self.assertEqual(workingDays,5)

    def test_workingDays_withManyDaysOff(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dl',
                ),
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dm',
                )],
            leaves=[],
        )
        self.assertEqual(workingDays,3)

    def test_workingDays_repeatedDaysOff_onlyCountsOne(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dl',
                ),
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dl',
                )],
            leaves=[],
        )
        self.assertEqual(workingDays,4)

    def test_workingDays_withOneHoliday(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=[],
        )
        self.assertEqual(workingDays,4)

    def test_workingDays_withDayOffInHolidays(self):
        workingDays = shiftload.workingDays(
            person='alice',
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dl',
                )],
            leaves=[],
        )
        self.assertEqual(workingDays,4)

    def test_singlePonderatedLoad_withHolidays(self):
        load = shiftload.singlePonderatedLoad(
            person='alice',
            load=10,
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=[],
        )
        self.assertEqual(load, 8.0)

    def test_singlePonderatedLoad_withHolidaysAndDayOff(self):
        load = shiftload.singlePonderatedLoad(
            person='alice',
            load=10,
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'alice',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dm',
                )],
            leaves=[],
        )
        self.assertEqual(load, 6.0)

    def test_singlePonderatedLoad_withHolidaysAndLeaves(self):
        load = shiftload.singlePonderatedLoad(
            person='alice',
            load=10,
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=['alice'],
        )
        self.assertEqual(load, 0.0)

    def test_ponderatedLoad_allWorkingDays(self):
        ideal = ns(
            alice=60,
            bob=60,
        )
        load = shiftload.ponderatedLoad(ideal,
            businessDays=['dl', 'dm', 'dx', 'dj', 'dv'],
            daysoff=[],
            leaves=[],
        )
        self.assertNsEqual(load, """\
            alice: 60.0
            bob: 60.0
        """)

    def test_ponderatedLoad_withHolidaysAndDayOff(self):
        ideal = ns(
            alice=10,
            bob=10,
        )
        load = shiftload.ponderatedLoad(ideal,
            businessDays=['dm', 'dx', 'dj', 'dv'],
            daysoff=[
                ns(
                    optional = False,
                    person = 'bob',
                    reason = 'a reason',
                    turns = '1111',
                    weekday = 'dm',
                )],
            leaves=[],
        )
        self.assertNsEqual(load, """\
            alice: 8.0
            bob: 6.0
        """)

    def test_dayCapacity_noBusy(self):
        capacity = shiftload.dayCapacity(busy='0000',maxPerDay=2)
        self.assertEqual(capacity, 2)

    def test_dayCapacity_allBusy(self):
        capacity = shiftload.dayCapacity(busy='1111',maxPerDay=2)
        self.assertEqual(capacity, 0)

    def test_dayCapacity_lastHalfDayBusy(self):
        capacity = shiftload.dayCapacity(busy='0011',maxPerDay=2)
        self.assertEqual(capacity, 2)

    def test_dayCapacity_firstHalfDayBusy(self):
        capacity = shiftload.dayCapacity(busy='1100',maxPerDay=2)
        self.assertEqual(capacity, 2)

    def test_dayCapacity_middleDayBusy(self):
        capacity = shiftload.dayCapacity(busy='0110',maxPerDay=2)
        self.assertEqual(capacity, 1)

    def test_dayCapacity_max1AndAvailable(self):
        capacity = shiftload.dayCapacity(busy='0011',maxPerDay=1)
        self.assertEqual(capacity, 1)

    def test_dayCapacity_max1AllBusy(self):
        capacity = shiftload.dayCapacity(busy='1111',maxPerDay=1)
        self.assertEqual(capacity, 0)

    def test_dayCapacity_max3_noBusy(self):
        capacity = shiftload.dayCapacity(busy='0000',maxPerDay=3)
        self.assertEqual(capacity, 3)

    def test_dayCapacity_max3_twoBusy(self):
        capacity = shiftload.dayCapacity(busy='1001',maxPerDay=3)
        self.assertEqual(capacity, 2)

    def test_dayCapacity_max3_threeBusy(self):
        capacity = shiftload.dayCapacity(busy='1011',maxPerDay=3)
        self.assertEqual(capacity, 1)

    def test_weekCapacity(self):
        capacity = shiftload.weekCapacity(busy=[
            '0000',
            '0011',
            '1111',
            '0111',
            '1001',
        ], maxPerDay = 2)
        self.assertEqual(capacity, 2+2+0+1+1)

    def test_weekCapacity_max3(self):
        capacity = shiftload.weekCapacity(busy=[
            '0000',
            '0011',
            '1111',
            '0111',
            '1001',
        ], maxPerDay = 3)
        self.assertEqual(capacity, 3+2+0+1+2)

    def test_weekCapacity_max4(self):
        capacity = shiftload.weekCapacity(busy=[
            '0000',
            '0011',
            '1111',
            '0111',
            '1001',
        ], maxPerDay = 4)
        self.assertEqual(capacity, 4+2+0+1+2)

    def setupBusy(self, lines=''):
        busytable = busy.BusyTable(
            days=['dl','dm'],
            nhours=4,
            persons=['alice'],
        )
        tmpfile = Path("tempfile")
        tmpfile.write_text(lines)
        busytable.load(str(tmpfile), busy.isodate('2020-01-02'))
        tmpfile.unlink()
        return busytable

    def test_capacity_noLimits(self):
        busytable = self.setupBusy()
        c = shiftload.capacity(busytable,4)

        self.assertNsEqual(c, """\
            alice: 8
        """)

    def test_capacity_limit3(self):
        busytable = self.setupBusy()
        c = shiftload.capacity(busytable,3)

        self.assertNsEqual(c, """\
            alice: 6
        """)

    def test_capacity_higherSpecificLimits(self):
        busytable = self.setupBusy()
        c = shiftload.capacity(busytable,3, ns(alice=4))

        self.assertNsEqual(c, """\
            alice: 8
        """)

    def test_capacity_lowerSpecificLimits(self):
        busytable = self.setupBusy()
        busytable.load
        c = shiftload.capacity(busytable,3, ns(alice=2))

        self.assertNsEqual(c, """\
            alice: 4
        """)

    def test_capacity_busyConstraints(self):
        busytable = self.setupBusy(
            '+alice dl 1001 # forbides 2 on monday\n'
        )
        c = shiftload.capacity(busytable,2)

        self.assertNsEqual(c, """\
            alice: 3
        """)

    def test_capacity_withLeaves(self):
        busytable = self.setupBusy()
        c = shiftload.capacity(busytable,2,leaves=['alice'])

        self.assertNsEqual(c, """\
            alice: 0
        """)

    def test_capacity_othersLeaves_takeNoEffect(self):
        busytable = self.setupBusy()

        c = shiftload.capacity(busytable,2,leaves=['bob'])

        self.assertNsEqual(c, """\
            alice: 4
        """)

    def test_achieveFullLoad_alreadyComplete(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=0,
                bob=0,
            ),
            shifts = ns(
                alice=2,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 2
            bob: 2
        """)

    def test_achieveFullLoad_withDebt(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=-1,
                bob=0,
            ),
            shifts = ns(
                alice=1,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 2
            bob: 2
        """)

    def test_achieveFullLoad_withDebtAndFullLoad_ignoresDebt(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=-1,
                bob=0,
            ),
            shifts = ns(
                alice=2,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 2
            bob: 2
        """)

    def test_achieveFullLoad_majorDebtorPays(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=-1,
                bob=-2,
            ),
            shifts = ns(
                alice=1,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 1
            bob: 3
        """)

    def test_achieveFullLoad_respectLimits(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=2,
            ),
            credits = ns(
                alice=-1,
                bob=-2,
            ),
            shifts = ns(
                alice=1,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 2
            bob: 2
        """)

    def test_achieveFullLoad_samePersonTwice(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=-5,
                bob=0,
            ),
            shifts = ns(
                alice=0,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 2
            bob: 2
        """)

    def test_achieveFullLoad_onceDebtsArePayed(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=0,
                bob=0,
            ),
            shifts = ns(
                alice=0,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 1
            bob: 3
        """)

    def test_achieveFullLoad_withNegativeDebts(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=1,
                bob=-2,
            ),
            shifts = ns(
                alice=0,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 0
            bob: 4
        """)

    def test_achieveFullLoad_settleDebt(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=-1,
                bob=-3,
            ),
            shifts = ns(
                alice=0,
                bob=0,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 1
            bob: 3
        """)

#---------------

    def test_decreaseUntilFullLoad_alreadyComplete(self):
        newShifts = shiftload.decreaseUntilFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=0,
                bob=0,
            ),
            shifts = ns(
                alice=2,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 2
            bob: 2
        """)

    def test_decreaseUntilFullLoad_withCredit(self):
        newShifts = shiftload.decreaseUntilFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=1,
                bob=0,
            ),
            shifts = ns(
                alice=3,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 2
            bob: 2
        """)

    def test_decreaseUntilFullLoad_withCreditAndFullLoad_ignoresCredit(self):
        newShifts = shiftload.decreaseUntilFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=+1,
                bob=0,
            ),
            shifts = ns(
                alice=2,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 2
            bob: 2
        """)

    def test_decreaseUntilFullLoad_majorCreditorPays(self):
        newShifts = shiftload.decreaseUntilFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=+1,
                bob=+2,
            ),
            shifts = ns(
                alice=3,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 3
            bob: 1
        """)

    def test_decreaseUntilFullLoad_respectLimits(self):
        newShifts = shiftload.decreaseUntilFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=2,
            ),
            credits = ns(
                alice=+1,
                bob=+2,
            ),
            shifts = ns(
                alice=5,
                bob=0,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 4
            bob: 0
        """)

    def test_decreaseUntilFullLoad_samePersonTwice(self):
        newShifts = shiftload.decreaseUntilFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=+5,
                bob=0,
            ),
            shifts = ns(
                alice=2,
                bob=2,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 2
            bob: 2
        """)

    def test_decreaseUntilFullLoad_onceCreditsArePayed(self):
        newShifts = shiftload.decreaseUntilFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=0,
                bob=0,
            ),
            shifts = ns(
                alice=0,
                bob=5,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 0
            bob: 4
        """)

    def test_decreaseUntilFullLoad_withNegativeCredit(self):
        newShifts = shiftload.decreaseUntilFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=-1,
                bob=+2,
            ),
            shifts = ns(
                alice=0,
                bob=6,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 0
            bob: 4
        """)

    def test_decreaseUntilFullLoad_settleCredit(self):
        newShifts = shiftload.decreaseUntilFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=+1,
                bob=+3,
            ),
            shifts = ns(
                alice=4,
                bob=4,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 3
            bob: 1
        """)

    def test_achieveFullLoad_overFullLoad(self):
        newShifts = shiftload.achieveFullLoad(
            fullLoad=4,
            limits = ns(
                alice=10,
                bob=10,
            ),
            credits = ns(
                alice=+1,
                bob=+3,
            ),
            shifts = ns(
                alice=4,
                bob=4,
            ),
        )
        self.assertNsEqual(newShifts, """\
            alice: 3
            bob: 1
        """)

    def test_loadSum_twoParams(self):
        self.assertNsEqual(
            shiftload.loadSum(
                ns(alice=1, bob=2, carol=3),
                ns(alice=20, bob=10, dave=4),
            ),  ns(alice=21, bob=12, carol=3, dave=4))

    def test_loadSum_threeParams(self):
        self.assertNsEqual(
            shiftload.loadSum(
                ns(alice=1, bob=2, carol=3),
                ns(alice=20, bob=10, dave=4),
                ns(alice=100, bob=200, eve=5),
            ),  ns(alice=121, bob=212, carol=3, dave=4, eve=5))

    def test_loadSum_noParams(self):
        self.assertNsEqual(
            shiftload.loadSum(
            ),  ns())


    def test_loadSubstract_substractNothing(self):
        self.assertNsEqual(
            shiftload.loadSubstract(
                ns(alice=1, bob=2),
                ns(alice=0, bob=0),
            ),  ns(alice=1, bob=2))


    def test_loadSubstract_substractSomething(self):
        self.assertNsEqual(
            shiftload.loadSubstract(
                ns(alice=1, bob=2),
                ns(alice=1, bob=-1),
            ),  ns(alice=0, bob=3))


    def test_loadSubstract_missingSubtrahend(self):
        self.assertNsEqual(
            shiftload.loadSubstract(
                ns(alice=1, bob=2),
                ns(alice=1),
            ),  ns(alice=0, bob=2))

    def test_loadSubstract_missingMinuend(self):
        self.assertNsEqual(
            shiftload.loadSubstract(
                ns(alice=1),
                ns(alice=1, bob=2),
            ),  ns(alice=0, bob=-2))


    def test_loadMin_allCases(self):
        self.assertNsEqual(
            shiftload.loadMin(
                ns(alice=3, carol=4),
                ns(alice=1, bob=1),
            ),  ns(alice=1, bob=0, carol=0))

    def test_loadMin_threeParams(self):
        self.assertNsEqual(
            shiftload.loadMin(
                ns(alice=3, carol=4),
                ns(alice=1, bob=1),
                ns(alice=4, bob=-1, dick=20),
            ),  ns(alice=1, bob=-1, carol=0, dick=0))

    def test_loadRound(self):
        self.assertNsEqual(
            shiftload.loadRound(
                ns(alice=1.5, bob=1.49)
            ),  ns(alice=2, bob=1))

    def test_loadDefault(self):
        self.assertNsEqual(
            shiftload.loadDefault(
                ns(alice=1, bob=2), ['alice', 'carol'], 3
            ),  ns(alice=1, carol=3))

    def test_augmentLoad_byDefault(self):
        self.assertNsEqual(
            shiftload.augmentLoad(
                ns(alice=1, bob=2)
            ),  ns(alice=2, bob=3))

    def test_augmentLoad_byTwo(self):
        self.assertNsEqual(
            shiftload.augmentLoad(
                ns(alice=1, bob=2), 2
            ),  ns(alice=3, bob=4))

    def test_clusterize_sortedByLoad(self):
        self.assertNsEqual(
            shiftload.clusterize(
                2, ns(alice=4,bob=2,carol=6)),
            ns(
                carol=[6,0],
                alice=[0,4],
                bob=  [0,2],
            ))

    def test_clusterize_splittingLast(self):
        self.assertNsEqual(
            shiftload.clusterize(
                2, ns(alice=4,bob=3,carol=5)),
            ns(
                carol=[5,0],
                alice=[0,4],
                bob=  [1,2],
            ))

    def test_clusterize_whenNotDivisible_raises(self):
        with self.assertRaises(Exception) as ctx:
            shiftload.clusterize(
                2, ns(alice=4,bob=3))
        self.assertEqual(format(ctx.exception),
            "Total load 7 is not divisible by 2 lines")

    def test_clusterize_ningu(self):
        self.assertNsEqual(
            shiftload.clusterize(
                2, ns(alice=1,bob=2,carol=4, ningu=5)),
            ns(
                carol=[4,0],
                bob=  [0,2],
                alice=[0,1],
                ningu=[2,3],
            ))

    def test_sortedCreditors(self):
        self.assertEqual(list(
            shiftload.sortedCreditors(ns(alice=1, bob=2, carol=-1))), [
                'bob',
                'alice',
                'carol',
            ])

    def test_sortedCreditors_strict(self):
        self.assertEqual(list(
            shiftload.sortedCreditors(ns(alice=0, bob=2, carol=-1), strict=True)), [
                'bob',
            ])

    def test_sortedDebtors(self):
        self.assertEqual(list(
            shiftload.sortedDebtors(ns(alice=1, bob=2, carol=-1))), [
                'carol',
                'alice',
                'bob',
            ])

    def test_sortedDebtors_strict(self):
        self.assertEqual(list(
            shiftload.sortedDebtors(ns(alice=0, bob=2, carol=-1), strict=True)), [
                'carol',
            ])

    def test_compensateDebtsAndCredits_noDebtNorCredit(self):
        self.assertNsEqual(
            shiftload.compensateDebtsAndCredits(
                shifts=ns(alice=1, bob=2),
                credits=ns(alice=0, bob=0),
                limits=ns(alice=100, bob=100),
            ),
            ns(alice=1, bob=2),
        )

    def test_compensateDebtsAndCredits_debitMatches(self):
        self.assertNsEqual(
            shiftload.compensateDebtsAndCredits(
                shifts=ns(alice=1, bob=2),
                credits=ns(alice=-1, bob=1),
                limits=ns(alice=100, bob=100),
            ),
            ns(alice=2, bob=1),
        )

    def test_compensateDebtsAndCredits_notBelowZero(self):
        self.assertNsEqual(
            shiftload.compensateDebtsAndCredits(
                shifts=ns(alice=2, bob=0),
                credits=ns(alice=-1, bob=1),
                limits=ns(alice=100, bob=100),
            ),
            ns(alice=2, bob=0),
        )

    def test_compensateDebtsAndCredits_notAboveLimits(self):
        self.assertNsEqual(
            shiftload.compensateDebtsAndCredits(
                shifts=ns(alice=1, bob=2),
                credits=ns(alice=-1, bob=1),
                limits=ns(alice=1, bob=100),
            ),
            ns(alice=1, bob=2),
        )

    def test_compensateDebtsAndCredits_secondRound(self):
        self.assertNsEqual(
            shiftload.compensateDebtsAndCredits(
                shifts=ns(alice=2, bob=4),
                credits=ns(alice=-2, bob=2),
                limits=ns(alice=100, bob=100),
            ),
            ns(alice=4, bob=2),
        )

    def test_compensateDebtsAndCredits_secondRound(self):
        self.assertNsEqual(
            shiftload.compensateDebtsAndCredits(
                shifts=ns(alice=2, bob=4),
                credits=ns(alice=-2, bob=2),
                limits=ns(alice=100, bob=100),
            ),
            ns(alice=4, bob=2),
        )

    def test_compensateDebtsAndCredits_modifiesCredits(self):
        credit = credits=ns(alice=2, bob=-1, claire=-2)
        shifts = ns(alice=2, bob=4, claire=2)
        self.assertNsEqual(
            shiftload.compensateDebtsAndCredits(
                shifts=shifts,
                credits=credits,
                limits=ns(alice=100, bob=100, claire=100),
            ),
            ns(alice=0, bob=5, claire=3),
        )
        self.assertNsEqual(credit, # modified
            ns(alice=0, bob=0, claire=-1))

        self.assertNsEqual(shifts, # unmodified
            ns(alice=2, bob=4, claire=2))

    def test_compensateDebtsAndCredits_unbalancedCompensation_notApplied(self):
        self.assertNsEqual(
            shiftload.compensateDebtsAndCredits(
                shifts=ns(alice=2, bob=4),
                credits=ns(alice=-0.4, bob=0.2),
                limits=ns(alice=100, bob=100),
            ),
            ns(alice=2, bob=4),
        )

    def test_compensateDebtsAndCredits_equivalentCompensation_notApplied(self):
        self.assertNsEqual(
            shiftload.compensateDebtsAndCredits(
                shifts=ns(alice=2, bob=4),
                credits=ns(alice=-0.5, bob=0.5),
                limits=ns(alice=100, bob=100),
            ),
            ns(alice=2, bob=4),
        )



# vim: et ts=4 sw=4
