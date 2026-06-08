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