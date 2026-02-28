{
    "name": "Timesheet Activity Report",
    "version": "17.0.1.0.0",
    "summary": "Executive PDF report breaking down employee timesheets by activity category and type",
    "description": """
Timesheet Activity Report
=========================
Generates a per-employee executive PDF report from logged timesheets.

Features:
- Categorize projects under activity categories (Billable, Internal, Admin, etc.)
- Break down hours per project or per activity type per category
- Idle time detection at both project and task level
- Role-based access: managers see all employees, employees see only themselves
- Configurable categories and activity types with sequence and color support
- Protected system categories to prevent accidental deletion or modification
    """,
    "category": "Services/Timesheets",
    "author": "Youssef Sameh @ TDS",
    "website": "",
    "license": "LGPL-3",
    "depends": [
        "project",
        "hr_timesheet",
        "timesheet_grid",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/paper_format.xml",
        "data/default_categories.xml",
        "views/project_views.xml",
        "views/task_views.xml",
        "views/timesheet_config_views.xml",
        "views/timesheet_wizard_view.xml",
        "report/timesheet_report_action.xml",
        "report/timesheet_report_template.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
