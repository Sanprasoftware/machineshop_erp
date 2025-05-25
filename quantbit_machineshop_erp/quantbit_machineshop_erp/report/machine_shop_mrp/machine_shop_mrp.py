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
        {"fieldname": "company", "fieldtype": "Data", "label": "Company", "width": 250},
        {"fieldname":"delivery_date", "fieldtype":"Date","label":"Delivery Date", "width" : 100},
        {"fieldname": "sales_order", "fieldtype": "Data", "label": "Sales Order", "width": 150},
        {"fieldname": "finished_item_code", "fieldtype": "Data", "label": "Finished Item Code", "width": 150},
        {"fieldname": "quantity", "fieldtype": "Int", "label": "Finished Quantity", "width": 50},
		{"fieldname": "row_type", "fieldtype": "Data", "label": "Raw Item Type", "width": 200},
        {"fieldname": "raw_item_code", "fieldtype": "Data", "label": "Raw Item Code", "width": 150},
		{"fieldname": "raw_item_name", "fieldtype": "Data", "label": "Raw Item Name", "width": 200},
        {"fieldname": "row_quantity", "fieldtype": "Int", "label" : "Raw Item Quantity", "width" : 50},
        {"fieldname": "total_raw_item_quantity", "fieldtype": "Int", "label": "Total Raw Item Quantity", "width": 50},
	]


def get_data(filters=None):
	if not filters:
		filters = {}

	conditions = []
	values = {}

	if filters.get("company"):
		conditions.append("ms.company = %(company)s")
		values["company"] = filters["company"]

	if filters.get("from_date") and filters.get("to_date"):
		conditions.append("soi.delivery_date BETWEEN %(from_date)s AND %(to_date)s")
		values["from_date"] = filters["from_date"]
		values["to_date"] = filters["to_date"]

	where_clause = f" {' AND '.join(conditions)}" if conditions else ""

	query = f"""
		SELECT
			ms.company,
			soi.parent AS sales_order,
			soi.delivery_date,
			soi.qty AS quantity,
			ms.finished_item_code,
			ms.raw_item as raw_item_code,
			'Machining Row' as row_type,
			ms.required_qty AS row_quantity,
			ms.raw_item_name AS raw_item_name,
			(soi.qty * ms.required_qty) AS total_raw_item_quantity
		FROM `tabSales Order Item` soi
		JOIN  `tabMachineShop Processflow` ms ON ms.finished_item_code = soi.item_code
		WHERE {where_clause} AND ms.is_enable = 1
		ORDER BY soi.delivery_date ASC
	"""

	data_1 = frappe.db.sql(query, values, as_dict=True)

	query = f"""
		SELECT
			ms.company,
			soi.parent AS sales_order,
			soi.delivery_date,
			soi.qty AS quantity,
			ms.finished_item_code,
			mdpd.raw_item_code,
			'Downstream Row' as row_type,
			mdpd.quantity AS row_quantity,
			mdpd.raw_item_name AS raw_item_name,
			(soi.qty * mdpd.quantity) AS total_raw_item_quantity
		FROM `tabSales Order Item` soi
		JOIN `tabMachineShop Processflow` ms  ON ms.finished_item_code = soi.item_code
		JOIN `tabMachineShop Downstream Process Details` mdpd ON ms.name = mdpd.parent
		WHERE {where_clause} AND ms.is_enable = 1
		ORDER BY soi.delivery_date ASC
	"""

	data_2 = frappe.db.sql(query, values, as_dict=True)
	data = data_1 + data_2

	return data
