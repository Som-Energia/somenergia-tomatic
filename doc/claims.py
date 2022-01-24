#! pyreverse -o png
## Not real classes. Just to generate database diagram with pyreverse

class CrmCaseSection:
    """
    Represents a case handling team

	ATC: Atenció al Client
		ATCI: INFO
		ATCF: FACTURES
		ATCCB: COBRAMENTS
		ATCR: RECLAMACIONS
		ATCC: CONTRACTES
			ATCCA: CONTRACTES - A
			ATCCB: CONTRACTES - B
			ATCCC: CONTRACTES - C
			ATCCM: CONTRACTES - M

    """
    name: str
    code: str # example: ATCCB
    parent: CrmCaseSection

class CrmCaseCategory:
    """
    Categoria pels casos CRM (Taula mestra)
    """
    name: str # example: "[ENTITATS I EMPRESES] Informació com contractar administradors d"
    catec_code: str
    section_id: CrmCaseSection

class CrmCase:
    """
    La base del cas, sigui o no reclamació. Tambe es fa servir per casos ATR.
    """
    name: str
    section_id: CrmCaseSection
    categ_id: CrmCategory
    categ_ids: list(CrmCategory)

class GiscedataSubtipusReclamacio:
    """
    Subtipus de reclamació (Taula mestra)
    """
    default_section: CrmCaseSection
    name: str # example: '003'
    desc: str

class GiscedataAtc(CrmCase):
    """
    S'afegeix al cas CRM si és una reclamació
    """
    subtipus_id: GiscedataSubtipusReclamacio


