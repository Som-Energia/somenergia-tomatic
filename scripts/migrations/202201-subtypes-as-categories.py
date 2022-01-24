#!/usr/bin/env python

from erppeek import Client
import dbconfig
from yamlns import namespace as ns
from consolemsg import step, warn, success
from erppeek_wst import ClientWST
import sys

erp = ClientWST(**dbconfig.erppeek)

def loadData(erp, context):
    category_ids = erp.CrmCaseCateg.search([])
    context.categories = [
        ns(c) for c in sorted(
            erp.CrmCaseCateg.read(category_ids, []),
            key=lambda x: x['name']
        )
    ]

    subtypes_ids = erp.GiscedataSubtipusReclamacio.search([])
    context.subtypes = [
        ns(t) for t in sorted(
            erp.GiscedataSubtipusReclamacio.read(subtypes_ids, []),
            key=lambda x: x['name']
        )
    ]

def apply():
    step("Fix double '][' in INFOENERGIA name")
    erp.CrmCaseCateg.write(91, dict(
        name='[INFOENERGIA] Consulta sobre els seus informes',
    ))

    step("Add category codes to existing categories")
    for id, code in ns.loads("""\
        83:  'IN01' # [INFO]  Dubtes informació general (com fer-me soci, com omplir)
        85:  'IN02' # [INFO]  Sóc Soci i vull Convidar. No sóc Soci i vull contractar
        86:  'IN03' # [INFO]  Bo social (com es demana, qui hi pot tenir accés, etc)
        87:  'IN04' # [INFO]  No tinc llum, què faig?
        88:  'OV01' # [OV]  Demanen canvis que els hem de dirigir a l'OV 
        89:  'OV02' # [OV] Problemes amb l'accés a OV (contrassenya, usuari, activació
        90:  'OV03' # [OV] Consultes sobre les seccions (infoenergia i corbes, GkWh, i
        91:  'IE01' # [INFOENERGIA]   Consulta sobre els seus informes
        92:  'FA01' # [FACTURA] Dubtes informació sobre les seves factures 
        93:  'FA02' # [FACTURA]Dubtes informació sobre les lectures - vol donar lectur
        94:  'FA03' # [FACTURA] Info comptadors, lloguer, canvi a telegestió, trifàsic
        95:  'CB01' # [COBRAMENTS] Dubtes informació amb factures impagades i com fer 
        96:  'CB02' # [COBRAMENTS] Informació sobre el tall de subministrament (com to
        97:  'CT01' # [CONTRACTES] Tot tipus de consultes referents a altes d'un nou p
        98:  'CT02' # [CONTRACTES] Tot tipus de consultes referents a baixes d’un punt
        99:  'CT03' # [CONTRACTES] Informació procés contractació, endarreriments, reb
        100: 'CT04' # [CONTRACTES] Informació sobre possible canvi de comer fraudulent
        101: 'CT05' # [CONTRACTES] Quina potència necessito? Info sobre nova tarifa
        102: 'CT06' # [CONTRACTES]Canvi de Titular - Canvi de Pagador. Com es fa, on, 
        103: 'CT07' # [CONTRACTES] Tràmits sobre l’autoconsum (com es fa, documentació
        104: 'EE01' # [ENTITATS I EMPRESES] Informació com contractar administradors d
        105: 'EE02' # [ENTITATS I EMPRESES] Informació sobre tarifa 3.X TD i 6.X TD
        106: 'PR01' # [PROJECTES - GENERACIÓ] Informació sobre les nostres plantes
        107: 'AU01' # [AUTOPRODUCCIÓ] Informació sobre les compres col·lectives, com i
        108: 'AP01' # [APORTACIONS - GKWH] Informació sobre les seves aportacions al G
        109: 'CO01' # [COMUNICACIÓ] Comentar noticies blog, campanyes, newsletter, mai
        110: 'PA01' # [GL - PARTICIPA - AULA POPULAR] Info sobre assemblea, sobre el P
    """).items():
        print("updating {id}: code {code}".format(id=id, code=code))
        erp.CrmCaseCateg.write(id, dict(
            categ_code=code,
        ))

    step("Create a new category for each claim subtype")
    for sub in context.subtypes:
        erp.CrmCaseCateg.create(dict(
            name = sub.desc,
            section_id = sub.default_section[0] if sub.default_section else False,
            categ_code = "R"+sub.name,
        ))


try:
    erp.begin()
    context = ns()

    step("Loading state before (dumped as content-before.yaml)")
    loadData(erp, context)
    context.dump('content-before.yaml')

    apply()

    step("Loading state after (dumped as content-after.yaml)")
    loadData(erp, context)
    context.dump('content-after.yaml')
except:
    warn("Error detected rolling back")
    erp.rollback()
    raise
else:
    if '--apply' in sys.argv:
        success("Applying changes")
        erp.commit()
    else:
        warn("Use --apply to really apply. Rolling back changes.")
        erp.rollback()




