from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class MembershipPortal(CustomerPortal):

    @route(['/my', '/my/home'], type='http', auth='user', website=True)
    def home(self, **kw):
        partner = request.env.user.partner_id

        values = self._prepare_portal_layout_values()
        values.update({
            'partner': partner,
            'page_name': 'home',
            'searched_member': False,
            'search_error': False,
            'search_value': '',
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

    @route(['/my/agent/member-search'], type='http', auth='user', website=True, methods=['POST'])
    def agent_member_search(self, **post):
        partner = request.env.user.partner_id
        search_value = post.get('member_search')

        values = self._prepare_portal_layout_values()
        values.update({
            'partner': partner,
            'searched_member': False,
            'search_error': False,
            'search_value': search_value,
        })

        if not partner.is_agent:
            values['search_error'] = 'Only agents can search members.'
            return request.render(
                'dsl_membership_loyalty.portal_agent_dashboard_template',
                values
            )

        if not search_value:
            values['search_error'] = 'Please enter member name, phone or email.'
            return request.render(
                'dsl_membership_loyalty.portal_agent_dashboard_template',
                values
            )

        searched_member = request.env['res.partner'].sudo().search([
            ('is_membership', '=', True),
            '|', '|',
            ('name', 'ilike', search_value),
            ('phone', 'ilike', search_value),
            ('email', 'ilike', search_value),
        ], limit=1)

        if not searched_member:
            values['search_error'] = 'No member found.'
        else:
            values['searched_member'] = searched_member

        return request.render(
            'dsl_membership_loyalty.portal_agent_dashboard_template',
            values
        )

    @route(['/my/membership-card'], type='http', auth='user', website=True)
    def membership_card_details_page(self, **kw):
        partner = request.env.user.partner_id

        values = self._prepare_portal_layout_values()
        values.update({
            'partner': partner,
        })

        return request.render(
            'dsl_membership_loyalty.portal_membership_card_details_template',
            values
        )