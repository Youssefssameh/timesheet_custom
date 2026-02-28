# Timesheet Activity Report

An Odoo 17 module that generates professional executive PDF reports from employee timesheets, breaking down logged hours by activity category and type.

---

## Features

- **Executive PDF Report** — clean, per-employee summary with hours and percentages
- **Activity Categories** — classify projects under categories (Billable, Internal, Admin, etc.)
- **Flexible Breakdown** — per category, choose between project breakdown or activity type breakdown
- **Idle Time Detection** — automatically detects and separates idle hours at both project and task level
- **Role-Based Access** — managers can generate reports for any employee; employees can only generate their own
- **Protected Categories** — system categories (e.g. Admin) are protected from accidental deletion or modification
- **Configurable** — fully manageable categories, activity types, sequences, and report colors from the UI

---

## Module Structure

```
timesheet_custom/
├── data/
│   ├── default_categories.xml
│   └── paper_format.xml
├── models/
│   ├── project.py
│   ├── task.py
│   ├── timesheet_activity_category.py
│   └── timesheet_activity_type.py
├── report/
│   ├── timesheet_report_action.xml
│   └── timesheet_report_template.xml
├── security/
│   ├── ir.model.access.csv
│   └── res_groups.xml
├── views/
│   ├── project_views.xml
│   ├── task_views.xml
│   ├── timesheet_config_views.xml
│   └── timesheet_wizard_view.xml
├── wizard/
│   └── timesheet_report_wizard.py
├── __init__.py
└── __manifest__.py
```

---

## Installation

1. Copy the module to your addons directory:
   ```bash
   cp -r timesheet_custom /mnt/extra-addons/
   ```

2. Install via CLI:
   ```bash
   odoo -u timesheet_custom -d <your_db>
   ```

   Or via UI: **Apps → Search "Timesheet Activity Report" → Install**

---

## Dependencies

| Module | Purpose |
|---|---|
| `project` | Project and Task models |
| `hr_timesheet` | Timesheet logging |
| `timesheet_grid` | Validated timesheets support |

---

## Security Groups

| Group | Permissions |
|---|---|
| **Timesheet Employee** | Generate report for themselves only |
| **Timesheet Report Manager** | Generate reports for any employee + Configuration menu |

> Admin is automatically assigned to the Manager group on install.

---

## How It Works

### 1. Setup
- Assign an **Activity Category** to each project via `Project → Settings → Activity Category`
- Assign an **Activity Type** to tasks when the category has `Show Activity Type Breakdown` enabled

### 2. Generate Report
- Go to `Timesheets → Reporting → Executive Report`
- Select employee(s), date range → click **Generate PDF Report**

### 3. Report Logic

```
Timesheet Line
    ↓
Has project?          → No  → Idle
    ↓ Yes
Has category?         → No  → Idle
    ↓ Yes
Category is_idle?     → Yes → Idle
    ↓ No
Task type is_idle?    → Yes → Idle
    ↓ No
show_type_breakdown?
    ├── Yes → Group by Activity Type
    └── No  → Group by Project
```

---

## Default Categories & Types

### Categories

| Name | Breakdown | Color |
|---|---|---|
| Billable | Per Project | `#27ae60` |
| Internal | Per Project | `#2980b9` |
| Admin | Per Activity Type | `#e67e22` |

### Activity Types

Daily Scrum Meetings · Department Meetings · Overall Management · Learning ·
Follow-up Intern Team · Support Tasks · Break / Personal · Public Holiday · Idle *(is_idle)*

---

## Configuration

Navigate to `Timesheets → Configuration` *(Managers only)*:

- **Activity Categories** — manage categories, colors, breakdown mode, idle flag
- **Activity Types** — manage types and idle flag

---

## Author

**Youssef Sameh @ TDS**  
Odoo 17 · LGPL-3
