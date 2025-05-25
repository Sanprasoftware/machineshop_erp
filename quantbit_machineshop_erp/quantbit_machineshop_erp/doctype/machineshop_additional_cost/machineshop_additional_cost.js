// Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("MachineShop Additional Cost", {
    setup: async function (frm, cdt, cdn) {
        frm.set_query("expense_head_account", function (doc, cdt, cdn) {
            return {
                filters: {
                    "company": frm.doc.company
                }
            };
        });
    }
});

