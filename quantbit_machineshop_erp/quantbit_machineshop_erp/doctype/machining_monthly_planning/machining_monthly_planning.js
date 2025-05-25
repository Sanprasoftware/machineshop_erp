// Copyright (c) 2025, Quantbit Technlogies Pvt Ltd and contributors.....
// For license information, please see license.txt .....

frappe.ui.form.on("Item Machining Schedule", {
  item_code: async function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.item_code) {
      await frm.call({
        method: "get_actual_qty",
        args: {
          item_code: row.item_code
        },
        doc: frm.doc,
        callback: function (response) {
          if (response.message) {
            frappe.model.set_value(cdt, cdn, "actual_quantity", response.message);
            // Automatically calculate planned_quantity
            let scheduled_quantity = row.scheduled_quantity || 0;
            frappe.model.set_value(cdt, cdn, "planned_quantity", response.message - scheduled_quantity);
          }
        }
      });
    }
  },
  scheduled_quantity: async function (frm, cdt, cdn) {
    await frm.call({
      method: 'settle_available_quantity',
      doc: frm.doc,
    })
    frm.refresh_field('item_machining_schedule');
  },
  item_machining_schedule_move: async function (frm) {
    await frm.call({
      method: 'settle_available_quantity',
      doc: frm.doc,
    })
    frm.refresh_field('item_machining_schedule');
  },
});

frappe.ui.form.on("Machining Monthly Planning", {
  refresh: function(frm) {

    highlightOverBookedRows(frm);
  },
  
  get_machine_data: async function (frm) {
    frm.clear_table("machine_availability_summary");
    frm.clear_table("machine_availability");
    await frm.call({
      method: "get_machine_data",
      doc: frm.doc,
    });
    frm.refresh_field("machine_availability_summary");
    frm.refresh_field("machine_availability");
    frm.dirty();
    
    setTimeout(() => highlightOverBookedRows(frm), 300);
  },
  
  get_data: async function (frm) {
    frm.clear_table("item_machining_schedule");
    frm.clear_table("machine_availability_summary");
    frm.clear_table("machine_availability");
    await frm.call({
      method: "get_data",
      doc: frm.doc,
    });
    frm.refresh_field("item_machining_schedule");
    frm.refresh_field("machine_availability_summary");
    frm.refresh_field("machine_availability");
    frm.dirty();

    setTimeout(() => highlightOverBookedRows(frm), 300);
  },
  
  setup: async function (frm, cdt, cdn) {
    frm.set_query("machine_type", "machine_availability", function (doc, cdt, cdn) {
      let d = locals[cdt][cdn];
      return {
        filters: {
          // 'is_enable': true,
          'company': frm.doc.company
        }
      };
    }),
    frm.set_query("machine_type", "machine_availability_summary", function (doc, cdt, cdn) {
      let d = locals[cdt][cdn];
      return {
        filters: {
          // 'is_enable': true,
          'company': frm.doc.company
        }
      };
    }),
    frm.set_query("machine_name", "machine_availability_summary", function (doc, cdt, cdn) {
      let d = locals[cdt][cdn];
      return {
        filters: {
          // 'is_enable': true,
          'company': frm.doc.company
        }
      };
    });
    frm.set_query("machineshop_processflow", "item_machining_schedule", function (doc, cdt, cdn) {
      let d = locals[cdt][cdn];
      return {
        filters: {
          // 'is_enable': true,
          'company': frm.doc.company,
          'finished_item_code': d.item_code
        }
      };
    });
  }
});


// Function to highlight overbooked rows and percentage fields
function highlightOverBookedRows(frm) {
  if (!frm.doc.machine_availability || !frm.fields_dict.machine_availability) return;
  
  setTimeout(() => {
    frm.doc.machine_availability.forEach((row, index) => {
      if (row.total_booked_percentage > 100) {
        const $row = frm.fields_dict.machine_availability.$wrapper.find(`.grid-row[data-idx="${index + 1}"]`);
        $row.css('background-color', '#ffcccc');
        const $percentageInput = $row.find(`[data-fieldname="total_booked_percentage"] .form-control`);
        if ($percentageInput.length) {
          $percentageInput.css('background-color', '#ff9999');
        }
        
        
        const $percentageText = $row.find(`[data-fieldname="total_booked_percentage"] .field-area`);
        $percentageText.css({
          'color': 'red',
          'font-weight': 'bold'
        });
      }
    });
    
    
    $('.grid-row-open').each(function() {
      const docname = $(this).attr('data-name');
      if (docname) {
        const doc = locals["Machine Availability"][docname];
        if (doc && doc.total_booked_percentage > 100) {         
          const $percentageField = $(this).find(`[data-fieldname="total_booked_percentage"] .form-control`);
          $percentageField.css({
            'background-color': '#ff9999',
            'color': 'red',
            'font-weight': 'bold'
          });
        }
      }
    });
  }, 100);
}


frappe.ui.form.on("Machine Availability", {
  total_booked_percentage: function(frm, cdt, cdn) {
    highlightOverBookedRows(frm);
  },
  
  form_render: function(frm, cdt, cdn) {    
    const row = locals[cdt][cdn];
    if (row && row.total_booked_percentage > 100) {
      setTimeout(() => {
        const $percentageField = $(`[data-fieldname="total_booked_percentage"] .form-control`);
        $percentageField.css({
          'background-color': '#ff9999',
          'color': 'red',
          'font-weight': 'bold'
        });
      }, 200);
    }
  }
});