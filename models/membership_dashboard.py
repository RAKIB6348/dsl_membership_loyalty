from odoo import api, fields, models


class MembershipDashboard(models.Model):
    _name = "membership.dashboard"
    _description = "Membership Dashboard"

    name = fields.Char(default="Membership Dashboard")

    total_members = fields.Integer(compute="_compute_dashboard_data")
    total_agents = fields.Integer(compute="_compute_dashboard_data")
    total_portal_users = fields.Integer(compute="_compute_dashboard_data")

    today_members = fields.Integer(compute="_compute_dashboard_data")
    today_agents = fields.Integer(compute="_compute_dashboard_data")

    def _compute_dashboard_data(self):
        Partner = self.env["res.partner"]
        today = fields.Date.context_today(self)

        for rec in self:
            rec.total_members = Partner.search_count([
                ("is_membership", "=", True)
            ])

            rec.total_agents = Partner.search_count([
                ("is_agent", "=", True)
            ])

            rec.total_portal_users = Partner.search_count([
                ("portal_user_id", "!=", False),
                "|",
                ("is_membership", "=", True),
                ("is_agent", "=", True),
            ])

            rec.today_members = Partner.search_count([
                ("is_membership", "=", True),
                ("create_date", ">=", f"{today} 00:00:00"),
                ("create_date", "<=", f"{today} 23:59:59"),
            ])

            rec.today_agents = Partner.search_count([
                ("is_agent", "=", True),
                ("create_date", ">=", f"{today} 00:00:00"),
                ("create_date", "<=", f"{today} 23:59:59"),
            ])

    @api.model
    def get_dashboard_record(self):
        record = self.search([], limit=1)
        if not record:
            record = self.create({"name": "Membership Dashboard"})
        return record