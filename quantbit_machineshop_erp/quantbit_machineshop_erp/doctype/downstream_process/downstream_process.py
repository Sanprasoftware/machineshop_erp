import frappe
from frappe.model.document import Document
from erpnext.stock.utils import get_stock_balance
from datetime import datetime
from frappe.utils import get_link_to_form

def getval(value):
    return value if value else 0

class DownstreamProcess(Document):
    
	def before_save(self):
		self.check_sr_no()
		self.remove_zero_rejections()
		if not self.downstream_additional_cost_details:
			self.add_additional_cost()
		self.check_total_quantity()
  
	def before_submit(self):
		self.check_sr_no()
		self.add_manufact_stock_entry_for_in_process()
		self.add_manufact_stock_entry()
		self.add_mat_trans_stock_entry()
	
	def check_sr_no(self):
		
		for i in self.get("quality_inspection_details"):
			finished_as_raw_serial_nos = []
			if i.finished_item_sr_no:
				finished_as_raw_serial_nos = [sr.strip() for sr in (i.finished_item_sr_no).split(",") if sr.strip()]

			finished_serial_nos = []
			if i.fr_serial_no:
				fr_serial_no_lst = [sr.strip() for sr in (i.fr_serial_no).split(",") if sr.strip()]
				finished_serial_nos.extend(fr_serial_no_lst)
				if (i.fr_quantity != len(fr_serial_no_lst)):
					frappe.throw(f"FR Quantity {i.fr_quantity} and FR Sr. No count {len(fr_serial_no_lst)} Doesn't match")
			if i.cr_serial_no:
				cr_serial_no_lst = [sr.strip() for sr in (i.cr_serial_no).split(",") if sr.strip()]
				finished_serial_nos.extend(cr_serial_no_lst)
				if (i.cr_quantity != len(cr_serial_no_lst)):
					frappe.throw(f"CR Quantity {i.cr_quantity} and CR Sr. No count {len(cr_serial_no_lst)} Doesn't match")
			if i.ok_serial_no:
				ok_serial_no_lst = [sr.strip() for sr in (i.ok_serial_no).split(",") if sr.strip()]
				finished_serial_nos.extend(ok_serial_no_lst)
				if (i.ok_quantity != len(ok_serial_no_lst)):
					frappe.throw(f"OK Quantity {i.ok_quantity} and OK Sr. No count {len(ok_serial_no_lst)} Doesn't match")
			if i.rw_serial_no:
				rw_serial_no_lst = [sr.strip() for sr in (i.rw_serial_no).split(",") if sr.strip()]
				finished_serial_nos.extend(rw_serial_no_lst)
				if (i.rw_quantity != len(rw_serial_no_lst)):
					frappe.throw(f"RW Quantity {i.rw_quantity} and RW Sr. No count {len(rw_serial_no_lst)} Doesn't match")
			if i.in_process_serial_no:
				in_process_serial_no_lst = [sr.strip() for sr in (i.in_process_serial_no).split(",") if sr.strip()]
				finished_serial_nos.extend(in_process_serial_no_lst)
				if (i.in_process_quantity != len(in_process_serial_no_lst)):
					frappe.throw(f"In Process Quantity {i.in_process_quantity} and In Process Sr. No count {len(in_process_serial_no_lst)} Doesn't match")
			# tot_qty = i.cr_quantity + i.rw_quantity + i.fr_quantity + i.ok_quantity + i.in_process_quantity
			if  (sorted(finished_serial_nos) != sorted(finished_as_raw_serial_nos)):
				frappe.throw(f"Finished Item Serial count doesn't match {finished_as_raw_serial_nos} \n {finished_serial_nos}")
			
	@frappe.whitelist()
	def add_dsp_casting_details(self):
		items_to_stay = [s for s in self.get("downstream_casting_details") if s.is_manually_added]
		self.downstream_casting_details.clear()
		for item in items_to_stay:
			self.append("downstream_casting_details",{
				"finished_item_code": item.finished_item_code,
                "finished_item_name": item.finished_item_name,
                "quantity": item.quantity,
                "available_stock": item.available_stock,
                "downstream_process_rate":item.downstream_process_rate,
                "uom":item.uom,
                "weight": item.weight,
                "total_weight": item.total_weight,
                "machining": item.machining,
                "machineshop_processflow": item.machineshop_processflow,
                "source_warehouse": item.source_warehouse,
                "target_warehouse": item.target_warehouse,
                "is_manually_added": 1
			})
		self.downstream_raw_material_details.clear()
		self.quality_inspection_details.clear()
		if self.machining:
			for i in self.machining:
				mac_doc = frappe.get_doc("Machining", i.machining_id)
				for m in mac_doc.get("machining_finished_item_details"):
					self.append("downstream_casting_details", {
						"finished_item_code": m.finished_item_code,
						"finished_item_name": m.item_name,
						"machining": i.machining_id,
						"machineshop_processflow": m.item,

					})
		self.add_quality_and_raw_material()

	@frappe.whitelist()
	def add_quality_and_raw_material(self):
		self.downstream_raw_material_details.clear()
		self.quality_inspection_details.clear()
		self.downstream_rejected_reasons_details.clear()
		for d in self.get("downstream_casting_details"):
			d.source_warehouse = frappe.get_value("MachineShop Downstream Process Details",{"parent":d.machineshop_processflow,"downstream_process":self.downstream_process},"source_warehouse") or frappe.get_value("MachineShop Setting",self.company, "source_warehouse")
			d.target_warehouse = frappe.get_value("MachineShop Setting",self.company, "target_warehouse")
			d.available_stock = get_stock_balance(item_code=d.finished_item_code, warehouse=d.source_warehouse, posting_date=self.downstream_date)
			dp_details = frappe.get_doc("MachineShop Processflow", d.machineshop_processflow)
			d.downstream_process_rate = sum(j.downstream_process_rate or 0 for j in dp_details.get("downstream_process_details"))
			d.uom, d.weight = frappe.get_value("Item", d.finished_item_code, ["custom_machining_weight_uom", "custom_machining_weight"]) 
			


			# self.append("downstream_raw_material_details", {
			# 	"finished_item_code": d.finished_item_code,
			# 	"finished_item_name": d.finished_item_name,
			# 	"raw_item_code": d.finished_item_code,
			# 	"raw_item_name": d.finished_item_name,
			# 	"machining": d.machining,
			# 	"machineshop_processflow": d.machineshop_processflow,
			# 	"source_warehouse": d.source_warehouse,
			# 	# "target_warehouse": d.target_warehouse,
			# 	"available_stock": d.available_stock,
			# 	# "downstream_process_rate": d.downstream_process_rate,
			# 	"uom": d.uom,
			# 	"weight": d.weight,
			# 	# "downstream_raw_material_name": frappe.get_value("Item", d.finished_item_code, ["custom_machining_raw_material_name"])
			# })
			has_serial_no,finished_item_group = frappe.get_value("Item",d.finished_item_code,["has_serial_no","item_group"]) or (0,None)
			self.append("quality_inspection_details", {
				"finished_item_code": d.finished_item_code,
				"finished_item_name": d.finished_item_name,
				##AV
				"has_serial_no": has_serial_no,
				"finished_item_group":finished_item_group,
				#
				"uom": d.uom,
				"weight": d.weight,
				"machining_id": d.machining,
				"machineshop_processflow": d.machineshop_processflow
			})
			msp_doc = frappe.get_doc("MachineShop Processflow", d.machineshop_processflow)
			# frappe.throw(str(d.machineshop_processflow))
			for s in msp_doc.get("downstream_process_details",{"downstream_process": self.downstream_process}):
				self.append("downstream_raw_material_details", {
					"finished_item_code": d.finished_item_code,
					"finished_item_name": d.finished_item_name,
					"raw_item_code": s.raw_item_code,
					"raw_item_name": s.raw_item_name,
					"machining": d.machining,
					"source_warehouse": s.source_warehouse,
					"machineshop_processflow": s.parent,
					"raw_material_qty":s.quantity,
					"uom":s.weight_uom,
					"weight":s.weight_per_unit,
					"available_stock": get_stock_balance(item_code=s.raw_item_code, warehouse=s.source_warehouse, posting_date=self.downstream_date),
					# "target_warehouse": d.target_warehouse,
					# "downstream_process_rate": d.downstream_process_rate,
					# "uom": d.uom,
					# "weight": d.weight,
					# "downstream_raw_material_name": frappe.get_value("Item", d.finished_item_code, ["custom_machining_raw_material_name"])
				})

	@frappe.whitelist()
	def add_additional_cost(self):
		self.downstream_additional_cost_details = []
		# Retrieve additional cost documents based on company and machining status
		add_cost_docs = frappe.get_all("MachineShop Additional Cost", {'company': self.company, "is_enable": True, "downstream": True}, ["name", "expense_head_account"])
		for i in add_cost_docs:
			expense_head_account = i.expense_head_account
			# Get the amount and wise type for the additional cost
			result = frappe.get_value('MachineShop Additional Cost Details', {"parent": i["name"], "from_date": ['<=', self.downstream_date], "to_date": ['>=', self.downstream_date]}, ['amount', 'wise'])
			if result:
				amount, wise = result
				# Calculate the total amount based on the wise type and append it to the table
				for d in self.get("quality_inspection_details"):
					total_amt = 0
					if wise == 'Unit':
						is_power_consumption = frappe.get_value("MachineShop Additional Cost Type", i.machineshop_additional_cost_type, 'is_power_consumption')
						if is_power_consumption:
							total_amt = getval(self.unit_consumption)
						else:
							total_amt = getval(d.ok_quantity) * amount
					elif wise == 'Weight':
						total_amt = getval(d.ok_weight) * amount
					elif wise == "Hour":
						total_amt = (self.time / 60) * amount

					self.append("downstream_additional_cost_details", {
						# "finished_item_code": d.item,
						# "finished_item_name": d.finished_item_name,
						# "operation": d.operation,
						# "operation_name": d.operation_name,
						"additional_cost_type": wise,
						"expense_head_account": expense_head_account,
						"amount": total_amt
					})

	@frappe.whitelist()
	def add_finished_item(self, finished_item_code):
		# frappe.throw(str(row))
		msp_doc = frappe.get_doc("MachineShop Processflow", {"finished_item_code": finished_item_code, "is_enable": True,"company":self.company})
		if not msp_doc:
			frappe.throw(f"MachineShop Processflow not found for Finished Item Code: {finished_item_code}")
		machineshop_processflow = msp_doc.name
		finished_item_name = msp_doc.finished_item_name
		source_warehouse,target_warehouse =  frappe.get_value("MachineShop Setting",self.company, ["source_warehouse","target_warehouse"]) or (None,None)
		# target_warehouse = frappe.get_value("MachineShop Setting",self.company, "target_warehouse")
		available_stock = get_stock_balance(item_code=finished_item_code, warehouse=source_warehouse, posting_date=self.downstream_date, posting_time=self.downstream_time)
		downstream_process_rate = sum(j.downstream_process_rate or 0 for j in msp_doc.get("downstream_process_details"))
		uom, weight = frappe.get_value("Item", finished_item_code, ["custom_machining_weight_uom", "custom_machining_weight"])
		return machineshop_processflow, finished_item_name, source_warehouse, target_warehouse, available_stock, downstream_process_rate, uom, weight

	@frappe.whitelist()
	def add_rejection_row(self, params):
		no_of_rows = []

		for item in self.get("downstream_rejected_reasons_details"):
			if (item.downstream_rejection_type == params.get("downstream_rejection_type", "") and
				item.finished_item_code == params.get("finished_item_code", "") and
				(item.machining_id == params.get("machining_id", None) or 
				(params.get("machining_id") is None and item.machining_id is None)) and
				item.machineshop_processflow == params.get("machineshop_processflow", "")):
				no_of_rows.append(item)

		if len(no_of_rows) > 1:
			for i in no_of_rows[1:]: 
				self.get("downstream_rejected_reasons_details").remove(i)

		existing_row = None
		for item in self.get("downstream_rejected_reasons_details"):
			if (item.downstream_rejection_type == params.get("downstream_rejection_type", "") and
				item.finished_item_code == params.get("finished_item_code", "") and
				(item.machining_id == params.get("machining_id", None) or 
				(params.get("machining_id") is None and item.machining_id is None)) and
				item.machineshop_processflow == params.get("machineshop_processflow", "")):
				existing_row = item
				break

		if existing_row:
			for key, value in params.items():
				existing_row.set(key, value)
		else:
			self.append("downstream_rejected_reasons_details", params)


	@frappe.whitelist()
	def remove_zero_rejections(self):
		no_of_rows = []
		# Collect rows with rejection_qty <= 0
		for item in self.get("downstream_rejected_reasons_details", {"quantity": [">", 0]}):
			no_of_rows.append(item)

		self.get("downstream_rejected_reasons_details").clear()		
		if no_of_rows:
			for row in no_of_rows:
				self.append("downstream_rejected_reasons_details",{
					"finished_item_code":row.finished_item_code,
					"finished_item_name":row.finished_item_name,
					"machining_id":row.machining_id,
					"machineshop_processflow":row.machineshop_processflow,
					"quantity":row.quantity,
					"uom":row.uom,
					"weight":row.weight,
					"total_weight":row.quantity * row.weight,
					"downstream_rejection_reason":row.downstream_rejection_reason,
					"downstream_rejection_type":row.downstream_rejection_type,
					"target_warehouse":row.target_warehouse
				})
	@frappe.whitelist()
	def update_rejection_row(self, params, row_idx):
		existing_table = self.get("downstream_rejected_reasons_details")
		self.downstream_rejected_reasons_details = []
		for i in existing_table:
			self.append("downstream_rejected_reasons_details", i)
			if i.idx == row_idx:
				self.append("downstream_rejected_reasons_details", params)
    
	def add_manufact_stock_entry(self):
		total_ok_qty = sum(j.ok_quantity or 0 for j in self.get("quality_inspection_details"))
		for i in self.get("downstream_casting_details"):
			row = self.get("quality_inspection_details",{"finished_item_code":i.finished_item_code,"machining_id":i.machining,"machineshop_processflow":i.machineshop_processflow,"ok_quantity":[">",0]})
			
			if row:
				manufact_doc = frappe.new_doc("Stock Entry")
				manufact_doc.stock_entry_type = "Downstream Manufacturing"
				manufact_doc.set_posting_time = True
				manufact_doc.posting_date = self.downstream_date
				manufact_doc.company = self.company
				uom = frappe.get_value("Item", i.finished_item_code, "custom_machining_weight_uom") or frappe.throw(f"set Machining weight UOM for item <b>{i.finished_item_code}</b>")
				manufact_doc.append("items",{
						# "is_finished_item": True,
						"item_code": i.finished_item_code,
						"s_warehouse": i.source_warehouse,
						"qty": row[0].ok_quantity,
						"uom": uom,
						"use_serial_batch_fields":True,
						"serial_no":row[0].ok_serial_no if row[0].ok_serial_no else None
				})
				flag = True
				for r in self.get("downstream_raw_material_details",{"finished_item_code":i.finished_item_code,"machineshop_processflow":i.machineshop_processflow}):
					if flag == True and i.finished_item_code != r.raw_item_code:
							manufact_doc.append("items",{
								"item_code": r.raw_item_code,
								"s_warehouse": r.source_warehouse,
								"qty": r.used_quantity,
								"uom": uom,
								"use_serial_batch_fields":True,
								# "serial_no":row[0].ok_serial_no if row[0].ok_serial_no else None
						})
					flag = False
				manufact_doc.append("items",{
						"is_finished_item": True,
						"item_code": i.finished_item_code,
						"t_warehouse": i.target_warehouse,
						"qty": row[0].ok_quantity,
						"uom": uom,
						"use_serial_batch_fields":True,
						"serial_no":row[0].ok_serial_no if row[0].ok_serial_no else None
				})
				# lst = []
				# for j in manufact_doc.items:
				# 	lst.append((j.s_warehouse,j.t_warehouse))
				# frappe.throw(str(manufact_doc.as_dict()))
				if total_ok_qty > 0:
					if self.get("downstream_additional_cost_details"):
						for j in self.get("downstream_additional_cost_details"):
							manufact_doc.append("additional_costs", {
								"amount": (row[0].ok_quantity / total_ok_qty) * j.amount,
								"expense_account": j.expense_head_account,
								"description": j.discription
							})
				# frappe.throw(str(manufact_doc.items))
					manufact_doc.save()
					manufact_doc.custom_downstream_ref = self.name
					manufact_doc.submit()
				
	def add_manufact_stock_entry_for_in_process(self):
		total_in_process_qty = sum(j.in_process_quantity or 0 for j in self.get("quality_inspection_details"))
		for i in self.get("downstream_casting_details"):
			row = self.get("quality_inspection_details",{"finished_item_code":i.finished_item_code,"machining_id":i.machining,"machineshop_processflow":i.machineshop_processflow,"ok_quantity":[">",0]})
			
			if row:
				manufact_doc = frappe.new_doc("Stock Entry")
				manufact_doc.stock_entry_type = "Downstream In Process Manufacturing"
				manufact_doc.set_posting_time = True
				manufact_doc.posting_date = self.downstream_date
				manufact_doc.company = self.company

				uom = frappe.get_value("Item", i.finished_item_code, "custom_machining_weight_uom") or frappe.throw(f"set Machining weight UOM for item <b>{i.finished_item_code}</b>")
				manufact_doc.append("items",{
						# "is_finished_item": True,
						"item_code": i.finished_item_code,
						"s_warehouse": i.source_warehouse,
						"qty": row[0].in_process_quantity,
						"uom": uom,
						"use_serial_batch_fields":True,
						"serial_no":row[0].in_process_serial_no if row[0].in_process_serial_no else None
				})
				flag = True
				for r in self.get("downstream_raw_material_details",{"finished_item_code":i.finished_item_code,"machineshop_processflow":i.machineshop_processflow}):
					if flag == True and i.finished_item_code != r.raw_item_code:
						manufact_doc.append("items",{
							# "is_finished_item": True,
							"item_code": r.raw_item_code,
							"s_warehouse": r.source_warehouse,
							"qty": r.used_quantity,
							"uom": uom,
							"use_serial_batch_fields":True,
							# "serial_no":r.used_qty_serial_no if r.used_qty_serial_no else None
						})
					flag = False
				manufact_doc.append("items",{
						"is_finished_item": True,
						"item_code": i.finished_item_code,
						"t_warehouse": i.source_warehouse,
						"qty": row[0].ok_quantity,
						"uom": uom,
						"use_serial_batch_fields":True,
						"serial_no":row[0].in_process_serial_no if row[0].in_process_serial_no else None
				})
					
				if total_in_process_qty > 0:
					if self.get("downstream_additional_cost_details"):
						for j in self.get("downstream_additional_cost_details"):
							manufact_doc.append("additional_costs", {
								"amount": (row[0].ok_quantity / total_in_process_qty) * j.amount,
								"expense_account": j.expense_head_account,
								"description": j.discription
							})
				# frappe.throw(str(manufact_doc.items))
					manufact_doc.save()
					manufact_doc.custom_downstream_ref = self.name
					manufact_doc.submit()
	def add_mat_trans_stock_entry(self):
		# frappe.throw("mat")
		is_mat_trans = False
		mat_trans_doc = frappe.new_doc("Stock Entry")
		mat_trans_doc.stock_entry_type = "Downstream Material Transfer"
		mat_trans_doc.set_posting_time = True
		mat_trans_doc.posting_date = self.downstream_date
		mat_trans_doc.company = self.company

		for i in self.get("downstream_casting_details"):
			row = self.get("quality_inspection_details",{"finished_item_code":i.finished_item_code,"machining_id":i.machining,"machineshop_processflow":i.machineshop_processflow})
			# frappe.throw(str(row[0].ok_quantity))
			if row:
				# frappe.throw("failed to")
				uom = frappe.get_value("Item", i.finished_item_code, "custom_machining_weight_uom") or frappe.throw(f"set Machining weight UOM for item <b>{i.finished_item_code}</b>")
				if row[0].fr_quantity and row[0].fr_quantity:
					t_warehouse = frappe.get_value("MachineShop Setting",self.company, "fr_target_warehouse")
					mat_trans_doc.append("items",{
							# "is_finished_item": True,
							"item_code": i.finished_item_code,
							"s_warehouse":i.source_warehouse,
							"t_warehouse": t_warehouse if t_warehouse else frappe.throw(f"Target Warehouse for FR Rejection is absent in MachineShop Setting"),
							"qty": row[0].fr_quantity,
							"uom": uom,
       						"use_serial_batch_fields":True,
							"serial_no":row[0].fr_serial_no if row[0].fr_serial_no else None
					})
					is_mat_trans = True
				if row[0].rw_quantity and row[0].rw_quantity:
					t_warehouse = frappe.get_value("MachineShop Setting",self.company, "rw_target_warehouse")
					mat_trans_doc.append("items",{
							# "is_finished_item": True,
							"item_code": i.finished_item_code,
       						"s_warehouse":i.source_warehouse,
							"t_warehouse": t_warehouse if t_warehouse else frappe.throw(f"Target Warehouse for RW Rejection is absent in MachineShop Setting"),
							"qty": row[0].rw_quantity,
							"uom": uom,
							"use_serial_batch_fields":True,
							"serial_no":row[0].rw_serial_no if row[0].rw_serial_no else None
					})
					is_mat_trans = True
				if row[0].cr_quantity and row[0].cr_quantity:
					t_warehouse = frappe.get_value("MachineShop Setting",self.company, "cr_target_warehouse")
					mat_trans_doc.append("items",{
							# "is_finished_item": True,
							"item_code": i.finished_item_code,
       						"s_warehouse":i.source_warehouse,
							"t_warehouse": t_warehouse if t_warehouse else frappe.throw(f"Target Warehouse for CR Rejection is absent in MachineShop Setting"),
							"qty": row[0].cr_quantity,
							"uom": uom,
							"use_serial_batch_fields":True,
							"serial_no":row[0].cr_serial_no if row[0].cr_serial_no else None
					})
					is_mat_trans = True
     
		# frappe.throw(str(mat_trans_doc.as_dict()))
		if is_mat_trans:		
			mat_trans_doc.save()
			mat_trans_doc.custom_downstream_ref = self.name
			mat_trans_doc.submit()
  
  
	def check_total_quantity(self):
		for i in self.get("quality_inspection_details"):
			total_qty = (i.ok_quantity or 0) + (i.cr_quantity or 0) + (i.rw_quantity or 0) + (i.fr_quantity or 0) + (i.in_process_quantity or 0)
			if i.total_casting_quantity != total_qty:
				frappe.throw(f"Total Casting Quantity is <b>{i.total_casting_quantity}</b> and Entered total quantity is <b>{total_qty}</b> in Quality inspection details")
		for j in self.get("downstream_casting_details"):
			if j.quantity <= 0:
				frappe.throw(f"Zero Quantity is not allowed in Downstream Casting details")
       
     
	@frappe.whitelist()
	def get_balance(self,item_code,warehouse):
		return get_stock_balance(item_code=item_code, warehouse=warehouse, posting_date=self.downstream_date)