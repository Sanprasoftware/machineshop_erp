// Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Itemwise Machining Register Report"] = {
	"filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
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
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "MultiSelectList",
            "options": "Company",
			"reqd": 1,
            "get_data": function(txt) {
                return frappe.db.get_link_options("Company", txt);
            }
        },
		{
			
			"fieldname": "operation",
            "label": __("Operation"),
            "fieldtype": "MultiSelectList",
            "options": "Company",
            "get_data": function(txt) {
                return frappe.db.get_link_options("MachineShop Operation", txt);
            }
		},
		{
			
			"fieldname": "item",
            "label": __("Finished Item Code"),
            "fieldtype": "MultiSelectList",
            "options": "Item",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Item", txt);
            }
		}
    ]
};
