{
    "name": "Library",
    "version": "1.0",
    "summary": "Library",
    "description": """
      Library
    """,
    "author": "Salameh",
    "website": "",
    "category": "Sales",
    "depends": ["base", 'sale', "sale_management", "mail", "mail_plugin",
                "website"],
    "data": [
        "security/group.xml",
        "security/ir.model.access.csv",
        'data/sequence.xml',
        "views/base_menu.xml",
        "views/book_view.xml",
        "views/category_view.xml",
        'views/order_sale_inherit.xml',
        'views/template.xml',
        'views/settings.xml'
        # 'wizard/book_category_wizard.xml',
        # 'reports/book_report.xml',
    ],
    "demo": [
        'demo/demo.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "library/static/src/css/style.css",
        ],
    },
    "application": True,
    'installable': True,
    "sequence": 1,
}
