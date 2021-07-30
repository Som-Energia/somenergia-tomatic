# -*- encoding: utf-8 -*-

class CrmCase(object):

    def __init__(self, erp):
        self.erp = erp

    def get_crm_categories(self):
        crm_categories_model = self.erp.model('crm.case.categ')
        all_crm_categories = crm_categories_model.search([])

        crm_categories = []
        for category_id in all_crm_categories:
            category = crm_categories_model.read(
                category_id, ['name']
            )
            categ_name = category.get('name')
            if categ_name.startswith('['):
                crm_categories.append(categ_name)

        return crm_categories


# vim: et ts=4 sw=4