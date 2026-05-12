from odoo import api, fields, models


class LeaveType(models.Model):
    _inherit = 'hr.leave.type'

    work_entry_type_id = fields.Many2one('work.entry.types',required=True)
