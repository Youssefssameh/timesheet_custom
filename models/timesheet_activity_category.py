from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class TimesheetActivityCategory(models.Model):
    _name = 'timesheet.activity.category'
    _description = 'Timesheet Activity Category'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_idle = fields.Boolean(
        string='Is Idle Category',
        default=False,
        help="Hours in this category count as Idle Time in the report",
    )
    show_project_breakdown = fields.Boolean(
        string='Show Project Breakdown',
        default=True,
        help="Show per-project lines in the report",
    )
    show_type_breakdown = fields.Boolean(
        string='Show Activity Type Breakdown',
        default=False,
        help="Show activity type breakdown lines in the report",
    )
    report_color = fields.Char(
        string='Report Color',
        default='#2c3e50',
        help="Left border color in the PDF report (hex code)",
    )
    is_protected = fields.Boolean(default=False, readonly=True)

    @api.constrains('name', 'active')
    def _check_unique_name(self):
        for rec in self:
            if not rec.active:
                continue
            duplicate = self.search_count([
                ('name', '=', rec.name),
                ('id', '!=', rec.id),
                ('active', '=', True),
            ])
            if duplicate:
                raise ValidationError(
                    f'Category "{rec.name}" already exists! Archive or rename the existing one first.'
                )

    def write(self, vals):
        # Protected categories (e.g. Admin) only allow cosmetic changes
        if self.filtered('is_protected'):
            allowed = {'name', 'sequence', 'report_color'}
            if set(vals.keys()) - allowed:
                raise UserError("Admin category core settings cannot be modified.")
        return super().write(vals)

    def unlink(self):
        if any(rec.is_protected for rec in self):
            raise UserError("Admin category cannot be deleted — it's required by the system.")
        return super().unlink()