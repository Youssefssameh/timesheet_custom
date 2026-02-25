# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProjectProject(models.Model):
    _inherit = "project.project"

    # many2one to be easy to change the category or add (for project and tasks )
    # group report manager 
    # for many employees 
    # count only approved hours not all hours 
    # independent 

    
    x_activity_category = fields.Selection(
        selection=[
            ("billable", "Billable"),
            ("internal", "Internal"),
            ("admin", "Admin"),
        ],
        string="Activity Category",
        copy=False,
        tracking=True,
        help="Used for timesheet activity reporting ",
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Auto-default ONLY if user didn't set it manually
        for vals in vals_list:
            if not vals.get("x_activity_category"):

                partner_id = vals.get("partner_id")
                if partner_id:
                    vals["x_activity_category"] = "billable"
                else:
                    vals["x_activity_category"] = "internal"
        return super().create(vals_list)