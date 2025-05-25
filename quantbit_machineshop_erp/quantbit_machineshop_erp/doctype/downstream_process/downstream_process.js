// Copyright (c) 2024, Quantbit Technologies Pvt Ltd and contributors
// For license information, please see license.txt
// temp change


//Avantika

async function calculateDuration(frm, start_date_time = null, end_date_time = null) {
    if (!start_date_time|| !end_date_time) {
        frappe.throw("Both Shift Start Date Time and Shift End Date Time time are required.");
        return;
    }

    let start_time = new Date(start_date_time);  
    let end_time = new Date(end_date_time);
    // console.log(end_date_time)

    let diff_ms = end_time.getTime() - start_time.getTime();
    // console.log(diff_ms);

    if (diff_ms < 0) {
        frappe.show_alert("Required Time cannot be negative")
        frm.set_value('total_working_time', 0);  
        return;
    }

    // Calculate the duration in minutes if no crossing midnight
    const minutes = diff_ms / (1000 * 60);
    await frm.set_value('total_working_time', Math.floor(minutes));
    frm.refresh_fields();
}
//


async function set_total(frm){
    let total_in_process_qty = total_in_process_wt = total_fr_qty = total_cr_qty = total_ok_qty = total_rw_qty = total_fr_wt = total_cr_wt = total_ok_wt = total_rw_wt = total_qty = total_qty_wt = total_rej_qty = total_rej_wt = 0
    frm.doc.quality_inspection_details.forEach(item => {
        total_fr_qty += item.fr_quantity || 0
        total_cr_qty += item.cr_quantity || 0
        total_ok_qty += item.ok_quantity || 0
        total_rw_qty += item.rw_quantity || 0
        total_in_process_qty += item.in_process_qty || 0
        total_fr_wt += item.fr_weight || 0
        total_cr_wt += item.cr_weight || 0
        total_ok_wt += item.ok_weight || 0
        total_rw_wt += item.rw_weight || 0
        total_in_process_wt += item.in_process_wt || 0
        total_qty +=(item.fr_quantity || 0) + (item.cr_quantity || 0) + (item.ok_quantity || 0) + (item.rw_quantity || 0) + (item.in_process_qty || 0)
        total_qty_wt += (item.fr_weight || 0) + (item.cr_weight || 0) + (item.ok_weight || 0) + (item.rw_weight || 0) + (item.in_process_wt || 0)
        total_rej_qty += (item.fr_quantity || 0) + (item.cr_quantity || 0) + (item.rw_quantity || 0)
        total_rej_wt += (item.fr_weight || 0) + (item.cr_weight || 0) + (item.rw_weight || 0)
    })
    frm.doc.total_fr_qty = total_fr_qty
    frm.doc.total_cr_qty = total_cr_qty
    frm.doc.total_ok_qty = total_ok_qty
    frm.doc.total_rw_qty = total_rw_qty
    frm.doc.total_fr_weight = total_fr_wt
    frm.doc.total_cr_weight = total_cr_wt
    frm.doc.total_ok_weight = total_ok_wt
    frm.doc.total_rw_weight = total_rw_wt
    frm.doc.total_quantity = total_qty
    frm.doc.total_qty_weight = total_qty_wt
    frm.doc.total_rejection_qty = total_rej_qty
    frm.doc.total_rejection_weight = total_rej_wt
    frm.doc.total_additional_cost = frm.doc.downstream_additional_cost_details.reduce((sum,item)=>{
        return sum += item.amount
    },0)
    frm.doc.total_casting_quantity = frm.doc.downstream_casting_details.reduce((sum,item) => {
        return sum += item.quantity
    }, 0);
    frm.doc.total_casting_weight = frm.doc.downstream_casting_details.reduce((sum, item) => {
        return sum += item.total_weight
    }, 0);


}
async function calculate_total_quantity(frm, cdt, cdn, rej_type, field) {
    let d = locals[cdt][cdn];
    // d.total_casting_quantity = (d.fr_quantity || 0) + (d.cr_quantity || 0) + (d.ok_quantity || 0) + (d.rw_quantity || 0) + (d.in_process_qty || 0);
    // frm.refresh_field("quality_inspection_details")
    // // d.earning_min = d.cycle_time * d.total_quantity
    // frm.refresh_field("quality_inspection_details");
    // console.log(field);


    // const item_working_time = frm.doc.machining_finished_item_details.filter(ele => d.item == ele.finished_item_code)[0].working_time
    // const current_working_time = frm.doc.machining_operation_details.reduce((sum, item) => {
    //     if (d.item == item.item) {
    //         return sum + item.earning_min;
    //     }
    //     return sum;
    // }, 0);

    // if (current_working_time > item_working_time) {
    //     locals[cdt][cdn][field] = ""
    //     frappe.msgprint("current working time Exceeded defined working time")
    //     frm.refresh_field("machining_operation_details")
    //     return
    // }
    console.log(field)
    if (!d.total_casting_quantity) {
        frappe.throw("select quantity in downstream casting details")
        return
    }
    const total_qty = (d.fr_quantity || 0) + (d.cr_quantity || 0) + (d.ok_quantity || 0) + (d.rw_quantity || 0) + (d.in_process_quantity || 0);
    

    if (total_qty > d.total_casting_quantity) {
        locals[cdt][cdn][field] = 0
        frappe.msgprint("Total quantity cannot be more than total casting quantity")
        return
    }

    if (rej_type != "OK" && rej_type != "in_process") {
        await frm.call({
            method: "add_rejection_row",
            doc: frm.doc,
            args: {
                params: {
                    "finished_item_code": d.finished_item_code,
                    "finished_item_name": d.finished_item_name,
                    "downstream_rejection_type": rej_type,
                    "target_warehouse": (await frappe.db.get_value("MachineShop Setting",frm.doc.company,rej_type.toLowerCase()+"_target_warehouse")).message[rej_type.toLowerCase()+"_target_warehouse"],
                    "machining_id": d.machining_id,
                    "machineshop_processflow": d.machineshop_processflow,
                    "quantity": locals[cdt][cdn][field],
                    "uom": d.uom,
                    "weight": d.weight,
                    "total_weight": locals[cdt][cdn][field] * d.weight
                }

            }
        })
    }
    

    // await frm.call({
    //     method: "add_downtime_row",
    //     doc: frm.doc,
    //     args: {
    //         "machine": frm.doc.machining_operation_details.length == 1 ? (d.machine || "") : null
    //     }
    // })
    // }

}

