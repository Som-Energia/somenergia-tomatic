# -*- coding: utf-8 -*-

from yamlns import namespace as ns
from .mongo import MongoConnector, FileProvider
import unittest
from htmlgen import HtmlGenFromSolution
import datetime

class MongoMockup(object):
    def __init__(self, timetables):
        self.timetables = timetables
    def find_one(self, week_dict):
        return {
            'yaml': self.timetables[
                week_dict['week']
            ],
            'week': week_dict['week']
        } if week_dict[
            'week'
        ] in self.timetables else None

    def insert_one(self, timetable_dict):
        self.timetables[
            timetable_dict[
                'week'
            ]
        ]=timetable_dict['yaml']

class MongoConnector_test(unittest.TestCase):

    def ns(self, data):
        return ns.loads(data)

    def test_mongoConnector_loadOne(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hours:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                names:
                    cesar: César
            """),
            solution={('dl',0,0):'ana'},
            date=datetime.datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            companys=['ana']
        )
        m = MongoConnector(MongoMockup({
            '2016-07-18': h.getYaml().dump()
        }))
        self.assertEqual(
            m.loadTimetable(
                '2016-07-18'
            ),
            h.getYaml()
        )
    def test_mongoConnector_insertLoadOne(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hours:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                names:
                    cesar: César
            """),
            solution={('dl',0,0):'ana'},
            date=datetime.datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            companys=['ana']
        )
        m = MongoConnector(MongoMockup({}))
        m.saveTimetable(h.getYaml())
        self.assertEqual(
            m.loadTimetable(
                '2016-07-18'
            ),
            h.getYaml()
        )
    def test_mongoConnector_insertExisting(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hours:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                names:
                    cesar: César
            """),
            solution={('dl',0,0):'ana'},
            date=datetime.datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            companys=['ana']
        )
        m = MongoConnector(MongoMockup({}))
        m.saveTimetable(h.getYaml())
        with self.assertRaises(Exception):
            m.saveTimetable(h.getYaml())

    def test_mongoConnector_insertForce(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hours:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                names:
                    cesar: César
            """),
            solution={('dl',0,0):'ana'},
            date=datetime.datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            companys=['ana']
        )
        m = MongoConnector(MongoMockup({}))
        m.saveTimetable(h.getYaml())
        self.assertEqual(
            m.saveTimetable(h.getYaml(),force=True),
            None
        )

    def test_mongoConnector_loadUnexisting(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hours:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                names:
                    cesar: César
            """),
            solution={('dl',0,0):'ana'},
            date=ns.loads('2016-07-18'),
            companys=['ana']
        )
        m = MongoConnector(MongoMockup({}))
        m.saveTimetable(h.getYaml())
        with self.assertRaises(Exception):
            m.loadTimetable('1900-01-02')
    def test_fileProvider_insert_find(self):
        yaml = """\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hours:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                names:
                    cesar: César
        """
        f = FileProvider("/tmp")
        f.insert_one({
           'week':'2016-04-02',
           'yaml':yaml
        })
        self.assertEqual(yaml,
            f.find_one({
               'week':'2016-04-02'
            })['yaml']
        )


