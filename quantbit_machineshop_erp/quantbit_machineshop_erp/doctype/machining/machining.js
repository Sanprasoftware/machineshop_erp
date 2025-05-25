// Copyright (c) 2024, Quantbit Technlogies Pvt Ltd and contributors
// For license information, please see license.txt
//----------------------------------------------------------------
//Set Total
async function calculateDuration(frm, from_time = null, to_time = null) {
    if (!from_time || !to_time) {
        frappe.throw("Both from time and to time are required.");
        return;
    }

    let start_time = new Date(from_time);  
    let end_time = new Date(to_time);

    let diff_ms = end_time.getTime() - start_time.getTime();

    if (diff_ms < 0) {
        frappe.show_alert("Required Time cannot be negative")
        return 0;
    }
    const minutes = diff_ms / (1000 * 60);  
    return Math.floor(minutes)
}

async function set_total(frm){
    let total_mr_qty = total_cr_qty = total_ok_qty = total_rw_qty = total_mr_wt = total_cr_wt = total_ok_wt = total_rw_wt = total_qty = total_qty_wt = total_rej_qty = total_rej_wt = total_in_process_qty = total_in_process_wt = 0
    frm.doc.machining_operation_details.forEach(item => {
        total_mr_qty += item.mr_qty || 0
        total_cr_qty += item.cr_qty || 0
        total_ok_qty += item.ok_qty || 0
        total_rw_qty += item.rw_qty || 0
        total_in_process_qty += item.in_process_qty || 0 // new
        total_mr_wt += item.mr_weight || 0
        total_cr_wt += item.cr_weight || 0
        total_ok_wt += item.ok_weight || 0
        total_rw_wt += item.rw_weight || 0
        total_in_process_wt += item.in_process_weight || 0 // new
        total_qty +=(item.mr_qty || 0) + (item.cr_qty || 0) + (item.ok_qty || 0) + (item.rw_qty || 0) + (item.in_process_qty || 0) // new
        total_qty_wt += (item.mr_weight || 0) + (item.cr_weight || 0) + (item.ok_weight || 0) + (item.rw_weight || 0) + (item.in_process_weight || 0) // new
        total_rej_qty += (item.mr_qty || 0) + (item.cr_qty || 0) + (item.rw_qty || 0)
        total_rej_wt += (item.mr_weight || 0) + (item.cr_weight || 0) + (item.rw_weight || 0)
    })
    frm.doc.total_mr_qty = total_mr_qty
    frm.doc.total_cr_qty = total_cr_qty
    frm.doc.total_ok_qty = total_ok_qty
    frm.doc.total_rw_qty = total_rw_qty
    frm.doc.total_mr_weight = total_mr_wt
    frm.doc.total_cr_weight = total_cr_wt
    frm.doc.total_ok_weight = total_ok_wt
    frm.doc.total_rw_weight = total_rw_wt
    frm.doc.total_quantity = total_qty
    frm.doc.total_qty_weight = total_qty_wt
    frm.doc.total_rejection_qty = total_rej_qty
    frm.doc.total_rejection_weight = total_rej_wt

    frm.doc.total_in_process_qty = total_in_process_qty
    frm.doc.total_in_process_weight = total_in_process_wt
    
    frm.doc.total_additional_cost = frm.doc.production_additional_cost_details.reduce((sum,item)=>{
        return sum += item.amount
    },0)

}
// Following Function calculates total quantity of CR, MR, RW, OK
async function calculate_total_quantity(frm, cdt, cdn, rej_type, field,wt_field) {
    let d = locals[cdt][cdn];
    d.total_quantity = (d.mr_qty || 0) + (d.cr_qty || 0) + (d.ok_qty || 0) + (d.rw_qty || 0) + (d.in_process_qty || 0);
    if(d.operation_start_date_time && d.operation_end_date_time && d.total_quantity){
        d.actual_cycle_time_in_min = d.operation_working_time / d.total_quantity
    }else{
        d.actual_cycle_time_in_min = d.cycle_time
    }
    d.earning_min = ((d.actual_cycle_time_in_min) * d.total_quantity) + d.setup_time_in_min 
    frm.refresh_field("machining_operation_details");

    const item_working_time = frm.doc.machining_finished_item_details.filter(ele => d.item == ele.finished_item_code)[0].working_time
    const current_working_time = frm.doc.machining_operation_details.reduce((sum, item) => {
        if (d.item == item.item) {
            return sum + item.earning_min;
        }
        return sum;
    }, 0);

    // if (current_working_time > item_working_time) {
    //     locals[cdt][cdn][field] = 0
    //     locals[cdt][cdn][wt_field] = 0
        
    //     d.total_quantity = (d.mr_qty || 0) + (d.cr_qty || 0) + (d.ok_qty || 0) + (d.rw_qty || 0) + (d.in_process_qty || 0);
    //     d.total_weight = (d.mr_weight || 0) + (d.cr_weight || 0) + (d.ok_weight || 0) + (d.rw_weight || 0) + (d.in_process_weight || 0);
    //     frappe.msgprint("current working time Exceeded defined working time")
    //     frm.refresh_field("machining_operation_details")
    //     return
    // }

    if (rej_type != "OK" && rej_type != "In Process") {
        console.log((await frappe.db.get_value("MachineShop Setting",self.company,rej_type.toLowerCase()+"_target_warehouse")).message[rej_type.toLowerCase()+"_target_warehouse"])
        await frm.call({
            method: "add_rejection_row",
            doc: frm.doc,
            args: {
                params: {
                    "finished_item": d.item,
                    "finished_item_name": d.finished_item_name,
                    "raw_item_code": d.raw_item_code,
                    "raw_item_name": d.raw_item_name,
                    "operation_code": d.operation,
                    "operation_name": d.operation_name,
                    "rejection_type": rej_type,
                    "rejection_qty": locals[cdt][cdn][field],
                    "target_warehouse": (await frappe.db.get_value("MachineShop Setting",frm.doc.company,rej_type.toLowerCase()+"_target_warehouse")).message[rej_type.toLowerCase()+"_target_warehouse"]
                }

            }
        })
    }
   
    await frm.call({
        method: "add_downtime_row",
        doc: frm.doc,
        args: {
            "machine": frm.doc.machining_operation_details.length == 1 ? (d.machine || "") : null
        }
    })
    // }

}

