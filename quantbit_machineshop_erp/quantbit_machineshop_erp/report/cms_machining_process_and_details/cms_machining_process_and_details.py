# Copyright (c) 2025, Quantbit Technlogies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"fieldname": "machine_name", "fieldtype": "Data", "label": "Machine Name", "width":100},
        {"fieldname": "operator_name", "fieldtype": "Data", "label": "Operator Name", "width": 200},
        {"fieldname": "date", "fieldtype": "Date", "label": "Date", "width": 100},
		{"fieldname":"shift", "fieldtype":"Data","label":"Shift", "width" : 100},
        {"fieldname": "machining_operation", "fieldtype": "Data", "label": "Machining Operation", "width": 100},
        {"fieldname": "raw_item_name", "fieldtype": "Data", "label": "Raw Item Name", "width": 150},
        {"fieldname": "drg_no", "fieldtype": "Data", "label": "Drawing No", "width": 100},
        {"fieldname": "item_description", "fieldtype": "Data", "label": "Item Description", "width": 100},
        {"fieldname": "casting_sl_no", "fieldtype": "Data", "label": "Casting Sl No", "width": 100},
        {"fieldname": "machining_hrs", "fieldtype": "Float", "label": "Machining Hrs", "width": 100},
        {"fieldname": "insert_name", "fieldtype": "Data", "label": "Insert Name", "width": 100},
        {"fieldname": "insert_consumption_qty", "fieldtype": "Int", "label": "Insert Consumption Qty (Nos) As Per Norms", "width": 100},
        {"fieldname": "insert_consumption_qty_actual_consume", "fieldtype": "Int", "label": "Insert Consumption Qty (Nos) Actual Consume", "width": 100},
        {"fieldname": "remarks", "fieldtype": "Data", "label": "Remarks", "width": 100},
	]


def get_data(filters=None):
    if not filters:
        filters = {}

    conditions = ["m.docstatus = 1"]
    values = {}
	
    if filters.get("company"):
        conditions.append("m.company = %(company)s")
        values["company"] = filters["company"]    

    if filters.get("raw_item_code"):
        conditions.append("mo.raw_item_code = %(raw_item_code)s")
        values["raw_item_code"] = filters["raw_item_code"]

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("m.date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = filters["from_date"]
        values["to_date"] = filters["to_date"]

    if filters.get("raw_item_serial_no"):
        serial_nos = filters["raw_item_serial_no"].split(",")
        serial_conditions = []

    

        for i, serial_no in enumerate(serial_nos):
            key = f"raw_item_serial_no_{i}"
            serial_conditions.append(f"FIND_IN_SET(%({key})s, mo.raw_item_serial_no) > 0")
            values[key] = serial_no

        conditions.append(f"({' OR '.join(serial_conditions)})")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""


    query = f"""
        SELECT  
            m.operator_name,  
            m.shift_time AS shift,  
            m.date,  
            m.total_working_hours AS machining_hrs, 
            mo.operation_name AS machining_operation,  
            mo.machine AS machine_name,  
            mo.raw_item_name AS raw_item_name,  
            mo.raw_item_code,  
            mo.raw_item_serial_no AS casting_sl_no,  
            i.custom_machine_drawing_no AS drg_no,  
            i.description AS item_description,  
            mtd.raw_item_name AS insert_name,
            mtd.required_quantity AS insert_consumption_qty,
            mtd.used_quantity AS insert_consumption_qty_actual_consume

        FROM  
            `tabMachining` AS m  
        LEFT JOIN  
            `tabMachining Operation Details` AS mo ON m.name = mo.parent 
        LEFT JOIN
            `tabMachining Tooling Details` AS mtd ON m.name = mtd.parent 
        LEFT JOIN  
            `tabItem` AS i ON mo.raw_item_name = i.item_name  
        
        {where_clause};
        
    """

    return frappe.db.sql(query, values, as_dict=True)