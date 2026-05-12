from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError



class ProvidentFundDetailLine(models.Model):
    _name = 'provident.fund.detail.lines'
    _description = 'Provident Fund Detail Lines'

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    payslip_id = fields.Many2one('hr.payslip', string='Payslip Refernce')
    salary_amount = fields.Float('Salary Amount')
    pf_percentage = fields.Integer(string="PF%")
    employee_contribution = fields.Float('Employee contribution')
    employer_contribution = fields.Float('Employer Contribution')
    total_PF_period = fields.Float('Total PF for the period')
    provident_fund_detail_id = fields.Many2one('provident.fund.detail', string='Provident Fund Details')
    profit_share = fields.Float('Profit Share')
    profit_disbursed = fields.Float('Profit Disbursed')
    profit_disbursed_date = fields.Date(string='Profit Disbursed Date')
    closing_balance = fields.Float('Closing Balance')