// Following Function calculated Total weight of MR, CR, RW, OK
async function calculate_total_weight(frm, cdt, cdn, rej_type, field) {
    let d = locals[cdt][cdn];
    if (d.item) {
        const field_qty = d[rej_type.toLowerCase() + "_qty"];
        const item_weight = (await frappe.db.get_value("Item", d.item, "custom_machining_weight")).message.custom_machining_weight
        locals[cdt][cdn][field] = (field_qty || 0) * (item_weight || 0)
        d.total_weight = (d.mr_weight || 0) + (d.cr_weight || 0) + (d.ok_weight || 0) + (d.rw_weight || 0) + (d.in_process_weight || 0);
        frm.refresh_field("machining_operation_details")
    }
}

frappe.ui.form.on("Machining Finished Item Details", {
    item: async function (frm, cdt, cdn) { 
        var d = locals[cdt][cdn]
        frm.doc.machining_finished_item_details.forEach((item) => {
            if (item.item == d.item && item.idx !== d.idx) { 
                d.item = d.item_name = "" 
                frm.refresh_field("machining_finished_item_details")
                frappe.msgprint("Item is already present Choose another One")
                frm.trigger("item")
                return
            }
        })

        if (d.item) { 
            var doc = (await frappe.db.get_doc("MachineShop Processflow", d.item)) 
            d.target_warehouse = doc.finished_item_warehouse
            d.finished_item_group = doc.finished_item_group
            if (frm.doc.machining_finished_item_details.length == 1) {
                d.working_time = frm.doc.required_time
            }

            frm.refresh_field("machining_finished_item_details")
            let msp_names = []
            frm.doc.machining_finished_item_details.forEach(ele => { msp_names.push(ele.item) }) // TODO

            await frm.call({
                method: "append_operations",
                doc: frm.doc,
                args: {
                    "msp": msp_names
                }
            })

        }
    },
    working_time: async function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        tot_work_time = frm.doc.machining_finished_item_details.reduce((sum, item) => sum + item.working_time, 0)
        if (tot_work_time > frm.doc.required_time) {
            d.working_time = ""
            frm.refresh_field("machining_finished_item_details")
            frappe.msgprint(`Working time exceeded Required time by <b>${Math.abs(tot_work_time - frm.doc.required_time)} Min</b>`)
            return
        }

    },

    machining_finished_item_details_remove: async function (frm, cdt, cdn) {
        let msp_names = []
        frm.doc.machining_finished_item_details.forEach(ele => { msp_names.push(ele.item) }) // TODO
        await frm.call({
            method: "append_operations",
            doc: frm.doc,
            args: {
                "msp": msp_names
            }
        })
    }

});

