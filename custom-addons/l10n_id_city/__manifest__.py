{
    'name': 'Indonesia - Wilayah Lengkap (Provinsi, Kab/Kota, Kecamatan, Desa)',
    'version': '18.0.2.0.0',
    'summary': 'Data wilayah administratif lengkap Indonesia: Provinsi, Kabupaten/Kota, Kecamatan, dan Kelurahan/Desa',
    'description': (
        'Menambahkan hierarki data wilayah administratif Indonesia pada form Kontak (res.partner): '
        'Provinsi (res.country.state), Kabupaten/Kota (res.city), '
        'Kecamatan (res.district), dan Kelurahan/Desa (res.village).'
    ),
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
    'license': 'LGPL-3',
}