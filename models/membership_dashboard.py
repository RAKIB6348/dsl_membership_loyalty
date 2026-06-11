from odoo import api, fields, models
from datetime import timedelta


class MembershipDashboard(models.Model):
    _name = "membership.dashboard"
    _description = "Membership Dashboard"

    name = fields.Char(default="Membership Dashboard")

    total_members = fields.Integer(compute="_compute_dashboard_data")
    total_agents = fields.Integer(compute="_compute_dashboard_data")
    total_portal_users = fields.Integer(compute="_compute_dashboard_data")
    today_members = fields.Integer(compute="_compute_dashboard_data")
    today_agents = fields.Integer(compute="_compute_dashboard_data")
    growth_rate = fields.Float(string="Monthly Growth Rate (%)", compute="_compute_dashboard_data", digits=(5, 2))

    def _compute_dashboard_data(self):
        Partner = self.env["res.partner"]
        today = fields.Date.context_today(self)
        first_day_this_month = today.replace(day=1)
        first_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = first_day_last_month.replace(day=1)

        for rec in self:
            # Basic counts
            rec.total_members = Partner.search_count([("is_membership", "=", True)])
            rec.total_agents = Partner.search_count([("is_agent", "=", True)])
            rec.total_portal_users = Partner.search_count([
                ("portal_user_id", "!=", False),
                "|", ("is_membership", "=", True), ("is_agent", "=", True)
            ])

            # Today's counts
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

            # Growth Rate: (New members this month - New members last month) / Last month * 100
            this_month_members = Partner.search_count([
                ("is_membership", "=", True),
                ("create_date", ">=", first_day_this_month),
            ])
            last_month_members = Partner.search_count([
                ("is_membership", "=", True),
                ("create_date", ">=", first_day_last_month),
                ("create_date", "<", first_day_this_month),
            ])

            if last_month_members > 0:
                rec.growth_rate = ((this_month_members - last_month_members) / last_month_members) * 100
            else:
                rec.growth_rate = this_month_members * 100  # fallback

    # ==================== BUTTON ACTIONS ====================
    def action_view_members(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Members",
            "res_model": "res.partner",
            "view_mode": "kanban,tree,form",
            "domain": [("is_membership", "=", True)],
            "target": "current",
        }

    def action_view_agents(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Agents",
            "res_model": "res.partner",
            "view_mode": "kanban,tree,form",
            "domain": [("is_agent", "=", True)],
            "target": "current",
        }

    def action_view_portal_users(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Portal Users",
            "res_model": "res.partner",
            "view_mode": "kanban,tree,form",
            "domain": [
                ("portal_user_id", "!=", False),
                "|", ("is_membership", "=", True), ("is_agent", "=", True)
            ],
            "target": "current",
        }

    def action_view_today_members(self):
        today = fields.Date.context_today(self)
        return {
            "type": "ir.actions.act_window",
            "name": "Today's Members",
            "res_model": "res.partner",
            "view_mode": "kanban,tree,form",
            "domain": [
                ("is_membership", "=", True),
                ("create_date", ">=", f"{today} 00:00:00"),
                ("create_date", "<=", f"{today} 23:59:59"),
            ],
            "target": "current",
        }

    def action_view_today_agents(self):
        today = fields.Date.context_today(self)
        return {
            "type": "ir.actions.act_window",
            "name": "Today's Agents",
            "res_model": "res.partner",
            "view_mode": "kanban,tree,form",
            "domain": [
                ("is_agent", "=", True),
                ("create_date", ">=", f"{today} 00:00:00"),
                ("create_date", "<=", f"{today} 23:59:59"),
            ],
            "target": "current",
        }