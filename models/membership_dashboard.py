from datetime import datetime, time, timedelta

import pytz

from odoo import api, fields, models


class MembershipDashboard(models.Model):
    _name = "membership.dashboard"
    _description = "Membership Dashboard"

    name = fields.Char(default="Membership Dashboard")

    total_members = fields.Integer(compute="_compute_dashboard_data")
    total_agents = fields.Integer(compute="_compute_dashboard_data")
    total_portal_users = fields.Integer(compute="_compute_dashboard_data")
    portal_coverage = fields.Float(
        string="Portal Coverage (%)",
        compute="_compute_dashboard_data",
        digits=(5, 1),
    )
    today_members = fields.Integer(compute="_compute_dashboard_data")
    today_agents = fields.Integer(compute="_compute_dashboard_data")
    this_month_members = fields.Integer(compute="_compute_dashboard_data")
    last_month_members = fields.Integer(compute="_compute_dashboard_data")
    growth_rate = fields.Float(
        string="Monthly Member Growth Rate (%)",
        compute="_compute_dashboard_data",
        digits=(6, 1),
    )
    this_month_agents = fields.Integer(compute="_compute_dashboard_data")
    last_month_agents = fields.Integer(compute="_compute_dashboard_data")
    agent_growth_rate = fields.Float(
        string="Monthly Agent Growth Rate (%)",
        compute="_compute_dashboard_data",
        digits=(6, 1),
    )
    total_loyalty_points = fields.Integer(compute="_compute_dashboard_data")
    total_loyalty_amount = fields.Float(
        compute="_compute_dashboard_data",
        digits=(16, 2),
    )

    def _get_period_boundaries(self):
        user_tz = pytz.timezone(self.env.user.tz or "UTC")
        today = fields.Date.context_today(self)
        tomorrow = today + timedelta(days=1)
        month_start = today.replace(day=1)
        next_month_start = (month_start + timedelta(days=32)).replace(day=1)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)

        def to_utc(date_value):
            local_datetime = user_tz.localize(datetime.combine(date_value, time.min))
            return local_datetime.astimezone(pytz.UTC).replace(tzinfo=None)

        return {
            "today_start": to_utc(today),
            "tomorrow_start": to_utc(tomorrow),
            "month_start": to_utc(month_start),
            "next_month_start": to_utc(next_month_start),
            "last_month_start": to_utc(last_month_start),
        }

    def _get_role_domain(self):
        return ["|", ("is_membership", "=", True), ("is_agent", "=", True)]

    def _get_portal_domain(self):
        return [("portal_user_id", "!=", False)] + self._get_role_domain()

    @api.depends_context("uid", "tz", "allowed_company_ids")
    def _compute_dashboard_data(self):
        partner_model = self.env["res.partner"]
        periods = self._get_period_boundaries()
        member_domain = [("is_membership", "=", True)]
        agent_domain = [("is_agent", "=", True)]
        role_domain = self._get_role_domain()

        total_members = partner_model.search_count(member_domain)
        total_agents = partner_model.search_count(agent_domain)
        total_profiles = partner_model.search_count(role_domain)
        total_portal_users = partner_model.search_count(self._get_portal_domain())
        today_domain = [
            ("create_date", ">=", periods["today_start"]),
            ("create_date", "<", periods["tomorrow_start"]),
        ]
        this_month_domain = [
            ("create_date", ">=", periods["month_start"]),
            ("create_date", "<", periods["next_month_start"]),
        ]
        last_month_domain = [
            ("create_date", ">=", periods["last_month_start"]),
            ("create_date", "<", periods["month_start"]),
        ]
        today_members = partner_model.search_count(member_domain + today_domain)
        today_agents = partner_model.search_count(agent_domain + today_domain)
        this_month_members = partner_model.search_count(member_domain + this_month_domain)
        last_month_members = partner_model.search_count(member_domain + last_month_domain)
        this_month_agents = partner_model.search_count(agent_domain + this_month_domain)
        last_month_agents = partner_model.search_count(agent_domain + last_month_domain)

        loyalty_groups = partner_model.read_group(
            role_domain,
            ["loyalty_points:sum", "loyalty_amount:sum"],
            [],
        )
        loyalty_totals = loyalty_groups[0] if loyalty_groups else {}

        if last_month_members:
            growth_rate = (
                (this_month_members - last_month_members) / last_month_members
            ) * 100
        elif this_month_members:
            growth_rate = 100.0
        else:
            growth_rate = 0.0

        if last_month_agents:
            agent_growth_rate = (
                (this_month_agents - last_month_agents) / last_month_agents
            ) * 100
        elif this_month_agents:
            agent_growth_rate = 100.0
        else:
            agent_growth_rate = 0.0

        portal_coverage = (
            total_portal_users / total_profiles * 100 if total_profiles else 0.0
        )

        for record in self:
            record.total_members = total_members
            record.total_agents = total_agents
            record.total_portal_users = total_portal_users
            record.portal_coverage = portal_coverage
            record.today_members = today_members
            record.today_agents = today_agents
            record.this_month_members = this_month_members
            record.last_month_members = last_month_members
            record.growth_rate = growth_rate
            record.this_month_agents = this_month_agents
            record.last_month_agents = last_month_agents
            record.agent_growth_rate = agent_growth_rate
            record.total_loyalty_points = loyalty_totals.get("loyalty_points", 0)
            record.total_loyalty_amount = loyalty_totals.get("loyalty_amount", 0.0)

    def _get_partner_action(self, name, domain):
        return {
            "type": "ir.actions.act_window",
            "name": name,
            "res_model": "res.partner",
            "view_mode": "kanban,tree,form",
            "domain": domain,
            "target": "current",
            "context": {"search_default_customer": 0},
        }

    def action_view_members(self):
        return self._get_partner_action(
            "Members",
            [("is_membership", "=", True)],
        )

    def action_view_agents(self):
        return self._get_partner_action(
            "Agents",
            [("is_agent", "=", True)],
        )

    def action_view_portal_users(self):
        return self._get_partner_action("Portal Users", self._get_portal_domain())

    def action_view_today_members(self):
        periods = self._get_period_boundaries()
        return self._get_partner_action(
            "Today's Members",
            [
                ("is_membership", "=", True),
                ("create_date", ">=", periods["today_start"]),
                ("create_date", "<", periods["tomorrow_start"]),
            ],
        )

    def action_view_today_agents(self):
        periods = self._get_period_boundaries()
        return self._get_partner_action(
            "Today's Agents",
            [
                ("is_agent", "=", True),
                ("create_date", ">=", periods["today_start"]),
                ("create_date", "<", periods["tomorrow_start"]),
            ],
        )

    def action_view_month_members(self):
        periods = self._get_period_boundaries()
        return self._get_partner_action(
            "This Month's Members",
            [
                ("is_membership", "=", True),
                ("create_date", ">=", periods["month_start"]),
                ("create_date", "<", periods["next_month_start"]),
            ],
        )

    def action_view_month_agents(self):
        periods = self._get_period_boundaries()
        return self._get_partner_action(
            "This Month's Agents",
            [
                ("is_agent", "=", True),
                ("create_date", ">=", periods["month_start"]),
                ("create_date", "<", periods["next_month_start"]),
            ],
        )

    def action_view_loyalty_profiles(self):
        return self._get_partner_action(
            "Membership Loyalty",
            self._get_role_domain(),
        )
