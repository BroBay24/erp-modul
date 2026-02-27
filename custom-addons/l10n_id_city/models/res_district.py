from odoo import fields, models

class ResDistrict(models.Model):
    _name = 'res.district'
    _description = 'District / Kecamatan'
    _order = 'name'

    name = fields.Char(required=True)
    regency_id = fields.Many2one('res.city', string='Regency/City', required=True, ondelete='cascade')
    state_id = fields.Many2one('res.country.state', string='Province', related='regency_id.state_id', store=True, readonly=True)
    country_id = fields.Many2one('res.country', string='Country', related='regency_id.country_id', store=True, readonly=True)
    code = fields.Char(string='District Code')