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
        self.size = size

    def _calls(self, user):
        callregistry = self.path / f'dailycalls/calls-{user}.yaml'
        if not callregistry.exists():
            return ns(calls=[])
        return ns.load(callregistry)


    def callsByUser(self, user):
        return self._calls(user).calls

    def updateCall(self, user, fields):
        calls = self.callsByUser(user)
        callregistry = self.path / f'dailycalls/calls-{user}.yaml'

        for call in calls:
            if call.date == fields.date:
                call.update(fields)
                break
        else: # for else, not typo, when not break
            calls.append(fields)

        if self.size:
            del calls[:-self.size]

        callregistry.parent.mkdir(parents=True, exist_ok=True)
        ns(calls=calls).dump(callregistry)

    def annotateCall(self, fields):
        from . import persons
        self.updateCall(fields.user, ns(
            (key, value)
            for key, value in fields.items()
            if key != 'user' # TODO: To keep the same behavior. Is this needed?
        ))
        self._appendToExtensionDailyInfo('cases', fields)

    def _appendToExtensionDailyInfo(self, prefix, info, date=datetime.today()):
        path = self.path / prefix / '{:%Y%m%d}.yaml'.format(date)
        warn("Saving {}", path)
        dailyInfo = ns()
        if path.exists():
            dailyInfo = ns.load(str(path))
        userInfo = dailyInfo.setdefault(info.user, [])
        for call in userInfo:
            if call.date == info.date:
                call.update(info)
                break
        else:
            userInfo.append(info)
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