frappe.ui.form.on("Machining Operation Details", {
    mr_qty: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "MR", "mr_qty","mr_weight");
        await calculate_total_weight(frm, cdt, cdn, "MR", "mr_weight");
    },
    cr_qty: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "CR", "cr_qty","cr_weight");
        await calculate_total_weight(frm, cdt, cdn, "CR", "cr_weight");
    },
    ok_qty: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "OK", "ok_qty","ok_weight");
        await calculate_total_weight(frm, cdt, cdn, "OK", "ok_weight");
    },
    rw_qty: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "RW", "rw_qty","rw_weight");
        await calculate_total_weight(frm, cdt, cdn, "RW", "rw_weight");
    },
    in_process_qty: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "In Process", "in_process_qty","in_process_weight");
        await calculate_total_weight(frm, cdt, cdn, "in_process", "in_process_weight");
    },
    operation_start_date_time: async function(frm,cdt,cdn){
        var d = locals[cdt][cdn]
        if(d.operation_start_date_time && d.operation_end_date_time){
            const time = await calculateDuration(frm, d.operation_start_date_time, d.operation_end_date_time);
            d.operation_working_time = time
        }
        frm.refresh_fields();

    },
    operation_end_date_time: async function(frm,cdt,cdn){
        var d = locals[cdt][cdn]
        if(d.operation_start_date_time && d.operation_end_date_time){
            const time = await calculateDuration(frm, d.operation_start_date_time, d.operation_end_date_time);
            d.operation_working_time = time
        }
        frm.refresh_fields();

    }




});
frappe.ui.form.on("Machining Downtime Reasons Details",{
    "time":async function(frm,cdt,cdn){
        let d = locals[cdt][cdn]
        if(d.time <= 0){
            frm.clear_table("downtime_reason_details")
            frm.add_child("downtime_reason_details",{
                "time": frm.doc.total_downtime - frm.doc.downtime_reason_details.reduce((sum, item) => sum + item.time, 0)
            })
        }
        if(frm.doc.downtime_reason_details.reduce((sum, item) => sum + item.time, 0) > frm.doc.total_downtime){
            frappe.msgprint(`Time exceeded total downtime by <b>${Math.abs(frm.doc.downtime_reason_details.reduce((sum, item) => sum + item.time, 0) - frm.doc.total_downtime)} Min</b>`)
            let total_sum = 0
            frm.doc.downtime_reason_details.forEach(item => {
                if(item.idx != d.idx){
                    total_sum += item.time
                 }
            })
            d.time = frm.doc.total_downtime - total_sum
        
        }

        if(frm.doc.downtime_reason_details.reduce((sum, item) => sum + item.time, 0) < frm.doc.total_downtime){
            frm.add_child("downtime_reason_details",{
                "time": frm.doc.total_downtime - frm.doc.downtime_reason_details.reduce((sum, item) => sum + item.time, 0)
            })
        }
       
        frm.refresh_field("downtime_reason_details")

    }
})

