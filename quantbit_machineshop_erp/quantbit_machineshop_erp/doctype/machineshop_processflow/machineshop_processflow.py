# Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MachineShopProcessflow(Document):
	def validate(self):
		self.check_enabled_item()
		self.add_materials()
		# self.check_raw_in_downstream()
  
	def check_enabled_item(self):
		if self.is_enable and frappe.db.exists("MachineShop Processflow",{"finished_item_code":self.finished_item_code,"is_enable":1,"name":["!=",self.name],"company":self.company}):
			frappe.throw(f"Multiple Finished Item <b>{self.finished_item_code}</b> cannot be enabled at once")
	
	def add_materials(self):
		flag = True
		for i in self.get("machining_operation_plan"):
			if flag:
				i.raw_material = self.raw_item
				flag = False
			else:
				i.raw_material = self.finished_item_code
    
	# def check_raw_in_downstream(self):
	# 	if any(i.raw_item_code == self.finished_item_code for i in self.get("downstream_process_details")):
	# 		frappe.throw("<b>Raw Item Cannot be equal to Finished Item</b>")
		