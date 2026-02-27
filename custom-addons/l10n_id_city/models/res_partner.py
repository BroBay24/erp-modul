from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    district_id = fields.Many2one(
        'res.district',
        string='Kecamatan',
        domain="[('regency_id', '=', city_id)]",
        ondelete='restrict',
    )
    village_id = fields.Many2one(
        'res.village',
        string='Kelurahan/Desa',
        domain="[('district_id', '=', district_id)]",
        ondelete='restrict',
    )
