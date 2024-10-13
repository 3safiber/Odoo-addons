{
    'name': "approval request trip ",
    'category': '',
    'version': '0.1',
    'sequence': -10,

    "depends": ['base', 'account', 'sale', 'hr', 'product', 'contacts', 'board', 'stock', 'approvals'],
    'data': ['views/business_trip.xml',
             'views/hr.employee.view.xml',
             'views/grade_view.xml',
             'views/approval_category_inherit.xml',

             'security/ir.model.access.csv',
             ],
}
