{
    'name': 'Indonesia - Kabupaten/Kota',
    'version': '18.0.1.0.0',
    'summary': 'Data Kabupaten/Kota untuk Indonesia',
    'description': 'Menambahkan data kabupaten/kota Indonesia pada modul Contact',
    'author': 'Bayfr',
    'category': 'Localization',
    'depends': ['base', 'contacts', 'base_address_extended'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'post_init_hook': '_post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}