frappe.ui.form.on("Machining Rejection Reasons Details", {
    
    rejection_qty: async function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if (d.rejection_qty <= 0) {
            d.rejection_qty = 1
            frappe.msgprint("zero or below zero is not allowed")
            frm.refresh_field("rejected_items_reasons")
            return
        }
        let total_rej_qty = 0
        let current_rej_qty = 0
        frm.doc.machining_operation_details.forEach(item => {
            if (item.item == d.finished_item && item.operation == d.operation_code) {
                total_rej_qty += item[(d.rejection_type).toLowerCase() + "_qty"]
            }
        })
        // console.log("total_rej_qty: " + total_rej_qty)
        frm.doc.rejected_items_reasons.forEach(item => {
            if (item.item == d.item && d.rejection_type == item.rejection_type && item.operation_code == d.operation_code) {
                current_rej_qty += item.rejection_qty
            }
        })
        // console.log("current_rej_qty: " + current_rej_qty)
        if (current_rej_qty >= total_rej_qty) {
            if (current_rej_qty == total_rej_qty) {
                return
            }
            d.rejection_qty = 1
            frappe.msgprint(`Total Rejection quantity defined in Machining Operation Details is <b>${total_rej_qty}</b> and Entered Total is rejection is <b>${current_rej_qty}</b>`)
            frm.refresh_field("rejected_items_reasons")
        
            return
        }
        await frm.call({
            method: "update_rejection_row",
            doc: frm.doc,
            args: {
                params: {
                    "operation_code": d.operation_code,
                    "finished_item": d.finished_item,
                    "finished_item_name": d.finished_item_name,
                    "raw_item_code": d.raw_item_code,
                    "raw_item_name": d.raw_item_name,
                    "operation_name": d.operation_name,
                    "rejection_type": d.rejection_type,
                    "rejection_qty": total_rej_qty - current_rej_qty,
                    "target_warehouse": d.target_warehouse
                },
                row_idx: d.idx
            }
        })
    }
});

