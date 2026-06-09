from odoo import api, models


class ReportMembershipAgentRecords(models.AbstractModel):
    _name = 'report.dsl_membership_loyalty.report_ma_records'
    _description = 'Membership Agent Records Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        report_type = data.get('report_type', 'both')
        member_ids = data.get('member_ids') or []
        agent_ids = data.get('agent_ids') or []

        domain = [
            ('create_date', '>=', '%s 00:00:00' % start_date),
            ('create_date', '<=', '%s 23:59:59' % end_date),
        ]

        if report_type == 'membership':
            domain.append(('is_membership', '=', True))

            if member_ids:
                domain.append(('id', 'in', member_ids))

        elif report_type == 'agent':
            domain.append(('is_agent', '=', True))

            if agent_ids:
                domain.append(('id', 'in', agent_ids))

        else:
            domain += [
                '|',
                ('is_membership', '=', True),
                ('is_agent', '=', True),
            ]

            selected_ids = list(set(member_ids + agent_ids))
            if selected_ids:
                domain.append(('id', 'in', selected_ids))

        partners = self.env['res.partner'].sudo().search(
            domain,
            order='create_date desc, id desc'
        )

        report_type_label = {
            'both': 'Member and Agent',
            'membership': 'Member Only',
            'agent': 'Agent Only',
        }.get(report_type, 'Member and Agent')

        return {
            'doc_ids': partners.ids,
            'doc_model': 'res.partner',
            'docs': partners,
            'data': data,
            'start_date': start_date,
            'end_date': end_date,
            'report_type_label': report_type_label,
        }