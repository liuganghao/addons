# -*- coding: utf-8 -*-
###########################################################################################
#
#    module name for OpenERP
#    Copyright (C) 2015 qdodoo Technology CO.,LTD. (<http://www.qdodoo.com/>).
#
###########################################################################################

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
import xlrd, base64

class qdodoo_product_import(models.Model):
    """
        科目导入wizard
    """
    _name = 'qdodoo.product.import'
    _description = 'qdodoo.product.import'

    excel_file = fields.Binary(string=u'文件', required=True)

    @api.multi
    def action_import(self):
        excel_obj = xlrd.open_workbook(file_contents=base64.decodestring(self.excel_file))
        sheets = excel_obj.sheets()
        product_obj = self.env['product.template']
        partner_obj = self.env['product.supplierinfo']
        data_obj = self.env['ir.model.data']
        # 获取所有供应商
        partner_ids = self.env['res.partner'].search([('supplier', '=', True)])
        # 循环所有供应商生成字典{(name,company_id)：id}
        partner_dict = {}
        for partner_id in partner_ids:
            partner_dict[(partner_id.name, partner_id.company_id.id)] = partner_id.id
        # 获取所有的产品分类
        category_ids = self.env['product.category'].search([])
        category_dict = {}
        for category_id in category_ids:
            category_dict[category_id.complete_name.replace(' ', '')] = category_id.id
        # 获取所有的产品公开分类
        category_public_ids = self.env['product.public.category'].search([])
        category_public_dict = {}
        for category_public_id in category_public_ids:
            category_public_dict[category_public_id.complete_name.replace(' ', '')] = category_public_id.id
        # 获取所有用户
        user_ids = self.env['res.users'].search([])
        # 循环所有用户{(name,company):id}
        user_dict = {}
        for user_id in user_ids:
            user_dict[(user_id.name, user_id.company_id.id)] = user_id.id
        # 获取所有公司信息
        company_id_l = self.env.user.company_id.id
        company_ids = self.env['res.company'].search([])
        # 循环所有公司组成字典{name:id}
        company_dict = {}
        for company_id in company_ids:
            company_dict[company_id.name] = company_id.id
        return_list = []
        for sh in sheets:
            for row in range(2, sh.nrows):
                row_n = row + 1
                data = {}
                name = sh.cell(row, 0).value
                sale_ok = sh.cell(row, 1).value
                purchase_ok = sh.cell(row, 2).value
                type = sh.cell(row, 3).value
                category = sh.cell(row, 4).value
                default_code = sh.cell(row, 5).value
                ean_13 = sh.cell(row, 6).value
                list_price = sh.cell(row, 7).value
                standard_price = sh.cell(row, 8).value
                company_name = sh.cell(row, 9).value
                state = sh.cell(row, 10).value
                manager_name = sh.cell(row, 11).value
                loc_rack = sh.cell(row, 12).value
                loc_row = sh.cell(row, 13).value
                loc_case = sh.cell(row, 14).value
                warranty = sh.cell(row, 15).value
                sale_delay = sh.cell(row, 16).value
                volume = sh.cell(row, 17).value
                weight = sh.cell(row, 18).value
                weight_net = sh.cell(row, 19).value
                partner = sh.cell(row, 20).value
                description = sh.cell(row, 21).value
                public_category = sh.cell(row, 22).value
                if not name:
                    raise except_orm(_(u'警告'), _(u'第%s行产品名称未填写') % row_n)
                data['name'] = name
                if sale_ok in ('Y', 'y'):
                    data['sale_ok'] = sale_ok
                if purchase_ok in ('Y', 'y'):
                    data['purchase_ok'] = purchase_ok
                if not type:
                    raise except_orm(_(u'警告'), _(u'第%s行产品类型名称未填写') % row_n)
                data['type'] = type
                if default_code:
                    data['default_code'] = default_code
                    if isinstance(default_code, float):
                        data['default_code'] = str(int(default_code))
                if list_price:
                    if isinstance(list_price, float) or isinstance(list_price, int):
                        data['list_price'] = list_price
                    else:
                        raise except_orm(_(u'警告'), _(u'第%s行标价填写错误') % row_n)
                if standard_price:
                    if isinstance(standard_price, float) or isinstance(standard_price, int):
                        data['standard_price'] = standard_price
                    else:
                        raise except_orm(_(u'警告'), _(u'第%s行成本价填写错误') % row_n)
                if company_name:
                    company_id = company_dict.get(company_name, False)
                    if not company_id:
                        raise except_orm(_(u'警告'), _(u'第%s行公司填写错误') % row_n)
                    company_id_l = company_id
                    data['company_id'] = company_id_l
                if state:
                    if state not in ('draft', 'sellable', 'end', 'obsolete'):
                        raise except_orm(_(u'警告'), _(u'第%s行状态填写错误') % row_n)
                    data['state'] = state
                if manager_name:
                    product_manager = user_dict.get((manager_name, company_id_l), False)
                    if not product_manager:
                        raise except_orm(_(u'警告'), _(u'第%s行产品经理填写错误') % row_n)
                    data['product_manager'] = product_manager
                if loc_rack:
                    data['loc_rack'] = loc_rack
                if loc_row:
                    data['loc_row'] = loc_row
                if loc_case:
                    data['loc_case'] = loc_case
                if warranty:
                    if isinstance(warranty, float) or isinstance(warranty, int):
                        data['warranty'] = warranty
                    else:
                        raise except_orm(_(u'警告'), _(u'第%s行质保填写错误') % row_n)
                if sale_delay:
                    if isinstance(sale_delay, float) or isinstance(sale_delay, int):
                        data['sale_delay'] = sale_delay
                    else:
                        raise except_orm(_(u'警告'), _(u'第%s行客户提前交货周期填写错误') % row_n)
                if volume:
                    if isinstance(volume, float) or isinstance(volume, int):
                        data['volume'] = volume
                    else:
                        raise except_orm(_(u'警告'), _(u'第%s行体积填写错误') % row_n)
                if weight:
                    if isinstance(weight, float) or isinstance(weight, int):
                        data['weight'] = weight
                    else:
                        raise except_orm(_(u'警告'), _(u'第%s行毛重填写错误') % row_n)
                if weight_net:
                    if isinstance(weight_net, float) or isinstance(weight_net, int):
                        data['weight_net'] = weight_net
                    else:
                        raise except_orm(_(u'警告'), _(u'第%s行净重填写错误') % row_n)
                if category:
                    if category.strip() not in category_dict:
                        raise except_orm(_(u'警告'), _(u'第%s行内部分类填写错误') % row_n)
                    data['categ_id'] = category_dict.get(category.strip())
                if public_category:
                    all_public_category_id = []
                    for pca in public_category.split("|"):
                        if pca.strip() not in category_public_dict:
                            raise except_orm(_(u'警告'), _(u'第%s行公开的产品分类填写错误') % row_n)
                        all_public_category_id.append(category_public_dict.get(pca.strip()))
                    data['public_categ_ids'] = [[6, False, all_public_category_id]]
                if description:
                    data['description'] = description
                create_obj = product_obj.create(data)
                create_id = create_obj.id
                return_list.append(create_id)
                if partner:
                    for par in partner.split("|"):
                        partner_list = par.split("/")
                        partner_id_d = partner_dict.get((partner_list[0], company_id_l), False)
                        if not partner_id_d:
                            raise except_orm(_(u'警告'), _(u'第%s行供应商填写错误') % row_n)
                        data2 = {
                            'name': partner_id_d,
                            'min_qty': float(partner_list[1]) or 0,
                            'delay': int(partner_list[2]) or 1,
                            'company_id': company_id_l,
                            'product_tmpl_id': create_id,
                        }
                        partner_obj.create(data2)

        if return_list:
            tree_model, tree_id = data_obj.get_object_reference('product', 'product_template_tree_view')
            form_model, form_id = data_obj.get_object_reference('product', 'product_template_only_form_view')
            return {
                'name': _(u'产品'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'product.template',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', return_list)],
                'views': [(tree_id, 'tree'), (form_id, 'form')],
                'view_id': [tree_id],
            }
        else:
            raise except_orm(_(u'警告'), _(u'导入出错'))
