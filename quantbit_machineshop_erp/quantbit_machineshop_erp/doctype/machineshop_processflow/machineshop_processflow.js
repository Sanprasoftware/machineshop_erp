

frappe.ui.form.on("MachineShop Downstream Process Details", {
     raw_item_code:async (frm,cdt,cdn)=>{
        var d = locals[cdt][cdn]
        const item_doc = (await frappe.db.get_value("Item",d.raw_item_code,["weight_uom","weight_per_unit","custom_machining_weight_uom","custom_machining_weight","item_group_type"])).message
        console.log(item_doc);
        if(item_doc.item_group_type == "Raw Material"){
            d.weight_uom = item_doc.weight_uom
            d.weight_per_unit = item_doc.weight_per_unit
        }else{
            d.weight_uom = item_doc.custom_machining_weight_uom 
            d.weight_per_unit = item_doc.custom_machining_weight
        }
        frm.refresh_fields()
        
    }
})
frappe.ui.form.on("MachineShop Tooling Details", {
    machineshop_tooling_details_add: function(frm,cdt,cdn){
        let d = locals[cdt][cdn]
        d.finished_item_code = frm.doc.finished_item_code
        d.finished_item_name = frm.doc.finished_item_name
        frm.refresh_fields()
    }
})
frappe.ui.form.on("MachineShop Consumable Details", {
    machineshop_consumable_details_add: function(frm,cdt,cdn){
        let d = locals[cdt][cdn]
        d.finished_item_code = frm.doc.finished_item_code
        d.finished_item_name = frm.doc.finished_item_name
        frm.refresh_fields()
    }
})
frappe.ui.form.on("MachineShop Processflow", {
	setup: function(frm) {
        
        frm.set_query("finished_item_warehouse",function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {
                        "Company":frm.doc.company,
                        "is_group":0
                    }
                };
    	});
        frm.set_query("target_warehouse",function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {
                        "Company":frm.doc.company,
                        "is_group":0

                    }
                };
    	});
        frm.set_query("source_warehouse","machining_operation_plan",function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {
                        "Company":frm.doc.company,
                        "is_group":0

                    }
                };
    	});
        frm.set_query("target_warehouse","machining_operation_plan",function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {
                        "Company":frm.doc.company,
                        "is_group":0
                    }
                };
    	});
        frm.set_query("source_warehouse","downstream_process_details",function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {
                    "Company":frm.doc.company,
                    "is_group":0
                }
                };
    	});
        frm.set_query("target_warehouse","downstream_process_details",function(doc, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                filters: {
                        "Company":frm.doc.company,
                        "is_group":0
                    }
                };
    	});
	},
});

// var item_group="CASTING";
// var pepl_item_group="CASTING - PEPL";
// var company_field ='custom_company';

// frappe.ui.form.on('Material Cycle Time', {
// 	setup: function(frm) {
//     	frm.set_query("item",function(doc, cdt, cdn) {
//             let d = locals[cdt][cdn];
//             return {
//                 filters: [
//                         ['Item', 'custom_is_finished_machineshop_casting_items', '=',1],
//                         ['Item', 'item_group', '=', pepl_item_group],
//                         ["Item", company_field, '=', frm.doc.company]
//                     ]
//                 };
//     	});
        
//         frm.set_query("raw_item",function(doc, cdt, cdn) {
//             let d = locals[cdt][cdn];
//             return {
//                 filters: [
//                         ["Item", company_field, '=', frm.doc.company]
//                     ]
//                 };
//     	});
    	
//         frm.set_query("operation","machine_operation_plan",function(doc, cdt, cdn) {
//             let d = locals[cdt][cdn];
//             return {
//                 filters: [
//                         ["Operation Master", "company", '=', frm.doc.company]
//                     ]
//                 };
//     	});
    	
//     	frm.set_query("downstream_process","row_items",function(doc, cdt, cdn) {
//             let d = locals[cdt][cdn];
//             return {
//                 filters: [
//                         ["Downstream Processes Master", "company", '=', frm.doc.company]
//                     ]
//                 };
//     	});
    	
//     	frm.set_query("item","row_items",function(doc, cdt, cdn) {
//             let d = locals[cdt][cdn];
//             return {
//                 filters: [
//                         ["Item", company_field, '=', frm.doc.company]
//                     ]
//                 };
//     	});
    	
// 	}
// });
