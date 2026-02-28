from odoo import models, fields


class TimesheetActivityType(models.Model):
    _name = 'timesheet.activity.type'
    _description = 'Timesheet Activity Type'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True, translate=True)
    is_idle = fields.Boolean(
        string='Is Idle',
        default=False,
        help="Hours logged under this type count as Idle Time in the report",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
