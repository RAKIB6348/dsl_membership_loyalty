import base64

from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class MembershipPortal(CustomerPortal):

    def _get_member_invoice_domain(self, partner):
        return [
            ('partner_id', '=', partner.id),
            ('move_type', '=', 'out_invoice'),
        ]

    def _get_member_invoice_count(self, partner):
        return request.env['account.move'].sudo().search_count(
            self._get_member_invoice_domain(partner)
        )

    def _ensure_partner_qr_code(self, partner):
        if not partner or not partner.exists():
            return

        if not partner.membership_agent_code:
            partner.sudo()._generate_membership_agent_code()

        if not partner.qr_code:
            partner.sudo()._generate_qr_code()

    @route(['/my/partner-qr/<int:partner_id>'], type='http', auth='user')
    def partner_qr_code_image(self, partner_id, **kw):
        current_partner = request.env.user.partner_id
        partner = request.env['res.partner'].sudo().browse(partner_id)

        if not partner.exists():
            return request.not_found()

        # Security: agent can view searched member QR, member can view own QR only
        if not current_partner.is_agent and partner.id != current_partner.id:
            return request.not_found()

        self._ensure_partner_qr_code(partner)

        if not partner.qr_code:
            return request.not_found()

        qr_code = partner.qr_code
        if isinstance(qr_code, str):
            qr_code = qr_code.encode('utf-8')

        image_content = base64.b64decode(qr_code)

        return request.make_response(
            image_content,
            headers=[
                ('Content-Type', 'image/png'),
                ('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0'),
            ]
        )

    @route(['/my', '/my/home'], type='http', auth='user')
    def home(self, **kw):
        partner = request.env.user.partner_id

        self._ensure_partner_qr_code(partner)

        invoice_count = self._get_member_invoice_count(partner)

        values = self._prepare_portal_layout_values()
        values.update({
            'partner': partner,
            'page_name': 'home',
            'searched_member': False,
            'search_error': False,
            'success_message': False,
            'search_value': '',
            'invoice_count': invoice_count,
        })

        if partner.is_agent:
            return request.render(
                'dsl_membership_loyalty.portal_agent_dashboard_template',
                values
            )

        return request.render(
            'dsl_membership_loyalty.portal_membership_card_template',
            values
        )

    @route(['/my/agent/member-search'], type='http', auth='user', methods=['POST'])
    def agent_member_search(self, **post):
        partner = request.env.user.partner_id
        search_value = post.get('member_search')

        self._ensure_partner_qr_code(partner)

        values = self._prepare_portal_layout_values()
        values.update({
            'partner': partner,
            'searched_member': False,
            'search_error': False,
            'success_message': False,
            'search_value': search_value,
        })

        if not partner.is_agent:
            values['search_error'] = 'Only agents can search members.'

        elif not search_value:
            values['search_error'] = 'Please enter member name, phone or email.'

        else:
            searched_member = request.env['res.partner'].sudo().search([
                ('is_membership', '=', True),
                '|', '|',
                ('name', 'ilike', search_value),
                ('phone', 'ilike', search_value),
                ('email', 'ilike', search_value),
            ], limit=1)

            if searched_member:
                self._ensure_partner_qr_code(searched_member)
                values['searched_member'] = searched_member
            else:
                values['search_error'] = 'No member found.'

        return request.render(
            'dsl_membership_loyalty.portal_agent_dashboard_template',
            values
        )

    @route(['/my/agent/room-booking'], type='http', auth='user', methods=['POST'])
    def agent_room_booking(self, **post):
        agent = request.env.user.partner_id

        self._ensure_partner_qr_code(agent)

        member_id = int(post.get('member_id') or 0)
        room_no = post.get('room_no') or ''
        room_charge = float(post.get('room_charge') or 0)
        used_points = int(post.get('used_points') or 0)

        member = request.env['res.partner'].sudo().browse(member_id)

        if member.exists():
            self._ensure_partner_qr_code(member)

        values = self._prepare_portal_layout_values()
        values.update({
            'partner': agent,
            'searched_member': member,
            'search_error': False,
            'success_message': False,
            'search_value': '',
        })

        if not agent.is_agent:
            values['search_error'] = 'Only agents can book rooms.'

        elif not member.exists() or not member.is_membership:
            values['search_error'] = 'Invalid member selected.'

        elif room_charge <= 0:
            values['search_error'] = 'Room charge must be greater than 0.'

        elif used_points < 0:
            values['search_error'] = 'Used points cannot be negative.'

        elif used_points > member.loyalty_points:
            values['search_error'] = 'Member does not have enough loyalty points.'

        else:
            config = request.env['loyalty.configuration'].sudo().search([
                ('active', '=', True),
                ('point', '>', 0),
            ], order='point desc', limit=1)

            if not config:
                values['search_error'] = 'Please configure loyalty point conversion first.'

            else:
                discount_amount = (used_points / config.point) * config.amount

                if discount_amount > room_charge:
                    values['search_error'] = 'Loyalty discount cannot be greater than room charge.'

                else:
                    member.sudo().write({
                        'loyalty_points': member.loyalty_points - used_points
                    })

                    agent.sudo().write({
                        'loyalty_points': agent.loyalty_points + used_points
                    })

                    member._update_loyalty_amount()
                    agent._update_loyalty_amount()

                    invoice = request.env['account.move'].sudo().create({
                        'move_type': 'out_invoice',
                        'partner_id': member.id,
                        'invoice_line_ids': [
                            (0, 0, {
                                'name': 'Hotel Room Booking - Room %s' % room_no,
                                'quantity': 1,
                                'price_unit': room_charge,
                            }),
                            (0, 0, {
                                'name': 'Loyalty Point Discount',
                                'quantity': 1,
                                'price_unit': -discount_amount,
                            }),
                        ],
                    })

                    values['success_message'] = 'Room booked successfully. Invoice created: %s' % invoice.name

        return request.render(
            'dsl_membership_loyalty.portal_agent_dashboard_template',
            values
        )

    @route(['/my/membership-card'], type='http', auth='user')
    def membership_card_details_page(self, **kw):
        partner = request.env.user.partner_id

        self._ensure_partner_qr_code(partner)

        invoice_count = self._get_member_invoice_count(partner)

        values = self._prepare_portal_layout_values()
        values.update({
            'partner': partner,
            'invoice_count': invoice_count,
        })

        return request.render(
            'dsl_membership_loyalty.portal_membership_card_details_template',
            values
        )

    @route(['/my/membership-invoices'], type='http', auth='user')
    def membership_invoice_records_page(self, **kw):
        partner = request.env.user.partner_id

        invoices = request.env['account.move'].sudo().search(
            self._get_member_invoice_domain(partner),
            order='invoice_date desc, id desc'
        )

        values = self._prepare_portal_layout_values()
        values.update({
            'partner': partner,
            'invoices': invoices,
            'invoice_count': len(invoices),
        })

        return request.render(
            'dsl_membership_loyalty.portal_membership_invoice_records_template',
            values
        )