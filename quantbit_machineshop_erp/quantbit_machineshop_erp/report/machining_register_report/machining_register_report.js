// Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Machining Register Report"] = {
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
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.nowdate(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.nowdate() 
        },
        {
            "fieldname": "shift",
            "label": __("Shift"),
            "fieldtype": "Link",
            "options": "MachineShop Shift",
            "reqd": 0
        },
        {
            "fieldname": "operator",
            "label": __("Operator"),
            "fieldtype": "MultiSelectList",
            "options": "MachineShop Operator Master",
            "reqd": 0,
			get_data : function(txt) {return frappe.db.get_link_options("MachineShop Operator Master",txt)}
        },
        {
            "fieldname": "supervisor",
            "label": __("Supervisor"),
            "fieldtype": "MultiSelectList",
            "options": "MachineShop Supervisor Master",
            "reqd": 0,
			get_data : function(txt) {return frappe.db.get_link_options("MachineShop Supervisor Master",txt)}
        }
    ]
};
