{
    'name': 'Pasiūlymų Generatorius',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'užduotis įgūdžiams parodyti',
    'description': """užduotis įgūdžiams parodyti.""",
    'author': 'Justinas Daunoras',
    'website': 'https://github.com/Daunoras',
    'depends': ['base', 'sale', 'product'],  # Add other dependencies if needed
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/offer_generator_form.xml',
        'views/offer_generator_view.xml',
        # 'data/data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}