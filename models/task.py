# -*- coding: utf-8 -*-
from odoo import fields, models

class ProjectTask(models.Model):
    _inherit = "project.task"

    x_project_category = fields.Selection(
        related='project_id.x_activity_category',
        string="Project Category",
        store=False,
        help="Related to the project category, used for timesheet activity reporting",
        required=True,
    )


    x_activity_type = fields.Selection(
        selection=[
            ("daily_scrum", "Daily Scrum Meetings"),
            ("dept_meeting", "Department Meetings"),
            ("management", "Over All Management"),
            ("learning", "Learning"),
            ("followup_interns", "Follow-up intern team"),
            ("support", "Support tasks"),
            ("break_personal", "Break / Personal (Praying/Eating)"),
            ("public_holiday", "Public Holiday"),
            ("idle", "Idle"),
        ],
        string="Activity Type",
        copy=False,
        help="Used for Administrative & Support breakdown and Idle time in the activity report.",
    )