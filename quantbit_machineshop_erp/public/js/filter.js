frappe.provide('frappe.custom');
frappe.custom.set_filters_for_doctype = function(doctype_name, frm) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "MachineShop Filter Setting",
            filters: {
                "doctype_name": doctype_name
            },
            fields: ['name', "docfield_name", "docchild_name", "doclink_name"],
        },
        callback: async function(response) {
            if (response.message) {
                let data = response.message;
                data.forEach(async function(item) {
                    let field = item.docfield_name;
                    let child_field = item.docchild_name
                    let filter_arg
                    if (item.filterfield_field) {
                        filter_arg = frm.doc[item.filterfield_field];
                    } else {
                        filter_arg = item.filterfield_data;
                    }
                    let filter = await get_filter_list(frm, item.name, item.doclink_name);
                    if (child_field) {
                        frm.set_query(field, child_field, function() {
                            return {
                                filters: filter
                            };
                        });
                    } else {
                        frm.set_query(field, function() {
                            return {
                                filters: filter
                            };
                        });
                    }
                });
            }
        }
    });
};



async function get_filter_list(frm, filters_parent, doclink_name) {
    let filter_list = []
    const val = await frappe.db.get_doc("MachineShop Filter Setting", filters_parent)
    data = val.foundry_filter_setting_doctype_details
    data.forEach(function(item) {
        let filter_arg
        if (item.filterfield_field) {
            filter_arg = frm.doc[item.filterfield_field];
        } else {
            filter_arg = item.filterfield_data;
        }
        let filter = [doclink_name, item.filterfield_name, item.filterfield_type, filter_arg];
        filter_list.push(filter)

    });
    return filter_list;
}

frappe.ui.form.on('Item', {
    setup: function(frm) {
        frm.set_query("custom_machining_draw", function() {
            return {
                filters: [
                    ['MachineShop Drawing Master', 'item_code', '=', frm.doc.item_code],
                ]
            };
            
        });
    }	
});