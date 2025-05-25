# Copyright (c) 2025, Quantbit Technlogies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters)
    # frappe.throw(str(data))
    return columns, data


def get_columns():
    return [
        {"fieldname": "sales_order", "fieldtype": "Data", "label": "Sales Order", "width":100},
        {"fieldname": "finished_item_code", "fieldtype": "Data", "label": "Finished Item Code", "width": 200},
        {"fieldname": "finished_item_name", "fieldtype": "Data", "label": "Finished Item Name", "width": 200},
		{"fieldname":"delivery_date", "fieldtype":"Date","label":"Delivery Date", "width" : 100},
        {"fieldname": "raw_item", "fieldtype": "Data", "label": "Raw Item Code", "width": 100},
        {"fieldname": "raw_item_name", "fieldtype": "Data", "label": "Raw Item Name", "width": 150},
        {"fieldname": "operation", "fieldtype": "Data", "label": "Operation Code", "width": 100},
        {"fieldname": "operation_name", "fieldtype": "Data", "label": "Operation Name", "width": 100},
        {"fieldname": "quantity", "fieldtype": "Int", "label": "Quantity", "width": 100},
        {"fieldname": "actual_quantity", "fieldtype": "Int", "label": "Actua Quantity", "width": 100},
        {"fieldname": "machine_type", "fieldtype": "Data", "label": "Machine Type", "width": 100},
        {"fieldname": "cycle_time", "fieldtype": "Float", "label": "Cycle Time Per Machine", "width": 100},
        {"fieldname": "setup_time_in_min", "fieldtype": "Float", "label": "Setup Time Per Machine", "width": 100},
        {"fieldname": "total_time", "fieldtype": "Float", "label": "Total Time", "width": 100},
        {"fieldname": "company", "fieldtype": "Data", "label": "Company", "width": 200},
	]


def get_data(filters=None):
    if not filters:
        filters = {}

    conditions = []
    values = {}
	
    if filters.get("company"):
        conditions.append("so.company = %(company)s")
        values["company"] = filters["company"]

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("soi.delivery_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = filters["from_date"]
        values["to_date"] = filters["to_date"]

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            so.company,  
            so.name AS sales_order,  
            soi.delivery_date,
            ms.finished_item_code,
            ms.finished_item_name,
            ms.raw_item,
            ms.raw_item_name,
            soi.item_code AS raw_item,
            soi.item_name AS raw_item_name,
            soi.item_code AS finished_item_code,
            soi.item_name AS finished_item_name,
            soi.qty AS quantity,
            mop.operation,
            mop.operation_name,
            mop.machine_type,
            mop.cycle_time,
            mop.setup_time_in_min,
            ((soi.qty * mop.cycle_time) + mop.setup_time_in_min) AS total_time
        FROM `tabSales Order` so 
        LEFT OUTER JOIN `tabSales Order Item` soi ON so.name = soi.parent 
        LEFT OUTER JOIN `tabMachineShop Processflow` ms ON ms.finished_item_code = soi.item_code
        LEFT OUTER JOIN `tabMachining Operation Plan` mop ON ms.name = mop.parent
        {where_clause}
        ORDER BY soi.delivery_date ASC;

    """

    return frappe.db.sql(query, values, as_dict=True)