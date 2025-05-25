# Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MachineShopDrawingMaster(Document):
	
	def validate(self):
		self.check_enabled_item()

	def check_enabled_item(self):
		if self.default and frappe.db.exists("MachineShop Drawing Master",{"company":self.company,"item_code":self.item_code,"default":True,"name":["!=",self.name]}):
			frappe.throw(f"Multiple Item Code <b>{self.item_code}</b> cannot be Default at once")
   
	@frappe.whitelist()
	def before_save(self):
		if self.default:
			frappe.db.set_value("Item", self.item_code, {
				'custom_machineshop': 1,
				'custom_machining_draw': self.name,
				"custom_machine_drawing_no":self.drawing_number,
				'custom_machining_revision': self.revision_no
			})
			