import frappe

def execute(filters=None):
    if not filters or not filters.get("period") or not filters.get("fiscal_year"):
        frappe.throw("Please provide a valid period and fiscal year in the filters.")

    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data

def get_columns(filters):
    period_type = filters.get("period")
    columns = [
        {"fieldname": "rejection_type", "label": "Rejection Type", "fieldtype": "Data", "width": 150},
        {"fieldname": "rejection_reason", "label": "Rejection Reason", "fieldtype": "Data", "width": 150}
    ]

    if period_type == "Monthly":
        month_names = ["April", "May", "June", "July", "August", "September", "October", "November", "December", "January", "February", "March"]
        for i, month_name in enumerate(month_names, start=1):
            columns.append({
                "fieldname": f"rejection_qty_m{i}",
                "label": f"{month_name} Rejection Quantity",
                "fieldtype": "Int",
                "width": 120
            })
    elif period_type == "Quarterly":
        quarters = [
            ("April - July", 4, 7),
            ("August - November", 8, 11),
            ("December - March", 12, 3)
        ]
        for i, (label, _, _) in enumerate(quarters, start=1):
            columns.append({
                "fieldname": f"rejection_qty_q{i}",
                "label": f"{label} Rejection Quantity",
                "fieldtype": "Int",
                "width": 120
            })
    elif period_type == "Half Yearly":
        half_years = [
            ("April - September", 4, 9),
            ("October - March", 10, 3)
        ]
        for i, (label, _, _) in enumerate(half_years, start=1):
            columns.append({
                "fieldname": f"rejection_qty_h{i}",
                "label": f"{label} Rejection Quantity",
                "fieldtype": "Int",
                "width": 120
            })
    elif period_type == "Yearly":
        columns.append({
            "fieldname": "rejection_qty_year",
            "label": "Yearly Rejection Quantity",
            "fieldtype": "Int",
            "width": 120
        })
    else:
        raise ValueError("Invalid period type")

    return columns

def get_data(filters):
    period_type = filters.get("period")
    fiscal_year = filters.get("fiscal_year")

    if not fiscal_year or len(fiscal_year) != 4:
        frappe.throw("Fiscal year must be a 4-digit string, e.g., '2324'.")

    start_year = int("20" + fiscal_year[:2])
    end_year = int("20" + fiscal_year[2:])

    conditions = "WHERE m.docstatus = 1"

    if filters.get("company"):
        conditions += " AND m.company = %(company)s"

    if fiscal_year:
        conditions += f" AND ((YEAR(m.date) = {start_year} AND MONTH(m.date) >= 4) OR (YEAR(m.date) = {end_year} AND MONTH(m.date) <= 3))"

    select_periods = []

    if period_type == "Monthly":
        for i in range(1, 13):
            month_index = (i + 3) % 12 + 1
            select_periods.append(f"SUM(CASE WHEN MONTH(m.date) = {month_index} THEN mr.rejection_qty ELSE 0 END) AS rejection_qty_m{i}")
    elif period_type == "Quarterly":
        quarters = [
            (4, 7),
            (8, 11),
            (12, 3)
        ]
        for i, (start_month, end_month) in enumerate(quarters, start=1):
            if start_month < end_month:
                select_periods.append(f"SUM(CASE WHEN MONTH(m.date) BETWEEN {start_month} AND {end_month} THEN mr.rejection_qty ELSE 0 END) AS rejection_qty_q{i}")
            else:
                select_periods.append(f"SUM(CASE WHEN MONTH(m.date) >= {start_month} OR MONTH(m.date) <= {end_month} THEN mr.rejection_qty ELSE 0 END) AS rejection_qty_q{i}")
    elif period_type == "Half Yearly":
        half_years = [
            (4, 9),
            (10, 3)
        ]
        for i, (start_month, end_month) in enumerate(half_years, start=1):
            if start_month < end_month:
                select_periods.append(f"SUM(CASE WHEN MONTH(m.date) BETWEEN {start_month} AND {end_month} THEN mr.rejection_qty ELSE 0 END) AS rejection_qty_h{i}")
            else:
                select_periods.append(f"SUM(CASE WHEN MONTH(m.date) >= {start_month} OR MONTH(m.date) <= {end_month} THEN mr.rejection_qty ELSE 0 END) AS rejection_qty_h{i}")
    elif period_type == "Yearly":
        select_periods.append("SUM(mr.rejection_qty) AS rejection_qty_year")

    query = f"""
    SELECT
        mr.rejection_type AS rejection_type,
        mr.rejection_reason AS rejection_reason,
        {', '.join(select_periods)}
    FROM `tabMachining` m
    LEFT JOIN `tabMachining Rejection Reasons Details` mr ON m.name = mr.parent
    {conditions}
    GROUP BY mr.rejection_type, mr.rejection_reason
    """

    data = frappe.db.sql(query, filters, as_dict=True)

    # Apply grouping logic based on filters
    if filters.get("based_on") == "Rejection Reason" and filters.get("group_by") == "Rejection Reason":
        data = group_by_item(data)
    elif filters.get("based_on") == "Rejection Reason" and filters.get("group_by") == "Rejection Type":
        data = group_by_item_group(data)

    return data

def group_by_item(data):
    grouped_data = {}

    for row in data:
        rejection_type = row['rejection_type']
        if rejection_type not in grouped_data:
            grouped_data[rejection_type] = []
        grouped_data[rejection_type].append(row)

    # Prepare result with group totals at the top
    result = []
    for rejection_type, rows in grouped_data.items():
        # Add group total at the top
        group_total = {
            'rejection_type': f"Total for Group: {rejection_type}",
            'rejection_reason': "",
        }
        for key in rows[0]:
            if key.startswith("rejection_qty_"):
                group_total[key] = sum(row[key] for row in rows if row[key] is not None)
        
        result.append(group_total)

        # Add individual rows below the group total
        result.extend(rows)

    return result

def group_by_item_group(data):
    grouped_data = {}

    for row in data:
        rejection_reason = row['rejection_reason']
        if rejection_reason not in grouped_data:
            grouped_data[rejection_reason] = []
        grouped_data[rejection_reason].append(row)

    # Prepare result with item totals at the top
    result = []
    for rejection_reason, rows in grouped_data.items():
        # Add item total at the top
        item_total = {
            'rejection_reason': f"Total for Item: {rejection_reason}",
        }
        for key in rows[0]:
            if key.startswith("rejection_qty_"):
                item_total[key] = sum(row[key] for row in rows if row[key] is not None)
        
        result.append(item_total)

        # Add individual rows below the item total
        result.extend(rows)

    return result
