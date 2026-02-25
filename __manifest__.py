{
    "name": "Timesheet Activity Report",
    "version": "17.0.1.0.0",
    "summary": "Executive activity report from timesheets",
    "category": "Services/Timesheets",
    "author": "TDS",
    "license": "LGPL-3",
    "depends": [
        "project",
        "hr_timesheet",
        "timesheet_grid",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/paper_format.xml",
        "views/project_views.xml",
        "views/task_views.xml",
        "views/timesheet_wizard_view.xml",
        "report/timesheet_report_action.xml",
        "report/timesheet_report_template.xml",
    ],
    "installable": True,
    "application": False,
}
