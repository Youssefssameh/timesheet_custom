from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    activity_category_id = fields.Many2one(
        'timesheet.activity.category',
        string="Activity Category",
        copy=False,
        tracking=True,
        ondelete='restrict',
        help="Used for timesheet activity reporting",
    )