// Following Function calculated Total weight of MR, CR, RW, OK
async function calculate_total_weight(frm, cdt, cdn, rej_type, field) {
    let d = locals[cdt][cdn];
    if (d.finished_item_code) {
        // console.log("weight");
        
        const field_qty = d[rej_type.toLowerCase() + "_quantity"];
        // console.log(field_qty);

        const item_weight = (await frappe.db.get_value("Item", d.finished_item_code, "custom_machining_weight")).message.custom_machining_weight
        locals[cdt][cdn][field] = (field_qty || 0) * (item_weight || 0)
        // console.log(field_qty, item_weight)
        // d.total_casting_weight = (d.fr_weight || 0) + (d.cr_weight || 0) + (d.ok_weight || 0) + (d.rw_weight || 0);
        frm.refresh_field("quality_inspection_details")
    }
}

frappe.ui.form.on('Downstream Process', {
    setup: function(frm){
        frm.set_query("downstream_rejection_reason","downstream_rejected_reasons_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    'rejection_type': d.downstream_rejection_type
                }
            }
        })
        frm.set_query("target_warehouse","downstream_casting_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("source_warehouse","downstream_casting_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("source_warehouse","downstream_raw_material_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("target_warehouse","downstream_rejected_reasons_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    'company': frm.doc.company,
                    "is_group":0
                }
            }
        })
        frm.set_query("expense_head_account","downstream_additional_cost_details",function(doc,cdt,cdn){
            let d = locals[cdt][cdn]
            return {
                filters: {
                    'company': frm.doc.company
                }
            }
        })
    },

    start_date_time: async function (frm) {
        // console.log(frm.doc.start_date_time)
        if (frm.doc.end_date_time && frm.doc.start_date_time) {
            await calculateDuration(frm, frm.doc.start_date_time, frm.doc.end_date_time);
        }
    },
    end_date_time: async function (frm) {
        if (frm.doc.end_date_time && frm.doc.start_date_time) {
            await calculateDuration(frm, frm.doc.start_date_time, frm.doc.end_date_time);
        }
    },
    before_save: async function (frm) {
        await calculateDuration(frm, frm.doc.start_date_time, frm.doc.end_date_time);
    },


    onload: function (frm) {
        frm.set_intro('Please Select Downstream Process To fill Other details', 'red');
    },
    downstream_process: function (frm) {
        if(frm.doc.downstream_process){
            frm.set_intro('')
        }else{
            frm.set_intro('Please Select Downstream Process To fill Other details', 'red');
        }
    },
    validate: async function(frm) {
        await set_total(frm)
    },
    refresh: function (frm) {
        const rej_addRowButton = frm.fields_dict['downstream_rejected_reasons_details'].grid.wrapper.find('.grid-add-row');
        const quality_addRowButton = frm.fields_dict['quality_inspection_details'].grid.wrapper.find('.grid-add-row');
        const addcost_delete_btn = frm.fields_dict['downstream_additional_cost_details'].grid.wrapper.find('.grid-remove-rows')
        const quality_delete_btn = frm.fields_dict['quality_inspection_details'].grid.wrapper.find('.grid-remove-rows')

        rej_addRowButton.css('text-decoration', 'line-through');
        quality_addRowButton.css('text-decoration', 'line-through');
        addcost_delete_btn.css('text-decoration', 'line-through');
        quality_delete_btn.css('text-decoration', 'line-through');
        
        
        quality_addRowButton.off('click').on('click', function (e) {
            e.stopImmediatePropagation();
            frappe.show_alert("<b>Downstream Quality Inspection Details</b> Details Table is automatically filled based on seleced Downstream Casting Details")
        });
        rej_addRowButton.off('click').on('click', function (e) {
            e.stopImmediatePropagation();
            frappe.show_alert("<b>Downstream Rejected Reasons Details</b> Table is automatically filled based on seleced Downstream Quality Inspection Details")

        });
        addcost_delete_btn.off('click').on('click', function (e) {
            e.stopImmediatePropagation();
            frappe.show_alert("<b>Downstream Additional Cost Details</b> Table is automatically filled based on seleced Downstream Casting Details")

        });
        quality_delete_btn.off('click').on('click', function (e) {
            e.stopImmediatePropagation();
            frappe.show_alert("<b>Downstream Additional Cost Details</b> Table is automatically filled based on seleced Downstream Casting Details")

        });

    },

    machining: async function (frm, cdt, cdn) {
        await frm.call({
            method: "add_dsp_casting_details",
            doc: frm.doc,
            callback: (r) => {
                frm.refresh_field("downstream_casting_details")
            }

        })
    },
});

