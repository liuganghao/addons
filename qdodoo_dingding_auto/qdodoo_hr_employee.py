# encoding:utf-8

from openerp import models, fields


class qdodoo_hr_employee(models.Model):
    _inherit = 'hr.employee'

    e_no = fields.Char(string=u'员工编号')
    dd_user_id = fields.Char(string=u'钉钉userid')
