from frappe import _
from frappe.utils import flt
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": _("Machining ID"), "fieldname": "machining_id", "fieldtype": "Data", "width": 150},
        {"label": _("Total Ok Quantity"), "fieldname": "total_ok_qty", "fieldtype": "Int", "width": 150},
        {"label": _("Total CR Quantity"), "fieldname": "total_cr_qty", "fieldtype": "Int", "width": 150},
        {"label": _("Total MR Quantity"), "fieldname": "total_mr_qty", "fieldtype": "Int", "width": 150},
        {"label": _("Total RW Quantity"), "fieldname": "total_rw_qty", "fieldtype": "Int", "width": 150},
        {"label": _("OK Weight"), "fieldname": "ok_weight", "fieldtype": "Float", "width": 150},
        {"label": _("CR Weight"), "fieldname": "cr_weight", "fieldtype": "Float", "width": 150},
        {"label": _("MR Weight"), "fieldname": "mr_weight", "fieldtype": "Float", "width": 150},
        {"label": _("RR Weight"), "fieldname": "rr_weight", "fieldtype": "Float", "width": 150},
        {"label": _("Additional Cost"), "fieldname": "additional_cost", "fieldtype": "Currency", "width": 150},
        {"label": _("Shift Time"), "fieldname": "shift_time", "fieldtype": "Data", "width": 120},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Data", "width": 150},
        {"label": _("Operator"), "fieldname": "operator", "fieldtype": "Data", "width": 150},
        {"label": _("Operator Name"), "fieldname": "operator_name", "fieldtype": "Data", "width": 150},
        {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 150},
        {"label": _("Supervisor Name"), "fieldname": "supervisor_name", "fieldtype": "Data", "width": 150}
    ]

def get_data(filters):
    conditions = []

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("m.date BETWEEN %(from_date)s AND %(to_date)s")
    if filters['company']:
        conditions.append("m.company IN %(company)s")
    if filters.get("shift"):
        conditions.append("m.shift_time = %(shift)s")
    if filters.get("operator"):
        operator_list = ",".join([f"'{op}'" for op in filters.get("operator")])
        conditions.append(f"m.operator IN ({operator_list})")
    if filters.get("supervisor"):
        supervisor_list = ",".join([f"'{sup}'" for sup in filters.get("supervisor")])
        conditions.append(f"m.supervisor IN ({supervisor_list})")

    conditions.append("m.docstatus = 1")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT 
            m.date AS posting_date,
            m.name AS machining_id,
            m.total_ok_qty AS total_ok_qty,
            m.total_cr_qty AS total_cr_qty,
            m.total_mr_qty AS total_mr_qty,
            m.total_rw_qty AS total_rw_qty,
            m.total_ok_weight AS ok_weight,
            m.total_cr_weight AS cr_weight,
            m.total_mr_weight AS mr_weight,
            m.total_rw_weight AS rr_weight,
            m.total_additional_cost AS additional_cost,
            m.shift_time AS shift_time,
            m.company AS company,
            m.operator AS operator,
            m.operator_name AS operator_name,
            m.supervisor AS supervisor,
            m.supervisor_name AS supervisor_name
        FROM 
            `tabMachining` m
        WHERE 
            {where_clause}
    """

    return frappe.db.sql(query, filters, as_dict=True)
