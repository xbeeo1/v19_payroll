# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date, datetime
from odoo.exceptions import ValidationError


class EmplyeePFWizard(models.TransientModel):
    _name = "employee.pf.wizard"
    _description = "Employee Provident Fund Wizard"

    date_from = fields.Date(string='Date From', required= True)
    date_to = fields.Date(string='Date To', required= True)
    department_id = fields.Many2one('hr.department', string='Department')
    employee_id = fields.Many2many(comodel_name="hr.employee", string="Employees" ,domain="[('department_id','=',department_id)]")


    def action_print_payslip(self):
        datas = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_id': self.employee_id.ids,
            'department_id': self.department_id.id,
        }
        if self.employee_id:
            employee_ids = self.employee_id.ids

        else:
            if self.department_id:
                employee_ids = self.env['hr.employee'].search([('department_id','=',self.department_id.id)]).ids
            else:
                employee_ids = self.env['hr.employee'].search([]).ids

        pf_detail_obj = self.env['provident.fund.detail.lines'].search([('date_from', '>=', self.date_from),('date_to', '<=', self.date_to),('employee_id','in',employee_ids)])


        if pf_detail_obj:

            return self.env.ref('xbo_payroll_report.action_employee_pf_report').report_action(self, datas)
        else:
            raise ValidationError('No Record Found!')


