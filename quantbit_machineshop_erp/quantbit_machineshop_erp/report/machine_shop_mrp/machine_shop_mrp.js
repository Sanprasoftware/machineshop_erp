// Copyright (c) 2025, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Machine Shop MRP"] = {
	"filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1) 
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.get_today() 
        },
        {
            "fieldname": "company",
            "fieldtype": "Link",
            "label": "Company",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company")
        },
    ]
};
