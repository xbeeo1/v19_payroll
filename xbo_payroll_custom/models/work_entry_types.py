from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class WorkEntrytypes(models.Model):
    _name = 'work.entry.types'
    _description = 'Work Entry Types'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'


    name = fields.Char('Name',required=True)
    code = fields.Char('Payroll Code',required=True)

    _sql_constraints = [('code_uniq', 'unique (code)', "This Code already exists!")]


