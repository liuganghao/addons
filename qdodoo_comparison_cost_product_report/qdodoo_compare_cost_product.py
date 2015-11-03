# -*- coding: utf-8 -*-
###########################################################################################
#
#    module name for OpenERP
#    Copyright (C) 2015 qdodoo Technology CO.,LTD. (<http://www.qdodoo.com/>).
#
###########################################################################################

from openerp import models, fields, api, _, tools
from openerp.exceptions import except_orm


class qdodoo_compare_product_cost_report(models.Model):
    _name = 'compare.product.cost'
    # mo_name = fields.Char(string=u'生产单号')
    product_id = fields.Many2one('product.product', string=u'产品名称')
    product_qty = fields.Float(digits=(16, 2), string=u'数量')
    location_id = fields.Many2one('stock.location', string=u'库位')
    assistant_id = fields.Many2one('account.analytic.account', string=u'辅助核算')
    actual_amount = fields.Float(digits=(16, 4), string=u'实际金额')
    actual_price = fields.Float(digits=(16, 4), string=u'实际单价')
    theoretical_amount = fields.Float(digits=(16, 4), string=u'理论金额')
    theoretical_price = fields.Float(digits=(16, 4), string=u'理论单价')
    save_amount = fields.Float(digits=(16, 4), string=u'节约金额')
    price_save = fields.Float(digits=(16, 4), string=u'单份节约金额')
    amount_difference_rate = fields.Char(string=u'金额差异率')


class qdodoo_search_compare_product_cost(models.Model):
    _name = 'qdodoo.search.compare.product.cost'

    date_start = fields.Date(string=u'开始时间', required=True)
    date_end = fields.Date(string=u'结束时间', required=True)
    location_id = fields.Many2one('stock.location', required=True)

    @api.multi
    def btn_search(self):
        mrp_obj = self.env['mrp.production']
        if self.date_start and self.date_end:
            datetime_start = self.date_start + " 00:00:01"
            datetime_end = self.date_end + " 23:59:29"
            mrp_ids = mrp_obj.search([('date_planned', '>=', datetime_start), ('state', '=', 'done'),
                                      ('location_dest_id', '=', self.location_id.id)])
            result_ids = []
            product_list1 = []
            product_list2 = []
            actual_amount_dict = {}
            theoretical_amount_dict = {}
            product_num_dict = {}
            if mrp_ids:
                for mrp_id in mrp_ids:
                    product_num_dict[(mrp_id.product_id.id, mrp_id.analytic_account.id)] = product_num_dict.get(
                        (mrp_id.product_id.id, mrp_id.analytic_account.id), 0) + mrp_id.product_qty
                    sql = """
                        select
                            mp.product_id,
                            mp.analytic_account,
                            sm.product_id as product_id_y,
                            sm.price_unit as price_unit,
                            sm.product_uom_qty as product_uom_qty
                        from mrp_production mp
                            LEFT JOIN stock_move sm ON sm.raw_material_production_id = mp.id
                        where mp.id=%s and mp.state='done' and sm.product_uom_qty>0 and mp.date_planned >= '%s' and mp.date_planned <= '%s'
                        group by
                            mp.product_id,mp.analytic_account,sm.product_id,mp.state,mp.date_planned,sm.price_unit,sm.product_uom_qty,sm.raw_material_production_id
                        """ % (mrp_id.id, datetime_start, datetime_end)

                    self.env.cr.execute(sql)
                    result = self.env.cr.fetchall()
                    price_unit_dict = {}
                    if result:
                        for i in result:
                            product_id, analytic_account, product_id_y, price_unit1, product_uom_qty1 = i
                            price_unit_dict[product_id_y] = price_unit1
                            if (product_id, analytic_account) in product_list1:
                                actual_amount_dict[(product_id, analytic_account)] += product_uom_qty1 * price_unit1
                            else:
                                actual_amount_dict[
                                    (product_id, analytic_account)] = product_uom_qty1 * price_unit1
                                product_list1.append((product_id, analytic_account))

                    sql2 = """
                        select
                        mp2.product_id,
                        mp2.analytic_account,
                        mppl.product_id,
                        mppl.product_qty
                        from  mrp_production mp2
                        LEFT JOIN mrp_production_product_line mppl ON mppl.production_id=mp2.id
                        WHERE mp2.id=%s and mp2.date_planned >= '%s' and mp2.date_planned <= '%s'
                        group by mp2.product_id,mp2.analytic_account,mppl.product_id,mppl.product_qty,mp2.id,mp2.date_planned
                    """ % (mrp_id.id, datetime_start, datetime_end)
                    self.env.cr.execute(sql2)
                    result2 = self.env.cr.fetchall()
                    for result_l in result2:
                        product_id, analytic_account, product_id_l, product_qty_l = result_l
                        if (product_id, analytic_account) in product_list2:
                            theoretical_amount_dict[
                                (product_id, analytic_account)] += price_unit_dict.get(product_id_l,
                                                                                       0) * product_qty_l
                        else:
                            theoretical_amount_dict[
                                (product_id, analytic_account)] = price_unit_dict.get(product_id_l,
                                                                                      0) * product_qty_l
                            product_list2.append((product_id, analytic_account))

                for ll in list(set(product_list2 + product_list1)):
                    if theoretical_amount_dict.get(ll, 0) == 0:
                        amount_difference_rate = "0%"
                    else:
                        amount_difference_rate = str(
                            '%.4f' % ((actual_amount_dict.get(ll, 0) - theoretical_amount_dict.get(ll,
                                                                                                   0)) / theoretical_amount_dict.get(
                                ll, 0) * 100)) + "%"
                    data = {
                        'product_id': ll[0],
                        'product_qty': product_num_dict.get(ll, 0),
                        'location_id': self.location_id.id,
                        'assistant_id': ll[1],
                        'actual_amount': actual_amount_dict.get(ll, 0),
                        'actual_price': actual_amount_dict.get(ll, 0) / product_num_dict.get(ll, 0),
                        'theoretical_amount': theoretical_amount_dict.get(ll, 0),
                        'theoretical_price': theoretical_amount_dict.get(ll, 0) / product_num_dict.get(ll, 0),
                        'save_amount': actual_amount_dict.get(ll, 0) - theoretical_amount_dict.get(ll, 0),
                        'price_save': (actual_amount_dict.get(ll, 0) - theoretical_amount_dict.get(ll,
                                                                                                   0)) / product_num_dict.get(
                            ll, 0),
                        'amount_difference_rate': amount_difference_rate
                    }

                    create_obj = self.env['compare.product.cost'].create(data)
                    result_ids.append(create_obj.id)
            view_model, view_id = self.env['ir.model.data'].get_object_reference(
                'qdodoo_comparison_cost_product_report', 'qdodoo_compare_cost_report_tree')
            return {
                'name': (u'产品标准原料成本与实际成本对比汇总表'),
                'view_type': 'form',
                "view_mode": 'tree',
                'res_model': 'compare.product.cost',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', result_ids)],
                'views': [(view_id, 'tree')],
                'view_id': [view_id],
            }
