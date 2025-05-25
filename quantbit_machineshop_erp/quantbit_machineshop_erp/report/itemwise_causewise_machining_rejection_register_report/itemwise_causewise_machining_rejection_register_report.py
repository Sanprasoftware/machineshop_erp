# Copyright (c) 2024, Quantbit Technlogies Pvt Ltd
# For license information, please see license.txt

from frappe import _
import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    """
    Define the columns for the report.
    """
    return [
        {"label": _("Finished Item Code"), "fieldname": "finished_item", "fieldtype": "Data", "width": 150},
        {"label": _("Finished Item Name"), "fieldname": "finished_item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Operation Code"), "fieldname": "operation_code", "fieldtype": "Data", "width": 150},
        {"label": _("Operation Name"), "fieldname": "operation_name", "fieldtype": "Data", "width": 200},
        {"label": _("Rejection Type"), "fieldname": "rejection_type", "fieldtype": "Data", "width": 150},
        {"label": _("Rejection Reason"), "fieldname": "rejection_reason", "fieldtype": "Data", "width": 200},
        {"label": _("Rejection Quantity"), "fieldname": "rejection_qty", "fieldtype": "Int", "width": 100},
    ]

def get_data(filters):
    """
    Fetch data for the report based on filters.
    """
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw(_("Please set From Date and To Date."))

    conditions = []
    parameters = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
    }

    def format_in_clause(field, values):
        escaped_values = [frappe.db.escape(value) for value in values]
        return f"{field} IN ({', '.join(escaped_values)})"

    if filters.get("company"):
        conditions.append(format_in_clause("m.company", filters["company"]))
    if filters.get("finished_item"):
        conditions.append(format_in_clause("mr.finished_item", filters["finished_item"]))
    if filters.get("rejection_type"):
        conditions.append(format_in_clause("mr.rejection_type", filters["rejection_type"]))
    if filters.get("rejection_reason"):
        conditions.append(format_in_clause("mr.rejection_reason", filters["rejection_reason"]))

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT 
            mr.finished_item AS finished_item,
            mr.finished_item_name AS finished_item_name,
            mr.operation_code AS operation_code,
            mr.operation_name AS operation_name,
            mr.rejection_type AS rejection_type,
            mr.rejection_reason AS rejection_reason,
            mr.rejection_qty AS rejection_qty
        FROM 
            `tabMachining` m
        INNER JOIN 
            `tabMachining Rejection Reasons Details` mr ON m.name = mr.parent
        WHERE 
            m.date BETWEEN %(from_date)s AND %(to_date)s
            {f" AND {where_clause}" if where_clause else ""}
    """

    return frappe.db.sql(query, parameters, as_dict=True)
