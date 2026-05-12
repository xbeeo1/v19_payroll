from collections import defaultdict
from datetime import timedelta
from pytz import utc
from odoo import api, fields, models, tools, _
from odoo.tools import float_utils
from odoo.tools import float_round

ROUNDING_FACTOR = 16

class ResourceMixin(models.AbstractModel):
    _inherit = "resource.mixin"

    def _get_work_days_data(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None):
        """
        Calculates paid days:
        - Includes attendance-based actual presence (proportional to schedule)
        - Includes weekly offs (if no schedule, still paid)
        - Excludes leaves and holidays

        Total hours = total paid days × daily scheduled hours
        """

        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        # Get employee linked to resource
        employee = self.env['hr.employee'].search([('id', '=', self.id)], limit=1)

        # Attendance hours from hr.attendance
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', from_datetime),
            ('check_out', '<=', to_datetime),
        ])
        print('attendances',attendances)
        day_hours = defaultdict(float)
        for att in attendances:
            date = att.check_in.astimezone(utc).date()
            worked = (att.check_out - att.check_in).total_seconds() / 3600
            day_hours[date] += worked

        # Scheduled hours from calendar
        intervals = calendar._attendance_intervals_batch(from_datetime, to_datetime, resource)
        day_total = defaultdict(float)
        for start, stop, meta in intervals[resource.id]:
            date = start.date()
            hours = (stop - start).total_seconds() / 3600
            day_total[date] += hours

        # Compute average scheduled daily hours (for final hours computation)
        scheduled_days = [day for day, hours in day_total.items() if hours > 0.0]
        avg_daily_hours = (
            sum(day_total[day] for day in scheduled_days) / len(scheduled_days)
            if scheduled_days else 8.0  # default fallback
        )

        # Now calculate days and total hours (derived from days × avg_daily_hours)
        total_days = 0.0
        current = from_datetime.date()
        end = to_datetime.date()

        while current <= end:
            scheduled = day_total.get(current, 0.0)
            actual = day_hours.get(current, 0.0)

            if scheduled > 0.0:
                # Scheduled workday
                if actual > 0.0:
                    ratio = min(actual / scheduled, 1.0)
                    day_val = float_utils.round(ratio * ROUNDING_FACTOR) / ROUNDING_FACTOR
                    total_days += day_val
                # else: no attendance, skip (no paid)
            else:
                # Off-day → paid
                total_days += 1.0

            current += timedelta(days=1)

        total_hours = float_round(total_days * avg_daily_hours, precision_digits=2)

        return {
            'days': total_days,
            'hours': total_hours,
        }

    def _get_absent_scheduled_days(self, from_datetime, to_datetime, calendar=None):
        """
        Calculate number of days employee was scheduled to work,
        but did not attend fully (includes half day handling).
        """

        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        # Get employee from resource
        employee = self.env['hr.employee'].search([('id', '=', self.id)], limit=1)

        # Fetch attendance records
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', from_datetime),
            ('check_out', '<=', to_datetime),
        ])

        # Actual worked hours per day
        day_hours = defaultdict(float)
        for att in attendances:
            date = att.check_in.astimezone(utc).date()
            worked = (att.check_out - att.check_in).total_seconds() / 3600
            day_hours[date] += worked

        # Scheduled hours per day from calendar
        intervals = calendar._attendance_intervals_batch(from_datetime, to_datetime, resource)
        day_scheduled = defaultdict(float)
        for start, stop, meta in intervals.get(resource.id, []):
            date = start.date()
            hours = (stop - start).total_seconds() / 3600
            day_scheduled[date] += hours

        # Count absent and half-days
        full_absents = []
        half_days = []

        for day, scheduled_hours in day_scheduled.items():
            actual_hours = day_hours.get(day, 0.0)

            if actual_hours == 0:
                full_absents.append(day)
            else:
                ratio = actual_hours / scheduled_hours
                if ratio < 0.25:
                    full_absents.append(day)
                elif ratio < 0.75:
                    half_days.append(day)

        return {
            'absent_scheduled_days': len(full_absents),
            'half_days': len(half_days),
            'absent_dates': sorted(full_absents),
            'half_day_dates': sorted(half_days),
        }
