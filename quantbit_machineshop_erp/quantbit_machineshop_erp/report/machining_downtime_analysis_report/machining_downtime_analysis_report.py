import frappe
from frappe import _
from datetime import timedelta, datetime

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        {"label": _("Downtime Reason"), "fieldname": "downtime_reason", "fieldtype": "Data", "width": 200},
        {"label": _("Machine"), "fieldname": "machine", "fieldtype": "Data", "width": 150},
        {"label": _("Time"), "fieldname": "time", "fieldtype": "Data", "width": 100},
        {"label": _("Breakdown Reason"), "fieldname": "breakdown_reason", "fieldtype": "Check", "width": 120},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Data", "width": 150}
       
    ]

def get_data(filters):
    data = frappe.db.sql("""
        SELECT 
            mdr.downtime_reason AS downtime_reason,
            mdr.machine AS machine,
            mdr.time AS time,
            mdr.is_break_down_reason AS breakdown_reason,
            md.company AS company
        FROM `tabMachining` md
        LEFT JOIN `tabMachining Downtime Reasons Details` mdr ON md.name = mdr.parent
        WHERE md.company = %(company)s 
        AND md.date BETWEEN %(from_date)s AND %(to_date)s
    """, filters, as_dict=True)

    return data
