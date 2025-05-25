import frappe
from frappe.utils import getdate

def execute(filters=None):
    if not filters:
        filters = {}

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    company = filters.get("company")
    
    # if not (start_date and end_date and company):
    #     frappe.throw("Please select Start Date, End Date, and Company")
        
# -------------------------------------------------------------------------------------------------

    # holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")

    
    # holiday_count = frappe.db.count("Holiday", 
    #     filters={"parent": holiday_list, "holiday_date": ["between", [start_date, end_date]]}
    # )
    
    
# ----------------------------------------------------------------------------------------
    
   # Fetch holiday count
    holiday_count_result = frappe.db.sql("""
        SELECT COUNT(*) as holiday_count
        FROM `tabHoliday` h 
        JOIN `tabHoliday List` hl ON h.parent = hl.name 
        WHERE hl.name = (SELECT default_holiday_list 
                         FROM `tabCompany` c
                         WHERE c.name = %(company)s) 
        AND h.holiday_date BETWEEN %(start_date)s AND %(end_date)s
        """, {"start_date": start_date, "end_date": end_date, "company": company}, as_dict=True)

    #  holiday count
    holiday_count = holiday_count_result[0]["holiday_count"] if holiday_count_result else 0


# -------------------------------------------------------------------------------------------

  
    total_days = (getdate(end_date) - getdate(start_date)).days + 1
    # frappe.msgprint(str(holiday_count_result[0]["holiday_count"]))
    # frappe.msgprint(str(holiday_count))
    
    working_days = total_days - holiday_count
    
    
    data = frappe.db.sql(
        """
        SELECT 
            mo.machine_name AS "Machine Name", mo.machine_type as "Machine Type",
            ((1440 - (mo.average_downtime) / 60)) * (
                %(working_days)s
            ) AS machine_required_time
        FROM `tabMachineShop Machine` mo
        GROUP BY mo.machine_name
        """, {"start_date": start_date,"end_date":end_date,"company":company,"working_days":working_days}, as_dict=True
    )

    # Append holiday count and working days to each row
    
    for row in data:
        row["holidays"] = holiday_count  
        row["working_days"] = working_days 
        row["total_days"]=total_days

    columns = [
        {"fieldname": "Machine Name", "label": "Machine Name", "fieldtype": "Data", "width": 150},
        {"fieldname": "Machine Type", "label": "Machine Type", "fieldtype": "Data", "width": 150},
        {"fieldname": "total_days", "label": "Total Days", "fieldtype": "Float", "width": 100},
         {"fieldname": "holidays", "label": "Holidays", "fieldtype": "Float", "width": 100},
         {"fieldname": "working_days", "label": "Working Days", "fieldtype": "Float", "width": 150},
        {"fieldname": "machine_required_time", "label": "Machine Available Time", "fieldtype": "Float", "width": 180},
       
    ]
    
    return columns, data

