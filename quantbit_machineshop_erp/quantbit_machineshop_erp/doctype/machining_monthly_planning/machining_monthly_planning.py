# Copyright (c) 2025, Quantbit Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import calendar
from frappe.utils import get_link_to_form
import math

def getval(value):
    return value if value else 0

class MachiningMonthlyPlanning(Document):
    def set_table(self ,table ,data_in , data_check = None , data_update = None):
        if not data_check:
            data_check = data_in

        table_data_check = self.get(table , filters= data_check)
        if table_data_check:
            if data_update:
                for d in table_data_check:
                    for key , value in data_update.items():
                        d.set(key, value )
        else:
            self.append(table,data_in)
               
    @frappe.whitelist()
    def before_save(self):
        pass

    @frappe.whitelist()
    def get_machine_data(self):
        if getattr(self, "__unsaved", 0):
            frappe.throw("Please save the document before getting Machine Availability.")

        if not self.month or not self.year or not self.company:
            frappe.throw("Please select Month, Year, and Company.")

        month_num = list(calendar.month_name).index(self.month)
        total_days = calendar.monthrange(int(self.year), month_num)[1]

        holiday_count = frappe.db.count("Holiday", {
                                                        "parent": frappe.db.get_value("Company", self.company, "default_holiday_list"),
                                                        "holiday_date": ["between", [f"{self.year}-{month_num}-01", f"{self.year}-{month_num}-{total_days}"]]
                                                    })
        working_days = total_days - holiday_count

        machineshop_machine_type = frappe.get_all("MachineShop Machine Type" , filters = {'company':self.company})
        data = frappe.db.exists("Machining Monthly Planning Setting",self.company)
        if not data:
            frappe.throw("Please set 'Machining Monthly Planning Setting'")

        mmps = frappe.get_doc("Machining Monthly Planning Setting",self.company)

                
        for i in machineshop_machine_type:
            mtype = frappe.get_doc("MachineShop Machine Type", i.name)
            query = f"""
                        SELECT ims.planned_quantity , mop.cycle_time , SUM(ims.planned_quantity * mop.cycle_time ) as total_cycle_time
                        FROM `tabItem Machining Schedule` ims
                        INNER JOIN `tabMachineShop Processflow` msp ON ims.machineshop_processflow = msp.name
                        LEFT JOIN `tabMachining Operation Plan` mop ON msp.name = mop.parent
                        WHERE msp.company = '{self.company}' AND ims.parent = '{self.name}'
                        AND mop.machine_type = '{i.name}'
                        GROUP BY ims.machineshop_processflow
                    """
            machines = frappe.db.sql(query, as_dict=True)
            estimeted_absenteeism_percentage = mtype.estimeted_absenteeism_percentage if mmps.enable_estimeted_absenteeism_percentage else mmps.estimeted_absenteeism_percentage
            estimeted_maintenance_percentage = mtype.estimeted_maintenance_percentage if mmps.enable_estimeted_maintenance_percentage else mmps.estimeted_maintenance_percentage
            other_total_time = mtype.other_total_time if mmps.enable_other_total_time else mmps.other_total_time
            estimeted_electricity_downtime = mtype.estimeted_electricity_downtime if mmps.enable_estimeted_electricity_downtime else mmps.estimeted_electricity_downtime
            estimeted_daily_downtime = mtype.estimeted_daily_downtime if mmps.enable_estimeted_daily_downtime else mmps.estimeted_daily_downtime
               
            total_booked_minutes = 0
            for j in machines:
                total_booked_minutes = j.total_cycle_time
            total_booked_hours = total_booked_minutes/60
            
            absenteeism_reduction = (estimeted_absenteeism_percentage * working_days /100)
            total_working_days = working_days - absenteeism_reduction
            estimeted_working_hours = total_working_days * (24-((estimeted_daily_downtime/60) or 0))
            estimeted_working_minutes = estimeted_working_hours * 60
            

            maintenance_reduction = (estimeted_maintenance_percentage * working_days /100)
            electricity_downtime = (estimeted_electricity_downtime)
            other_reduction = (other_total_time )

            total_working_minutes = estimeted_working_minutes - (maintenance_reduction + electricity_downtime + other_reduction)
            total_booked_percentage = (total_booked_minutes * 100) / total_working_minutes
            self.set_table('machine_availability',  {
                                                        'machine_type': i.name,
                                                        'total_working_days': total_working_days,
                                                        'estimeted_working_hours': estimeted_working_hours,
                                                        'estimeted_working_minutes': estimeted_working_minutes,
                                                        'total_working_minutes': total_working_minutes,
                                                        'total_booked_minutes':total_booked_minutes,
                                                        'total_booked_hours':total_booked_hours,
                                                        'total_booked_percentage':total_booked_percentage,
                                                        'maintenance_reduction':maintenance_reduction,
                                                        'electricity_downtime': electricity_downtime,
                                                        'other_reduction':other_reduction,
                                                        'absenteeism_reduction':absenteeism_reduction
                                                    })

    @frappe.whitelist()
    def get_data(self):
        self.__unsaved = 0       
        casting_rejection_percentage = frappe.get_value("Machining Monthly Planning Setting",self.company,['casting_rejection_percentage']) or 0
        
        month_num = list(calendar.month_name).index(self.month)  # Convert "January" → 1

        total_days = calendar.monthrange(int(self.year), month_num)[1]  # Get total days in the selected month
        
        start_date = f"{self.year}-{month_num:02d}-01"
        last_date = f"{self.year}-{month_num:02d}-{total_days}"
        
        
        query = """
            SELECT 
                msp.finished_item_code, msp.finished_item_name, msp.company, mop.machine_type,SUM(mop.cycle_time) AS total_cycle_time,
                soi.delivery_date, soi.custom_job_work_item_code as item_code , soi.qty, soi.parent AS sales_order , so.transaction_date,msp.name AS msp
            FROM `tabMachineShop Processflow` msp
            INNER JOIN `tabMachining Operation Plan` mop ON mop.parent = msp.name
            INNER JOIN `tabSales Order Item` soi ON msp.finished_item_code = soi.custom_job_work_item_code
            INNER JOIN `tabSales Order` so ON so.name = soi.parent
            WHERE msp.company = %(company)s
            AND so.company = %(company)s
            AND msp.is_enable = 1 AND so.docstatus = 1
            AND soi.delivery_date BETWEEN %(start_date)s AND %(last_date)s
            GROUP BY msp.finished_item_code, soi.delivery_date, soi.qty, soi.parent
            ORDER BY soi.delivery_date , so.transaction_date
        """
        
        result = frappe.db.sql(query, {"company": self.company, "start_date": start_date, "last_date": last_date}, as_dict=True)
        
        for i in result:
            item_data = frappe.get_value("Item" , i.finished_item_code , ['stock_uom' , 'custom_machine_drawing_no'], as_dict = True)
            ordered_quantity = i.qty
            estimated_rejection_quantity = math.ceil((casting_rejection_percentage * i.qty)/100)
            self.append("item_machining_schedule",{
                "sales_order" : i.sales_order,
                "item_code": i.finished_item_code,
                "item_name": i.finished_item_name,
                "delivery_date":i.delivery_date,
                "ordered_quantity": ordered_quantity,
                "estimated_rejection_quantity": estimated_rejection_quantity ,
                "scheduled_quantity":ordered_quantity + estimated_rejection_quantity,
                "uom":item_data.stock_uom,
                "drg_no": item_data.custom_machine_drawing_no,
                "machineshop_processflow":i.msp

            })
        self.settle_available_quantity()

    @frappe.whitelist()
    def settle_available_quantity(self):
        warehouse = frappe.get_all("Machining Monthly Planning Setting Warehouse Details" , {"parent": self.company } , ['warehouse'] , pluck = 'warehouse')
        if not warehouse:
            frappe.throw(f"Please set warehouse on 'Machining Monthly Planning Setting' to get available quantity from")

        item_machining_schedule = self.get('item_machining_schedule')
        bin_data = {}
        
        for i in item_machining_schedule :
            if i.item_code in bin_data:
                available_quantity = getval(bin_data[i.item_code])
            else:
                available_quantity = getval(frappe.get_value("Bin", {"item_code": i.item_code , "warehouse": ['in', warehouse]}, "SUM(actual_qty)"))

            if i.scheduled_quantity >= available_quantity:
                i.available_quantity = available_quantity
                bin_data[i.item_code] = 0
            else:
                i.available_quantity = i.scheduled_quantity
                bin_data[i.item_code] = available_quantity- i.scheduled_quantity
                
            
            i.planned_quantity = i.scheduled_quantity - i.available_quantity


            
    # @frappe.whitelist()

# frappe.throw(f'party {get_link_to_form("Farmer List",i.party_code)} not have add any "Active" as well as "Approved" bank for vendor type "Farmer"')
        