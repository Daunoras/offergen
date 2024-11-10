from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = "product.product"

    short_name = fields.Char('Produkto pavadinimo trumpinys')