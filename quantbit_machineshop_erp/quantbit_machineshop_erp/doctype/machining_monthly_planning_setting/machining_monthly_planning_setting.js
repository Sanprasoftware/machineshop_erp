// Copyright (c) 2025, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Machining Monthly Planning Setting", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Machining Monthly Planning Setting', {
    setup: function(frm) {
        frm.set_query("warehouse", "machining_monthly_planning_setting_warehouse_details", function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: [
                    ["Warehouse", "company", '=', frm.doc.company],
                    ["Warehouse", "is_group", '=', 0] 
                ]
            };
        });
    }
});	

