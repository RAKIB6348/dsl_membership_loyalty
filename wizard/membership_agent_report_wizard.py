from odoo import fields, models
from odoo.exceptions import UserError


class MembershipAgentReportWizard(models.TransientModel):
    _name = 'membership.agent.report.wizard'
    _description = 'Membership Agent Report Wizard'

    start_date = fields.Date(
        string='Start Date',
        required=True
    )

    end_date = fields.Date(
        string='End Date',
        required=True
    )

    report_type = fields.Selection(
        [
            ('both', 'Member and Agent'),
            ('membership', 'Member Only'),
            ('agent', 'Agent Only'),
        ],
        string='Report Type',
        default='both',
        required=True
    )

    member_ids = fields.Many2many(
        'res.partner',
        'membership_report_wizard_member_rel',
        'wizard_id',
        'partner_id',
        string='Members',
        domain=[('is_membership', '=', True)]
    )

    agent_ids = fields.Many2many(
        'res.partner',
        'membership_report_wizard_agent_rel',
        'wizard_id',
        'partner_id',
        string='Agents',
        domain=[('is_agent', '=', True)]
    )

    def action_print_report(self):
        self.ensure_one()

        if self.start_date > self.end_date:
            raise UserError('End Date must be greater than or equal to Start Date.')

        data = {
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'report_type': self.report_type,
            'member_ids': self.member_ids.ids,
            'agent_ids': self.agent_ids.ids,
        }

        return self.env.ref(
            'dsl_membership_loyalty.action_report_membership_agent_records'
        ).report_action(self, data=data)