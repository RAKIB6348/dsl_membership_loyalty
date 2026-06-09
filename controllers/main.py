from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home


class CustomLogin(Home):

    @http.route(
        '/web/login',
        type='http',
        auth='none',
        website=True,
        sitemap=False,
        csrf=False,
        methods=['GET', 'POST']
    )
    def web_login(self, redirect=None, **kw):

        allowed_types = ['admin', 'agent', 'membership']

        # Before login: check select option is selected
        if request.httprequest.method == 'POST':
            login_user_type = kw.get('login_user_type')

            if not login_user_type:
                values = request.params.copy()
                values.update({
                    'error': 'Please select login type.',
                    'login_success': False,
                })
                return request.render('web.login', values)

            if login_user_type not in allowed_types:
                values = request.params.copy()
                values.update({
                    'error': 'Invalid login type selected.',
                    'login_success': False,
                })
                return request.render('web.login', values)

        # Odoo default login process
        response = super().web_login(redirect=redirect, **kw)

        # After successful login: check selected type with logged-in user
        if request.httprequest.method == 'POST' and request.session.uid:
            login_user_type = kw.get('login_user_type')

            user = request.env['res.users'].sudo().browse(request.session.uid)
            partner = user.partner_id

            is_allowed = False

            if login_user_type == 'admin':
                # Admin/Internal backend user
                is_allowed = (
                    user.has_group('base.group_system')
                    or user.has_group('base.group_user')
                )

            elif login_user_type == 'agent':
                # Agent user must have partner.is_agent = True
                is_allowed = bool(partner.is_agent)

            elif login_user_type == 'membership':
                # Membership user must have partner.is_membership = True
                is_allowed = bool(partner.is_membership)

            if not is_allowed:
                request.session.logout()

                values = request.params.copy()
                values.update({
                    'error': 'Selected login type does not match this user.',
                    'login_success': False,
                })
                return request.render('web.login', values)

        return response