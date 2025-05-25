// Copyright (c) 2025, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Casting Treatment Rejection Register"] = {
	"filters": [
		{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "MultiSelectList",
            "options": "Company",
            "reqd": 1,
            get_data : function(txt) {return frappe.db.get_link_options("Company",txt)}
        },
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "rejection_reason",
			"label": __("Casting Treatment Rejection Reason"),
			"fieldtype": "Link",
			"options": "Casting Treatment Rejection Reason Master"
		},
		{
            "fieldname": "supervisor_id",
            "label": __("Supervisor ID"),
            "fieldtype": "MultiSelectList",
            "options": "Foundry Supervisor Master" ,
            get_data : function(txt) {return frappe.db.get_link_options("Foundry Supervisor Master",txt)}
                
            
            
        },
        {
            "fieldname": "operator_id",
            "label": __("Operator ID"),
            "fieldtype": "MultiSelectList",
            "options": "Foundry Operator Master",
            get_data : function(txt) {return frappe.db.get_link_options("Foundry Operator Master",txt)}
        },
	
		{
			"fieldname": "rejection_type",
			"label": __("Casting Treatment Rejection Type"),
			"fieldtype": "Link",
			"options": "Casting Treatment Rejection Type"
		},
		{
			"fieldname": "casting_treatment",
			"label": __("Casting Treatment"),
			"fieldtype": "Link",
			"options": "Casting Treatment Master"
		},
		{"fieldname":"item_code", "label": __("Casting Item Code"), "fieldtype": "MultiSelectList", "options": "Item",get_data : function(txt) {return frappe.db.get_link_options("Item",txt)}},
		{
            "fieldname": "group_by",
            "label": __("Group By"),
            "fieldtype": "Select",
            "options": "\nRejection Reason\nRejection Type\nItem",
            "default": ""
        }
	]
};
