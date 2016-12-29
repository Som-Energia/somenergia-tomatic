# -*- coding: utf-8 -*-

from yamlns import namespace as ns

class MongoConnector(object):
    def __init__(self,client):
        self.client=client
    def saveTimetable(self, tt,force=None):
        if not self.client.find_one(
            {'week':tt.week }
        ) or force:
            self.client.insert_one(
                {'week':tt.week, 'yaml': tt.dump()}
            )
        else:
            raise Exception
    def loadTimetable(self, week):
        response = self.client.find_one(
            {'week': week}
        )
        if response:
            return ns.loads(response['yaml'])
        else:
            raise Exception

class FileProvider(object):
    def __init__(self,directory):
        self.directory=directory
    def find_one(self, week_dict):
        try:
            y = open(
                self.directory+"/"+
                week_dict['week']+
                ".yaml"
            ).read()
        except IOError:
            return None
        return {'week':
            week_dict['week']
            ,'yaml':y}
    def insert_one(self, arg):
        with open(
            self.directory+"/"+
            arg['week']+".yaml",
            "w"
        ) as f:
            f.write(arg['yaml'])

