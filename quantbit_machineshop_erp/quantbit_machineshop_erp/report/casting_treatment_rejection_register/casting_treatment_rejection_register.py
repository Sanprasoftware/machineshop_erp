from frappe import _
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    grouped_data = group_rows_with_totals(data, filters.get("group_by"))
    return columns, grouped_data

def get_columns():
    return [
        _("Casting Treatment Name") + ":Link/Casting Treatment:150",
        _("Casting Treatment") + "::Data:150",
        _("Casting Item Code") + ":Data:130",
        _("Casting Item Name") + ":Data:150",
        _("Supervisor") + ":Data:120",
        _("Supervisor Name") + ":Data:160",
        _("Heat No") + ":Data:160",
        _("Pouring Supervisor Name") + ":Data:160",
        _("Pouring Operator Name") + ":Data:160",
        _("Rejection Type") + ":Data:120",
        _("Rejection Reason") + ":Data:150",
        _("Quantity") + ":Int:90",
        _("Weight Per Unit") + ":Float:110",
        _("Total Weight") + ":Float:110",
        _("Amount") + ":Currency:150",
        _("Pouring Code") + ":Link/Pouring:120",
        _("Company") + ":Link/Company:120",
    ]

def get_data(filters):
    conditions = []
    filters['company'] = filters.get('company') or []
    filters['supervisor_id'] = filters.get('supervisor_id') or []
    filters['operator_id'] = filters.get('operator_id') or []

    if filters.get("from_date"):
        conditions.append("ct.treatment_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("ct.treatment_date <= %(to_date)s")
    if filters['company']:
        conditions.append("p.company IN %(company)s")
    if filters.get("item_code"):
        conditions.append("ctr.casting_item_code = %(item_code)s")
    if filters.get("casting_treatment"):
        conditions.append("ct.casting_treatment = %(casting_treatment)s")
    if filters.get("supervisor"):
        conditions.append("ct.supervisor_id = %(supervisor)s")
    if filters['supervisor_id']:
        conditions.append("p.supervisor_id IN %(supervisor_id)s")
    if filters['operator_id']:
        conditions.append("p.operator_id IN %(operator_id)s")
    if filters.get("rejection_type"):
        conditions.append("ctr.casting_treatment_rejection_type = %(rejection_type)s")
    if filters.get("rejection_reason"):
        conditions.append("ctr.casting_treatment_rejection_reason = %(rejection_reason)s")

    condition_sql = " AND ".join(conditions)
    if condition_sql:
        condition_sql = "WHERE " + condition_sql

    return frappe.db.sql(f"""
        SELECT
            ct.name AS casting_treatment,
            ct.casting_treatment,
            ctr.casting_item_code,
            ctr.casting_item_name,
            ct.supervisor_id,
            ct.supervisor_name,
            p.heat_number,
            p.supervisor_name,
            p.operator_name,
            ctr.casting_treatment_rejection_type,
            ctr.casting_treatment_rejection_reason,
            SUM(ctr.quantity),
            SUM(ctr.weight),
            SUM(ctr.total_weight),
            SUM(sed_raw.amount),
            ctr.pouring_code,
            ct.company
        FROM
            `tabCasting Treatment` ct
        JOIN
            `tabCasting Treatment Rejected Reasons Details` ctr
                ON ctr.parent = ct.name
        LEFT JOIN 
            `tabPouring` p ON ctr.pouring_code = p.name
        LEFT JOIN 
            `tabStock Entry` se ON ct.name = se.custom_casting_treatment
        LEFT JOIN 
            `tabStock Entry Detail` sed_raw ON se.name = sed_raw.parent 
                                             AND ctr.casting_item_code = sed_raw.item_code
        {condition_sql}
        GROUP BY  ct.name ,
            ct.casting_treatment,
            ctr.casting_item_code,
            ctr.casting_item_name,
            ct.supervisor_id,
            ct.supervisor_name,
            p.heat_number,
            p.supervisor_name,
            p.operator_name,
            ctr.casting_treatment_rejection_type,
            ctr.casting_treatment_rejection_reason
        ORDER BY ct.treatment_date DESC, ct.name DESC
    """, filters, as_list=True)

from collections import defaultdict
def format_rows(data):
    return [format_row(row) for row in data]

def format_row(row):
    new_row = row[:]
    new_row[11] = int(new_row[11] or 0)  # Quantity
    new_row[12] = round(new_row[12] or 0, 2)  # Weight Per Unit
    new_row[13] = round(new_row[13] or 0, 2)  # Total Weight
    return new_row
def group_rows_with_totals(data, group_by):
    if not group_by:
        return format_rows(data)

    group_index = {
        "Rejection Reason": 10,
        "Rejection Type": 9,
        "Item": 2
    }.get(group_by)

    if group_index is None:
        return format_rows(data)

    grouped_map = defaultdict(list)

    for row in data:
        group_value = row[group_index]
        grouped_map[group_value].append(row)

    grouped_data = []

    for group_value in sorted(grouped_map.keys()):
        rows = grouped_map[group_value]
        total_quantity = sum(r[11] or 0 for r in rows)
        total_weight = sum(r[13] or 0 for r in rows)
        total_amount = sum(r[14] or 0 for r in rows)

        grouped_data.append([f"🔹 {group_by}: {group_value}"] + [""] * (len(rows[0]) - 1))

        for r in rows:
            new_row = r[:]
            new_row[group_index] = ""
            grouped_data.append(format_row(new_row))

        grouped_data.append(get_total_row(group_value, total_quantity, total_weight, total_amount))

    return grouped_data



def get_total_row(group_value, total_qty, total_wt, total_amt):
    return [
        "", "", "", "", "", "", "", "", "",
        "", f"Total for {group_value}",  # Group label
        total_qty, "", total_wt, total_amt,
        "", ""
    ]
