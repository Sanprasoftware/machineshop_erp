// Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Itemwise Causewise Machining Rejection Register REport"] = {
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
            fieldname: "finished_item",
            label: __("Finished Item"),
            fieldtype: "MultiSelectList",
            options: "Item",
            get_data: function (txt) {
                return frappe.db.get_link_options("Item", txt);
            },
        },
        {
            fieldname: "rejection_type",
            label: __("Rejection Type"),
            fieldtype: "MultiSelectList",
            options: "Rejection Type",
            get_data: function (txt) {
                return frappe.db.get_link_options("MachineShop Rejection Type", txt);
            },
        },
        {
            fieldname: "rejection_reason",
            label: __("Rejection Reason"),
            fieldtype: "MultiSelectList",
            options: "Rejection Reason",
            get_data: function (txt) {
                return frappe.db.get_link_options("MachineShop Rejection Reason", txt);
            },
        },
	]
};
