# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    employee_id = fields.Many2one('hr.employee', string="Employee Refernce")
    payslip_id = fields.Many2one('hr.payslip', string='Payslip Refernce')
