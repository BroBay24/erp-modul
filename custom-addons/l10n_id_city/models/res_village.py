from odoo import fields, models


class ResVillage(models.Model):
    _name = 'res.village'
    _description = 'Village / Kelurahan / Desa'
    _order = 'name'

    name = fields.Char(string='Kelurahan/Desa', required=True)
    district_id = fields.Many2one(
        'res.district',
        string='Kecamatan',
        required=True,
        ondelete='cascade',
    )
    city_id = fields.Many2one(
        'res.city',
        string='Kabupaten/Kota',
        related='district_id.regency_id',
        store=True,
        readonly=True,
    )
    state_id = fields.Many2one(
        'res.country.state',
        string='Provinsi',
        related='district_id.state_id',
        store=True,
        readonly=True,
    )
    country_id = fields.Many2one(
        'res.country',
        string='Negara',
        related='district_id.country_id',
        store=True,
        readonly=True,
    )
    code = fields.Char(string='Kode Desa/Kelurahan', help='Kode wilayah dari Kemendagri')
