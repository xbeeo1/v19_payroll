# -*- coding: utf-8 -*-
{
    "name": "Xbo Payroll Custom",

    'version': '19.0.0.0',

    'summary': """Xbo Payroll Custom""",

    'description': """Xbo Payroll Custom""",

    'category': 'payroll',

    'author': "Musadiq Fiaz",

    'website': 'https://xbeeo.com/',

    "depends": ['base','om_hr_payroll','om_hr_payroll_account'],

    "data": [
        'security/hr_loan_security.xml',
        'security/ir.model.access.csv',

        'data/ir_sequence_data.xml',
        'data/hr_payroll_category_demo.xml',
        'data/hr_salary_rule_demo.xml',
        'data/hr_rule_input_demo.xml',
        'data/work_entry_type_demo.xml',

        'views/hr_loan_views.xml',
        'views/res_config_setting.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
        'views/loan_type_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/provident_fund_view.xml',
        'views/hr_contract_view.xml',
        'views/work_entry_types_views.xml',
        'views/hr_leave_type_view.xml',
        'views/provident_fund_detail_view.xml',
        'wizards/provident_fund_profit.xml',
        'wizards/provident_fund_disbursed.xml',
        'wizards/print_employee_payslip.xml',
    ],

}

