from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_membership = fields.Boolean(string='Is Membership', default=False)
    is_agent = fields.Boolean(string='Is Agent', default=False)
    loyalty_points = fields.Integer(string='Loyalty Points', default=0)

    portal_user_id = fields.Many2one(
        'res.users',
        string='Portal User',
        readonly=True,
        copy=False
    )

    def action_open_loyalty_point_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Loyalty Points',
            'res_model': 'membership.loyalty.point.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_member_ids': [(6, 0, self.ids)],
            }
        }

    def action_view_loyalty_points(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Loyalty Points',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def _create_portal_user(self):
        if self.env.context.get('skip_membership_portal_user'):
            return

        portal_group = self.env.ref('base.group_portal')

        for partner in self:
            if not partner.is_membership and not partner.is_agent:
                continue

            if partner.portal_user_id or partner.user_ids:
                continue

            if not partner.email:
                raise ValidationError("Email is required to create a portal user.")

            existing_user = self.env['res.users'].sudo().search([
                ('login', '=', partner.email)
            ], limit=1)

            if existing_user:
                partner.with_context(skip_membership_portal_user=True).sudo().write({
                    'portal_user_id': existing_user.id
                })
                continue

            user = self.env['res.users'].sudo().with_context(
                skip_membership_portal_user=True
            ).create({
                'name': partner.name,
                'login': partner.email,
                'email': partner.email,
                'partner_id': partner.id,
                'groups_id': [(6, 0, [portal_group.id])],
            })

            partner.with_context(skip_membership_portal_user=True).sudo().write({
                'portal_user_id': user.id
            })

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._create_portal_user()
        return partners

    def write(self, vals):
        res = super().write(vals)

        if self.env.context.get('skip_membership_portal_user'):
            return res

        if vals.get('is_membership') or vals.get('is_agent') or vals.get('email'):
            self._create_portal_user()

        return res