from odoo import fields, models
from odoo.exceptions import ValidationError


class MembershipLoyaltyPointWizard(models.TransientModel):
    _name = 'membership.loyalty.point.wizard'
    _description = 'Membership Loyalty Point Wizard'

    member_ids = fields.Many2many(
        'res.partner',
        string='Members',
        domain="[('is_membership', '=', True)]",
        required=True
    )

    points = fields.Integer(string='Loyalty Points', required=True)

    note = fields.Text(string='Note')

    def action_generate_loyalty_points(self):
        if self.points <= 0:
            raise ValidationError("Loyalty points must be greater than 0.")

        for member in self.member_ids:
            member.loyalty_points += self.points

        return {'type': 'ir.actions.act_window_close'}