frappe.ui.form.on("Machining", {
    shift_start_date_time: async function (frm) {

        if (frm.doc.shift_start_date_time && frm.doc.shift_end_date_time) {
            const time = await calculateDuration(frm, frm.doc.shift_start_date_time, frm.doc.shift_end_date_time);
            frm.set_value('total_working_hours', time/60); 
        }
        frm.refresh_fields();

    },
    shift_end_date_time: async function (frm) {
        if (frm.doc.shift_start_date_time && frm.doc.shift_end_date_time) {
            const time = await calculateDuration(frm, frm.doc.shift_start_date_time, frm.doc.shift_end_date_time);
            frm.set_value('total_working_hours', time/60); 

        }
        frm.refresh_fields();

    },
    
    onload: function (frm) {
        frm.set_intro('Please Select Shift Time To fill Other details', 'red');
    },
    shift_time: async function (frm) {
        frm.doc.required_time = (await frappe.db.get_value("MachineShop Shift",frm.doc.shift_time,"minutes")).message.minutes
        frm.refresh_fields()
        if(frm.doc.required_time){
            frm.set_intro('')
        }else{
            frm.set_intro('Please Select Shift Time To fill Other details', 'red');
        }
    },
    refresh: function (frm) {
        const opr_addRowButton = frm.fields_dict['machining_operation_details'].grid.wrapper.find('.grid-add-row');
        const rej_addRowButton = frm.fields_dict['rejected_items_reasons'].grid.wrapper.find('.grid-add-row');
        opr_addRowButton.off('click').on('click', function (e) {
            e.stopImmediatePropagation();
            frappe.show_alert("<b>Machining Operation Details</b> Details Table is automatically filled based on seleced machineshop processflow")
        });
        rej_addRowButton.off('click').on('click', function (e) {
            e.stopImmediatePropagation();
            frappe.show_alert("<b>Machining Rejection Reasons Details</b> Table is automatically filled based on seleced machineshop processflow")

        });

    },
    before_save: async function (frm) {
        await frm.doc.machining_finished_item_details.forEach(item => {
            if(item.item){
                let total_opr_qty = 0
                frm.doc.machining_operation_details.forEach(opr_item => {
                    if(opr_item.machineshop_processflow == item.item){
                        total_opr_qty += opr_item.total_quantity
                    }
                })
                if(total_opr_qty <= 0){
                    frappe.throw(`Total Operation Qty <b>${item.item}</b> is zero in Machining Operation Details`)
                    return
                }
            }
        })
        await calculateDuration(frm, frm.doc.shift_start_date_time, frm.doc.shift_end_date_time);
        await set_total(frm)
        const tot_work_time = frm.doc.machining_finished_item_details.reduce((sum, item) => sum + item.working_time, 0)
        if (tot_work_time != frm.doc.required_time) {
            frappe.throw(`Total working Time and Required time mismatched by <b>${Math.abs(tot_work_time - frm.doc.required_time)} Min</b>`)
            return
        }
        for (const item of frm.doc.machining_operation_details) {
            let tot_mr_rej = item.mr_qty || 0;
            let tot_cr_rej = item.cr_qty || 0;
            let tot_rw_rej = item.rw_qty || 0;

            let tot_mr_rej_reason = 0;
            let tot_cr_rej_reason = 0;
            let tot_rw_rej_reason = 0;


            for (const rej of frm.doc.rejected_items_reasons) {
                if (rej.finished_item == item.item && rej.operation_code == item.operation) {
                    if (rej.rejection_type === 'MR') {
                        tot_mr_rej_reason += rej.rejection_qty;
                    } else if (rej.rejection_type === 'CR') {
                        tot_cr_rej_reason += rej.rejection_qty;
                    } else if (rej.rejection_type === 'RW') {
                        tot_rw_rej_reason += rej.rejection_qty;
                    }
                }
            }


            if (tot_mr_rej !== tot_mr_rej_reason) {
                frappe.throw(`Mismatch in MR rejections for item <b>${item.item}</b>. You've recorded <b>${tot_mr_rej}</b> rejected quantity, but provided reasons for only <b>${tot_mr_rej_reason}</b>. Please specify reasons for the remaining <b>${tot_mr_rej - tot_mr_rej_reason}</b> MR rejections.`);
            }

            if (tot_cr_rej !== tot_cr_rej_reason) {
                frappe.throw(`Mismatch in CR rejections for item <b>${item.item}</b>. You've recorded <b>${tot_cr_rej}</b> rejected quantity, but provided reasons for only <b>${tot_cr_rej_reason}</b>. Please specify reasons for the remaining <b>${tot_cr_rej - tot_cr_rej_reason}</b> CR rejections.`);
            }

            if (tot_rw_rej !== tot_rw_rej_reason) {
                frappe.throw(`Mismatch in RW rejections for item <b>${item.item}</b>. You've recorded <b>${tot_rw_rej}</b> rejected quantity, but provided reasons for only <b>${tot_rw_rej_reason}</b>. Please specify reasons for the remaining <b>${tot_rw_rej - tot_rw_rej_reason}</b> RW rejections.`);
            }

        }


        const total_earn_min = frm.doc.machining_operation_details.reduce((sum, item) => sum + item.earning_min, 0);
        const total_downtime = frm.doc.downtime_reason_details.reduce((sum, item) => sum + item.time, 0)

        if (!(frm.doc.required_time == (total_earn_min + total_downtime))) {
            frappe.throw(`Provide Downtime Reason for Remaining <b>${Math.abs(frm.doc.required_time - (total_earn_min + total_downtime))} Min </b>`)
            return
        }
        // if (frm.doc.production_additional_cost_details.length == 0) {
            await frm.call({
                method: "add_additional_cost",
                doc: frm.doc
            })

        // }
        await frm.call({
            method:"remove_zero_rejections",
            doc:frm.doc
        })

    },
    setup: async function (frm, cdt, cdn) {
        frm.set_query("item", "machining_finished_item_details", function (doc, cdt, cdn) { // todo
            let d = locals[cdt][cdn];
            return {
                filters: {
                    'is_enable': true
                }
            };
        });
       
       
        frm.set_query("rejection_reason","rejected_items_reasons",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    'rejection_type': d.rejection_type
                }
            }
        })
        frm.set_query("target_warehouse","machining_operation_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    "Company":frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("source_warehouse","machining_operation_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    "Company":frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("target_warehouse","machining_finished_item_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    "Company":frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("item","machining_finished_item_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    "company":frm.doc.company,
                    "is_enable":1
                }
            }
        })

    },
});














