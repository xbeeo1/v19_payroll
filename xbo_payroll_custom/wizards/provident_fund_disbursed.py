# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, date, datetime
from odoo.exceptions import ValidationError


class ProvidentFundDisbursed(models.TransientModel):
    _name = "provident.fund.disbursed"
    _description = "Provident Fund Disbursed"

    date_from = fields.Date(string='Date From', required= True)
    date_to = fields.Date(string='Date To', required= True)

    def action_confirm(self):
        detail_obj = self.env['provident.fund.detail.lines'].search(
            [('date_from', '=', self.date_from), ('date_to', '=', self.date_to)])

        if detail_obj:
            for y in detail_obj:
                y.write({
                    'profit_disbursed':y.profit_share,
                    'profit_disbursed_date': fields.Date.today()
                })

        else:
            raise ValidationError('No Record Found!')

