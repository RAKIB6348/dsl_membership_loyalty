from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_membership = fields.Boolean(string='Is Membership', default=False)
    is_agent = fields.Boolean(string='Is Agent', default=False)