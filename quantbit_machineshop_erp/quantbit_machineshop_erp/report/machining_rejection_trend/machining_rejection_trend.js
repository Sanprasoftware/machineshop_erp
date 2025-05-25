// Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Machining Rejection Trend"] = {
	"filters":   [
        {
            "fieldname": "period",
            "label": __("Period"),
            "fieldtype": "Select",
            "options": [
                { "value": "Monthly", "label": __("Monthly") },
                { "value": "Quarterly", "label": __("Quarterly") },
                { "value": "Half Yearly", "label": __("Half Yearly") },
                { "value": "Yearly", "label": __("Yearly") }
            ],
            "default": "Monthly",
            "reqd": 1
        },
        {
            "fieldname": "group_by",
            "label": __("Group By"),
            "fieldtype": "Select",
            "options": [
                { "value": "", "label": __("Select Group By") },
                { "value": "Rejection Reason", "label": __("Rejection Reason") },
                { "value": "Rejection Type", "label": __("Rejection Type") }
            ],
            "default": "",
        },
        {
            "fieldname": "based_on",
            "label": __("Based On"),
            "fieldtype": "Select",
            "options": [
                { "value": "", "label": __("Select Based On") },
				{ "value": "Rejection Reason", "label": __("Rejection Reason") },
                { "value": "Rejection Type", "label": __("Rejection Type") }
            ]
		},

	  {
            "fieldname": "fiscal_year",
            "label": __("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "default": frappe.defaults.get_user_default("fiscal_year"),
            "reqd": 1
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("company"),
            "reqd": 1
        }
	]
};
