from odoo import models, fields, api

class OfferGen(models.Model):
    _name = 'offer.generator'
    _description = 'generates offers'

    name = fields.Char(string='Pavadinimas', required=True, default='Naujas')
    state = fields.Selection([
        ('new', 'Naujas'),
        ('comfirmed', 'Patvirtintas'),
        ('canceled', 'Atšauktas')
        ], default='new')
    client = fields.Many2one('res.partner', string='Klientas', required=True)
    sale = fields.Many2one('sale.order', string='Pardavimas', readonly=True)
    products = fields.Char(string='Produktai')
    product_count = fields.Integer(string='Produktų skaičius', compute="_compute_product_count", store=False)


    @api.model
    def create(self, vals):
        if vals.get('name', 'Naujas') == 'Naujas':
            vals['name'] = self.env['ir.sequence'].next_by_code('offer.generator.sequence')
        return super(OfferGen, self).create(vals)

    def _compute_product_count(self):
        return len(set(self.products.split()))