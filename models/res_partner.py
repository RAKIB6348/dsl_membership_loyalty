import base64
from io import BytesIO

import qrcode

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_membership = fields.Boolean(string='Is Membership', default=False)
    is_agent = fields.Boolean(string='Is Agent', default=False)

    membership_agent_code = fields.Char(
        string='Unique Code',
        readonly=True,
        copy=False,
        index=True
    )

    loyalty_points = fields.Integer(string='Loyalty Points', default=0)
    loyalty_amount = fields.Float(string='Loyalty Amount', default=0.0)

    portal_user_id = fields.Many2one(
        'res.users',
        string='Portal User',
        readonly=True,
        copy=False
    )

    qr_code = fields.Binary(
        string='QR Code',
        readonly=True,
        copy=False
    )

    qr_code_text = fields.Char(
        string='QR Code Text',
        readonly=True,
        copy=False
    )

    def _get_qr_user_type(self):
        self.ensure_one()

        if self.is_agent:
            return 'Agent'

        if self.is_membership:
            return 'Membership'

        return 'Contact'

    def _get_unique_code_sequence_code(self):
        self.ensure_one()

        if self.is_agent:
            return 'dsl_membership_loyalty.agent_code_sequence'

        if self.is_membership:
            return 'dsl_membership_loyalty.membership_code_sequence'

        return False

    def _generate_membership_agent_code(self):
        for partner in self:
            if not partner.is_membership and not partner.is_agent:
                continue

            if partner.membership_agent_code:
                continue

            sequence_code = partner._get_unique_code_sequence_code()
            if not sequence_code:
                continue

            code = self.env['ir.sequence'].sudo().next_by_code(sequence_code)

            partner.with_context(skip_code_generation=True).sudo().write({
                'membership_agent_code': code
            })

    def _prepare_qr_code_text(self):
        self.ensure_one()

        user_type = self._get_qr_user_type()

        return (
            f"Code: {self.membership_agent_code or ''}\n"
            f"Name: {self.name or ''}\n"
            f"Type: {user_type}\n"
            f"Email: {self.email or ''}\n"
            f"Phone: {self.phone or ''}\n"
            f"Partner ID: {self.id}"
        )

    def _generate_qr_code(self):
        for partner in self:
            if not partner.is_membership and not partner.is_agent:
                partner.with_context(skip_qr_generation=True).sudo().write({
                    'qr_code': False,
                    'qr_code_text': False,
                })
                continue

            if not partner.membership_agent_code:
                partner._generate_membership_agent_code()

            qr_text = partner._prepare_qr_code_text()

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format='PNG')

            qr_code_base64 = base64.b64encode(buffer.getvalue())

            partner.with_context(skip_qr_generation=True).sudo().write({
                'qr_code': qr_code_base64,
                'qr_code_text': qr_text,
            })

    def _update_loyalty_amount(self):
        config = self.env['loyalty.configuration'].search([
            ('active', '=', True),
            ('point', '>', 0),
        ], order='point desc', limit=1)

        for partner in self:
            if config:
                partner.loyalty_amount = (partner.loyalty_points / config.point) * config.amount
            else:
                partner.loyalty_amount = 0.0

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

    def action_view_loyalty_amount(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Loyalty Amount',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def action_generate_qr_code(self):
        self._generate_membership_agent_code()
        self._generate_qr_code()
        return True

    def action_download_membership_agent_card(self):
        self.ensure_one()

        if not self.membership_agent_code:
            self._generate_membership_agent_code()

        if not self.qr_code:
            self._generate_qr_code()

        return self.env.ref(
            'dsl_membership_loyalty.action_report_membership_agent_card'
        ).report_action(self)

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

        partners._generate_membership_agent_code()
        partners._create_portal_user()
        partners._update_loyalty_amount()

        if not self.env.context.get('skip_qr_generation'):
            partners._generate_qr_code()

        return partners

    def write(self, vals):
        res = super().write(vals)

        if self.env.context.get('skip_membership_portal_user'):
            return res

        if not self.env.context.get('skip_code_generation'):
            if vals.get('is_membership') or vals.get('is_agent'):
                self._generate_membership_agent_code()

        if vals.get('is_membership') or vals.get('is_agent') or vals.get('email'):
            self._create_portal_user()

        if 'loyalty_points' in vals:
            self._update_loyalty_amount()

        qr_trigger_fields = [
            'name',
            'email',
            'phone',
            'is_membership',
            'is_agent',
            'membership_agent_code',
        ]

        if not self.env.context.get('skip_qr_generation') and any(field in vals for field in qr_trigger_fields):
            self._generate_qr_code()

        return res