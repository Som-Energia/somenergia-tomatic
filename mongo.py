# -*- coding: utf-8 -*-
from yamlns import namespace as ns
class MongoConnector(object):
    def __init__(self,client):
        self.client=client
    def saveTimetable(self, tt,force=None):
        if not self.client.find_one(
            {'week':tt.setmana.strftime(
                '%Y_%m_%d'
            )}
        ) or force:
            self.client.insert_one(
                    {'week':tt.setmana.strftime(
                        '%Y_%m_%d'
                     ), 'yaml': tt.dump()}
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
