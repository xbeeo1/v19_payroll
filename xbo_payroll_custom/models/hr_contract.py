from datetime import date, datetime,timedelta, time
from dateutil.relativedelta import relativedelta
from docutils.parsers.rst.directives import percentage
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError





class HrContract(models.Model):

    _inherit = 'hr.version'

    gross_salary = fields.Monetary(string="Gross Salary", help="Gross Salary")
    minimum_wage = fields.Monetary(string="Minimum Wage", help="Minimum Wage")
    social_security_percentage = fields.Float(string="Social Security %")
    pf_percentage = fields.Float(string="PF %")
    eobi_percentage = fields.Float(string="EOBI %")
    wht_amount = fields.Monetary(string="W.H.T Amount", help="W.H.T Amount")


    @api.onchange('gross_salary')
    def set_salary_calculation(self):
        if self.gross_salary:
            self.wage = (self.gross_salary/100)*40
            self.hra = (self.gross_salary/100)*20
            self.travel_allowance = (self.gross_salary/100)*20
            self.medical_allowance = (self.gross_salary/100)*20


    def _numberOfDays(self, y, m):
        leap = 0
        if y % 400 == 0:
            leap = 1
        elif y % 100 == 0:
            leap = 0
        elif y % 4 == 0:
            leap = 1
        if m == 2:
            return 28 + leap
        list = [1, 3, 5, 7, 8, 10, 12]
        if m in list:
            return 31
        return 30

    @api.model
    def el_calculation(self, payslip):
        leaves = self.env['hr.leave'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'validate'),  # ensure only approved leaves are counted
            ('request_unit_half', '=', False),  # ensure only full day leaves are counted
            ('holiday_status_id.work_entry_type_id.code', 'in',['LEAVE140','LEAVE110']),
            ('request_date_to', '>=', payslip.date_from),
            ('request_date_from', '<=', payslip.date_to),
        ])
        total_leave_days = 0
        if leaves:
            total_leave_days = sum(leaves.mapped('number_of_days'))
        day_from = datetime.combine(fields.Date.from_string(payslip.date_from), time.min)
        day_to = datetime.combine(fields.Date.from_string(payslip.date_to), time.max)
        absent_data = self.employee_id._get_absent_scheduled_days(
            day_from,
            day_to,
            calendar=self.resource_calendar_id,
        )

        payslip_start_date = datetime.strptime(str(payslip.date_from), '%Y-%m-%d')
        payslip_start_month = payslip_start_date.month
        payslip_start_year = payslip_start_date.year
        no_of_days = self._numberOfDays(payslip_start_year, payslip_start_month)

        ph_obj = self.env['resource.calendar.leaves'].search([
            ('date_from', '<=', payslip.date_to),
            ('date_to', '>=', payslip.date_from),
        ])
        valid_ph = []
        if ph_obj:
            for ph in ph_obj:
                current_date = ph.date_from.date()
                end_date = ph.date_to.date()
                while current_date <= end_date:
                    attendances = self.env['hr.attendance'].search([
                        ('employee_id', '=', self.employee_id.id),
                        ('check_in', '>=', datetime.combine(current_date, time.min)),
                        ('check_out', '<=', datetime.combine(current_date, time.max)),
                    ])
                    if not attendances:
                        valid_ph.append(ph.id)

                    current_date += timedelta(days=1)

        absent_days  =absent_data['absent_scheduled_days']  - total_leave_days - len(valid_ph)

        if absent_days and  absent_days > 0:
            amount = (self.wage / no_of_days) * absent_days
            return amount
        else:
            return 0

    @api.model
    def hdl_calculation(self, payslip):
        leaves = self.env['hr.leave'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'validate'),  # ensure only approved leaves are counted
            ('request_unit_half', '=', True),  # ensure only full day leaves are counted
            ('holiday_status_id.work_entry_type_id.code', 'in', ['LEAVE140', 'LEAVE110']),
            ('request_date_to', '>=', payslip.date_from),
            ('request_date_from', '<=', payslip.date_to),
        ])
        total_leave_days = 0
        if leaves:
            total_leave_days = len(leaves)
        day_from = datetime.combine(fields.Date.from_string(payslip.date_from), time.min)
        day_to = datetime.combine(fields.Date.from_string(payslip.date_to), time.max)
        absent_data = self.employee_id._get_absent_scheduled_days(
            day_from,
            day_to,
            calendar=self.resource_calendar_id,
        )

        payslip_start_date = datetime.strptime(str(payslip.date_from), '%Y-%m-%d')
        payslip_start_month = payslip_start_date.month
        payslip_start_year = payslip_start_date.year
        no_of_days = self._numberOfDays(payslip_start_year, payslip_start_month)
        absent_half_days = absent_data['half_days'] - total_leave_days

        if absent_half_days and absent_half_days > 0:
            amount = (self.wage / no_of_days) * (absent_half_days/2)
            return amount
        else:
            return 0

    # @api.model
    # def ph_calculation(self, payslip):
    #     """
    #     Public Holiday Calculation
    #     Rules:
    #     1. Saturday/Sunday (weekly off) → ignore
    #     2. Approved leave → ignore
    #     3. Full day attendance → ignore
    #     4. Half day attendance → cover only 0.5 (avoid 1.5x pay issue)
    #     5. Short attendance (2 hr etc.) → treat as absent, PH covers full
    #     6. Absent on PH → PH covers full
    #     """
    #
    #     ph_obj = self.env['resource.calendar.leaves'].search([
    #         ('date_from', '<=', payslip.date_to),
    #         ('date_to', '>=', payslip.date_from),
    #     ])
    #
    #     if not ph_obj:
    #         return 0
    #
    #     valid_ph = []
    #
    #     for ph in ph_obj:
    #         current_date = ph.date_from.date()
    #         end_date = ph.date_to.date()
    #
    #         while current_date <= end_date:
    #
    #             # 1. Expected hours (skip weekly off)
    #             tz = self.resource_calendar_id.tz  # calendar ka timezone
    #             if tz:
    #                 tz = timezone(tz)
    #                 start = tz.localize(datetime.combine(current_date, time.min))
    #                 end = tz.localize(datetime.combine(current_date, time.max))
    #             else:
    #                 start = datetime.combine(current_date, time.min)
    #                 end = datetime.combine(current_date, time.max)
    #
    #             expected_hours = self.resource_calendar_id.get_work_hours_count(
    #                 start, end, compute_leaves=False
    #             )
    #             if expected_hours == 0:
    #                 current_date += timedelta(days=1)
    #                 continue
    #
    #             # 2. Approved leave check
    #             leave_exists = self.env['hr.leave'].search_count([
    #                 ('employee_id', '=', self.employee_id.id),
    #                 ('state', '=', 'validate'),
    #                 ('request_date_from', '<=', current_date),
    #                 ('request_date_to', '>=', current_date),
    #             ])
    #             if leave_exists:
    #                 current_date += timedelta(days=1)
    #                 continue
    #
    #             # 3. Attendance check
    #             attendances = self.env['hr.attendance'].search([
    #                 ('employee_id', '=', self.employee_id.id),
    #                 ('check_in', '>=', datetime.combine(current_date, time.min)),
    #                 ('check_out', '<=', datetime.combine(current_date, time.max)),
    #             ])
    #             worked_hours = sum(a.worked_hours for a in attendances)
    #
    #             # 4. Apply rules
    #             if worked_hours >= expected_hours:
    #                 # Full day → ignore PH
    #                 pass
    #             elif worked_hours > 0:
    #                 ratio = worked_hours / expected_hours
    #                 if 0.25 <= ratio < 0.75:
    #                     # Half day → only half cover (avoid 1.5x pay)
    #                     valid_ph.append(0.5)
    #                 else:
    #                     # Short attendance (like 2hr) → treat as absent, full PH cover
    #                     valid_ph.append(1)
    #             else:
    #                 # Absent → PH covers full
    #                 valid_ph.append(1)
    #
    #             current_date += timedelta(days=1)
    #
    #     # 5. Final calculation
    #     total_ph = sum(valid_ph)
    #
    #     payslip_start_date = datetime.strptime(str(payslip.date_from), '%Y-%m-%d')
    #     payslip_start_month = payslip_start_date.month
    #     payslip_start_year = payslip_start_date.year
    #     no_of_days = self._numberOfDays(payslip_start_year, payslip_start_month)
    #
    #     if total_ph > 0:
    #         amount = (self.wage / no_of_days) * total_ph
    #         return amount
    #     return 0






    @api.model
    def pto_calculation(self,code,payslip):
        # Find all approved leaves that overlap the payslip period and match the type
        leaves = self.env['hr.leave'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'validate'),  # ensure only approved leaves are counted
            ('holiday_status_id.work_entry_type_id.code', '=', code),
            ('request_date_to', '>=', payslip.date_from),
            ('request_date_from', '<=', payslip.date_to),
        ])
        if leaves:
            # Sum the duration
            total_leave_days = sum(leaves.mapped('number_of_days'))
            payslip_start_date = datetime.strptime(str(payslip.date_from), '%Y-%m-%d')
            payslip_start_month = payslip_start_date.month
            payslip_start_year = payslip_start_date.year
            no_of_days = self._numberOfDays(payslip_start_year, payslip_start_month)

            amount = (self.wage/no_of_days) * total_leave_days
            return amount
        else:
            return 0

    @api.model
    def pf_calculation(self,payslip):
        wage_pf_percent = (self.wage/100) * self.pf_percentage
        total_wage_pf_percent = 2 * wage_pf_percent
        pf_obj = self.env['provident.fund'].search([('payslip_id','=',payslip.id)])
        if not pf_obj:
            self.env['provident.fund'].create({
                'date_from':payslip.date_from,
                'date_to':payslip.date_to,
                'employee_id':self.employee_id.id,
                'department_id':self.employee_id.department_id.id,
                'payslip_id':payslip.id,
                'salary_amount':self.wage,
                'pf_percentage':self.pf_percentage,
                'employee_contribution':wage_pf_percent,
                'employer_contribution':wage_pf_percent,
                'total_PF_period':total_wage_pf_percent,
            })
        else:
            pf_obj.write({
                'date_from': payslip.date_from,
                'date_to': payslip.date_to,
                'employee_id': self.employee_id.id,
                'department_id': self.employee_id.department_id.id,
                'payslip_id': payslip.id,
                'salary_amount': self.wage,
                'pf_percentage': self.pf_percentage,
                'employee_contribution': wage_pf_percent,
                'employer_contribution': wage_pf_percent,
                'total_PF_period': total_wage_pf_percent,

            })

        return wage_pf_percent

    @api.model
    def loan_calculation(self, inputs):
        obj_amount = sum(self.env['hr.payslip.input'].search([('payslip_id','=',inputs.id),('code','=','LO')]).mapped('amount'))
        return obj_amount

    @api.model
    def loan_pf_calculation(self, inputs):
        obj_amount = sum(
            self.env['hr.payslip.input'].search([('payslip_id', '=', inputs.id), ('code', '=', 'LOPF')]).mapped('amount'))
        return obj_amount

    @api.model
    def loan_as_calculation(self, inputs):
        obj_amount = sum(
            self.env['hr.payslip.input'].search([('payslip_id', '=', inputs.id), ('code', '=', 'LOAS')]).mapped(
                'amount'))
        return obj_amount
