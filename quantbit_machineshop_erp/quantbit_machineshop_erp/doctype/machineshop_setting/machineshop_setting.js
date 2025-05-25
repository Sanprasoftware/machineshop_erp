// Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("MachineShop Setting", {
	setup(frm) {
        frm.set_query("mr_target_warehouse",function(){
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("cr_target_warehouse",function(){
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("rw_target_warehouse",function(){
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("fr_target_warehouse",function(){
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("source_warehouse",function(){
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("target_warehouse",function(){
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("default_tooling_source_warehouse",function(){
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("default_consumables_source_warehouse",function(){
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
	},
});