class action_employee_pf_report(models.AbstractModel):
    _name = 'report.xbo_payroll_report.employee_pf_report_template'
    _description = 'Employee Provident Fund Report'

    @api.model
    def _get_report_values(self, docids, data):
        employee_ids = data['employee_id']
        department_id = data['department_id']
        date_from = data['date_from']
        date_to = data['date_to']
        if employee_ids:
            employee_ids = employee_ids
        else:
            if department_id:
                employee_ids = self.env['hr.employee'].search([('department_id', '=', department_id)]).ids
            else:
                employee_ids = self.env['hr.employee'].search([]).ids
        pf_line_obj = self.env['provident.fund.detail.lines'].search([('date_from', '>=', date_from),('date_to', '<=', date_to),('employee_id','in',employee_ids)])

        code_names = ['Date From', 'Date To', 'Employee Name','PF %' , 'Basic Salary','Employee Contribution', 'Employer Contribution', 'Total PF Amount','Profit Share','Profit Disbursed','Closing Balance']
        department_wise = pf_line_obj.read_group([('date_from', '>=', date_from),('date_from', '<=', date_to),('employee_id','in',employee_ids)],
                                               fields=['department_id'], groupby=['department_id'])

        pf_line = []
        for emp in department_wise:
            employees = pf_line_obj.search(emp['__domain'])
            if employees:
                pf_line.append({'dept_name': employees[0].employee_id.department_id.name})

            for pay in employees:
                pf_details = {
                    'Date From': pay.date_from.strftime('%d-%m-%Y'),
                    'Date To': pay.date_to.strftime('%d-%m-%Y'),
                    'Employee Name': pay.employee_id.name,
                    'Basic Salary': pay.salary_amount,
                    'PF %': pay.pf_percentage,
                    'Employee Contribution': pay.employee_contribution,
                    'Employer Contribution': pay.employer_contribution,
                    'Total PF Amount': pay.total_PF_period,
                    'Profit Share': pay.profit_share,
                    'Profit Disbursed': pay.profit_disbursed,
                    'Closing Balance': pay.closing_balance,



                    'Employee_wise': True,
                }
                pf_line.append(pf_details)

            # departwise sub total
            dept_details = {}
            dept_details['Date From'] = 'Dep Total'
            value_salary_amount = sum(self.env['provident.fund.detail.lines'].search(
                [('id', 'in', employees.ids)]).mapped('salary_amount')) or 0.0
            dept_details['Basic Salary'] = "{0:,.1f}".format(value_salary_amount)
            value_employee_contribution = sum(self.env['provident.fund.detail.lines'].search(
                [('id', 'in', employees.ids)]).mapped('employee_contribution')) or 0.0
            dept_details['Employee Contribution'] = "{0:,.1f}".format(value_employee_contribution)
            value_employer_contribution = sum(self.env['provident.fund.detail.lines'].search(
                [('id', 'in', employees.ids)]).mapped('employer_contribution')) or 0.0
            dept_details['Employer Contribution'] = "{0:,.1f}".format(value_employer_contribution)
            value_total_PF_period = sum(self.env['provident.fund.detail.lines'].search(
                [('id', 'in', employees.ids)]).mapped('total_PF_period')) or 0.0
            dept_details['Total PF Amount'] = "{0:,.1f}".format(value_total_PF_period)
            value_profit_share = sum(self.env['provident.fund.detail.lines'].search(
                [('id', 'in', employees.ids)]).mapped('profit_share')) or 0.0
            dept_details['Profit Share'] = "{0:,.1f}".format(value_profit_share)
            value_profit_disbursed = sum(self.env['provident.fund.detail.lines'].search(
                [('id', 'in', employees.ids)]).mapped('profit_disbursed')) or 0.0
            dept_details['Profit Disbursed'] = "{0:,.1f}".format(value_profit_disbursed)
            value_closing_balance = sum(self.env['provident.fund.detail.lines'].search(
                [('id', 'in', employees.ids)]).mapped('closing_balance')) or 0.0
            dept_details['Closing Balance'] = "{0:,.1f}".format(value_closing_balance)
            dept_details['departwise'] = True
            pf_line.append(dept_details)

        # Grand Total

        dept_grand_total = {}
        dept_grand_total['Date From'] = ' Grand Total'
        value_salary_amount = sum(self.env['provident.fund.detail.lines'].search(
            [('id', 'in', pf_line_obj.ids)]).mapped('salary_amount')) or 0.0
        dept_grand_total['Basic Salary'] = "{0:,.1f}".format(value_salary_amount)
        value_employee_contribution = sum(self.env['provident.fund.detail.lines'].search(
            [('id', 'in', pf_line_obj.ids)]).mapped('employee_contribution')) or 0.0
        dept_grand_total['Employee Contribution'] = "{0:,.1f}".format(value_employee_contribution)

        value_employer_contribution = sum(self.env['provident.fund.detail.lines'].search(
            [('id', 'in', pf_line_obj.ids)]).mapped('employer_contribution')) or 0.0
        dept_grand_total['Employer Contribution'] = "{0:,.1f}".format(value_employer_contribution)
        value_total_PF_period = sum(self.env['provident.fund.detail.lines'].search(
            [('id', 'in', pf_line_obj.ids)]).mapped('total_PF_period')) or 0.0
        dept_grand_total['Total PF Amount'] = "{0:,.1f}".format(value_total_PF_period)
        value_profit_share = sum(self.env['provident.fund.detail.lines'].search(
            [('id', 'in', pf_line_obj.ids)]).mapped('profit_share')) or 0.0
        dept_grand_total['Profit Share'] = "{0:,.1f}".format(value_profit_share)
        value_profit_disbursed = sum(self.env['provident.fund.detail.lines'].search(
            [('id', 'in', pf_line_obj.ids)]).mapped('profit_disbursed')) or 0.0
        dept_grand_total['Profit Disbursed'] = "{0:,.1f}".format(value_profit_disbursed)
        value_closing_balance = sum(self.env['provident.fund.detail.lines'].search(
            [('id', 'in', pf_line_obj.ids)]).mapped('closing_balance')) or 0.0
        dept_grand_total['Closing Balance'] = "{0:,.1f}".format(value_closing_balance)


        return {
            'docs': pf_line,
            'pf_lines': pf_line,
            'code_names': code_names,
            'employees': employees,
            'department_wise': department_wise,
            'pf_line_obj': pf_line_obj,
            'dept_grand_total': dept_grand_total,
            'from_date': datetime.strptime(date_from, '%Y-%m-%d').strftime('%d-%m-%Y'),
            'to_date':  datetime.strptime(date_to, '%Y-%m-%d').strftime('%d-%m-%Y')
        }
