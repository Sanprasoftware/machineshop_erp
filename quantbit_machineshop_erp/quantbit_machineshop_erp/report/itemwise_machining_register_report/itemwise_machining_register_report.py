# Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
# For license information, please see license.txt
import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        {"label": "Operation", "fieldname": "operation", "fieldtype": "Data", "width": 150},
        {"label": "Operation Name", "fieldname": "operation_name", "fieldtype": "Data", "width": 150},
        {"label": "Finished Item Code", "fieldname": "finished_item_code", "fieldtype": "Data", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": "Machine", "fieldname": "machine", "fieldtype": "Data", "width": 150},
        {"label": "Machine Type", "fieldname": "machine_type", "fieldtype": "Data", "width": 150},
        {"label": "Cycle Time", "fieldname": "cycle_time", "fieldtype": "Float", "width": 100},
        {"label": "Boring", "fieldname": "boring", "fieldtype": "Data", "width": 100},
        {"label": "MR Quantity", "fieldname": "mr_qty", "fieldtype": "Int", "width": 100},
        {"label": "MR Weight", "fieldname": "mr_weight", "fieldtype": "Float", "width": 100},
        {"label": "CR Quantity", "fieldname": "cr_qty", "fieldtype": "Int", "width": 100},
        {"label": "CR Weight", "fieldname": "cr_weight", "fieldtype": "Float", "width": 100},
        {"label": "OK Quantity", "fieldname": "ok_qty", "fieldtype": "Int", "width": 100},
        {"label": "OK Weight", "fieldname": "ok_weight", "fieldtype": "Float", "width": 100},
        {"label": "RW Quantity", "fieldname": "rw_qty", "fieldtype": "Int", "width": 100},
        {"label": "RW Weight", "fieldname": "rw_weight", "fieldtype": "Float", "width": 100},
        {"label": "OR1 Quantity", "fieldname": "or1_qty", "fieldtype": "Int", "width": 100},
        {"label": "OR2 Quantity", "fieldname": "or2_qty", "fieldtype": "Int", "width": 100},
        {"label": "Total Quantity", "fieldname": "total_quantity", "fieldtype": "Int", "width": 100},
        {"label": "Total Weight", "fieldname": "total_weight", "fieldtype": "Float", "width": 100}
    ]

def get_data(filters):
    conditions = []
    values = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date")
    }

    if filters.get("company"):
        companies = ", ".join([f"'{c}'" for c in filters.get("company")])
        conditions.append(f"m.company IN ({companies})")
    if filters.get("operation"):
        operations = ", ".join([f"'{op}'" for op in filters.get("operation")])
        conditions.append(f"ms.operation IN ({operations})")
    if filters.get("item"):
        item_codes = ", ".join([f"'{item}'" for item in filters.get("item")])
        conditions.append(f"mf.finished_item_code IN ({item_codes})")


    conditions = " AND ".join(conditions)

    query = f"""
        SELECT
            ms.operation,
            ms.operation_name,
            mf.finished_item_code,
            mf.item_name,
            ms.machine,
            ms.machine_type,
            ms.cycle_time,
            ms.boring,
            ms.mr_qty,
            ms.mr_weight,
            ms.cr_qty,
            ms.cr_weight,
            ms.ok_qty,
            ms.ok_weight,
            ms.rw_qty,
            ms.rw_weight,
            ms.or1_qty,
            ms.or2_qty,
            ms.total_quantity,
            ms.total_weight
        FROM `tabMachining` m
        LEFT JOIN `tabMachining Operation Details` ms ON m.name = ms.parent
        LEFT JOIN `tabMachining Finished Item Details` mf ON m.name = mf.parent
        WHERE m.date BETWEEN %(from_date)s AND %(to_date)s
        AND m.docstatus = 1
        {f"AND {conditions}" if conditions else ""}
    """
    results = frappe.db.sql(query, values, as_dict=True)
    for row in results:
        for key in row:
            if "weight" in key and row[key] is not None:
                row[key] = round(row[key], 2)
            elif "qty" in key and row[key] is not None:
                row[key] = int(row[key])
    return results
