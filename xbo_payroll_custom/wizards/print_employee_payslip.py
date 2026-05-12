# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date, datetime
from odoo.exceptions import ValidationError


class PrintEmployeePayslip(models.TransientModel):
    _name = "print.employee.payslip"
    _description = "Provident Fund Profit"

    payslip_date= fields.Date(string='For The Month OF', required= True)

    def action_print(self):
        employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).ids
        if not employee_id:
            raise ValidationError('No Employee Record Found!')
        pay_slips = self.env['hr.payslip'].search(
            [('date_from', '<=', self.payslip_date), ('date_to', '>=', self.payslip_date), ('employee_id', '=', employee_id),
             ('state', '=', 'done')])

        if pay_slips:

            return self.env.ref('om_hr_payroll.action_report_payslip').report_action(pay_slips)
        else:
            raise ValidationError('No Record Found For This Month!')