// Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("MachineShop Operator Master", {
    setup: function (frm) {
        frappe.custom.set_filters_for_doctype(frm.doctype, frm);
	},
});
