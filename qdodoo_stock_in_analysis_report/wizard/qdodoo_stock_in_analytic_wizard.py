# -*- coding: utf-8 -*-
###########################################################################################
#
#    module name for OpenERP
#    Copyright (C) 2015 qdodoo Technology CO.,LTD. (<http://www.qdodoo.com/>).
#
###########################################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class qdodoo_stock_in_analytic_wizard(models.Model):
    """
    入库分析表wizard
    """
    _name = 'qdodoo.stock.in.analytic.wizard'
    _description = 'qdodoo.stock.in.analytic.wizard'

    search_choice = fields.Selection(((1, u'年月'), (2, u'季度'), (3, u'日期'), (4, u'时间段')),
                                     string=u'查询方式', required=True, default=4)
    year = fields.Many2one('account.fiscalyear', string=u'年度')
    month = fields.Selection((('01', u'一月'), ('02', u'二月'), ('03', u'三月'), ('04', u'四月'),
                              ('05', u'五月'), ('06', u'六月'), ('07', u'七月'), ('08', u'八月'), ('09', u'九月'),
                              ('10', u'十月'), ('11', u'十一月'), ('12', u'十二月')), string=u'月份')
    quarter = fields.Selection((('1', u'第一季度'), ('2', u'第二季度'), ('3', u'第三季度'), ('4', u'第四季度')), string=u'季度')
    company_id = fields.Many2one('res.company', string=u'公司')
    partner_id = fields.Many2one('res.partner', string=u'供应商')
    date = fields.Date(string=u'日期')
    start_date = fields.Date(string=u'开始时间')
    end_date = fields.Date(string=u'结束时间')
    product_id = fields.Many2one('product.product', string=u'产品')

    @api.multi
    def action_done(self):
        report_obj = self.env['qdodoo.stock.in.analytic.report']
        model_obj = self.env['ir.model.data']
        result_list = []
        sql_l = """
                select
                    af.id as af_id,
                    ai.date_invoice,
                    ai.period_id as period_id,
                    ail.product_id as product_id,
                    ail.quantity as product_qty,
                    ail.price_unit as price_unit,
                    (ail.price_unit * ail.quantity) as product_amount,
                    po.location_id as location_id,
                    po.partner_id as partner_id,
                    po.company_id as company_id
                from account_invoice_line ail
                    LEFT JOIN purchase_invoice_rel pir ON pir.invoice_id = ail.invoice_id
                    LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id and pir.invoice_id=ai.id
                    LEFT JOIN purchase_order po ON po.id = pir.purchase_id
                    LEFT JOIN account_journal aj ON aj.id = ai.journal_id
                    LEFT JOIN account_period ap ON ap.id = ai.period_id
                    LEFT JOIN account_fiscalyear af ON af.id=ap.fiscalyear_id
                where po.state = 'done' and ai.state != 'cancel'
            """
        if int(self.search_choice) == 1:
            sql_domain = []
            if self.year and not self.month:
                year_list = []
                year_ids = self.env['account.fiscalyear'].search([('name', '=', self.year.name)])
                if year_ids:
                    for i in year_ids:
                        year_list.append(i.id)
                sql_l = sql_l + ' and af.id in %s'
                sql_domain.append(tuple(year_list))
            elif self.year and self.month:
                per_list = []
                per_ids = self.env['account.period'].search(
                    [('name', '=', str(self.month) + '/' + str(self.year.name))])
                if per_ids:
                    for i in per_ids:
                        per_list.append(i.id)
                    sql_domain.append(tuple(per_list))
                    sql_l = sql_l + ' and ap.id in %s'
            if self.product_id:
                sql_l = sql_l + ' and ail.product_id = %s'
                sql_domain.append(self.product_id.id)
            if self.partner_id:
                sql_l = sql_l + ' and ai.partner_id = %s'
                sql_domain.append(self.partner_id.id)
            if self.company_id and self.company_id.name != u'惠美集团':
                sql_l = sql_l + ' and ai.company_id=%s'
                sql_domain.append(self.company_id.id)
            sql = sql_l % tuple(sql_domain)
            self.env.cr.execute(sql)
            res = self.env.cr.fetchall()
            if res:
                for i in res:
                    data = {
                        'year': i[0],
                        'date': i[1],
                        'product_id': i[3],
                        'product_qty': i[4],
                        'price_unit': i[5],
                        'product_amount': i[6],
                        'location_id': i[7],
                        'company_id': i[9],
                        'partner_id': i[8]
                    }
                    cre_obj = report_obj.create(data)
                    result_list.append(cre_obj.id)
            if result_list:
                vie_model, view_id = model_obj.get_object_reference('qdodoo_stock_in_analysis_report',
                                                                    'qdodoo_stock_in_analytic_report1')
                view_model, search_id = model_obj.get_object_reference('qdodoo_stock_in_analysis_report',
                                                                       'qdodoo_stock_in_analytic_search1')
                return {
                    'name': _('入库分析表'),
                    'view_type': 'form',
                    "view_mode": 'tree',
                    'res_model': 'qdodoo.stock.in.analytic.report',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', result_list)],
                    'views': [(view_id, 'tree')],
                    'view_id': [view_id],
                    'search_view_id': [search_id]
                }
        elif int(self.search_choice) == 2:
            per_obj = self.env['account.period']
            if not self.year and not self.quarter:
                if self.company_id and self.company_id.name != u'惠美集团':
                    year_list = self.env['account.fiscalyear'].search([('company_id', '=', self.company_id.id)])
                else:
                    year_list = self.env['account.fiscalyear'].search([])
            elif self.year and not self.quarter:
                if self.company_id and self.company_id.name != u'惠美集团':
                    year_list = self.env['account.fiscalyear'].search(
                        [('name', '=', self.year.name), ('company_id', '=', self.company_id.id)])
                else:
                    year_list = self.env['account.fiscalyear'].search([('name', '=', self.year.name)])
            elif not self.year and self.quarter:
                if self.company_id and self.company_id.name != u'惠美集团':
                    year_list = self.env['account.fiscalyear'].search(
                        [('name', '=', self.year.name), ('company_id', '=', self.company_id.id)])
                else:
                    year_list = self.env['account.fiscalyear'].search([('name', '=', self.year.name)])
            else:
                if self.company_id and self.company_id.name != u'惠美集团':
                    year_list = self.env['account.fiscalyear'].search(
                        [('name', '=', self.year.name), ('company_id', '=', self.company_id.id)])
                else:
                    year_list = self.env['account.fiscalyear'].search([('name', '=', self.year.name)])
            if year_list:
                name_dict = {}
                for i in year_list:
                    if int(self.quarter) == 1:
                        p_list = []
                        name_list = []
                        name_list.append('01' + '/' + str(i.name))
                        name_list.append('02' + '/' + str(i.name))
                        name_list.append('03' + '/' + str(i.name))
                        per_ids = per_obj.search([('name', 'in', name_list), ('fiscalyear_id', '=', i.id)])
                        if per_ids:
                            for p in per_ids:
                                p_list.append(p.id)
                        name_dict[(str(i.name) + "第一季度", i.id)] = p_list
                    elif int(self.quarter) == 2:
                        p_list = []
                        name_list = []
                        name_list.append('04' + '/' + str(i.name))
                        name_list.append('05' + '/' + str(i.name))
                        name_list.append('06' + '/' + str(i.name))
                        per_ids = per_obj.search([('name', 'in', name_list), ('fiscalyear_id', '=', i.id)])
                        if per_ids:
                            for p in per_ids:
                                p_list.append(p.id)
                        name_dict[(str(i.name) + "第二季度", i.id)] = p_list
                    elif int(self.quarter) == 3:
                        p_list = []
                        name_list = []
                        name_list.append('07' + '/' + str(i.name))
                        name_list.append('08' + '/' + str(i.name))
                        name_list.append('09' + '/' + str(i.name))
                        per_ids = per_obj.search([('name', 'in', name_list), ('fiscalyear_id', '=', i.id)])
                        if per_ids:
                            for p in per_ids:
                                p_list.append(p.id)
                        name_dict[(str(i.name) + "第三季度", i.id)] = p_list
                    elif int(self.quarter) == 4:
                        p_list = []
                        name_list = []
                        name_list.append('10' + '/' + str(i.name))
                        name_list.append('11' + '/' + str(i.name))
                        name_list.append('12' + '/' + str(i.name))
                        per_ids = per_obj.search([('name', 'in', name_list), ('fiscalyear_id', '=', i.id)])
                        if per_ids:
                            for p in per_ids:
                                p_list.append(p.id)
                        name_dict[(str(i.name) + "第四季度", i.id)] = p_list
                    else:
                        p_list1 = []
                        name_list1 = []
                        p_list2 = []
                        name_list2 = []
                        p_list3 = []
                        name_list3 = []
                        p_list4 = []
                        name_list4 = []
                        name_list1.append('01' + '/' + str(i.name))
                        name_list1.append('02' + '/' + str(i.name))
                        name_list1.append('03' + '/' + str(i.name))
                        per_ids1 = per_obj.search([('name', 'in', name_list1), ('fiscalyear_id', '=', i.id)])
                        if per_ids1:
                            for p1 in per_ids1:
                                p_list1.append(p1.id)
                        name_dict[(str(i.name) + "第一季度", i.id)] = p_list1
                        name_list2.append('04' + '/' + str(i.name))
                        name_list2.append('05' + '/' + str(i.name))
                        name_list2.append('06' + '/' + str(i.name))
                        per_ids2 = per_obj.search([('name', 'in', name_list2), ('fiscalyear_id', '=', i.id)])
                        if per_ids2:
                            for p2 in per_ids2:
                                p_list2.append(p2.id)
                        name_dict[(str(i.name) + "第二季度", i.id)] = p_list2
                        name_list3.append('07' + '/' + str(i.name))
                        name_list3.append('08' + '/' + str(i.name))
                        name_list3.append('09' + '/' + str(i.name))
                        per_ids3 = per_obj.search([('name', 'in', name_list3), ('fiscalyear_id', '=', i.id)])
                        if per_ids3:
                            for p3 in per_ids3:
                                p_list3.append(p3.id)
                        name_dict[(str(i.name) + "第三季度", i.id)] = p_list3
                        name_list4.append('10' + '/' + str(i.name))
                        name_list4.append('11' + '/' + str(i.name))
                        name_list4.append('12' + '/' + str(i.name))
                        per_ids4 = per_obj.search([('name', 'in', name_list4), ('fiscalyear_id', '=', i.id)])
                        if per_ids4:
                            for p4 in per_ids4:
                                p_list4.append(p4.id)
                        name_dict[(str(i.name) + "第四季度", i.id)] = p_list4
                for d in name_dict.keys():
                    if name_dict.get(d, []):
                        sql_l = """
                        select
                            af.id as af_id,
                            ai.period_id as period_id,
                            ail.product_id as product_id,
                            ail.quantity as product_qty,
                            ail.price_unit as price_unit,
                            (ail.price_unit * ail.quantity) as product_amount,
                            po.location_id as location_id,
                            po.partner_id as partner_id,
                            po.company_id as company_id
                        from account_invoice_line ail
                            LEFT JOIN purchase_invoice_rel pir ON pir.invoice_id = ail.invoice_id
                            LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id and pir.invoice_id=ai.id
                            LEFT JOIN purchase_order po ON po.id = pir.purchase_id
                            LEFT JOIN account_journal aj ON aj.id = ai.journal_id
                            LEFT JOIN account_period ap ON ap.id = ai.period_id
                            LEFT JOIN account_fiscalyear af ON af.id=ap.fiscalyear_id
                        where po.state = 'done' and ai.state != 'cancel'
                    """
                        sql_domain = []
                        if self.product_id:
                            sql_l = sql_l + ' and ail.product_id = %s'
                            sql_domain.append(self.product_id.id)
                        if self.partner_id:
                            sql_l = sql_l + ' and ai.partner_id = %s'
                            sql_domain.append(self.partner_id.id)
                        p_list = name_dict.get(d)
                        sql_l = sql_l + ' and ai.period_id in %s'
                        sql_domain.append(tuple(p_list))
                        sql = sql_l % tuple(sql_domain)
                        self.env.cr.execute(sql)
                        res = self.env.cr.fetchall()
                        if res:
                            for r in res:
                                data = {
                                    'quarter': d[0],
                                    'partner_id': r[-2],
                                    'product_id': r[2],
                                    'product_qty': r[3],
                                    'price_unit': r[4],
                                    'product_amount': r[5],
                                    'location_id': r[-3],
                                    'company_id': r[-1]
                                }
                                cre_obj = report_obj.create(data)
                                result_list.append(cre_obj.id)
                if result_list:
                    vie_model, view_id = model_obj.get_object_reference(
                        'qdodoo_stock_in_analysis_report',
                        'qdodoo_stock_in_analytic_report2')
                    view_model, search_id = model_obj.get_object_reference('qdodoo_stock_in_analysis_report',
                                                                           'qdodoo_stock_in_analytic_search2')
                    return {
                        'name': _('入库分析表'),
                        'view_type': 'form',
                        "view_mode": 'tree',
                        'res_model': 'qdodoo.stock.in.analytic.report',
                        'type': 'ir.actions.act_window',
                        'domain': [('id', 'in', result_list)],
                        'views': [(view_id, 'tree')],
                        'view_id': [view_id],
                        'search_view_id': [search_id]
                    }
        elif int(self.search_choice) == 3:
            sql_domain = []
            if self.date:
                sql_l = sql_l + " and ai.date_invoice = '%s'"
                sql_domain.append(self.date)
            if self.product_id:
                sql_l = sql_l + ' and ail.product_id = %s'
                sql_domain.append(self.product_id.id)
            if self.partner_id:
                sql_l = sql_l + ' and ai.partner_id = %s'
                sql_domain.append(self.partner_id.id)
            if self.company_id and self.company_id.name != u'惠美集团':
                sql_l = sql_l + ' and ai.company_id = %s'
                sql_domain.append(self.company_id.id)
            sql = sql_l % tuple(sql_domain)
            self.env.cr.execute(sql)
            res = self.env.cr.fetchall()
            if res:
                for i in res:
                    data = {
                        'date': i[1],
                        'product_id': i[3],
                        'product_qty': i[4],
                        'price_unit': i[5],
                        'product_amount': i[6],
                        'location_id': i[7],
                        'company_id': i[9],
                        'partner_id': i[8]
                    }
                    cre_obj = report_obj.create(data)
                    result_list.append(cre_obj.id)
                vie_model, view_id = model_obj.get_object_reference(
                    'qdodoo_stock_in_analysis_report',
                    'qdodoo_stock_in_analytic_report3')
                view_model, search_id = model_obj.get_object_reference('qdodoo_stock_in_analysis_report',
                                                                       'qdodoo_stock_in_analytic_search3')
                return {
                    'name': _('入库分析表'),
                    'view_type': 'form',
                    "view_mode": 'tree',
                    'res_model': 'qdodoo.stock.in.analytic.report',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', result_list)],
                    'views': [(view_id, 'tree')],
                    'view_id': [view_id],
                    'search_view_id': [search_id]
                }
        elif int(self.search_choice) == 4:
            sql_domain = []
            sql_l = sql_l + " and ai.date_invoice >= '%s'"
            sql_domain.append(self.start_date)
            sql_l = sql_l + " and ai.date_invoice <= '%s'"
            sql_domain.append(self.end_date)
            if self.company_id and self.company_id.name != u'惠美集团':
                sql_l = sql_l + ' and ai.company_id = %s'
                sql_domain.append(self.company_id.id)
            if self.product_id:
                sql_l = sql_l + 'and ail.product_id = %s'
                sql_domain.append(self.product_id.id)
            if self.partner_id:
                sql_l = sql_l + ' and ai.partner_id = %s'
                sql_domain.append(self.partner_id.id)
            sql = sql_l % tuple(sql_domain)
            self.env.cr.execute(sql)
            res = self.env.cr.fetchall()
            if res:
                for i in res:
                    data = {
                        'date': i[1],
                        'product_id': i[3],
                        'product_qty': i[4],
                        'price_unit': i[5],
                        'product_amount': i[6],
                        'location_id': i[7],
                        'company_id': i[9],
                        'partner_id': i[8]
                    }
                    cre_obj = report_obj.create(data)
                    result_list.append(cre_obj.id)
                vie_model, view_id = model_obj.get_object_reference(
                    'qdodoo_stock_in_analysis_report',
                    'qdodoo_stock_in_analytic_report3')
                view_model, search_id = model_obj.get_object_reference('qdodoo_stock_in_analysis_report',
                                                                       'qdodoo_stock_in_analytic_search3')
                return {
                    'name': _('入库分析表'),
                    'view_type': 'form',
                    "view_mode": 'tree',
                    'res_model': 'qdodoo.stock.in.analytic.report',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', result_list)],
                    'views': [(view_id, 'tree')],
                    'view_id': [view_id],
                    'search_view_id': [search_id]
                }
