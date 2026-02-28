from odoo import models, fields, api
from odoo.exceptions import AccessError
from collections import defaultdict


class TimesheetReportWizard(models.TransientModel):
    _name = 'timesheet.executive.report.wizard'
    _description = 'Executive Timesheet Report Wizard'

    # ── Fields ──────────────────────────────────────
    employee_ids = fields.Many2many('hr.employee', string='Employees', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    is_manager = fields.Boolean(compute='_compute_is_manager', store=False)

    # ── ORM Overrides ────────────────────────────────
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        is_manager = self.env.user.has_group('timesheet_custom.group_timesheet_report_manager')
        res['is_manager'] = is_manager
        if not is_manager:
            employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1
            )
            if employee:
                res['employee_ids'] = [(6, 0, [employee.id])]
        return res

    # ── Helpers ──────────────────────────────────────
    @api.depends_context('uid')
    def _compute_is_manager(self):
        is_manager = self.env.user.has_group('timesheet_custom.group_timesheet_report_manager')
        for rec in self:
            rec.is_manager = is_manager

    def _decimal_to_hhmm(self, decimal_hours):
        total_minutes = int(round(decimal_hours * 60))
        return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

    def _safe_pct(self, val, total):
        if total == 0:
            return 0.0
        return round((val / total) * 100, 1)

    def _compute_report_data(self):
        all_employees_data = []

        for employee in self.employee_ids:
            lines = self.env['account.analytic.line'].sudo().search([
                ('employee_id', '=', employee.id),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
            ])

            category_buckets = {}
            idle_hours = 0.0

            for line in lines:
                project = line.project_id
                task = line.task_id
                hours = line.unit_amount

                # Skip unvalidated lines on projects that require validation
                mode = project.timesheet_progress_mode if hasattr(project, 'timesheet_progress_mode') else 'all'
                if mode == 'validated' and not line.validated:
                    continue

                if not project:
                    idle_hours += hours
                    continue

                category = project.activity_category_id
                if not category:
                    idle_hours += hours
                    continue

                if category.is_idle:
                    idle_hours += hours
                    continue

                activity_type = task.x_activity_type_id if task else False
                if activity_type and activity_type.is_idle:
                    idle_hours += hours
                    continue

                if category.id not in category_buckets:
                    category_buckets[category.id] = {
                        'rec': category,
                        'hours': 0.0,
                        'projects': defaultdict(float),
                        'types': defaultdict(float),
                    }

                bucket = category_buckets[category.id]
                bucket['hours'] += hours

                if category.show_type_breakdown:
                    type_name = activity_type.name if activity_type else 'Unknown'
                    bucket['types'][type_name] += hours
                else:
                    bucket['projects'][project.name] += hours

            grand_total = sum(b['hours'] for b in category_buckets.values()) + idle_hours

            sections = []
            for _, bucket in sorted(category_buckets.items(), key=lambda x: x[1]['rec'].sequence):
                category = bucket['rec']
                hours = bucket['hours']

                project_lines = [
                    {
                        'name': name,
                        'hhmm': self._decimal_to_hhmm(hrs),
                        'pct': self._safe_pct(hrs, grand_total),
                    }
                    for name, hrs in sorted(bucket['projects'].items())
                ]

                type_lines = [
                    {
                        'label': name,
                        'hhmm': self._decimal_to_hhmm(hrs),
                        'pct': self._safe_pct(hrs, grand_total),
                    }
                    for name, hrs in sorted(bucket['types'].items())
                ]

                sections.append({
                    'name': category.name,
                    'hours': hours,
                    'hhmm': self._decimal_to_hhmm(hours),
                    'pct': self._safe_pct(hours, grand_total),
                    'color': category.report_color or '#2c3e50',
                    'show_projects': not category.show_type_breakdown,
                    'show_types': category.show_type_breakdown,
                    'project_lines': project_lines,
                    'type_lines': type_lines,
                })

            # Fix floating point rounding so total always equals 100%
            raw_sum = sum(s['pct'] for s in sections) + self._safe_pct(idle_hours, grand_total)
            diff = round(100.0 - raw_sum, 1)
            if diff != 0 and sections:
                largest = max(sections, key=lambda x: x['hours'])
                largest['pct'] = round(largest['pct'] + diff, 1)

            all_employees_data.append({
                'employee_name': employee.name,
                'date_from': self.date_from.strftime('%b %d, %Y'),
                'date_to': self.date_to.strftime('%b %d, %Y'),
                'month_label': self.date_from.strftime('%B %Y'),
                'total_hhmm': self._decimal_to_hhmm(grand_total),
                'sections': sections,
                'idle_hhmm': self._decimal_to_hhmm(idle_hours),
                'pct_idle': self._safe_pct(idle_hours, grand_total),
            })

        return all_employees_data

    # ── Actions ──────────────────────────────────────
    def action_print_report(self):
        is_manager = self.env.user.has_group('timesheet_custom.group_timesheet_report_manager')
        if not is_manager:
            employee = self.env['hr.employee'].search(
                [('user_id', '=', self.env.uid)], limit=1
            )
            if not employee:
                raise AccessError("No employee record linked to your account.")
            if self.employee_ids != employee:
                raise AccessError("You can only generate a report for yourself.")
        return self.env.ref(
            'timesheet_custom.action_timesheet_executive_report'
        ).report_action(self)
