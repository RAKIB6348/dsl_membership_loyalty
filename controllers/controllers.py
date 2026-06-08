from odoo import http
from odoo.http import request


class MembershipPortal(http.Controller):

    @http.route('/my', type='http', auth='user')
    def membership_card_page(self, **kw):
        partner = request.env.user.partner_id
        return request.render(
            'dsl_membership_loyalty.portal_membership_card_template',
            {'partner': partner}
        )

    @http.route('/my/membership-card', type='http', auth='user')
    def membership_card_details_page(self, **kw):
        partner = request.env.user.partner_id
        return request.render(
            'dsl_membership_loyalty.portal_membership_card_details_template',
            {'partner': partner}
        )