from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    check_box_nod = fields.Boolean('Calc on Salary Days', default=False)

