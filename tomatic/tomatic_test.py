# -*- coding: utf-8 -*-
import unittest
import datetime
from yamlns import namespace as ns
import b2btest
import sys
from parse import parse
import random
import datetime

from htmlgen import HtmlGenFromYaml
from htmlgen import HtmlGenFromSolution
from htmlgen import HtmlGenFromAsterisk
from mongo import MongoConnector, FileProvider

config=None
try:
    import config
except ImportError:
    pass
if config:
    import asterisk
    from paramiko import SSHClient,AutoAddPolicy
    from Asterisk.Manager import Manager

class SSHMockup(object):
    def __init__(self, pbxMockupObject):
        self.pbxMockupObject = pbxMockupObject
    def put(self, conf):
        self.pbxMockupObject.conf = conf

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

class ScheduleHours_Test(unittest.TestCase):
    def eqOrdDict(self, dict1,dict2, 
         msg=None):
         if not msg:
             msg="{}!={}".format(dict1,dict2)

         if dict1 == None or dict2 == None:
             raise self.failureException(msg+"\n\n{} or {} is None".format(dict1,dict2))

         if type(dict1) is not ns or type(dict2) is not ns:
             raise self.failureException(msg+"\n\n{} or {} are not yamlns".format(dict1,dict2))

         shared_keys = set(dict2.keys()) & set(dict2.keys())        

         if not ( len(shared_keys) == len(dict1.keys()) and len(shared_keys) == len(dict2.keys())):
             raise self.failureException(
                msg+"\n\nLen of keys {} and {} are different".format(
                    dict1.keys(), dict2.keys()))
         for key in dict1.keys():
             if type(dict1[key]) is ns:
                 if key not in dict2:
                    raise self.failureException(msg+"\n\n"+("{} is not in the second element".format(dict1[key])))
                 if not self.eqOrdDict(dict1[key],dict2[key],msg=msg):
                    raise self.failureException(msg)
             else:
                 if not key in dict2:
                    raise self.failureException(msg+"\n\n"+("{} is not in the second element".format(dict1[key])))
                 if not dict1[key] == dict2[key]:
                    raise self.failureException(msg+"\n\n"+("{}!={}".format(dict1[key],dict2[key])))
         return True

    def ns(self,content):
        return ns.loads(content)
    def setUp(self):
        self.addTypeEqualityFunc(ns,self.eqOrdDict)
    def tearDown(self):
        return # TODO: Recover this
        if config:
            sshconfig = config.pbx['scp']
            with SSHClient() as ssh:
                ssh.set_missing_host_key_policy(AutoAddPolicy())
                ssh.connect(sshconfig['pbxhost'],
                    username=sshconfig['username'],
                    password=sshconfig['password'])
                path= "/".join(sshconfig['path'].split("/")[:-1])
                file = sshconfig['path'].split("/")[-1]
                ssh.exec_command('cd {}; git checkout {}'.format(path,file))
            pbx = Manager(**config.pbx['pbx'])
            pbx.Command('reload')

    def test_yamlSolution_oneholiday(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
                    cesar: César
            """),
            solution={},
            date=datetime.datetime.strptime(
                '2016-07-11','%Y-%m-%d').date(),
            companys=['ana']
        )
        self.assertEqual(
            h.getYaml(),
            {'timetable': ns(
                {'dl': ns(
                    {1: ['festiu']})
                }),
              'hores': [
                '09:00',
                '10:15'
              ],
              'torns': [
                'T1'
              ],
              'colors': ns(
                {'ana': '98bdc0'}
              ),
              'extensions': ns(
                {'ana': 3181}
              ),
              'noms': ns(
                {'cesar': u'César'}
              ),
              'setmana': datetime.date(
                2016,7,11),
              'companys': ['ana']
            }
        )
    def test_mongoConnector_loadOne(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
                    cesar: César
            """),
            solution={('dl',0,0):'ana'},
            date=datetime.datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            companys=['ana']
        )
        m = MongoConnector(MongoMockup({
            '2016_07_18': h.getYaml().dump()
        }))
        self.assertEqual(
            m.loadTimetable(
                '2016_07_18'
            ),
            h.getYaml()
        )
    def test_mongoConnector_insertLoadOne(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
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
                '2016_07_18'
            ),
            h.getYaml()
        )
    def test_mongoConnector_insertExisting(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
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
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
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
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
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
            m.loadTimetable('1900_01_02')
    def test_fileProvider_insert_find(self):
        yaml = """\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
                    cesar: César
        """
        f = FileProvider("/tmp")
        f.insert_one({
           'week':'2016_04_02',
           'yaml':yaml
        })
        self.assertEqual(yaml,
            f.find_one({
               'week':'2016_04_02'
            })['yaml']
        )

    def test_yamlSolution_oneslot(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
                nTelefons: 1
                diesVisualitzacio: ['dl']
                hores:  # La darrera es per tancar
                - '09:00'
                - '10:15'
                colors:
                    ana: 98bdc0
                extensions:
                    ana: 3181
                noms:
                    cesar: César
            """),
            solution={('dl',0,0):'ana'},
            date=datetime.datetime.strptime(
                '2016-07-18','%Y-%m-%d').date(),
            companys=['ana']
        )
        
        self.assertEqual(
            h.getYaml(), 
            ns(
                {'timetable': ns(
                    {'dl': ns(
                        {1: ['ana']})
                    }),
                  
                  'hores': [
                    '09:00',
                    '10:15'
                  ],
                  'torns': [
                    'T1'
                  ],
                  'colors': ns(
                    {'ana': '98bdc0'}
                  ),
                  'extensions': ns(
                    {'ana': 3181}
                  ),
                  'noms': ns(
                    {'cesar': u'César'}
                  ),
                  'setmana': datetime.date(
                    2016,7,18),
                  'companys': ['ana']
                },
            )
        )
    
    def test_yamlSolution_completeTimetable(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
        nTelefons: 3
        diesCerca: ['dx','dm','dj', 'dl', 'dv',] # Els mes conflictius davant
        diesVisualitzacio: ['dl','dm','dx','dj','dv']

        hores:  # La darrera es per tancar
        - '09:00'
        - '10:15'
        - '11:30'
        - '12:45'
        - '14:00'
        randomColors: false # Si vols generar colors aleatoris o fer cas de 'colors'
        colors:
           marc:   'fbe8bc'
           eduard: 'd8b9c5'
           pere:   '8f928e'
           david:  'ffd3ac'
           aleix:  'eed0eb'
           carles: 'c98e98'
           marta:  'eb9481'
           monica: '7fada0'
           yaiza:  '90cdb9'
           erola:  '8789c8'
           manel:  '88dfe3'
           tania:  'c8abf4'
           judit:  'e781e8'
           silvia: '8097fa'
           joan:   'fae080'
           ana:    '98bdc0'
           victor: 'ff3333'
           jordi: 'ff9999' 
        extensions:
           marta:  3040
           monica: 3041
           manel:  3042
           erola:  3043
           yaiza:  3044
           eduard: 3045
           marc:   3046
           judit:  3047
           judith: 3057
           tania:  3048
           carles: 3051
           pere:   3052
           aleix:  3053
           david:  3054
           silvia: 3055
           joan:   3056
           ana:    3181
           victor: 3182
           jordi:  3183 
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
            """),
            solution={
                ('dl',0,0):'jordi',
                ('dl',0,1):'marta',
                ('dl',0,2):'tania',
                ('dl',1,0):'tania',
                ('dl',1,1):'yaiza',
                ('dl',1,2):'silvia',
                ('dl',2,0):'judith',
                ('dl',2,1):'pere',
                ('dl',2,2):'ana',
                ('dl',3,0):'ana',
                ('dl',3,1):'judith',
                ('dl',3,2):'erola',
                ('dm',0,0):'pere',
                ('dm',0,1):'jordi',
                ('dm',0,2):'victor',
                ('dm',1,0):'carles',
                ('dm',1,1):'victor',
                ('dm',1,2):'ana',
                ('dm',2,0):'joan',
                ('dm',2,1):'silvia',
                ('dm',2,2):'eduard',
                ('dm',3,0):'david',
                ('dm',3,1):'joan',
                ('dm',3,2):'monica',
                ('dx',0,0):'yaiza',
                ('dx',0,1):'monica',
                ('dx',0,2):'pere',
                ('dx',1,0):'erola',
                ('dx',1,1):'joan',
                ('dx',1,2):'marta',
                ('dx',2,0):'victor',
                ('dx',2,1):'eduard',
                ('dx',2,2):'jordi',
                ('dx',3,0):'eduard',
                ('dx',3,1):'david',
                ('dx',3,2):'victor',
                ('dj',0,0):'judith',
                ('dj',0,1):'jordi',
                ('dj',0,2):'carles',
                ('dj',1,0):'silvia',
                ('dj',1,1):'tania',
                ('dj',1,2):'judith',
                ('dj',2,0):'monica',
                ('dj',2,1):'ana',
                ('dj',2,2):'judit',
                ('dj',3,0):'judit',
                ('dj',3,1):'erola',
                ('dj',3,2):'joan',
                ('dv',0,0):'ana',
                ('dv',0,1):'judith',
                ('dv',0,2):'jordi',
                ('dv',1,0):'jordi',
                ('dv',1,1):'ana',
                ('dv',1,2):'judith',
                ('dv',2,0):'victor',
                ('dv',2,1):'carles',
                ('dv',2,2):'yaiza',
                ('dv',3,0):'marta',
                ('dv',3,1):'victor',
                ('dv',3,2):'silvia',
                },
            date=datetime.datetime.strptime(
                '2016-07-11','%Y-%m-%d').date(),
            companys= [
                'aleix',
                'ana',
                'carles',
                'david',
                'eduard',
                'erola',
                'joan',
                'jordi',
                'judit',
                'judith',
                'manel',
                'marc',
                'marta',
                'monica',
                'pere',
                'silvia',
                'tania',
                'victor',
                'yaiza'
            ]
        )

        self.assertEqual(
            h.getYaml(), 
            ns(
                {'timetable': ns(
                    {'dl': ns(
                        {1: 
                            ['jordi',
                             'marta',
                             'tania'
                             ]
                        ,
                        2: 
                            ['tania',
                             'yaiza',
                             'silvia'
                             ]
                        ,
                        3: 
                            ['judith',
                             'pere',
                             'ana'
                             ]
                        ,
                        4: 
                            ['ana',
                             'judith',
                             'erola'
                             ]
                        }),
                     'dm': ns({
                        1: 
                           ['pere',
                            'jordi',
                            'victor'
                            ]
                        ,
                        2: 
                           ['carles',
                            'victor',
                            'ana'
                            ]
                        ,
                        3: 
                           ['joan',
                            'silvia',
                            'eduard'
                            ]
                        ,
                        4: 
                           ['david',
                            'joan',
                            'monica'
                            ]
                        }),

                     'dx': ns({
                        1: 
                           ['yaiza',
                            'monica',
                            'pere'
                            ]
                        ,
                        2: 
                           ['erola',
                            'joan',
                            'marta'
                            ]
                        ,
                        3: 
                           ['victor',
                            'eduard',
                            'jordi'
                            ]
                        ,
                        4: 
                           ['eduard',
                            'david',
                            'victor'
                            ]
                        }),
                     
                     'dj': ns({
                        1: 
                           ['judith',
                            'jordi',
                            'carles'
                            ]
                        ,
                        2: 
                           ['silvia',
                            'tania',
                            'judith'
                            ]
                        ,
                        3: 
                           ['monica',
                            'ana',
                            'judit'
                            ]
                        ,
                        4: 
                           ['judit',
                            'erola',
                            'joan'
                            ]
                        }),

                     'dv': ns({
                        1: 
                           ['ana',
                            'judith',
                            'jordi'
                            ]
                        ,
                        2: 
                           ['jordi',
                            'ana',
                            'judith'
                            ]
                        ,
                        3: 
                           ['victor',
                            'carles',
                            'yaiza'
                            ]
                        ,
                        4: 
                           ['marta',
                            'victor',
                            'silvia'
                            ]
                        }),
                    }),
                  
                  'hores': [
                    '09:00',
                    '10:15',
                    '11:30',
                    '12:45',
                    '14:00'
                  ],
                  'torns': [
                    'T1',
                    'T2',
                    'T3'
                  ],
                  'colors': ns(
                    {'ana':    '98bdc0',
                     'marc':   'fbe8bc',
                     'eduard': 'd8b9c5',
                     'pere':   '8f928e',
                     'david':  'ffd3ac',
                     'aleix':  'eed0eb',
                     'carles': 'c98e98',
                     'marta':  'eb9481',
                     'monica': '7fada0',
                     'yaiza':  '90cdb9',
                     'erola':  '8789c8',
                     'manel':  '88dfe3',
                     'tania':  'c8abf4',
                     'judit':  'e781e8',
                     'silvia': '8097fa',
                     'joan':   'fae080',
                     'ana':    '98bdc0',
                     'victor': 'ff3333',
                     'jordi':  'ff9999',
                    }
                  ),
                  'extensions': ns(
                    {'ana':    3181,
                     'marta':  3040,
                     'monica': 3041,
                     'manel':  3042,
                     'erola':  3043,
                     'yaiza':  3044,
                     'eduard': 3045,
                     'marc':   3046,
                     'judit':  3047,
                     'judith': 3057,
                     'tania':  3048,
                     'carles': 3051,
                     'pere':   3052,
                     'aleix':  3053,
                     'david':  3054,
                     'silvia': 3055,
                     'joan':   3056,
                     'ana':    3181,
                     'victor': 3182,
                     'jordi':  3183, 
                    }
                  ),
                  'noms': ns({
                     'silvia': u'Sílvia',
                     'monica': u'Mònica',
                     'tania':  u'Tània',
                     'cesar':  u'César',
                     'victor': u'Víctor',
                  }),
                  'setmana': datetime.date(
                    2016,7,11),
                  'companys': [
                    'aleix',
                    'ana',
                    'carles',
                    'david',
                    'eduard',
                    'erola',
                    'joan',
                    'jordi',
                    'judit',
                    'judith',
                    'manel',
                    'marc',
                    'marta',
                    'monica',
                    'pere',
                    'silvia',
                    'tania',
                    'victor',
                    'yaiza'
                  ]
                },
            )
        )
    
    def test_yamlSolution_completeHolidaysTimetable(self):
        h=HtmlGenFromSolution(
            config=self.ns("""\
        nTelefons: 3
        diesCerca: ['dx','dm','dj', 'dl', 'dv',] # Els mes conflictius davant
        diesVisualitzacio: ['dl','dm','dx','dj','dv']

        hores:  # La darrera es per tancar
        - '09:00'
        - '10:15'
        - '11:30'
        - '12:45'
        - '14:00'
        randomColors: false # Si vols generar colors aleatoris o fer cas de 'colors'
        colors:
           marc:   'fbe8bc'
           eduard: 'd8b9c5'
           pere:   '8f928e'
           david:  'ffd3ac'
           aleix:  'eed0eb'
           carles: 'c98e98'
           marta:  'eb9481'
           monica: '7fada0'
           yaiza:  '90cdb9'
           erola:  '8789c8'
           manel:  '88dfe3'
           tania:  'c8abf4'
           judit:  'e781e8'
           silvia: '8097fa'
           joan:   'fae080'
           ana:    '98bdc0'
           victor: 'ff3333'
           jordi: 'ff9999' 
        extensions:
           marta:  3040
           monica: 3041
           manel:  3042
           erola:  3043
           yaiza:  3044
           eduard: 3045
           marc:   3046
           judit:  3047
           judith: 3057
           tania:  3048
           carles: 3051
           pere:   3052
           aleix:  3053
           david:  3054
           silvia: 3055
           joan:   3056
           ana:    3181
           victor: 3182
           jordi:  3183 
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
            """),
            solution={
                ('dl',0,0):'jordi',
                ('dl',0,1):'marta',
                ('dl',0,2):'tania',
                ('dl',1,0):'tania',
                ('dl',1,1):'yaiza',
                ('dl',1,2):'silvia',
                ('dl',2,0):'judith',
                ('dl',2,1):'pere',
                ('dl',2,2):'ana',
                ('dl',3,0):'ana',
                ('dl',3,1):'judith',
                ('dl',3,2):'erola',
                ('dm',0,0):'pere',
                ('dm',0,1):'jordi',
                ('dm',0,2):'victor',
                ('dm',1,0):'carles',
                ('dm',1,1):'victor',
                ('dm',1,2):'ana',
                ('dm',2,0):'joan',
                ('dm',2,1):'silvia',
                ('dm',2,2):'eduard',
                ('dm',3,0):'david',
                ('dm',3,1):'joan',
                ('dm',3,2):'monica',
                ('dx',0,0):'yaiza',
                ('dx',0,1):'monica',
                ('dx',0,2):'pere',
                ('dx',1,0):'erola',
                ('dx',1,1):'joan',
                ('dx',1,2):'marta',
                ('dx',2,0):'victor',
                ('dx',2,1):'eduard',
                ('dx',2,2):'jordi',
                ('dx',3,0):'eduard',
                ('dx',3,1):'david',
                ('dx',3,2):'victor',
                ('dj',0,0):'judith',
                ('dj',0,1):'jordi',
                ('dj',0,2):'carles',
                ('dj',1,0):'silvia',
                ('dj',1,1):'tania',
                ('dj',1,2):'judith',
                ('dj',2,0):'monica',
                ('dj',2,1):'ana',
                ('dj',2,2):'judit',
                ('dj',3,0):'judit',
                ('dj',3,1):'erola',
                ('dj',3,2):'joan',
                },
            date=datetime.datetime.strptime(
                '2016-07-11','%Y-%m-%d').date(),
            companys= [
                'aleix',
                'ana',
                'carles',
                'david',
                'eduard',
                'erola',
                'joan',
                'jordi',
                'judit',
                'judith',
                'manel',
                'marc',
                'marta',
                'monica',
                'pere',
                'silvia',
                'tania',
                'victor',
                'yaiza'
            ]
        )

        self.assertEqual(
            h.getYaml(), 
            ns(
                {'timetable': ns(
                    {'dl': ns(
                        {1: 
                            ['jordi',
                             'marta',
                             'tania'
                             ]
                        ,
                        2: 
                            ['tania',
                             'yaiza',
                             'silvia'
                             ]
                        ,
                        3: 
                            ['judith',
                             'pere',
                             'ana'
                             ]
                        ,
                        4: 
                            ['ana',
                             'judith',
                             'erola'
                             ]
                        }),
                     'dm': ns({
                        1: 
                           ['pere',
                            'jordi',
                            'victor'
                            ]
                        ,
                        2: 
                           ['carles',
                            'victor',
                            'ana'
                            ]
                        ,
                        3: 
                           ['joan',
                            'silvia',
                            'eduard'
                            ]
                        ,
                        4: 
                           ['david',
                            'joan',
                            'monica'
                            ]
                        }),

                     'dx': ns({
                        1: 
                           ['yaiza',
                            'monica',
                            'pere'
                            ]
                        ,
                        2: 
                           ['erola',
                            'joan',
                            'marta'
                            ]
                        ,
                        3: 
                           ['victor',
                            'eduard',
                            'jordi'
                            ]
                        ,
                        4: 
                           ['eduard',
                            'david',
                            'victor'
                            ]
                        }),
                     
                     'dj': ns({
                        1: 
                           ['judith',
                            'jordi',
                            'carles'
                            ]
                        ,
                        2: 
                           ['silvia',
                            'tania',
                            'judith'
                            ]
                        ,
                        3: 
                           ['monica',
                            'ana',
                            'judit'
                            ]
                        ,
                        4: 
                           ['judit',
                            'erola',
                            'joan'
                            ]
                        }),

                     'dv': ns({
                        1: 
                           ['festiu',
                            'festiu',
                            'festiu'
                            ]
                        ,
                        2: 
                           ['festiu',
                            'festiu',
                            'festiu'
                            ]
                        ,
                        3: 
                           ['festiu',
                            'festiu',
                            'festiu'
                            ]
                        ,
                        4: 
                           ['festiu',
                            'festiu',
                            'festiu'
                            ]
                        }),
                    }),
                  
                  'hores': [
                    '09:00',
                    '10:15',
                    '11:30',
                    '12:45',
                    '14:00'
                  ],
                  'torns': [
                    'T1',
                    'T2',
                    'T3'
                  ],
                  'colors': ns(
                    {'ana':    '98bdc0',
                     'marc':   'fbe8bc',
                     'eduard': 'd8b9c5',
                     'pere':   '8f928e',
                     'david':  'ffd3ac',
                     'aleix':  'eed0eb',
                     'carles': 'c98e98',
                     'marta':  'eb9481',
                     'monica': '7fada0',
                     'yaiza':  '90cdb9',
                     'erola':  '8789c8',
                     'manel':  '88dfe3',
                     'tania':  'c8abf4',
                     'judit':  'e781e8',
                     'silvia': '8097fa',
                     'joan':   'fae080',
                     'ana':    '98bdc0',
                     'victor': 'ff3333',
                     'jordi':  'ff9999',
                    }
                  ),
                  'extensions': ns(
                    {'ana':    3181,
                     'marta':  3040,
                     'monica': 3041,
                     'manel':  3042,
                     'erola':  3043,
                     'yaiza':  3044,
                     'eduard': 3045,
                     'marc':   3046,
                     'judit':  3047,
                     'judith': 3057,
                     'tania':  3048,
                     'carles': 3051,
                     'pere':   3052,
                     'aleix':  3053,
                     'david':  3054,
                     'silvia': 3055,
                     'joan':   3056,
                     'ana':    3181,
                     'victor': 3182,
                     'jordi':  3183, 
                    }
                  ),
                  'noms': ns({
                     'silvia': u'Sílvia',
                     'monica': u'Mònica',
                     'tania':  u'Tània',
                     'cesar':  u'César',
                     'victor': u'Víctor',
                  }),
                  'setmana': datetime.date(
                    2016,7,11),
                  'companys': [
                    'aleix',
                    'ana',
                    'carles',
                    'david',
                    'eduard',
                    'erola',
                    'joan',
                    'jordi',
                    'judit',
                    'judith',
                    'manel',
                    'marc',
                    'marta',
                    'monica',
                    'pere',
                    'silvia',
                    'tania',
                    'victor',
                    'yaiza'
                  ]
                },
            )
        )

    def test_htmlTable_oneslot(self):
        h=HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
            timetable:
              dl:
                1:
                - ana
            hores:
            - 09:00
            - '10:15'
            torns:
            - T1
            colors:
              ana: 98bdc0
            extensions:
              ana: 3181
            noms: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            """)
        )

        self.assertMultiLineEqual(
            h.htmlTable(), 
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=1>dl</th></tr>\n"""
            u"""<tr><td></td><th>T1</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")
        
    def test_htmlTable_twoTelephonesOneTurnOneDay(self):
        h=HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
            timetable:
              dl:
                1:
                - ana
                - jordi
            hores:
            - 09:00
            - '10:15'
            torns:
            - T1
            - T2
            colors:
              ana: 98bdc0
              jordi: ff9999
            extensions:
              ana: 3181
              jordi: 3183
            noms: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            """)
        )
        self.assertMultiLineEqual(
            h.htmlTable(),
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=2>dl</th></tr>\n"""
            u"""<tr><td></td><th>T1</th><th>T2</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")
        
    def test_htmlTable_twoTelephonesTwoTurnsOneDay(self):
        h=HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
            timetable:
              dl:
                1:
                - ana
                - jordi
                2:
                - jordi
                - aleix
            hores:
            - 09:00
            - '10:15'
            - '11:30'
            torns:
            - T1
            - T2
            colors:
              ana: 98bdc0
              jordi: ff9999
            extensions:
              ana: 3181
              jordi: 3183
            noms: # Els que no només cal posar en majúscules
               silvia: Sílvia
               monica: Mònica
               tania: Tània
               cesar: César
               victor: Víctor            
            """)
        )
        self.assertMultiLineEqual(
            h.htmlTable(),
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=2>dl</th></tr>\n"""
            u"""<tr><td></td><th>T1</th><th>T2</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>10:15-11:30</th>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")

    def test_htmlTable_twoTelephonesTwoTurnsTwoDays(self):
        self.maxDiff = None
        h=HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
            timetable:
              dl:
                1:
                - ana
                - jordi
                2:
                - jordi
                - aleix
              dm:
                1:
                - victor
                - marta
                2:
                - ana
                - victor
            hores:
            - 09:00
            - '10:15'
            - '11:30'
            torns:
            - T1
            - T2
            colors:
              ana: 98bdc0
              jordi: ff9999
            extensions:
              ana: 3181
              jordi: 3183
            noms: # Els que no només cal posar en majúscules
               silvia: Sílvia
               monica: Mònica
               tania: Tània
               cesar: César
               victor: Víctor
            """)
        )
        self.assertMultiLineEqual(
            h.htmlTable(),
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=2>dl</th><td></td><th colspan=2>dm</th>"""
            u"""</tr>\n"""
            u"""<tr><td></td><th>T1</th><th>T2</th><td></td><th>T1</th><th>T2</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='marta'>Marta</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>10:15-11:30</th>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")
    
    def test_htmlTable_manyTelephonesmanyTurnsmanyDays(self):
        self.maxDiff = None
        h=HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
            timetable:
              dl:
                1:
                - ana
                - jordi
                - pere
                2:
                - jordi
                - aleix
                - pere
                3:
                - carles
                - joan
                - eduard
                4:
                - yaiza
                - joan
                - eduard
              dm:
                1:
                - victor
                - marta
                - ana
                2:
                - ana
                - victor
                - marta
                3:
                - silvia
                - eduard
                - monica
                4:
                - david
                - silvia
                - marc
              dx:
                1:
                - aleix
                - pere
                - yaiza
                2:
                - pere
                - aleix
                - carles
                3:
                - marc
                - judit
                - victor
                4:
                - david
                - silvia
                - victor
              dj:
                1:
                - judit
                - jordi
                - carles
                2:
                - joan
                - silvia
                - jordi
                3:
                - monica
                - marc
                - tania
                4:
                - tania
                - monica
                - marc
              dv:
                1:
                - marta
                - victor
                - judit
                2:
                - victor
                - joan
                - judit
                3:
                - eduard
                - yaiza
                - jordi
                4:
                - jordi
                - carles
                - aleix
            hores:
            - 09:00
            - '10:15'
            - '11:30'
            - '12:45'
            - '14:00'
            torns:
            - T1
            - T2
            - T3
            noms: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            """)
        )
        self.assertMultiLineEqual(
            h.htmlTable(),
            u"""<table>\n"""
            u"""<tr><td></td><th colspan=3>dl</th>"""
            u"""<td></td><th colspan=3>dm</th>"""
            u"""<td></td><th colspan=3>dx</th>"""
            u"""<td></td><th colspan=3>dj</th>"""
            u"""<td></td><th colspan=3>dv</th></tr>\n"""
            u"""<tr>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""<td></td><th>T1</th><th>T2</th><th>T3</th>"""
            u"""</tr>\n"""
            u"""<tr><th>09:00-10:15</th>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='pere'>Pere</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='marta'>Marta</td>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""<td class='pere'>Pere</td>\n"""
            u"""<td class='yaiza'>Yaiza</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='judit'>Judit</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='carles'>Carles</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='marta'>Marta</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='judit'>Judit</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>10:15-11:30</th>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""<td class='pere'>Pere</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='ana'>Ana</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='marta'>Marta</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='pere'>Pere</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""<td class='carles'>Carles</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='joan'>Joan</td>\n"""
            u"""<td class='silvia'>Sílvia</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td class='joan'>Joan</td>\n"""
            u"""<td class='judit'>Judit</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>11:30-12:45</th>\n"""
            u"""<td class='carles'>Carles</td>\n"""
            u"""<td class='joan'>Joan</td>\n"""
            u"""<td class='eduard'>Eduard</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='silvia'>Sílvia</td>\n"""
            u"""<td class='eduard'>Eduard</td>\n"""
            u"""<td class='monica'>Mònica</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='marc'>Marc</td>\n"""
            u"""<td class='judit'>Judit</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='monica'>Mònica</td>\n"""
            u"""<td class='marc'>Marc</td>\n"""
            u"""<td class='tania'>Tània</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='eduard'>Eduard</td>\n"""
            u"""<td class='yaiza'>Yaiza</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""</tr>\n"""
            u"""<tr><th>12:45-14:00</th>\n"""
            u"""<td class='yaiza'>Yaiza</td>\n"""
            u"""<td class='joan'>Joan</td>\n"""
            u"""<td class='eduard'>Eduard</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='david'>David</td>\n"""
            u"""<td class='silvia'>Sílvia</td>\n"""
            u"""<td class='marc'>Marc</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='david'>David</td>\n"""
            u"""<td class='silvia'>Sílvia</td>\n"""
            u"""<td class='victor'>Víctor</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='tania'>Tània</td>\n"""
            u"""<td class='monica'>Mònica</td>\n"""
            u"""<td class='marc'>Marc</td>\n"""
            u"""<td>&nbsp;</td>\n"""
            u"""<td class='jordi'>Jordi</td>\n"""
            u"""<td class='carles'>Carles</td>\n"""
            u"""<td class='aleix'>Aleix</td>\n"""
            u"""</tr>\n"""
            u"""</table>""")
    def test_htmlExtension_oneExtension(self):
        h = HtmlGenFromYaml(self.ns("""\
            extensions:
               marta:  3040
            noms:
               cesar: César
               """)
        )
        self.assertMultiLineEqual(h.htmlExtensions(),
        """<h3>Extensions</h3>\n""" 
        """<div class="extensions">\n"""
        """<div class="extension marta">Marta<br/>3040</div>\n"""
        """</div>""")
    
    def test_htmlExtension_twoExtensions(self):
        h = HtmlGenFromYaml(self.ns("""\
            extensions:
               marta:  3040
               aleix:  3053
            noms:
               cesar: César
               """)
        )
        self.assertMultiLineEqual(h.htmlExtensions(),
        """<h3>Extensions</h3>\n""" 
        """<div class="extensions">\n"""
        """<div class="extension aleix">Aleix<br/>3053</div>\n"""
        """<div class="extension marta">Marta<br/>3040</div>\n"""
        """</div>""")

    def test_htmlExtension_noExtensions(self):
        h = HtmlGenFromYaml(self.ns("""\
            noms:
               cesar: César
               """)
        )
        self.assertMultiLineEqual(h.htmlExtensions(),
        """<h3>Extensions</h3>\n""" 
        """<div class="extensions">\n"""
        """</div>""")

    def test_htmlHeader_properSetmana(self):
        h = HtmlGenFromYaml(self.ns("""\
            setmana: 2016-07-25
                """)
        )
        self.assertMultiLineEqual(h.htmlSetmana(),"""<h1>Setmana 2016-07-25</h1>""")

    def test_htmlHeader_noSetmana(self):
        h = HtmlGenFromYaml(self.ns("""\
            noms:
               cesar: César
                """)
        )
        self.assertMultiLineEqual(h.htmlSetmana(),"""<h1>Setmana ???</h1>""")

    def test_htmlColors_oneColor(self):
        h = HtmlGenFromYaml(self.ns("""\
            colors:
               marc: fbe8bc
            companys:
            - marc
                """)
        )
        self.assertMultiLineEqual(
            h.htmlColors(),
            """.marc { background-color: #fbe8bc; }"""
        )

    def test_htmlColors_forceRandomColor(self):
        h = HtmlGenFromYaml(self.ns("""\
            colors:
               marc: fbe8bc
            randomColors: true
            companys:
            - marc
                """)
        )
        colors = h.htmlColors()
        self.assertNotEqual(
            colors,
            """.marc { background-color: #fbe8bc; }"""
        )

        self.assertRegexpMatches(parse(
            """.marc {{ background-color: {} }}""",
                  colors
                  )[0],
            '#[0-9a-f]{6};'
        )
    
    def test_htmlColors_randomColor(self):
        h = HtmlGenFromYaml(self.ns("""\
            companys:
            - cesar
                """)
        )
        self.assertRegexpMatches(parse(
            """.cesar {{ background-color: {} }}""",
                  h.htmlColors()
                  )[0],
            '#[0-9a-f]{6};'
        )

    def test_htmlParse_completeHtml(self):
       self.maxDiff = None
       h = HtmlGenFromYaml(self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - jordi
            - pere
            2:
            - jordi
            - aleix
            - pere
            3:
            - carles
            - joan
            - eduard
            4:
            - yaiza
            - joan
            - eduard
          dm:
            1:
            - victor
            - marta
            - ana
            2:
            - ana
            - victor
            - marta
            3:
            - silvia
            - eduard
            - monica
            4:
            - david
            - silvia
            - marc
          dx:
            1:
            - aleix
            - pere
            - yaiza
            2:
            - pere
            - aleix
            - carles
            3:
            - marc
            - judit
            - victor
            4:
            - david
            - silvia
            - victor
          dj:
            1:
            - judit
            - jordi
            - carles
            2:
            - joan
            - silvia
            - jordi
            3:
            - monica
            - marc
            - tania
            4:
            - tania
            - monica
            - marc
          dv:
            1:
            - marta
            - victor
            - judit
            2:
            - victor
            - joan
            - judit
            3:
            - eduard
            - yaiza
            - jordi
            4:
            - jordi
            - carles
            - aleix
        hores:
        - 09:00
        - '10:15'
        - '11:30'
        - '12:45'
        - '14:00'
        torns:
        - T1
        - T2
        - T3
        colors:
          marc: fbe8bc
          eduard: d8b9c5
          pere: 8f928e
          david: ffd3ac
          aleix: eed0eb
          carles: c98e98
          marta: eb9481
          monica: 7fada0
          yaiza: 90cdb9
          erola: 8789c8
          manel: 88dfe3
          tania: c8abf4
          judit: e781e8
          silvia: 8097fa
          joan: fae080
          ana: 98bdc0
          victor: ff3333
          jordi: ff9999
          judith: cb8a85
        extensions:
          marta: 3040
          monica: 3041
          manel: 3042
          erola: 3043
          yaiza: 3044
          eduard: 3045
          marc: 3046
          judit: 3047
          judith: 3057
          tania: 3048
          carles: 3051
          pere: 3052
          aleix: 3053
          david: 3054
          silvia: 3055
          joan: 3056
          ana: 3181
          victor: 3182
          jordi: 3183
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        companys:
        - marta
        - monica
        - manel
        - erola
        - yaiza
        - eduard
        - marc
        - judit
        - judith
        - tania
        - carles
        - pere
        - aleix
        - david
        - silvia
        - joan
        - ana
        - victor
        - jordi""")
       )
       self.b2bdatapath = "testcases"
       self.assertB2BEqual(h.htmlParse().encode('utf-8'))
    
    def test_htmlParse_completeHtmlWithHoliday(self):
       self.maxDiff = None
       h = HtmlGenFromYaml(self.ns("""\
        timetable:
          dl:
            1:
            - festiu
            - festiu
            - festiu
            2:
            - festiu
            - festiu
            - festiu
            3:
            - festiu
            - festiu
            - festiu
            4:
            - festiu
            - festiu
            - festiu
          dm:
            1:
            - victor
            - marta
            - ana
            2:
            - ana
            - victor
            - marta
            3:
            - silvia
            - eduard
            - monica
            4:
            - david
            - silvia
            - marc
          dx:
            1:
            - aleix
            - pere
            - yaiza
            2:
            - pere
            - aleix
            - carles
            3:
            - marc
            - judit
            - victor
            4:
            - david
            - silvia
            - victor
          dj:
            1:
            - judit
            - jordi
            - carles
            2:
            - joan
            - silvia
            - jordi
            3:
            - monica
            - marc
            - tania
            4:
            - tania
            - monica
            - marc
          dv:
            1:
            - marta
            - victor
            - judit
            2:
            - victor
            - joan
            - judit
            3:
            - eduard
            - yaiza
            - jordi
            4:
            - jordi
            - carles
            - aleix
        hores:
        - 09:00
        - '10:15'
        - '11:30'
        - '12:45'
        - '14:00'
        torns:
        - T1
        - T2
        - T3
        colors:
          marc: fbe8bc
          eduard: d8b9c5
          pere: 8f928e
          david: ffd3ac
          aleix: eed0eb
          carles: c98e98
          marta: eb9481
          monica: 7fada0
          yaiza: 90cdb9
          erola: 8789c8
          manel: 88dfe3
          tania: c8abf4
          judit: e781e8
          silvia: 8097fa
          joan: fae080
          ana: 98bdc0
          victor: ff3333
          jordi: ff9999
          judith: cb8a85
        extensions:
          marta: 3040
          monica: 3041
          manel: 3042
          erola: 3043
          yaiza: 3044
          eduard: 3045
          marc: 3046
          judit: 3047
          judith: 3057
          tania: 3048
          carles: 3051
          pere: 3052
          aleix: 3053
          david: 3054
          silvia: 3055
          joan: 3056
          ana: 3181
          victor: 3182
          jordi: 3183
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        companys:
        - marta
        - monica
        - manel
        - erola
        - yaiza
        - eduard
        - marc
        - judit
        - judith
        - tania
        - carles
        - pere
        - aleix
        - david
        - silvia
        - joan
        - ana
        - victor
        - jordi""")
       )
       self.b2bdatapath = "testcases"
       self.assertB2BEqual(h.htmlParse().encode('utf-8'))

    def test_asteriskParse_oneTurnOneLocal(self):
       self.maxDiff = None
       h = HtmlGenFromYaml(self.ns("""\
        timetable:
          dl:
            1:
            - ana
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
        setmana: 2016-07-25
        companys:
        - ana
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        """)
       )
       self.assertMultiLineEqual(h.asteriskParse(),
        u"""[entrada_cua_dl_1]\n"""
        u"""member = SIP/217\n"""
       )

    @unittest.skip("Blocking itself")
    def test_asteriskParse_manyTurnOneLocal(self):
       self.maxDiff = None
       h = HtmlGenFromYaml(self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - jordi
            - pere
            2:
            - jordi
            - aleix
            - pere
            3:
            - carles
            - joan
            - eduard
            4:
            - yaiza
            - joan
            - eduard
          dm:
            1:
            - victor
            - marta
            - ana
            2:
            - ana
            - victor
            - marta
            3:
            - silvia
            - eduard
            - monica
            4:
            - david
            - silvia
            - marc
          dx:
            1:
            - aleix
            - pere
            - yaiza
            2:
            - pere
            - aleix
            - carles
            3:
            - marc
            - judit
            - victor
            4:
            - david
            - silvia
            - victor
          dj:
            1:
            - judit
            - jordi
            - carles
            2:
            - joan
            - silvia
            - jordi
            3:
            - monica
            - marc
            - tania
            4:
            - tania
            - monica
            - marc
          dv:
            1:
            - marta
            - victor
            - judit
            2:
            - victor
            - joan
            - judit
            3:
            - eduard
            - yaiza
            - jordi
            4:
            - jordi
            - carles
            - aleix
        hores:
        - 09:00
        - '10:15'
        - '11:30'
        - '12:45'
        - '14:00'
        torns:
        - T1
        - T2
        - T3
        colors:
          marc: fbe8bc
          eduard: d8b9c5
          pere: 8f928e
          david: ffd3ac
          aleix: eed0eb
          carles: c98e98
          marta: eb9481
          monica: 7fada0
          yaiza: 90cdb9
          erola: 8789c8
          manel: 88dfe3
          tania: c8abf4
          judit: e781e8
          silvia: 8097fa
          joan: fae080
          ana: 98bdc0
          victor: ff3333
          jordi: ff9999
          judith: cb8a85
        extensions:
          marta:  206
          monica: 216
          manel:  212
          erola:  213
          yaiza:  205
          eduard: 222
          marc:   203
          judit:  202
          judith: 211
          tania:  208
          carles: 223
          pere:   224
          aleix:  214
          david:  204
          silvia: 207
          joan:   215
          ana:    217
          victor: 218
          jordi:  210
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        companys:
        - marta
        - monica
        - manel
        - erola
        - yaiza
        - eduard
        - marc
        - judit
        - judith
        - tania
        - carles
        - pere
        - aleix
        - david
        - silvia
        - joan
        - ana
        - victor
        - jordi""")
       )
       self.assertMultiLineEqual(h.asteriskParse(),
        u"""[entrada_cua_dl_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/217,1\n"""
        u"""member = SIP/210,2\n"""
        u"""member = SIP/224,3\n"""
        u"""[entrada_cua_dl_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/210,1\n"""
        u"""member = SIP/214,2\n"""
        u"""member = SIP/224,3\n"""
        u"""[entrada_cua_dl_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/223,1\n"""
        u"""member = SIP/215,2\n"""
        u"""member = SIP/222,3\n"""
        u"""[entrada_cua_dl_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/205,1\n"""
        u"""member = SIP/215,2\n"""
        u"""member = SIP/222,3\n"""
        u"""[entrada_cua_dm_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/218,1\n"""
        u"""member = SIP/206,2\n"""
        u"""member = SIP/217,3\n"""
        u"""[entrada_cua_dm_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/217,1\n"""
        u"""member = SIP/218,2\n"""
        u"""member = SIP/206,3\n"""
        u"""[entrada_cua_dm_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/207,1\n"""
        u"""member = SIP/222,2\n"""
        u"""member = SIP/216,3\n"""
        u"""[entrada_cua_dm_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/204,1\n"""
        u"""member = SIP/207,2\n"""
        u"""member = SIP/203,3\n"""
        u"""[entrada_cua_dx_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/214,1\n"""
        u"""member = SIP/224,2\n"""
        u"""member = SIP/205,3\n"""
        u"""[entrada_cua_dx_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/224,1\n"""
        u"""member = SIP/214,2\n"""
        u"""member = SIP/223,3\n"""
        u"""[entrada_cua_dx_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/203,1\n"""
        u"""member = SIP/202,2\n"""
        u"""member = SIP/218,3\n"""
        u"""[entrada_cua_dx_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/204,1\n"""
        u"""member = SIP/207,2\n"""
        u"""member = SIP/218,3\n"""
        u"""[entrada_cua_dj_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/202,1\n"""
        u"""member = SIP/210,2\n"""
        u"""member = SIP/223,3\n"""
        u"""[entrada_cua_dj_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/215,1\n"""
        u"""member = SIP/207,2\n"""
        u"""member = SIP/210,3\n"""
        u"""[entrada_cua_dj_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/216,1\n"""
        u"""member = SIP/203,2\n"""
        u"""member = SIP/208,3\n"""
        u"""[entrada_cua_dj_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/208,1\n"""
        u"""member = SIP/216,2\n"""
        u"""member = SIP/203,3\n"""
        u"""[entrada_cua_dv_1]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/206,1\n"""
        u"""member = SIP/218,2\n"""
        u"""member = SIP/202,3\n"""
        u"""[entrada_cua_dv_2]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/218,1\n"""
        u"""member = SIP/215,2\n"""
        u"""member = SIP/202,3\n"""
        u"""[entrada_cua_dv_3]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/222,1\n"""
        u"""member = SIP/205,2\n"""
        u"""member = SIP/210,3\n"""
        u"""[entrada_cua_dv_4]\n"""
        u"""music=default\n"""
        u"""strategy=linear\n"""
        u"""eventwhencalled=yes\n"""
        u"""timeout=15\n"""
        u"""retry=1\n"""
        u"""wrapuptime=0\n"""
        u"""maxlen = 0\n"""
        u"""; Periodic-announce = /var/lib/asterisk/sounds/bienvenida\n"""
        u"""Periodic-announce-frequency = 15\n"""
        u"""announce-frequency = 0\n"""
        u"""announce-holdtime = no\n"""
        u"""announce-position =no\n"""
        u"""context = bustia_veu\n"""        
        u"""member = SIP/210,1\n"""
        u"""member = SIP/223,2\n"""
        u"""member = SIP/214,3\n"""
       )
    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskSend_oneTurnOneSip(self):
       self.maxDiff = None
       h = HtmlGenFromYaml(self.ns("""\
        timetable:
          dl:
            1:
            - ana
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
        setmana: 2016-07-25
        companys:
        - ana
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        """)
       )
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       queues = pbx.receiveConf()
       self.assertIn('entrada_cua_dl_1',queues)
       queue = queues['entrada_cua_dl_1']
       self.assertIn('members',queue)
       members = queue['members']
       self.assertIn('SIP/217',members)
       
    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskSend_oneTurnManySip(self):
       self.maxDiff = None
       h = HtmlGenFromYaml(self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - jordi
            - pere
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          jordi: 210
          pere: 224
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        """)
       )
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       queues = pbx.receiveConf()
       self.assertIn('entrada_cua_dl_1',queues)
       queue = queues['entrada_cua_dl_1']
       self.assertIn('members',queue)
       members = queue['members']
       self.assertIn('SIP/217',members)
       self.assertIn('SIP/210',members)
       self.assertIn('SIP/224',members)
    
    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskSend_manyTurnManySip(self):
       self.maxDiff = None
       h = HtmlGenFromYaml(self.ns("""\
        timetable:
          dl:
            1:
            - ana
            - jordi
            - pere
            2:
            - pere
            - jordi
          dm:
            1:
            - jordi
            - ana
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          jordi: 210
          pere: 224
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        """)
       )
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       queues = pbx.receiveConf()
       self.assertIn('entrada_cua_dl_1',queues)
       queue = queues['entrada_cua_dl_1']
       self.assertIn('members',queue)
       members = queue['members']
       self.assertIn('SIP/217',members)
       self.assertIn('SIP/210',members)
       self.assertIn('SIP/224',members)
       self.assertIn('entrada_cua_dl_2',queues)
       queue = queues['entrada_cua_dl_2']
       self.assertIn('members',queue)
       members = queue['members']
       self.assertIn('SIP/210',members)
       self.assertIn('SIP/224',members)
       self.assertIn('entrada_cua_dm_1',queues)
       queue = queues['entrada_cua_dm_1']
       self.assertIn('members',queue)
       members = queue['members']
       self.assertIn('SIP/210',members)
       self.assertIn('SIP/217',members)
    
    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskReceive_oneTurnManySip(self):
       self.maxDiff = None
       yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        """
       h = HtmlGenFromYaml(self.ns(yaml))
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       h_asterisk = HtmlGenFromAsterisk(h.getYaml(),pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('timetable',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.timetable)
       self.assertIn(1,h_asterisk_yaml.timetable.dl)
       self.assertEqual(
           set(h_asterisk.getYaml().timetable.dl[1]), 
           set(self.ns(yaml).timetable.dl[1])
       )

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskReceive_manyTurnManySip(self):
       self.maxDiff = None
       yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
          dm:
            1:
            - ana
            - pere
            - jordi
            2:
            - pere
            - jordi
            - ana
        hores:
        - 09:00
        - '10:15'
        - 11:30
        torns:
        - T1
        - T2
        - T3

        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        """
       h = HtmlGenFromYaml(self.ns(yaml))
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       h_asterisk = HtmlGenFromAsterisk(h.getYaml(),pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('timetable',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.timetable)
       self.assertIn(1,h_asterisk_yaml.timetable.dl)
       self.assertEqual(
           set(h_asterisk.getYaml().timetable.dl[1]), 
           set(self.ns(yaml).timetable.dl[1])
       )
       self.assertIn('dm',h_asterisk_yaml.timetable)
       self.assertIn(1,h_asterisk_yaml.timetable.dm)
       self.assertIn(2,h_asterisk_yaml.timetable.dm)
       self.assertEqual(
           set(h_asterisk.getYaml().timetable.dm[1]), 
           set(self.ns(yaml).timetable.dm[1])
       )
       self.assertEqual(
           set(h_asterisk.getYaml().timetable.dm[2]), 
           set(self.ns(yaml).timetable.dm[2])
       )
    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskPause_oneSipPaused(self):
       yaml = """\
        timetable:
          dl:
            1:
            - ana
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        colors:
          ana: 98bdc0
        extensions:
          ana: 217
        setmana: 2016-07-25
        companys:
        - ana
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        """
       h = HtmlGenFromYaml(self.ns(yaml))
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       pbx.pause('dl',1,217)
       h_asterisk = HtmlGenFromAsterisk(h.getYaml(),pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('paused',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.paused)
       self.assertIn(1,h_asterisk_yaml.paused.dl)
       self.assertEqual(h_asterisk_yaml.paused.dl[1],['ana']) 

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskPause_manySipOnePaused(self):
       yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        """
       h = HtmlGenFromYaml(self.ns(yaml))
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       pbx.pause('dl',1,217)
       h_asterisk = HtmlGenFromAsterisk(h.getYaml(),pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('paused',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.paused)
       self.assertIn(1,h_asterisk_yaml.paused.dl)
       self.assertEqual(h_asterisk_yaml.paused.dl[1],['ana']) 

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskResume_oneSipOneResumed(self):
       yaml = """\
        timetable:
          dl:
            1:
            - ana
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        colors:
          ana: 98bdc0
        extensions:
          ana: 217
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        companys:
        - ana
        """
       h = HtmlGenFromYaml(self.ns(yaml))
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       pbx.pause('dl',1,217)
       pbx.resume('dl',1,217)
       h_asterisk = HtmlGenFromAsterisk(h.getYaml(),pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('paused',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.paused)
       self.assertIn(1,h_asterisk_yaml.paused.dl)
       self.assertEqual(h_asterisk_yaml.paused.dl[1],[]) 

    @unittest.skipIf(not config, "depends on pbx")
    def test_asteriskPause_OnePausedOneResumed(self):
       yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
       h = HtmlGenFromYaml(self.ns(yaml))
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       pbx.pause('dl',1,217)
       pbx.pause('dl',1,218)
       pbx.resume('dl',1,217)
       h_asterisk = HtmlGenFromAsterisk(h.getYaml(),pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('paused',h_asterisk_yaml)
       self.assertIn('dl',h_asterisk_yaml.paused)
       self.assertIn(1,h_asterisk_yaml.paused.dl)
       self.assertEqual(h_asterisk_yaml.paused.dl[1],['pere']) 

    def test_nameToExtension_oneSip(self):
        yaml = """\
            timetable:
              dl:
                1:
                - ana
            hores:
            - 09:00
            - '10:15'
            torns:
            - T1
            noms: # Els que no només cal posar en majúscules
              silvia: Sílvia
              monica: Mònica
              tania: Tània
              cesar: César
              victor: Víctor
            colors:
              ana: 98bdc0
            extensions:
              ana: 217
            setmana: 2016-07-25
            companys:
            - ana
            """
        h = HtmlGenFromYaml(self.ns(yaml))
        self.assertEqual(h.nameToExtension('ana'),217)

    def test_nameToExtension_manySip(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        self.assertEqual(h.nameToExtension('ana'),217)
        
    def test_extensionToName_oneSip(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        self.assertEqual(h.extensionToName(217),'ana')
    def test_extensionToName_manySip(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        self.assertEqual(h.extensionToName(217),'ana')

    def test_comparePaused_oneDifference_added(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
        yaml_paused="""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        paused:
          dl:
            1:
            - ana
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        h_paused = HtmlGenFromYaml(self.ns(yaml_paused))
        difference = self.ns("""\
                                dl:
                                  1:
                                    217:    added
                                """)
                                        
        self.assertEqual(h.comparePaused(h_paused),difference)

    def test_comparePaused_oneDifference_removed(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        companys:
        - ana
        - pere
        - jordi
        paused:
          dl:
            1:
            - ana
        """
        yaml_paused="""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        h_paused = HtmlGenFromYaml(self.ns(yaml_paused))
        difference = self.ns("""\
                                dl:
                                  1:
                                    217:    removed
                                """)
                                        
        self.assertEqual(h.comparePaused(h_paused),difference)
    
    def test_comparePaused_oneDifference_changed(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        paused:
          dl:
            1:
            - ana
        """
        yaml_paused="""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        paused:
          dl:
            1:
            - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        h_paused = HtmlGenFromYaml(self.ns(yaml_paused))
        difference = self.ns("""\
                                dl:
                                  1:
                                    217:    removed
                                    219:  added
                                """)
                                        
        self.assertEqual(h.comparePaused(h_paused),difference)

    def test_comparePaused_oneDifference_dynamic(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        paused:
          dl:
            1:
            - ana
        """
        yaml_paused="""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        paused:
          dynamic:
            - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        h_paused = HtmlGenFromYaml(self.ns(yaml_paused))
        difference = self.ns("""\
                                dl:
                                    1:
                                        217: removed
                                dynamic:
                                    219:  added
                                """)
                                        
        self.assertEqual(h.comparePaused(h_paused),difference)
    def test_comparePaused_oneDifference_dynamic(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        companys:
        - ana
        - pere
        - jordi
        paused:
          dynamic:
            - pere
            - ana
        """
        yaml_paused="""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        paused:
          dynamic:
            - jordi
            - ana
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        h_paused = HtmlGenFromYaml(self.ns(yaml_paused))
        difference = self.ns("""\
                                dynamic:
                                    219: added
                                    218: removed
                                """)
                                        
        self.assertEqual(h.comparePaused(h_paused),difference)

    def test_comparePaused_manyDifferences(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
          dm:
            1:
            - ana
            - pere
          dx:
            2:
            - pere
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        paused:
          dl:
            1:
            - ana
          dx:
            2:
            - pere
        """
        yaml_paused="""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        paused:
          dl:
            1:
            - ana
          dm:
            1:
            - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        h_paused = HtmlGenFromYaml(self.ns(yaml_paused))
        difference = self.ns("""\
                                dx:
                                  2:
                                    218:  removed
                                dm:
                                  1:
                                    219: added
                                """)
                                        
        self.assertEqual(h.comparePaused(h_paused),difference)

    @unittest.skipIf(not config, "depends on pbx")
    def test_parsePause_onePaused(self):
       yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
          dm:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
       difference = self.ns("""\
                                dm:
                                  1:
                                    219: added
                                """)
       h = HtmlGenFromYaml(self.ns(yaml))
       asterisk_conf = h.asteriskParse()
       pbx = asterisk.Pbx(Manager(**config.pbx['pbx']),config.pbx['scp'])
       pbx.sendConfNow(asterisk_conf)
       pbx.parsePause(difference)
       h_asterisk = HtmlGenFromAsterisk(h.getYaml(),pbx.receiveConf())
       h_asterisk_yaml = h_asterisk.getYaml()
       self.assertIn('paused',h_asterisk_yaml)
       self.assertIn('dm',h_asterisk_yaml.paused)
       self.assertIn(1,h_asterisk_yaml.paused.dm)
       self.assertEqual(h_asterisk_yaml.paused.dm[1],['jordi']) 
    def test_compareDynamic_oneDifference_added(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
        yaml_dynamic="""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        dynamic:
        - ana
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        h_dynamic = HtmlGenFromYaml(self.ns(yaml_dynamic))
        difference = self.ns("""\
                                217: added
                                """)
                                        
        self.assertEqual(h.compareDynamic(h_dynamic),difference)
    
    def test_compareDynamic_oneDifference_removed(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        dynamic:
        - jordi
        """
        yaml_dynamic="""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        h_dynamic = HtmlGenFromYaml(self.ns(yaml_dynamic))
        difference = self.ns("""\
                                219: removed
                                """)
                                        
        self.assertEqual(h.compareDynamic(h_dynamic),difference)
    
    def test_compareDynamic_manyDifferences(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        companys:
        - ana
        - pere
        - jordi
        dynamic:
        - jordi
        - ana
        """
        yaml_dynamic="""\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        dynamic:
        - jordi
        - pere
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        h_dynamic = HtmlGenFromYaml(self.ns(yaml_dynamic))
        difference = self.ns("""\
                                217: removed
                                218: added
                                """)
                                        
        self.assertEqual(h.compareDynamic(h_dynamic),difference)
    
    def test_getCurrentQueue_getMonday(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        companys:
        - ana
        - pere
        - jordi
        dynamic:
        - jordi
        - ana
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        day, _= h.getCurrentQueue(datetime.datetime(2016,9,12,10,0))
        self.assertEqual(day,'dl')

    def test_getCurrentQueue_getFirstTurn(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
        hores:
        - 09:00
        - '10:15'
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        companys:
        - ana
        - pere
        - jordi
        dynamic:
        - jordi
        - ana
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        _, turn= h.getCurrentQueue(datetime.datetime(2016,9,12,10,0))
        self.assertEqual(turn,1)

    def test_getCurrentQueue_getSecondTurn(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
            2:
            - jordi
            - pere
            - ana

        hores:
        - 09:00
        - '10:15'
        - '11:30'
        
        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor

        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        dynamic:
        - jordi
        - ana
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        _, turn= h.getCurrentQueue(datetime.datetime(2016,9,12,11,29))
        self.assertEqual(turn,2)
    
    def test_getCurrentQueue_getIntermediateTurn(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
            2:
            - jordi
            - pere
            - ana
          dm:
            1:
            - jordi
            - ana
            - pere
            2:
            - jordi
            - pere
            - ana
            3:
            - jordi
            - pere
            - ana

        hores:
        - 09:00
        - '10:15'
        - '11:30'
        - '12:45'

        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        dynamic:
        - jordi
        - ana
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        _, turn= h.getCurrentQueue(datetime.datetime(2016,9,13,11,29))
        self.assertEqual(turn,2)
    
    def test_getCurrentQueue_getInvalidTurn(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
            2:
            - jordi
            - pere
            - ana
          dm:
            1:
            - jordi
            - ana
            - pere
            2:
            - jordi
            - pere
            - ana
            3:
            - jordi
            - pere
            - ana

        hores:
        - 09:00
        - '10:15'
        - '11:30'
        - '12:45'

        noms: # Els que no només cal posar en majúscules
          silvia: Sílvia
          monica: Mònica
          tania: Tània
          cesar: César
          victor: Víctor
        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        dynamic:
        - jordi
        - ana
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        with self.assertRaises(Exception):
            h.getCurrentQueue(datetime.datetime(2016,9,13,7,29))
    
    def test_partialCurrentQueue_getFirstTurn(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi

        hores:
        - 09:00
        - '10:15'
        
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor

        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        self.assertEqual(h.partialCurrentQueue('dl',1),
            (u"""<table>\n"""
             u"""<tr><td></td><th colspan="100%">dl"""
             u"""</th></tr>\n"""
             u"""<tr><td></td><th>T1</th>"""
             u"""<th>T2</th><th>T3</th>"""
             u"""</tr>\n"""
             u"""<tr><th>09:00-10:15</th>\n"""
             u"""<td class='ana'>Ana</td>\n"""
             u"""<td class='pere'>Pere</td>\n"""
             u"""<td class='jordi'>Jordi</td>\n"""
             u"""</tr>\n"""
             u"""</table>"""
             )
        )
    def test_partialCurrentQueue_getSecondTurn(self):
        yaml = """\
        timetable:
          dl:
            1:
            - ana
            - pere
            - jordi
            2:
            - jordi
            - pere
            - ana
        hores:
        - 09:00
        - '10:15'
        - '11:30'
        
        noms: # Els que no només cal posar en majúscules
           silvia: Sílvia
           monica: Mònica
           tania: Tània
           cesar: César
           victor: Víctor

        torns:
        - T1
        - T2
        - T3
        colors:
          pere: 8f928e
          ana: 98bdc0
          jordi: ff9999
        extensions:
          ana: 217
          pere: 218
          jordi: 219
        setmana: 2016-07-25
        companys:
        - ana
        - pere
        - jordi
        """
        h = HtmlGenFromYaml(self.ns(yaml))
        self.assertEqual(h.partialCurrentQueue('dl',2),
            (u"""<table>\n"""
             u"""<tr><td></td><th colspan="100%">dl"""
             u"""</th></tr>\n"""
             u"""<tr><td></td><th>T1</th>"""
             u"""<th>T2</th><th>T3</th>"""
             u"""</tr>\n"""
             u"""<tr><th>10:15-11:30</th>\n"""
             u"""<td class='jordi'>Jordi</td>\n"""
             u"""<td class='pere'>Pere</td>\n"""
             u"""<td class='ana'>Ana</td>\n"""
             u"""</tr>\n"""
             u"""</table>"""
             )
        )
if __name__ == "__main__":

    if '--accept' in sys.argv:
        sys.argv.remove('--accept')
        unittest.TestCase.acceptMode = True
    
    unittest.main()
# vim: ts=4 sw=4 et
