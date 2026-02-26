from odoo import fields, models


class ResCity(models.Model):
    _inherit = 'res.city'

    code = fields.Char(string='City Code', help='Kode Kabupaten/Kota (Kemendagri)')