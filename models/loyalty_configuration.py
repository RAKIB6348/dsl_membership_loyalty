from odoo import fields, models


class LoyaltyConfiguration(models.Model):
    _name = "loyalty.configuration"
    _description = "Loyalty Point Configuration"

    point = fields.Float(string="Point", required=True)
    amount = fields.Float(string="Amount", required=True)
    active = fields.Boolean(string="Active", default=True)