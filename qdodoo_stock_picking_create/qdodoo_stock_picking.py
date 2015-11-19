# -*- coding: utf-8 -*-
###########################################################################################
#
#    module name for OpenERP
#    Copyright (C) 2015 qdodoo Technology CO.,LTD. (<http://www.qdodoo.com/>).
#
###########################################################################################

from openerp import models, fields, api
from openerp.osv import osv
from datetime import datetime


class qdodoo_stock_picking(models.Model):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                pack_datas = {
                    'product_id': prod.product_id.id,
                    'product_uom_id': prod.product_uom_id.id,
                    'product_qty': prod.quantity,
                    'package_id': prod.package_id.id,
                    'lot_id': prod.lot_id.id,
                    'location_id': prod.sourceloc_id.id,
                    'location_dest_id': prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date': prod.date if prod.date else datetime.now(),
                    'owner_id': prod.owner_id.id,
                }
                if prod.packop_id:
                    prod.packop_id.with_context(no_recompute=True).write(pack_datas)
                    processed_ids.append(prod.packop_id.id)
                else:
                    pack_datas['picking_id'] = self.picking_id.id
                    packop_id = self.env['stock.pack.operation'].create(pack_datas)
                    processed_ids.append(packop_id.id)
        # Delete the others
        packops = self.env['stock.pack.operation'].search(
            ['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
        packops.unlink()
        self.picking_id.do_transfer()
        #####创建发票
        ite_obj = self.item_ids[0]
        location_model_cus, lo_id = self.env['ir.model.data'].get_object_reference('stock', 'stock_location_suppliers')
        location_model_cus2, lo_id2 = self.env['ir.model.data'].get_object_reference('stock',
                                                                                     'stock_location_customers')
        if self.picking_id.acc:
            if ite_obj.sourceloc_id.id in (lo_id, lo_id2) and self.picking_id.invoice_state == '2binvoiced':
                onshipping_id = self.env['stock.invoice.onshipping'].create({'invoice_date': self.picking_id.date_done})
                onshipping_id.create_invoice()
            elif ite_obj.destinationloc_id.id in (lo_id, lo_id2) and self.picking_id.invoice_state == '2binvoiced':
                onshipping_id = self.env['stock.invoice.onshipping'].create({'invoice_date': self.picking_id.date_done})
                onshipping_id.create_invoice()
            return True
        if ite_obj.sourceloc_id.id in (lo_id, lo_id2) and self.picking_id.invoice_state == '2binvoiced':
            onshipping_id = self.env['stock.invoice.onshipping'].create({'invoice_date': fields.date.today()})
            onshipping_id.create_invoice()
        elif ite_obj.destinationloc_id.id in (lo_id, lo_id2) and self.picking_id.invoice_state == '2binvoiced':
            onshipping_id = self.env['stock.invoice.onshipping'].create({'invoice_date': fields.date.today()})
            onshipping_id.create_invoice()
        return True

class qdodoo_stock_move_inherit_tfs(models.Model):
    _inherit = 'stock.move'

    tfs_price_unit = fields.Float(u'成本价')

    def create(self, cr, uid, valus, context=None):
        product_obj = self.pool.get('product.product')
        users_obj = self.pool.get('res.users')
        if valus.get('product_id'):
            # 获取产品公司id
            company_id = product_obj.browse(cr, uid, valus.get('product_id')).company_id.id
            # 查询该公司的人
            company_uid = users_obj.search(cr, uid, [('company_id','=',company_id)])
            if not company_uid:
                 raise osv.except_osv('错误', "该产品所属的公司没有用户!'")
            else:
                valus['tfs_price_unit'] = product_obj.browse(cr, company_uid[0], valus.get('product_id')).standard_price
        return super(qdodoo_stock_move_inherit_tfs, self).create(cr, uid, valus, context=context)

    def write(self, cr, uid, ids, valus, context=None):
        product_obj = self.pool.get('product.product')
        users_obj = self.pool.get('res.users')
        if valus.get('product_id'):
            # 获取产品公司id
            company_id = product_obj.browse(cr, uid, valus.get('product_id')).company_id.id
            # 查询该公司的人
            company_uid = users_obj.search(cr, uid, [('company_id','=',company_id)])
            if not company_uid:
                 raise osv.except_osv('错误', "该产品所属的公司没有用户!'")
            else:
                valus['tfs_price_unit'] = product_obj.browse(cr, company_uid[0], valus.get('product_id')).standard_price
        return super(qdodoo_stock_move_inherit_tfs, self).write(cr, uid, ids, valus, context=context)
