# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date, datetime
from odoo.exceptions import ValidationError


class ProvidentFundProfit(models.TransientModel):
    _name = "provident.fund.profit"
    _description = "Provident Fund Profit"

    date_from = fields.Date(string='Date From', required= True)
    date_to = fields.Date(string='Date To', required= True)
    profit_amount = fields.Float(string='Profit Amount', required= True)

    def action_confirm(self):
        provident_fund_obj = self.env['provident.fund'].search(
            [('date_from', '=', self.date_from), ('date_to', '=', self.date_to),('state', '=', 'done')])


        if provident_fund_obj:
            total_pf = sum(provident_fund_obj.mapped('total_PF_period'))

            for x in provident_fund_obj:
                provident_fund_detail_obj = self.env['provident.fund.detail'].search(
                    [('employee_id', '=', x.employee_id.id), ('department_id', '=', x.department_id.id)])
                if not provident_fund_detail_obj:
                    provident_fund_detail_obj = self.env['provident.fund.detail'].create({
                        'employee_id': x.employee_id.id,
                        'department_id': x.department_id.id,
                        'state':'done'
                    })

                detail_obj = self.env['provident.fund.detail.lines'].search([('date_from','=',x.date_from),('date_to','=',x.date_to),('employee_id','=',x.employee_id.id),('department_id','=',x.department_id.id)])
                if not detail_obj:
                    self.env['provident.fund.detail.lines'].create({
                        'date_from': x.date_from,
                        'date_to': x.date_to,
                        'employee_id': x.employee_id.id,
                        'department_id': x.department_id.id,
                        'payslip_id': x.payslip_id.id,
                        'salary_amount': x.salary_amount,
                        'pf_percentage': x.pf_percentage,
                        'employee_contribution': x.employee_contribution,
                        'employer_contribution': x.employer_contribution,
                        'total_PF_period': x.total_PF_period,
                        'provident_fund_detail_id': provident_fund_detail_obj.id,
                        'profit_share': (x.total_PF_period/total_pf)*self.profit_amount,
                        'closing_balance': x.total_PF_period,
                    })

        else:
            raise ValidationError('No Record Found!')