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

    def _categoriesFile(self):
        return self.path.parent/'categories.yaml'

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
        path = self.path.parent / 'cases' / '{:%Y%m%d}.yaml'.format(date)
        log = self.path.parent / 'cases' / 'logs' / '{:%Y%m%d}.log'.format(date)
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

        for personCases in cases.values():
            for case in personCases:
                try:
                    id = claims.create_case(case)
                    logging.info(f" CRM case {id} created.")
                except Exception as e:
                    logging.error(" Something went wrong in {}: {}".format(
                        path,
                        str(e))
                    )
                    logging.error(" CASE: {}".format(case))




# vim: ts=4 sw=4 et
