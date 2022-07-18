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
        self.path = Path(path or CONFIG.callinfoPath)
        self.path.mkdir(parents=True, exist_ok=True)
        self.callregistry_path = self.path / 'dailycalls.yaml'
        self.size = size

    def _calls(self):
        if not self.callregistry_path.exists():
            return ns()
        return ns.load(self.callregistry_path)

    def callsByUser(self, user):
        return self._calls().get(user,[])

    def updateCall(self, user, fields):
        calls = self._calls()
        extensionCalls = calls.setdefault(user,[])
        for call in extensionCalls:
            if call.data == fields.data:
                call.update(fields)
                break
        else: # exiting when not found
            extensionCalls.append(fields)

        if self.size:
            extensionCalls=extensionCalls[-self.size:]

        calls.dump(self.callregistry_path)

    def annotateCall(self, fields):
        from . import persons
        self.updateCall(fields.user, ns(
            data = fields.date,
            telefon = fields.phone,
            partner = fields.partner,
            contracte = fields.contract,
            motius = fields.reason,
        ))
        self._appendToExtensionDailyInfo('cases', fields)

    def _appendToExtensionDailyInfo(self, prefix, info, date=datetime.today()):
        path = self.path / prefix / '{:%Y%m%d}.yaml'.format(date)
        warn("Saving {}", path)
        dailyInfo = ns()
        if path.exists():
            dailyInfo = ns.load(str(path))
        dailyInfo.setdefault(info.user, []).append(info)
        path.parent.mkdir(parents=True, exist_ok=True)
        dailyInfo.dump(str(path))

    def _categoriesFile(self):
        return self.path/'categories.yaml'

    def updateAnnotationCategories(self, erp):
        """Takes the topics (crm categories and atc subtypes)"""
        claims = Claims(erp)
        categories = claims.categories()
        self._categoriesFile().write_text(
            categories.dump(),
            encoding='utf-8',
        )

    def annotationCategories(self):
        try:
            return ns.load(self._categoriesFile())
        except Exception as e:
            error(
                "Error carregant categories locals {}\n{}",
                self._categoriesFile(), e
            )
            return ns(
                categories=[],
                sections=[],
            )

    def uploadCases(self, erp, date):
        claims = Claims(erp)
        path = self.path / 'cases' / '{:%Y%m%d}.yaml'.format(date)
        log = self.path / 'cases' / 'logs' / '{:%Y%m%d}.log'.format(date)
        cases = ns()
        if path.exists():
            cases = ns.load(path)

        log.parent.mkdir(parents=True, exist_ok=True)
        import logging
        logging.basicConfig(
            filename=log,
            level=logging.INFO
        )
        logging.info(" Script starts: let's go!")
        case_ids = []
        for personCases in cases.values():
            for case in personCases:
                try:
                    id = claims.create_case(case)
                    case_ids.append(id)
                    logging.info(f" CRM case {id} created.")
                except Exception as e:
                    logging.error(" Something went wrong in {}: {}".format(
                        path,
                        str(e))
                    )
                    logging.error(" CASE: {}".format(case))
        # TODO: Testme!!
        return id




# vim: ts=4 sw=4 et