frappe.ui.form.on('Downstream Casting Details', {
    source_warehouse: async function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if (d.source_warehouse){
            const bal = await frm.call({
                method:"get_balance",
                doc:frm.doc,
                args:{
                    "item_code":d.finished_item_code,
                    "warehouse":d.source_warehouse
                }
            })
            console.log(bal)
            d.available_stock = bal.message || 0
        }
        frm.refresh_fields()
    },
    quantity: async function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        d.total_weight = d.quantity * d.weight
        
        frm.doc.quality_inspection_details.forEach(item => {
            if (item.finished_item_code == d.finished_item_code && item.machining_id == d.machining && item.machineshop_processflow == d.machineshop_processflow) {
                item.total_casting_quantity = d.quantity
                item.total_casting_weight = d.total_weight
            }
        })
        if (d.quantity) {
            if (d.machining){
                let idx = 0
                let mac_doc = await frappe.db.get_doc("Machining",d.machining)
                mac_doc.machining_operation_details.forEach(item=>{
                    if(item.item == d.finished_item_code){
                        idx = idx + 1
                    }
                })
                
                mac_qty = mac_doc.machining_operation_details[idx-1].ok_qty
                if(d.quantity > mac_qty){
                    frappe.msgprint(`Machining quantity is ${mac_qty} and you entered ${d.quantity}`)
                    d.quantity = 0
                    return
            }
            }
            
            frm.doc.downstream_raw_material_details.forEach(item => {
                if (item.finished_item_code == d.finished_item_code && item.machining == d.machining && item.machineshop_processflow == d.machineshop_processflow) {
                    item.required_quantity = item.used_quantity = (item.raw_material_qty || 0) * (d.quantity || 0)
                }
            })
        }
        else if(d.quantity && !d.machining){
            if(d.quantity > d.available_stock){
                frappe.msgprint(`Available stock is ${d.available_stock} and you entered ${d.quantity}`)
                d.quantity = 0
                return
            }
        }
        
        
        frm.refresh_fields("downstream_raw_material_details")
        frm.refresh_field("downstream_casting_details")
        frm.refresh_field("quality_inspection_details")
    },
    finished_item_code: async function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        await frm.call({
            method: "add_finished_item",
            doc: frm.doc,
            args: {
                finished_item_code: d.finished_item_code,
            },
            callback: async (r) => {
                if (r.message) {
                    row = r.message
                    d.machineshop_processflow = row[0]
                    d.finished_item_name = row[1]
                    d.source_warehouse = row[2]
                    d.target_warehouse = row[3]
                    d.available_stock = row[4]
                    d.downstream_process_rate = row[5]
                    d.uom = row[6]
                    d.weight = row[7]
                    d.is_manually_added = true
                    frm.refresh_field("downstream_casting_details")
                    await frm.call({
                        method: "add_quality_and_raw_material",
                        doc: frm.doc,

                    })
                 

                }
            }


        })
    },
    downstream_casting_details_remove: async function (frm, cdt, cdn) {
        await frm.call({
            method: "add_quality_and_raw_material",
            doc: frm.doc

        })
    }
});


