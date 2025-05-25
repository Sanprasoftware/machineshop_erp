# Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance
# import json
def getval(value):
	return value if value else 0

class Machining(Document):
	def before_submit(self):
		# self.add_stock_entry()
		self.check_serial_no()
		self.manufacturing_stock_entry()
		self.manufacturing_stock_entry_for_in_process()
		self.rejection_stock_entry()


	def check_serial_no(self):
		for i in self.get("machining_operation_details"):
			raw_serial_nos = []
			if i.raw_item_serial_no:
				raw_serial_nos = [sr.strip() for sr in i.raw_item_serial_no.split(",") if sr.strip()]

			finished_serial_nos = []

			if i.mr_serial_no:
				mr_serial_no_lst = [sr.strip() for sr in i.mr_serial_no.split(",") if sr.strip()]
				finished_serial_nos.extend(mr_serial_no_lst)
				if i.mr_qty != len(mr_serial_no_lst):
					frappe.throw(f"MR Quantity {i.mr_quantity} and MR Sr. No count {len(mr_serial_no_lst)} Doesn't match")

			if i.cr_serial_no:
				cr_serial_no_lst = [sr.strip() for sr in i.cr_serial_no.split(",") if sr.strip()]
				finished_serial_nos.extend(cr_serial_no_lst)
				if i.cr_qty != len(cr_serial_no_lst):
					frappe.throw(f"CR Quantity {i.cr_quantity} and CR Sr. No count {len(cr_serial_no_lst)} Doesn't match")

			if i.ok_serial_no:
				ok_serial_no_lst = [sr.strip() for sr in i.ok_serial_no.split(",") if sr.strip()]
				finished_serial_nos.extend(ok_serial_no_lst)
				if i.ok_qty != len(ok_serial_no_lst):
					frappe.throw(f"OK Quantity {i.ok_quantity} and OK Sr. No count {len(ok_serial_no_lst)} Doesn't match")

			if i.rw_serial_no:
				rw_serial_no_lst = [sr.strip() for sr in i.rw_serial_no.split(",") if sr.strip()]
				finished_serial_nos.extend(rw_serial_no_lst)
				if i.rw_qty != len(rw_serial_no_lst):
					frappe.throw(f"RW Quantity {i.rw_quantity} and RW Sr. No count {len(rw_serial_no_lst)} Doesn't match")
			
			if i.in_process_serial_no:
				in_process_serial_no_lst = [sr.strip() for sr in i.in_process_serial_no.split(",") if sr.strip()]
				finished_serial_nos.extend(in_process_serial_no_lst)
				if i.in_process_qty != len(in_process_serial_no_lst):
					frappe.throw(f"In Process Quantity {i.in_process_quantity} and In Process Sr. No count {len(in_process_serial_no_lst)} Doesn't match")

			if not (sorted(raw_serial_nos) == sorted(finished_serial_nos)):
				frappe.throw("Raw Material Sr No. and Finished Material Sr No. Doesn't match")

	
	@frappe.whitelist()
	def append_operations(self, msp=None):
		self.machining_operation_details.clear()
		self.rejected_items_reasons.clear()
		self.machining_tooling_section.clear()
		self.machining_consumable_details.clear()
		if msp:
			for d in msp:
				doc = frappe.get_doc("MachineShop Processflow", d)
				for i in doc.get("machining_operation_plan"):
					finished_item_group,has_serial_no = frappe.get_value("Item", doc.finished_item_code,["item_group", "has_serial_no"]) or (None,None)
					self.append("machining_operation_details", {
						"operation": i.operation,
						"operation_name": i.operation_name,
						"machine_type": i.machine_type,
						"operation_rate": i.operation_rate,
						"cycle_time": i.cycle_time,
						"setup_time_in_min":i.setup_time_in_min or 0,
						"boring": i.boring,
						"source_warehouse": i.source_warehouse,
						"target_warehouse":i.target_warehouse,
						"source_inventory_dimension": i.source_inventory_dimension,
						"target_inventory_dimension": i.target_inventory_dimension or None,
						"raw_item_code": i.raw_material,
						"item": doc.finished_item_code,
						"finished_item_name": doc.finished_item_name,
						"raw_item_name": doc.raw_item_name,
						"available_quantity": get_stock_balance(item_code=doc.finished_item_code, warehouse=i.source_warehouse, posting_date=self.date, posting_time=self.posting_time),
						"machineshop_processflow":doc.name,
						##AV##
						"finished_item_group" :finished_item_group,
						"raw_item_group": frappe.get_value("Item", i.raw_material, "item_group"),
						"has_serial_no": has_serial_no,
						##
					})
	
				for i in doc.get("machineshop_tooling_details"):
					self.append("machining_tooling_section", i)

				for i in doc.get("machineshop_consumable_details"):
					self.append("machining_consumable_details", i)

	@frappe.whitelist()
	def add_rejection_row(self, params):
		no_of_rows = []
		for item in self.get("rejected_items_reasons"):
			if item.rejection_type == params["rejection_type"] and item.finished_item == params["finished_item"] and item.operation_code == params["operation_code"]:
				no_of_rows.append(item)
			
		if len(no_of_rows) > 1:
			for i in no_of_rows:
				self.get("rejected_items_reasons").remove(i)
				
		existing_row = None
		for item in self.get("rejected_items_reasons"):
			if item.rejection_type == params["rejection_type"] and item.finished_item == params["finished_item"] and item.operation_code == params["operation_code"]:
				existing_row = item
				break

		if existing_row:
			for key, value in params.items():
				existing_row.set(key, value)
		else:
			self.append("rejected_items_reasons", params)
	
	@frappe.whitelist()
	def add_downtime_row(self, machine):
		self.downtime_reason_details.clear()
		# if self.required_time > sum(i.earning_min for i in self.get("machining_operation_details")):
		self.append("downtime_reason_details", {
			"time": self.required_time - sum(i.earning_min for i in self.get("machining_operation_details")),
			"machine": machine
		})
		self.total_downtime = self.required_time - sum(i.earning_min for i in self.get("machining_operation_details"))
	
	
        
	@frappe.whitelist()
	def update_rejection_row(self, params, row_idx):
		existing_table = self.get("rejected_items_reasons")
		self.rejected_items_reasons = []
		for i in existing_table:
			self.append("rejected_items_reasons", i)
			if i.idx == row_idx:
				self.append("rejected_items_reasons", params)

	@frappe.whitelist()
	def add_additional_cost(self):
		if not self.production_additional_cost_details:
			# self.production_additional_cost_details = []
			add_cost_docs = frappe.get_all("MachineShop Additional Cost", {'company': self.company, "is_enable": True, "machining": True}, ["name", "expense_head_account"])
			for i in add_cost_docs:
				expense_head_account = i.expense_head_account
				result = frappe.get_value('MachineShop Additional Cost Details', {"parent": i["name"], "from_date": ['<=', self.date], "to_date": ['>=', self.date]}, ['amount', 'wise'])
				if result:
					amount, wise = result
					for d in self.get("machining_operation_details"):
						total_amt = 0
						if wise == 'Unit':
							is_power_consumption = frappe.get_value("MachineShop Additional Cost Type", i.machineshop_additional_cost_type, 'is_power_consumption')
							if is_power_consumption:
								total_amt = getval(self.unit_consumption)
							else:
								total_amt = getval(d.total_quantity) * amount
						elif wise == 'Weight':
							total_amt = getval(d.total_weight) * amount
						elif wise == "Hour":
							total_amt = (d.earning_min / 60) * amount
						
						self.append("production_additional_cost_details", {
							"finished_item_code": d.item,
							"finished_item_name": d.finished_item_name,
							"operation": d.operation,
							"operation_name": d.operation_name,
							"expense_head_account": expense_head_account,
							"amount": total_amt
						})
		else:
			existing_costs = {row.finished_item_code: row for row in self.production_additional_cost_details}
			
			add_cost_docs = frappe.get_all("MachineShop Additional Cost", {'company': self.company, "is_enable": True, "machining": True}, ["name", "expense_head_account"])
			for i in add_cost_docs:
				expense_head_account = i.expense_head_account
				result = frappe.get_value('MachineShop Additional Cost Details', {"parent": i["name"], "from_date": ['<=', self.date], "to_date": ['>=', self.date]}, ['amount', 'wise'])
				if result:
					amount, wise = result
					for d in self.get("machining_operation_details"):
						total_amt = 0
						if wise == 'Unit':
							is_power_consumption = frappe.get_value("MachineShop Additional Cost Type", i.machineshop_additional_cost_type, 'is_power_consumption')
							if is_power_consumption:
								total_amt = getval(self.unit_consumption)
							else:
								total_amt = getval(d.total_quantity) * amount
						elif wise == 'Weight':
							total_amt = getval(d.total_weight) * amount
						elif wise == "Hour":
							total_amt = (d.earning_min / 60) * amount
						
						if d.item in existing_costs:
							existing_row = existing_costs[d.item]
							existing_row.amount = total_amt
						else:
							self.append("production_additional_cost_details", {
								"finished_item_code": d.item,
								"finished_item_name": d.finished_item_name,
								"operation": d.operation,
								"operation_name": d.operation_name,
								"expense_head_account": expense_head_account,
								"amount": total_amt
							})
			
			
	@frappe.whitelist()
	def remove_zero_rejections(self):
		no_of_rows = []
		for item in self.get("rejected_items_reasons", {"rejection_qty": [">", 0]}):
			no_of_rows.append(item)

		self.get("rejected_items_reasons").clear()		
		if no_of_rows:
			for row in no_of_rows:
				self.append("rejected_items_reasons",{
					"finished_item":row.finished_item,
					"finished_item_name":row.finished_item_name,
					"raw_item_code":row.raw_item_code,
					"raw_item_name":row.raw_item_name,
					"operation_code":row.operation_code,
					"operation_name":row.operation_name,
					"rejection_type":row.rejection_type,
					"rejection_reason":row.rejection_reason,
					"rejection_qty":row.rejection_qty,
					"target_warehouse":row.target_warehouse,
					"is_applicable_for_oee":row.is_applicable_for_oee
				})
			
		


	#Method to add stock entries for machining operations
	# def add_stock_entry(self):
	# 	is_mat_trans = False
	# 	# Create a new Stock Entry document for machining rejection
	# 	mat_trans_doc = frappe.new_doc("Stock Entry")
	# 	mat_trans_doc.stock_entry_type = "Machining Rejection"
	# 	mat_trans_doc.set_posting_time = True
	# 	mat_trans_doc.posting_date = self.date	
	# 	total_ok_qty = sum(j.ok_qty if j.ok_qty else 0 for j in self.get("machining_operation_details"))
	
	# 	# Iterate over machining operation details to create manufacturing stock entries
	# 	for i in self.get("machining_operation_details"):
	# 		manufact_doc = frappe.new_doc("Stock Entry")
	# 		manufact_doc.stock_entry_type = "Machining Manufacturing"
	# 		manufact_doc.set_posting_time = True
	# 		manufact_doc.posting_date = self.date
	# 		uom = frappe.get_value("Item", i.item, "custom_machining_weight_uom") or frappe.throw(f"set Machining weight UOM for item <b>{i.item}</b>")

	# 		# Append finished item details to the manufacturing stock entry
	# 		manufact_doc.append("items", {
	# 			# "is_finished_item": True,
	# 			"item_code": i.item,
	# 			"s_warehouse": i.source_warehouse,
	# 			"machineshop_operation":i.source_inventory_dimension,
	# 			"qty": i.ok_qty,
	# 			"uom": uom,
	# 		})

	# 		manufact_doc.append("items", {
	# 			"is_finished_item": True,
	# 			"item_code": i.item,
	# 			# "t_warehouse": frappe.get_value("Machining Finished Item Details", {"parent": self.name, "finished_item_code": i.item}, "target_warehouse"),
	# 			"t_warehouse":i.target_warehouse,
	# 			"to_machineshop_operation":i.target_inventory_dimension,
	# 			"qty": i.ok_qty,
	# 			"uom": uom,
	# 		})
	# 		if i.boring:
	# 			manufact_doc.append("items", {
	# 				"is_scrap_item": True,
	# 				"item_code": frappe.get_value("MachineShop Processflow",i.machineshop_processflow, "boring_item_code"),
	# 				# "t_warehouse": frappe.get_value("Machining Finished Item Details", {"parent": self.name, "finished_item_code": i.item}, "target_warehouse"),
	# 				"t_warehouse":frappe.get_value("MachineShop Processflow",i.machineshop_processflow, "target_warehouse"),
	# 				"to_machineshop_operation":i.target_inventory_dimension,
	# 				"qty":i.get("boring", 0) * (i.get("ok_qty", 0) + sum(i.get(f"{r.lower()}_qty", 0) for r in frappe.get_all("MachineShop Rejection Type", {"consider_boring": 1}, pluck="name"))),
	# 				"uom": uom,
	# 			})
	# 		# Add additional costs to the manufacturing stock entry
	# 		if total_ok_qty > 0:
	# 			for j in self.get("production_additional_cost_details",{"operation":i.operation}):
	# 				manufact_doc.append("additional_costs", {
	# 					"amount": (i.ok_qty / total_ok_qty) * j.amount,
	# 					"expense_account": j.expense_head_account,
	# 					"description": j.discription
	# 				})
	# 			manufact_doc.insert()
	# 			manufact_doc.custom_machining_ref = self.name
	# 			manufact_doc.submit()
	# 		# Create material transfer entries for rejected, rework, and machine rejection quantities
	# 		if i.mr_qty and i.mr_qty > 0:
	# 			t_warehouse = frappe.db.get_value("MachineShop Setting",self.company,"mr_target_warehouse")
	# 			mat_trans_doc.append("items", {
	# 				"is_finished_item": True,
	# 				"item_code": i.item,
	# 				"s_warehouse": i.source_warehouse,
	# 				"t_warehouse": t_warehouse if t_warehouse else frappe.throw(f"Target warehouse for MR Quantity is absent in MachineShop Setting "),
	# 				"qty": i.mr_qty,
	# 				"uom": uom,
	# 			})
	# 			is_mat_trans = True
	# 		if i.cr_qty and i.cr_qty > 0:
	# 			t_warehouse = frappe.get_value("MachineShop Setting",self.company, "cr_target_warehouse")
	# 			mat_trans_doc.append("items", {
	# 				"is_finished_item": True,
	# 				"item_code": i.item,
	# 				"s_warehouse": i.source_warehouse,
	# 				"t_warehouse": t_warehouse if t_warehouse else frappe.throw(f"Target warehouse for CR Quantity is absent in MachineShop Setting "),
	# 				"qty": i.cr_qty,
	# 				"uom": uom,
	# 			})
	# 			is_mat_trans = True

	# 		if i.rw_qty and i.rw_qty > 0:
	# 			t_warehouse = frappe.get_value("MachineShop Setting",self.company, "rw_target_warehouse")
	# 			mat_trans_doc.append("items", {
	# 				"is_finished_item": True,
	# 				"item_code": i.item,
	# 				"s_warehouse": i.source_warehouse,
	# 				"t_warehouse": t_warehouse if t_warehouse else frappe.throw(f"Target warehouse for RW Quantity is absent in MachineShop Setting "),
	# 				"qty": i.rw_qty,
	# 				"uom": uom,
	# 			})
	# 			is_mat_trans = True

	# 	# Save and submit the material transfer document if any items were added
	# 	if is_mat_trans:
	# 		mat_trans_doc.insert()
	# 		mat_trans_doc.custom_machining_ref = self.name
	# 		mat_trans_doc.submit()



		
	def manufacturing_stock_entry(self):
		total_ok_qty = sum(j.ok_qty if j.ok_qty else 0 for j in self.get("machining_operation_details"))
		for i in self.get("machining_operation_details"):
			manufact_doc = frappe.new_doc("Stock Entry")
			manufact_doc.stock_entry_type = "Machining Manufacturing"
			manufact_doc.set_posting_time = True
			manufact_doc.posting_date = self.date
			manufact_doc.company = self.company
			# uom = frappe.get_value("Item", i.item, "custom_machining_weight_uom") or frappe.throw(f"set Machining weight UOM for item <b>{i.item}</b>")
			# frappe.throw(f"{total_ok_qty} {i.ok_qty}")
			if i.ok_qty > 0:
				manufact_doc.append("items", {
					"item_code": i.item,
					"s_warehouse": i.source_warehouse,
					"machineshop_operation":i.source_inventory_dimension if i.source_inventory_dimension else None,
					"qty": i.ok_qty,
					# "uom": uom,
					"use_serial_batch_fields":True,
					"serial_no":i.ok_serial_no if i.ok_serial_no else None
				})
   
			for t in self.get("machining_tooling_section",{"operation_code":i.operation}):
				manufact_doc.append("items", {
				"item_code": t.raw_item_code,
				"s_warehouse": frappe.get_value("MachineShop Setting",{"company":self.company},"default_tooling_source_warehouse") or frappe.throw("Missing Default Source Warehouse for Tooling in MachineShop Setting"),
				# "machineshop_operation":i.source_inventory_dimension,
				"qty": t.used_quantity,
				# "uom": t.uom,
    			"use_serial_batch_fields":True,
				"serial_no":t.tooling_item_sr_no if t.tooling_item_sr_no else None
			})

			for c in self.get("machining_consumable_details",{"operation_code":i.operation}):
				manufact_doc.append("items", {
				"item_code": c.raw_item_code,
				"s_warehouse": frappe.get_value("MachineShop Setting",{"company":self.company},"default_consumption_source_warehouse") or frappe.throw("Missing Default Source Warehouse for Consumption in MachineShop Setting"),
				# "machineshop_operation":i.source_inventory_dimension,
				"qty": c.used_quantity,
				# "uom": c.uom,
    			"use_serial_batch_fields":True,
				"serial_no":c.consumable_item_sr_no if c.consumable_item_sr_no else None
			})
    
			if i.ok_qty > 0:
				manufact_doc.append("items", {
					"is_finished_item": True,
					"item_code": i.item,
					"t_warehouse":i.target_warehouse,
					"to_machineshop_operation":i.target_inventory_dimension if i.target_inventory_dimension else None,
					"qty": i.ok_qty,
					# "uom": uom,
					"use_serial_batch_fields":True,
					"serial_no":i.ok_serial_no if i.ok_serial_no else None
				})

			if i.boring:
				manufact_doc.append("items", {
					"is_scrap_item": True,
					"item_code": frappe.get_value("MachineShop Processflow",i.machineshop_processflow, "boring_item_code"),
					"t_warehouse":frappe.get_value("MachineShop Processflow",i.machineshop_processflow, "target_warehouse"),
					"to_machineshop_operation":i.target_inventory_dimension,
					"qty":i.get("boring", 0) * (i.get("ok_qty", 0) + sum(i.get(f"{r.lower()}_qty", 0) for r in frappe.get_all("MachineShop Rejection Type", {"consider_boring": 1}, pluck="name"))),
					# "uom": uom,
				})

			if i.ok_qty > 0:
				for j in self.get("production_additional_cost_details",{"operation":i.operation}):
					manufact_doc.append("additional_costs", {
						"amount": (i.ok_qty / total_ok_qty) * j.amount,
						"expense_account": j.expense_head_account,
						"description": j.discription
					})

			
				manufact_doc.custom_machining_ref = self.name
				# frappe.throw(str(manufact_doc.as_dict()))
				manufact_doc.save()
				manufact_doc.submit()
   
	def manufacturing_stock_entry_for_in_process(self):
		total_in_process_qty = sum(j.in_process_qty if j.in_process_qty else 0 for j in self.get("machining_operation_details"))
		for i in self.get("machining_operation_details"):
			manufact_doc = frappe.new_doc("Stock Entry")
			manufact_doc.stock_entry_type = "Machining In Process Manufacturing"
			manufact_doc.set_posting_time = True
			manufact_doc.posting_date = self.date
			manufact_doc.company = self.company
			# uom = frappe.get_value("Item", i.item, "custom_machining_weight_uom") or frappe.throw(f"set Machining weight UOM for item <b>{i.item}</b>")

			if i.in_process_qty > 0:
				manufact_doc.append("items", {
					"item_code":i.raw_item_code,
					"s_warehouse": i.source_warehouse,
					"qty": i.in_process_qty,
					# "uom": uom,
					"use_serial_batch_fields":True,
					"serial_no":i.in_process_serial_no if i.in_process_serial_no else None
				})

				manufact_doc.append("items", {
					"is_finished_item": True,
					"item_code": i.item,
					"t_warehouse":i.source_warehouse,
					"qty": i.in_process_qty,
					# "uom": uom,
					"use_serial_batch_fields":True,
					"serial_no":i.in_process_serial_no if i.in_process_serial_no else None
				})
   
			if i.in_process_qty > 0:
				for j in self.get("production_additional_cost_details",{"operation":i.operation}):
					manufact_doc.append("additional_costs", {
						"amount": (i.in_process_qty / total_in_process_qty) * j.amount,
						"expense_account": j.expense_head_account,
						"description": j.discription
					})

			if i.in_process_qty > 0:
				manufact_doc.custom_machining_ref = self.name
				manufact_doc.save()
				# frappe.throw(str(manufact_doc.as_dict()))
				manufact_doc.submit()

	def rejection_stock_entry(self):
		is_mat_trans = False
		mat_trans_doc = frappe.new_doc("Stock Entry")
		mat_trans_doc.stock_entry_type = "Machining Rejection"
		mat_trans_doc.set_posting_time = True
		mat_trans_doc.posting_date = self.date	
		mat_trans_doc.company = self.company


		for i in self.get("machining_operation_details"):
			if i.mr_qty and i.mr_qty > 0:
				t_warehouse = frappe.db.get_value("MachineShop Setting",self.company,"mr_target_warehouse")
				mat_trans_doc.append("items", {
					"is_finished_item": True,
					"item_code": i.item,
					"s_warehouse": i.source_warehouse,
					"t_warehouse": t_warehouse if t_warehouse else frappe.throw(f"Target warehouse for MR Quantity is absent in MachineShop Setting "),
					"qty": i.mr_qty,
					"use_serial_batch_fields":True,
					"serial_no":i.mr_serial_no if i.mr_serial_no else None
				})
				is_mat_trans = True
			if i.cr_qty and i.cr_qty > 0:
				t_warehouse = frappe.get_value("MachineShop Setting",self.company, "cr_target_warehouse")
				mat_trans_doc.append("items", {
					"is_finished_item": True,
					"item_code": i.item,
					"s_warehouse": i.source_warehouse,
					"t_warehouse": t_warehouse if t_warehouse else frappe.throw(f"Target warehouse for CR Quantity is absent in MachineShop Setting "),
					"qty": i.cr_qty,
					"use_serial_batch_fields":True,
					"serial_no":i.cr_serial_no if i.cr_serial_no else None
				})
				is_mat_trans = True
				
			if i.rw_qty and i.rw_qty > 0:
				t_warehouse = frappe.get_value("MachineShop Setting",self.company, "rw_target_warehouse")
				mat_trans_doc.append("items", {
					"is_finished_item": True,
					"item_code": i.item,
					"s_warehouse": i.source_warehouse,
					"t_warehouse": t_warehouse if t_warehouse else frappe.throw(f"Target warehouse for RW Quantity is absent in MachineShop Setting "),
					"qty": i.rw_qty,
					"use_serial_batch_fields":True,
					"serial_no":i.rw_serial_no if i.rw_serial_no else None
				})
				is_mat_trans = True

		if is_mat_trans:
			mat_trans_doc.custom_machining_ref = self.name
			mat_trans_doc.save()
			mat_trans_doc.submit()







	





