{
    'name': 'Contact Renewal',
    'version': '1.0',
    'depends': ['hr', 'l10n_sa_hr_payroll', 'contacts', 'hr_contract'],
    'data': ["security/security.xml",
             "security/ir.model.access.csv",
             "views/contract_renewal.xml",
             "views/contract_renewal_cron.xml",
             "views/global_renewal_view.xml",
             "views/hr_contract_inherit.xml",
             "views/hr_employee_inherit.xml",
             "wizard/new_renewal_contract_wizard_view.xml"
             ],
    "assets": {
        "web.assets_backend": [
            "contract_renewal/static/src/css/style.css",
        ],
    },
    "sequence": 1,

    'installable': True,
    'application': False,
}
