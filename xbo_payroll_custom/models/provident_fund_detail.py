from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError



class ProvidentFundDetail(models.Model):
    _name = 'provident.fund.detail'
    _rec_name = 'employee_id'

    _description = 'Provident Fund Detail'

    creation_date = fields.Date(string='Creation Date', default=fields.Date.today)
    provident_fund_detail_lines_ids = fields.One2many('provident.fund.detail.lines', 'provident_fund_detail_id',
                                               string="Lines")

    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', default='draft')