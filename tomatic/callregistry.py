# -*- coding: utf-8 -*-

from datetime import datetime
from pathlib import Path
from yamlns import namespace as ns
from consolemsg import error, step, warn, u
from .claims import Claims

def fillConfigurationInfo():
    return ns.load('config.yaml')

CONFIG = fillConfigurationInfo()

class CallRegistry(object):
    def __init__(self, path=None, size=20):
        self.path = Path(path or CONFIG.my_calls_log)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.size = size

    def _calls(self):
        if not self.path.exists():
            return ns()
        return ns.load(self.path)

    def callsByExtension(self, extension):
        return self._calls().get(extension,[])

    def updateCall(self, extension, fields):
        calls = self._calls()
        extensionCalls = calls.setdefault(extension,[])
        for call in extensionCalls:
            if call.data == fields.data:
                call.update(fields)
                break
        else: # exiting when not found
            extensionCalls.append(fields)

        if self.size:
            extensionCalls=extensionCalls[-self.size:]

        calls.dump(self.path)

    def annotateCall(self, fields):
        from . import persons
        extension = persons.extension(fields.user) or fields.user
        self.updateCall(extension, ns(
            data = fields.date,
            telefon = fields.phone,
            partner = fields.partner,
            contracte = fields.contract,
            motius = fields.reason,
        ))
        self._appendToExtensionDailyInfo('cases', fields)

    def _appendToExtensionDailyInfo(self, prefix, info, date=datetime.today()):
        path = self.path.parent / prefix / '{:%Y%m%d}.yaml'.format(date)
        warn("Saving {}", path)
        dailyInfo = ns()
        if path.exists():
            dailyInfo = ns.load(str(path))
        dailyInfo.setdefault(info.user, []).append(info)
        path.parent.mkdir(parents=True, exist_ok=True)
        dailyInfo.dump(str(path))

    def infoRequestTypes(self):
        try:
            content = Path(CONFIG.info_cases).read_text(encoding='utf8')
        except Exception as e:
            error("Error carregant el tipus d'anotacions de trucades: {}", e)
            return []
        return [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

    def claimTypes(self):
        try:
            content = Path(CONFIG.claims_file).read_text(encoding='utf8')
        except Exception as e:
            error("Error carregant el tipus d'anotacions de trucades: {}", e)
            return []
        return [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

    def importClaimTypes(self, erp):
        claims = Claims(erp)
        erp_claims = claims.get_claims()

        Path(CONFIG.claims_file).write_text(
            '\n'.join([u(x) for x in erp_claims]),
            encoding='utf8',
        )

    def importCrmCategories(self, erp):
        claims = Claims(erp)
        erp_crm_categories = claims.crm_categories()

        Path(CONFIG.info_cases).write_text(
            '\n'.join([u(x) for x in erp_crm_categories]),
            encoding='utf8',
        )

    def claimKeywords(self):
        return ns.load(CONFIG.claims_dict_file)

# vim: ts=4 sw=4 et
