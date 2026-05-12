from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class LoanType(models.Model):
    _name = 'loan.type'
    _description = 'Loan Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Name',required=True)
    type = fields.Selection([('advnace', 'Advance'),
                                      ('loan', 'Loan'),
                                      ('pfloan', 'PF Loan'),
                                      ], string='Type', default='advnace', required=True)

    _sql_constraints = [('type_uniq', 'unique (type)', "This Type already exists!")]