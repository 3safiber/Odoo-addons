
{
    'name': 'Base report xlsx',
    'version': '17.0.1.0.0',
    'summary': 'Subscription Modification',
    'sequence': -1,
    'depends': ["base", "web"],
    'demo': ["demo/report.xml"],
    "assets": {
        "web.assets_backend": [
            "report_xlsx/static/src/js/report/action_manager_report.esm.js",
        ],
    },
    'data': [
    ],
    'external_dependencies': {"python": ["xlsxwriter", "xlrd"]},
    'installable': True,

    'application': True,
    'license': 'LGPL-3',
}
