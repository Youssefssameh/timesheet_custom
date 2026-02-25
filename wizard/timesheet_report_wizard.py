from odoo import models, fields
from collections import defaultdict


class TimesheetReportWizard(models.TransientModel):
    _name = 'timesheet.executive.report.wizard'
    _description = 'Executive Timesheet Report Wizard'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)

    # ─── Helpers ───────────────────────────────────────────

    def _decimal_to_hhmm(self, decimal_hours):
        total_minutes = int(round(decimal_hours * 60))
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    def _safe_pct(self, val, total):
        if total == 0:
            return 0.0
        return round((val / total) * 100, 1)

    # ─── Core Engine ───────────────────────────────────────

    def _compute_report_data(self):
        lines = self.env['account.analytic.line'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ])

        billable_projects = defaultdict(float)
        internal_projects = defaultdict(float)
        admin_breakdown   = defaultdict(float)
        idle_hours        = 0.0

        for line in lines:
            project  = line.project_id
            task     = line.task_id
            hours    = line.unit_amount

            if not project:
                idle_hours += hours
                continue
            


            category = project.x_activity_category

            if category == 'billable':
                billable_projects[project.name] += hours

            elif category == 'internal':
                internal_projects[project.name] += hours

            elif category == 'admin':
                activity = task.x_activity_type if task else False
                if activity == 'idle':
                    idle_hours += hours
                else:
                    admin_breakdown[activity or 'unknown'] += hours

        # ── Totals ──
        total_billable = sum(billable_projects.values())
        total_internal = sum(internal_projects.values())
        total_admin    = sum(admin_breakdown.values())
        grand_total    = total_billable + total_internal + total_admin + idle_hours

        # ── Percentages ──
        pct_b = self._safe_pct(total_billable, grand_total)
        pct_i = self._safe_pct(total_internal, grand_total)
        pct_a = self._safe_pct(total_admin,    grand_total)
        pct_d = self._safe_pct(idle_hours,     grand_total)

        # ── Rounding correction (largest bucket absorbs the diff) ──
        diff = round(100.0 - (pct_b + pct_i + pct_a + pct_d), 1)
        if diff != 0:
            largest = max(
                [('b', pct_b, total_billable),
                 ('i', pct_i, total_internal),
                 ('a', pct_a, total_admin),
                 ('d', pct_d, idle_hours)],
                key=lambda x: x[2]
            )
            if   largest[0] == 'b': pct_b = round(pct_b + diff, 1)
            elif largest[0] == 'i': pct_i = round(pct_i + diff, 1)
            elif largest[0] == 'a': pct_a = round(pct_a + diff, 1)
            else:                   pct_d = round(pct_d + diff, 1)

        # ── Admin breakdown lines ──
        LABELS = {
            'daily_scrum':       'Daily Scrum',
            'dept_meeting':      'Department Meetings',
            'management':        'Overall Management',
            'learning':          'Learning',
            'followup_interns':  'Follow-up Intern Team',
            'support':           'Support Tasks',
            'break_personal':    'Break / Personal',
            'public_holiday':    'Public Holiday',
        }

        admin_lines = [
            {
                'label': LABELS.get(k, k),
                'hhmm':  self._decimal_to_hhmm(v),
                'pct':   self._safe_pct(v, grand_total),
            }
            for k, v in sorted(admin_breakdown.items())
        ]

        billable_lines = [
            {
                'name': name,
                'hhmm': self._decimal_to_hhmm(hrs),
                'pct':  self._safe_pct(hrs, grand_total),
            }
            for name, hrs in sorted(billable_projects.items())
        ]

        internal_lines = [
            {
                'name': name,
                'hhmm': self._decimal_to_hhmm(hrs),
            }
            for name, hrs in sorted(internal_projects.items())
        ]

        return {
            'employee_name': self.employee_id.name,
            'date_from':     self.date_from.strftime('%b %d, %Y'),
            'date_to':       self.date_to.strftime('%b %d, %Y'),
            'month_label':   self.date_from.strftime('%B %Y'),
            'total_hhmm':    self._decimal_to_hhmm(grand_total),
            # overview
            'pct_billable':  pct_b,
            'pct_internal':  pct_i,
            'pct_admin':     pct_a,
            'pct_idle':      pct_d,
            'hhmm_billable': self._decimal_to_hhmm(total_billable),
            'hhmm_internal': self._decimal_to_hhmm(total_internal),
            'hhmm_admin':    self._decimal_to_hhmm(total_admin),
            'hhmm_idle':     self._decimal_to_hhmm(idle_hours),
            # details
            'billable_lines':  billable_lines,
            'internal_lines':  internal_lines,
            'admin_lines':     admin_lines,
            'idle_hhmm':       self._decimal_to_hhmm(idle_hours),
        }

    # ─── Button Action ─────────────────────────────────────

    def action_print_report(self):
        return self.env.ref(
            'timesheet_custom.action_timesheet_executive_report'
        ).report_action(self)
