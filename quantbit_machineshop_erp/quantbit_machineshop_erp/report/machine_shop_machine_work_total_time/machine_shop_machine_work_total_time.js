// Copyright (c) 2025, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Machine Shop Machine Work Total Time"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "company",
            "fieldtype": "Link",
            "label": "Company",
            "options": "Company"
        },
    ],
};
