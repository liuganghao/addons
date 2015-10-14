# -*- coding: utf-8 -*-
###########################################################################################
#
# module name for OpenERP
# Copyright (C) 2015 qdodoo Technology CO.,LTD. (<http://www.qdodoo.com/>).
#
###########################################################################################

from openerp import models, fields, tools


class qdodoo_pop_change(models.Model):
    _name = 'qdodoo.pop.change'
    _auto = False

    # product_id = fields.Many2one('product.product', string=u'产品')
    product_name = fields.Char(string=u'产品')
    delivery_place = fields.Many2one('stock.location', string=u'交货地点')
    date_planned = fields.Datetime(string=u'订单日期')
    unit_price = fields.Float(string=u'单价', digits=(16, 4))
    company_id = fields.Many2one('res.company', string=u'公司')
    partner_id = fields.Many2one('res.partner', string=u'供应商')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'qdodoo_pop_change')
        cr.execute("""
            create or replace view qdodoo_pop_change as (
                select
                    po.id as id,
                    pp.name_template as product_name,
                    po.date_order as date_planned,
                    ail.price_unit as unit_price,
                    po.company_id as company_id,
                    po.partner_id as partner_id,
                    spt.default_location_dest_id as delivery_place
                from account_invoice_line ail
                    LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
                    LEFT JOIN purchase_invoice_rel pir ON pir.invoice_id=ai.id
                    LEFT JOIN purchase_order po ON po.id = pir.purchase_id
                    LEFT JOIN stock_picking_type spt ON po.picking_type_id = spt.id
                    LEFT JOIN product_product pp on pp.id=ail.product_id
                where po.state = 'done' and ai.state != 'cancel'
                group by
                    po.id,pp.name_template,po.date_order,ail.price_unit,spt.default_location_dest_id,po.company_id,po.partner_id,ai.id,ail.invoice_id,pir.invoice_id,pir.purchase_id,po.picking_type_id,spt.id,pp.id,ail.product_id,ai.state
            )
        """)
