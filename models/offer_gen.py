from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class OfferGenerator(models.Model):
    _name = 'offer.generator'
    _description = 'generates offers'

    name = fields.Char(string='Pavadinimas', required=True, default='Naujas')
    state = fields.Selection([
        ('new', 'Naujas'),
        ('comfirmed', 'Patvirtintas'),
        ('canceled', 'Atšauktas')
        ], default='new')
    client_id = fields.Many2one('res.partner', string='Klientas', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Pardavimas', readonly=True)
    products = fields.Char(string='Produktai')
    product_count = fields.Integer(string='Produktų skaičius', compute="_compute_product_count", store=False)
    product_lines = fields.One2many('offer.generator.line', 'offer_id', string="Sugeneruotos produktų eilutės")
    error_html = fields.Html(string="Klaidos", compute='_compute_errors')
    has_errors = fields.Boolean(string="Ar turi klaidų", compute='_compute_errors', store=True)

    @api.depends('client_id', 'product_lines', 'product_lines.product_id')
    def _compute_errors(self):
        for record in self:
            errors = []
            if not record.client_id:
                errors.append("Neįvestas klientas")
            for line in record.product_lines:
                if not line.product_id:
                    errors.append(f"Produktas {line.input_value} nerastas")
            record.has_errors = bool(errors)
            record.error_html = "<br/>".join([f"<strong>Klaida:</strong> {e}" for e in errors])

    @api.model
    def create(self, vals):
        if vals.get('name', 'Naujas') == 'Naujas':
            vals['name'] = self.env['ir.sequence'].next_by_code('offer.generator.sequence')
        return super(OfferGenerator, self).create(vals)

    @api.depends('product_lines')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_lines.mapped('product_id'))

    def action_confirm(self):
        if self.has_errors:
            error_message = "Pasiūlymas negali būti sukurtas. Klaidos: " + ",".join([e for e in self._get_error_list()])
            raise UserError(error_message)
        sale_order = self.env['sale.order'].create({
            'partner_id': self.client_id.id,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'procuct_uom_qty': line.quantity,
            }) for line in self.product_lines],
        })
        self.sale_order_id = sale_order.id
        self.state = 'confirmed'

    def action_cancel(self):
        if self.sale_order_id and self.sale_order_id.state != 'draft':
            raise UserError("Negalima atšaukti. Susietas pardavimas nėra juodraštis.")
        self.state = 'canceled'
        if self.sale_order_id:
            self.sale_order_id.action_cancel()

    def action_reset_to_draft(self):
        if not self.sale_order_id:
            self.state = 'new'

    def _get_error_list(self):
        return ["Klientas neįvestas" if not self.client_id else ""] + [line.input_value for line in self.product_lines if not line.product_id]

class OfferGeneratorLine(models.Model):
    _name = 'offer.generator.line'
    _description = 'Pasiūlymų generatoriaus eilutė'

    offer_id = fields.Many2one('offer.generator', string="Pasiūlymas", required=True)
    product_id = fields.Many2one('product.product', string="Produktas", required=True)
    product_uom_id = fields.Many2one('uom.uom', string="Units of measure", related='product_id.uom_id', readonly=True)
    quantity = fields.Integer(string="Kiekis", required=True, default=1)
    input_value = fields.Char()