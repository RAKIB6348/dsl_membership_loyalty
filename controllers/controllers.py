# -*- coding: utf-8 -*-
# from odoo import http


# class DslMembershipLoyalty(http.Controller):
#     @http.route('/dsl_membership_loyalty/dsl_membership_loyalty', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dsl_membership_loyalty/dsl_membership_loyalty/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('dsl_membership_loyalty.listing', {
#             'root': '/dsl_membership_loyalty/dsl_membership_loyalty',
#             'objects': http.request.env['dsl_membership_loyalty.dsl_membership_loyalty'].search([]),
#         })

#     @http.route('/dsl_membership_loyalty/dsl_membership_loyalty/objects/<model("dsl_membership_loyalty.dsl_membership_loyalty"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dsl_membership_loyalty.object', {
#             'object': obj
#         })