frappe.ui.form.on("Downstream Quality Inspection Details", {
    fr_quantity: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "FR", "fr_quantity");
        await calculate_total_weight(frm, cdt, cdn, "FR", "fr_weight");
    },
    cr_quantity: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "CR", "cr_quantity");
        await calculate_total_weight(frm, cdt, cdn, "CR", "cr_weight");
    },
    ok_quantity: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "OK", "ok_quantity");
        await calculate_total_weight(frm, cdt, cdn, "OK", "ok_weight");
    },
    rw_quantity: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "RW", "rw_quantity");
        await calculate_total_weight(frm, cdt, cdn, "RW", "rw_weight");
    },
    in_process_quantity: async function (frm, cdt, cdn) {
        await calculate_total_quantity(frm, cdt, cdn, "in_process", "in_process_quantity");
        await calculate_total_weight(frm, cdt, cdn, "in_process", "in_process_weight");
    },
    all_goes_to:async function (frm, cdt, cdn){
        var d = locals[cdt][cdn]
        const rej_type = d.all_goes_to
        console.log(d.all_goes_to)
        d[rej_type.toLowerCase() + "_quantity"] = d.total_casting_quantity - d.ok_quantity 
        await calculate_total_weight(frm, cdt, cdn, d.all_goes_to, `${rej_type.toLowerCase()}_weight`);
        
        frm.refresh_field("quality_inspection_details")
        
    }

});

frappe.ui.form.on("Downstream Rejected Reasons Details", {
    quantity: async function (frm, cdt, cdn) {
        var d = locals[cdt][cdn]
        if (d.quantity <= 0) {
            d.quantity = 1
            frappe.msgprint("zero or below zero is not allowed")
            frm.refresh_field("downstream_rejected_reasons_details")
            return
        }
        let total_rej_qty = 0
        let current_rej_qty = 0
        frm.doc.quality_inspection_details.forEach(item => {
            if (item.finished_item_code == d.finished_item_code && item.machineshop_processflow == d.machineshop_processflow && item.machining_id == d.machining_id) {
                total_rej_qty += item[(d.downstream_rejection_type).toLowerCase() + "_quantity"]
            }
        })
        // console.log("total_rej_qty: " + total_rej_qty)
        frm.doc.downstream_rejected_reasons_details.forEach(item => {
            if (item.finished_item_code == d.finished_item_code && d.machining_id == item.machining_id && item.machineshop_processflow == d.machineshop_processflow && item.downstream_rejection_type == d.downstream_rejection_type) {
                current_rej_qty += item.quantity
            }
        })
        // console.log("current_rej_qty: " + current_rej_qty)
        if (current_rej_qty >= total_rej_qty) {
            if (current_rej_qty == total_rej_qty) {
                return
            }
            d.quantity = 1
            frappe.msgprint(`Total Rejection quantity defined in Downstream Quality Inspection Details is <b>${total_rej_qty}</b> and Entered Total is rejection is <b>${current_rej_qty}</b>`)
            frm.refresh_field("downstream_rejected_reasons_details")
            return
        }
        await frm.call({
            method: "update_rejection_row",
            doc: frm.doc,
            args: {
                params: {
                    "machining_id": d.machining_id,
                    "finished_item_code": d.finished_item_code,
                    "finished_item_name": d.finished_item_name,
                    "uom": d.uom,
                    "weight": d.weight,
                    "machineshop_processflow": d.machineshop_processflow,
                    "downstream_rejection_type": d.downstream_rejection_type,
                    "quantity": total_rej_qty - current_rej_qty,
                    "target_warehouse": d.target_warehouse,
                    "total_weight":d.weight * frm.doc.quantity
                },
                row_idx: d.idx
            },
            callback:(r)=>{
                frm.doc.downstream_rejected_reasons_details.forEach(item => {
                    item.total_weight = item.quantity * item.weight
                })
                frm.refresh_field("downstream_rejected_reasons_details")

            }
        })
    }
});




