from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    show_activity_type = fields.Boolean(
        related='project_id.activity_category_id.show_type_breakdown',
        store=False,
    )

    x_activity_type_id = fields.Many2one(
        'timesheet.activity.type',
        string="Activity Type",
        copy=False,
        ondelete='restrict',
        help="Used for Admin breakdown and Idle time in the report.",
    )