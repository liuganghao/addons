# -*- coding: utf-8 -*-
# #############################################################################
#
# Copyright (C) 2014 Rainsoft  (<http://www.agilebg.com>)
#    Author:Kevin Kong <kfx2007@163.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _

class hr_payroll_fix(models.Model):
    _name='hr.payslip.line'
    _inherit='hr.payslip.line'

    #employee_id = fields.Many2one('hr.employee',string='Employee',related="slip_id.employee_id")
    #contract_id = fields.Many2one('hr.contract',string='Contract',related="slip_id.contract_id")
